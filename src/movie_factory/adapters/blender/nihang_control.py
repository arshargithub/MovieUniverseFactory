"""Trusted no-edit native control. Not an animation builder or art evaluator.

Imports bpy only inside the worker. Recipes never contain code, paths, camera
changes or pose edits. A future authoring vocabulary needs separate qualification.
"""
import hashlib
import json
from pathlib import Path

OBJECTS = ('horse.rig', 'HORSE hind support pivot', 'mounted leader',
           '320 articulated upper body mounted leader')
# Exact diagnosed legacy320 defect, permitted ONLY for this unchanged negative
# control. It is not a working-rig certificate or a general invalid-driver waiver.
LEGACY_DRIVER_DEFECT = '054bf94aeb90448916005e7c0e8c5dbe163e7fbbea52cde230adf8c32ee0e21c'


def validate(recipe):
    if not isinstance(recipe, dict) or set(recipe) != {'operation', 'frame', 'width', 'height', 'samples'}:
        raise ValueError('NIHANG_RECIPE_FIELDS')
    if recipe['operation'] not in {'nihang_save', 'nihang_render', 'nihang_rig_inspect'}:
        raise ValueError('NIHANG_OPERATION')
    for key, lo, hi in [('frame', 252, 441), ('width', 64, 1080), ('height', 64, 1920), ('samples', 1, 32)]:
        if type(recipe[key]) is not int or not lo <= recipe[key] <= hi:
            raise ValueError('NIHANG_RECIPE_BOUND:' + key)
    return recipe


def rig_inventory(bpy):
    """Read-only ownership evidence. Never execute asset scripts or repair by inference."""
    rig = bpy.data.objects.get('horse.rig')
    if rig is None or rig.type != 'ARMATURE':
        raise ValueError('NIHANG_HORSE_RIG_MISSING')
    def vector(v): return [float(x) for x in v]
    def matrix(m): return [vector(row) for row in m]
    bones = {}
    for b in rig.pose.bones:
        constraints = []
        for c in b.constraints:
            row = {'name': c.name, 'type': c.type, 'influence': c.influence,
                   'mute': c.mute, 'valid': c.is_valid}
            for key in ('target', 'pole_target'):
                target = getattr(c, key, None)
                row[key] = target.name if target else None
            for key in ('subtarget', 'pole_subtarget', 'chain_count', 'pole_angle',
                        'use_stretch', 'owner_space', 'target_space', 'mix_mode'):
                if hasattr(c, key): row[key] = getattr(c, key)
            constraints.append(row)
        bones[b.name] = {'parent': b.parent.name if b.parent else None,
            'deform': b.bone.use_deform, 'head_rest': vector(b.bone.head_local),
            'tail_rest': vector(b.bone.tail_local), 'rest': matrix(b.bone.matrix_local),
            'head': vector(b.head), 'tail': vector(b.tail), 'matrix': matrix(b.matrix),
            'basis': matrix(b.matrix_basis), 'constraints': constraints,
            'properties': {k: v for k, v in b.items() if isinstance(v, (int, float, str, bool))}}
    drivers = []
    for owner in (rig, rig.data):
        ad = owner.animation_data
        for fc in ad.drivers if ad else []:
            d = fc.driver
            drivers.append({'owner': owner.name, 'owner_type': type(owner).__name__,
                'path': fc.data_path, 'index': fc.array_index, 'type': d.type,
                'valid': d.is_valid, 'expression': d.expression,
                'variables': [{'name': v.name, 'type': v.type,
                    'targets': [{'id': t.id.name if t.id else None, 'id_type': t.id_type,
                                 'data_path': t.data_path, 'bone_target': t.bone_target}
                                for t in v.targets]} for v in d.variables]})
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        mods = [m for m in obj.modifiers if m.type == 'ARMATURE' and m.object == rig]
        if not mods: continue
        meshes.append({'name': obj.name, 'vertices': len(obj.data.vertices),
            'groups': [g.name for g in obj.vertex_groups],
            'modifiers': [{'name': m.name, 'type': m.type, 'viewport': m.show_viewport,
                           'render': m.show_render} for m in obj.modifiers]})
    return {'rig': rig.name, 'world': matrix(rig.matrix_world), 'bones': bones,
            'drivers': drivers, 'deformed_meshes': meshes,
            'scope': 'Read-only horse controls, rest/evaluated joints, constraint ownership and driver target paths.'}


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
    result['authored_meshes'] = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith('MF Nihang '):
            geometry = {'vertices': [[round(float(x), 6) for x in v.co] for v in obj.data.vertices],
                        'faces': [list(p.vertices) for p in obj.data.polygons]}
            mats = []
            for mat in obj.data.materials:
                node = mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
                if node:
                    mats.append({'color': list(node.inputs['Base Color'].default_value),
                                 'roughness': node.inputs['Roughness'].default_value})
            result['authored_meshes'][obj.name] = {'geometry_hash': hashlib.sha256(
                json.dumps(geometry, sort_keys=True).encode()).hexdigest(),
                'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons), 'materials': mats}
    return result


def script_diagnostics(bpy):
    """Inspect untrusted embedded code as DATA; never execute or register it.

    Autoexec warning alone is not a failed dependency. Only Blender's simple
    expression evaluator is admitted; Python namespace drivers stay blocked.
    """
    texts = []
    for item in bpy.data.texts:
        body = item.as_string()
        if len(body.encode()) > 256000:
            raise ValueError('NIHANG_EMBEDDED_TEXT_TOO_LARGE')
        texts.append({'name': item.name, 'use_module': bool(item.use_module),
                      'sha256': hashlib.sha256(body.encode()).hexdigest(), 'body': body})
    drivers = []
    # All animation-capable IDs, including shape keys and material node trees.
    visited = set()
    def inspect(item):
        if item.as_pointer() in visited:
            return
        visited.add(item.as_pointer())
        data = getattr(item, 'animation_data', None)
        for curve in data.drivers if data else []:
            d = curve.driver
            drivers.append({'owner': item.name, 'owner_type': type(item).__name__, 'users': item.users,
                'path': curve.data_path, 'index': curve.array_index,
                'type': d.type, 'expression': d.expression, 'valid': bool(d.is_valid),
                'simple': bool(d.is_simple_expression),
                'targets': [{'name': v.name, 'type': v.type, 'ids': [t.id.name if t.id else None for t in v.targets]}
                            for v in d.variables]})
        tree = getattr(item, 'node_tree', None)
        if tree: inspect(tree)
    for prop in bpy.data.bl_rna.properties:
        if prop.type == 'COLLECTION':
            for item in getattr(bpy.data, prop.identifier):
                if isinstance(item, bpy.types.ID): inspect(item)
    blocked = [d for d in drivers if d['users'] > 0 and
               (not d['valid'] or (d['type'] == 'SCRIPTED' and not d['simple']))]
    legacy = hashlib.sha256(json.dumps(blocked, sort_keys=True).encode()).hexdigest() == LEGACY_DRIVER_DEFECT
    return {'autoexec_warning': bool(bpy.app.autoexec_fail),
            'message': bpy.app.autoexec_fail_message, 'embedded_texts': texts, 'drivers': drivers,
            'blocked_drivers': [] if legacy else blocked,
            'known_source_defects': blocked if legacy else [],
            'rig_qualified': not blocked,
            'orphan_driver_count': sum(d['users'] == 0 for d in drivers)}


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
    diagnostics = script_diagnostics(bpy)
    (out / 'script-diagnostics.json').write_text(json.dumps(diagnostics, indent=2) + '\n')
    if diagnostics['blocked_drivers']:
        raise ValueError('NIHANG_UNSAFE_OR_INVALID_DRIVER')
    deps = dependencies(bpy, root)
    (out / 'snapshot.json').write_text(json.dumps(state, sort_keys=True, indent=2) + '\n')
    (out / 'dependencies.json').write_text(json.dumps(deps, sort_keys=True, indent=2) + '\n')
    artifacts = ['snapshot.json', 'dependencies.json']
    if recipe['operation'] == 'nihang_rig_inspect':
        (out / 'rig.json').write_text(json.dumps(rig_inventory(bpy), indent=2) + '\n')
        artifacts.append('rig.json')
    elif recipe['operation'] == 'nihang_save':
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
