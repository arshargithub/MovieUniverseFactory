"""Bounded hair-only forehead opening from immutable hairline03.

Authored and tested repository operation, never runtime-generated code. All
non-hair state is protected. This is a visual candidate, not likeness acceptance.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'hairline-package-03/hair-raised.blend'
SOURCE_SHA = '5c3388bd759760386c3222107ec7a172ba8a49cf41dda9b657fbcf4e937f31a0'
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}
LIFTS = {1: .18, 2: .25, 3: .12}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview', 'package') or type(job['candidate']) is not int or job['candidate'] not in LIFTS:
        raise ValueError('Unsupported operation')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REFBASE / n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != h:
            raise ValueError('Pinned input changed')
    out = BASE / f'forehead-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    if job['operation'] == 'package':
        p = BASE / f'forehead-preview-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file():
            raise ValueError('Preview required')
        r = json.loads(p.read_text())
        if r.get('handler_sha256') != digest(Path(__file__)) or not r.get('protected_exact'):
            raise ValueError('Stale preview or failed protection')
    return out


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


def displacement(x, y, z, candidate):
    # Preserve posterior locks/ear coverage, open both centre and outer brows.
    front = 1 - smooth((y + .55) / .50)
    vertical = smooth((z + .05) / .45) * (1 - smooth((z - 1.0) / .55))
    return LIFTS[candidate] * front * vertical


def build(candidate):
    import bpy
    from mathutils import Vector
    from hair_volume_sculpt import skull_surface
    from hair_anatomy_refinement import is_hair
    tree = skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    origin = Vector((0, 0, .3))
    moved = 0
    maximum = 0.
    for ob in bpy.context.scene.objects:
        if not is_hair(ob):
            continue
        ob.hide_set(ob.hide_render)
        if ob.hide_render or ob.type != 'MESH':
            continue
        for v in ob.data.vertices:
            old = v.co.copy()
            dz = displacement(*old, candidate)
            if dz < 1e-8:
                continue
            target = old + Vector((0, 0, dz))
            a, _, _, _ = tree.ray_cast(origin, (old - origin).normalized())
            b, _, _, _ = tree.ray_cast(origin, (target - origin).normalized())
            if a is not None and b is not None:
                offset = (old - origin).length - (a - origin).length
                target = origin + (target - origin).normalized() * ((b - origin).length + offset)
            maximum = max(maximum, (target - old).length)
            v.co = target
            moved += 1
        ob.data.update()
    return {'moved_hair_vertices': moved, 'maximum_vertex_shift': maximum,
            'nominal_front_lift': LIFTS[candidate], 'uvs_and_materials_unchanged': True,
            'face_skin_or_controls_changed': False, 'rear_style': 'PROVISIONAL_PREVIOUS_WAVES_RETAINED'}


def run(job):
    out = validate(job)
    out.mkdir()
    shutil.copyfile(Path(__file__), out / 'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    before = protection()
    info = build(job['candidate'])
    visibility()
    assert protection() == before
    review(bpy.context.scene, out, (0, 0, -.03), 3.8,
           (('front', 0), ('left', -45), ('right', 45), ('back', 180)))
    result = {'candidate': job['candidate'], 'source_sha256': SOURCE_SHA,
              'reference_authority': REFERENCES, 'handler_sha256': digest(Path(__file__)),
              'protected_exact': protection() == before, 'changes': info,
              'clothing_rendered': False, 'director_acceptance': 'PENDING', 'hair_motion_qualified': False}
    if job['operation'] == 'package':
        review(bpy.context.scene, out, (0, 0, -.03), 3.8,
               (('portrait-front', 0), ('portrait-left', -45), ('portrait-right', 45)), portrait=True)
        native = out / 'hair-forehead.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        result['fresh_reopen_protected_exact'] = protection() == before
        assert result['fresh_reopen_protected_exact']
        result['native_sha256'] = digest(native)
    assert protection() == before and digest(SOURCE) == SOURCE_SHA
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
