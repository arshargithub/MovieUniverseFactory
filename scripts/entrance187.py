"""Fixed, source-bound entrance context operations. No external code or paths."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe186 as actor

SOURCE = actor.base.BASE / 'wardrobe186-delivery06/riding-corrected.blend'
SOURCE_SHA = '2dffaf976e1e2e9848f832c149c4578a4a65bbdbaefca67ba1c7e8703db8340e'
FRAMES = (217, 265, 309, 360)


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in ('inspect01', 'inspect02', 'look01', 'look02'):
        raise ValueError('Fixed enum operation required')
    if SOURCE.is_symlink() or not SOURCE.is_file() or actor.base.digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Actor source mismatch')
    out = actor.base.BASE / ('entrance187-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve existing evidence')
    return out


def world_points(ob):
    import bpy
    import numpy as np
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    p = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', p)
    ev.to_mesh_clear()
    matrix = np.array(ev.matrix_world)
    return p.reshape(-1, 3) @ matrix[:3, :3].T + matrix[:3, 3]


def inspect(out):
    import bpy
    import numpy as np
    scene = bpy.context.scene
    rows = []
    horse = bpy.data.objects['MF185_gait_horse']
    # Evaluate the admission target only, not expensive groom/body dependents.
    # Restore exact visibility before collecting the production inventory.
    states = [(o, o.hide_viewport) for o in scene.objects if o.type in ('MESH', 'CURVE', 'CURVES')]
    try:
        for ob, _ in states:
            ob.hide_viewport = ob != horse
        for frame in range(217, 361):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            p = world_points(horse)
            rows.append({'frame': frame, 'min': p.min(0).tolist(), 'max': p.max(0).tolist()})
            if (frame - 217) % 24 == 0:
                print('187 isolated ground audit', frame, flush=True)
    finally:
        for ob, hidden in states:
            ob.hide_viewport = hidden
        bpy.context.view_layer.update()
    visible = []
    for ob in scene.objects:
        if ob.hide_render or ob.type not in ('MESH', 'CURVE', 'CURVES', 'LIGHT'):
            continue
        visible.append({'name': ob.name, 'type': ob.type,
                        'materials': [m.name if m else None for m in getattr(ob.data, 'materials', [])]})
    record = {'source_sha256': SOURCE_SHA, 'horse_bounds': rows,
              'ground_z': min(row['min'][2] for row in rows),
              'visible_objects': visible, 'scene_units': scene.unit_settings.scale_length,
              'camera': {'lens': scene.camera.data.lens, 'sensor_height': scene.camera.data.sensor_height},
              'visual_gate': 'NOT_RUN'}
    (out / 'result.json').write_text(json.dumps(record, indent=2) + '\n')


def look(out):
    import bpy
    import entrance187_context as context
    scene = bpy.context.scene
    audit = json.loads((actor.base.BASE / 'entrance187-inspect02/result.json').read_text())
    if audit['source_sha256'] != SOURCE_SHA:
        raise ValueError('Wrong inspection source')
    dependencies = json.loads((SOURCE.parent / 'result.json').read_text())['shared_cache_dependencies']
    for row in dependencies:
        path = (SOURCE.parent / row['path']).resolve()
        if not path.is_relative_to(actor.base.BASE) or not path.is_file() or actor.base.digest(path) != row['sha256']:
            raise ValueError('Missing or changed admitted dependency')
    (out / 'context-handler.py').write_bytes(Path(context.__file__).read_bytes())
    record = context.construct(scene, audit['ground_z'])
    horse = bpy.data.objects['MF185_gait_horse']
    # Derivative look only: existing horse geometry, motion and registration
    # remain untouched. This material is a proposal, not a horse-design lock.
    horse.data = horse.data.copy()
    horse.data.materials.clear()
    horse.data.materials.append(context.material('bay-coat-proposal', (.075, .024, .009), (.24, .09, .03), .45, .012))
    for poly in horse.data.polygons:
        poly.material_index = 0
    scene.camera.animation_data_clear()
    rig = bpy.data.objects['MF_body156_fit_rig']
    # Pause unrelated expensive surface evaluation while setting camera keys.
    from wardrobe_motion178_controls import render_geometry_paused
    keys = []
    with render_geometry_paused():
        for frame in range(217, 361):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            keys.append(context.camera(scene, rig, frame))
            row = keys[-1]
            travel = context.TRAVEL_NATIVE_PER_SECOND * (frame - 217) / 24
            ground = context.height(row['position'][0], row['position'][1] - travel, audit['ground_z'])
            if row['position'][2] - ground < 2:
                raise ValueError('Camera crosses terrain at frame %d' % frame)
            row['ground_clearance'] = row['position'][2] - ground
            scene.camera.keyframe_insert(data_path='location', frame=frame)
            scene.camera.keyframe_insert(data_path='rotation_euler', frame=frame)
            scene.camera.data.keyframe_insert(data_path='lens', frame=frame)
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 432
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.use_persistent_data = True
    scene.frame_start, scene.frame_end = 217, 360
    for text in bpy.data.texts:
        text.use_module = False
    actor.base.check_protected()
    scene.frame_set(217)
    scene.render.filepath = '//frame-'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'entrance-context.blend'), compress=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'entrance-context.blend'), compress=True)
    record.update({'source_sha256': SOURCE_SHA, 'native_sha256': actor.base.digest(out / 'entrance-context.blend'),
                   'camera_keys': keys, 'frames': list(FRAMES), 'cache_dependencies': dependencies,
                   'visual_gate': 'NOT_RUN', 'director_acceptance': 'PENDING',
                   'limitations': ['Look candidate only', 'Full camera playback not rendered',
                                   'Dust/sound/fork/branch and final horse/tack art unfinished',
                                   'Not standalone export; shared185 caches required']})
    (out / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    for frame in FRAMES:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(out / ('frame-%04d.png' % frame))
        bpy.ops.render.render(write_still=True)
        print('187 scene keyframe complete', frame, flush=True)


def main():
    import bpy
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    job = json.loads(Path(args[0]).read_text())
    out = validate(job)
    out.mkdir()
    (out / 'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    actor.base.check_protected()
    if job['operation'].startswith('inspect'):
        inspect(out)
    else:
        look(out)
    actor.base.check_protected()
    if actor.base.digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Protected input changed')


if __name__ == '__main__':
    main()
