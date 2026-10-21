"""Trusted no-edit native control. Not an animation builder or art evaluator.

Imports bpy only inside the worker. Recipes never contain code, paths, camera
changes or pose edits. A future authoring vocabulary needs separate qualification.
"""
import hashlib
import json
from pathlib import Path

OBJECTS = ('horse.rig', 'HORSE hind support pivot', 'mounted leader',
           '320 articulated upper body mounted leader')


def validate(recipe):
    if not isinstance(recipe, dict) or set(recipe) != {'operation', 'frame', 'width', 'height', 'samples'}:
        raise ValueError('NIHANG_RECIPE_FIELDS')
    if recipe['operation'] not in {'nihang_save', 'nihang_render'}:
        raise ValueError('NIHANG_OPERATION')
    for key, lo, hi in [('frame', 252, 441), ('width', 64, 1080), ('height', 64, 1920), ('samples', 1, 32)]:
        if type(recipe[key]) is not int or not lo <= recipe[key] <= hi:
            raise ValueError('NIHANG_RECIPE_BOUND:' + key)
    return recipe


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def selected_state(bpy, frame):
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    def matrix(m):
        return [[round(float(v), 6) for v in row] for row in m]
    result = {'frame': frame, 'objects': {}, 'camera': scene.camera.name if scene.camera else None,
              'object_count': len(bpy.data.objects)}
    for name in OBJECTS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError('NIHANG_REQUIRED_OBJECT_MISSING:' + name)
        result['objects'][name] = {'type': obj.type, 'world': matrix(obj.matrix_world),
            'parent': obj.parent.name if obj.parent else None}
        if obj.pose:
            result['objects'][name]['bones'] = {bone.name: {
                'matrix': matrix(bone.matrix), 'basis': matrix(bone.matrix_basis)}
                for bone in sorted(obj.pose.bones, key=lambda b: b.name)}
    if not scene.camera:
        raise ValueError('NIHANG_CAMERA_MISSING')
    result['camera_matrix'] = matrix(scene.camera.matrix_world)
    result['camera_lens'] = scene.camera.data.lens
    result['autoexec_fail'] = bool(bpy.app.autoexec_fail)
    return result


def dependencies(bpy, root):
    """Scoped external-file inventory; not complete simulation portability."""
    found = {}
    for collection in ('images', 'libraries', 'cache_files', 'movieclips', 'sounds', 'fonts', 'volumes'):
        for item in getattr(bpy.data, collection):
            filename = getattr(item, 'filepath', '')
            if not filename or filename == '<builtin>' or getattr(item, 'packed_file', None):
                continue
            if collection == 'images' and item.source in {'GENERATED', 'VIEWER'}:
                continue
            resolved = Path(bpy.path.abspath(filename, library=getattr(item, 'library', None))).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError('NIHANG_EXTERNAL_DEPENDENCY_OUTSIDE_ROOT:' + item.name)
            if resolved.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.exr', '.hdr', '.tif', '.tiff', '.webp',
                    '.blend', '.abc', '.vdb', '.usd', '.usdc', '.ogg', '.wav', '.mp3', '.mp4', '.mov', '.bphys'}:
                raise ValueError('NIHANG_UNSUPPORTED_DEPENDENCY:' + item.name)
            if not resolved.is_file():
                raise ValueError('NIHANG_MISSING_DEPENDENCY:' + item.name)
            rel = str(resolved.relative_to(root))
            found[rel] = {'path': rel, 'sha256': digest_file(resolved)}
    return {'bindings': found, 'scope': 'Images, libraries, cache_files, clips, sounds, fonts, volumes; '
            'not arbitrary node paths or complete simulation-cache closure'}


def run(out, job):
    import bpy
    recipe = validate(job['recipe'])
    parent = Path(job['parent_native']).resolve(strict=True)
    root = Path(job['repository_root']).resolve(strict=True)
    if parent == (out / 'scene.blend').resolve() or not parent.is_relative_to(root):
        raise ValueError('NIHANG_PARENT_BOUNDARY')
    bpy.ops.wm.open_mainfile(filepath=str(parent), load_ui=False, use_scripts=False)
    state = selected_state(bpy, recipe['frame'])
    if state['autoexec_fail']:
        raise ValueError('NIHANG_DISABLED_SCRIPT_DEPENDENCY')
    deps = dependencies(bpy, root)
    (out / 'snapshot.json').write_text(json.dumps(state, sort_keys=True, indent=2) + '\n')
    (out / 'dependencies.json').write_text(json.dumps(deps, sort_keys=True, indent=2) + '\n')
    artifacts = ['snapshot.json', 'dependencies.json']
    if recipe['operation'] == 'nihang_save':
        bpy.context.preferences.filepaths.save_version = 0
        # Remap relative external paths so relocation does not change their target.
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'), check_existing=False,
                                  compress=True, relative_remap=True)
        artifacts.append('scene.blend')
    else:
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = recipe['samples']
        scene.cycles.seed = 333
        scene.render.resolution_x = recipe['width']
        scene.render.resolution_y = recipe['height']
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(out / 'frame.png')
        bpy.ops.render.render(write_still=True)
        artifacts.append('frame.png')
    return artifacts
