"""Fixed source-bound blink timing control; never changes accepted geometry."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

SOURCE_SHA = '2fefd16846a0719448ece68718749c41c3bf66f4c801fce2e661a2d34ada9267'


def blink(frame):
    # Authored quick close, longer recovery, no closed hold. Not a measured
    # biological standard. Subframe keys avoid an accidental Bezier pause.
    if frame < 311.5 or frame > 313.5:
        return 0.
    x = (frame - 311.5) / .5 if frame <= 312 else (313.5 - frame) / 1.5
    return x*x*(3-2*x)


def validate(job):
    if job not in ({'operation': 'blink01'}, {'operation': 'blink02'}, {'operation': 'blink03'}):
        raise ValueError('Fixed blink control required')
    source = base.BASE / 'entrance189-performance14/scene.blend'
    if source.is_symlink() or base.digest(source) != SOURCE_SHA:
        raise ValueError('Changed performance source')
    out = base.BASE / ('entrance190-'+job['operation'])
    if out.exists():
        raise ValueError('Preserve evidence')
    record = json.loads((source.parent / 'result.json').read_text())
    for row in record['caches']:
        p = (source.parent / row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p) != row['sha256']:
            raise ValueError('Changed cache')
    return source, out, record


def main():
    import bpy
    import os
    source, out, record = validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()))
    out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    base.check_protected()
    scene = bpy.context.scene
    body = bpy.data.objects['MF_studio_adult_body']
    sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))
    from worker import action_channels
    for name in ('eyeBlinkLeft', 'eyeBlinkRight'):
        output=body.data.shape_keys.key_blocks[name]
        drivers=[d for d in body.data.shape_keys.animation_data.drivers if d.data_path==output.path_from_id('value')]
        if len(drivers)!=1 or len(drivers[0].driver.variables)!=1:raise ValueError('Unexpected driver')
        target=drivers[0].driver.variables[0].targets[0]
        keys=target.id
        if target.id_type!='KEY' or target.data_path!=keys.key_blocks[name].path_from_id('value'):raise ValueError('Unexpected source')
        channels=list(action_channels(keys.animation_data.action))
        k = keys.key_blocks[name]
        fc = next(c for c in channels if c.data_path == k.path_from_id('value'))
        fc.keyframe_points.clear()
        for tick in range(217*8, 360*8+1):
            f = tick/8
            p = fc.keyframe_points.insert(f, blink(f));p.interpolation = 'LINEAR'
    errors = []
    from wardrobe_motion178_controls import render_geometry_paused
    with render_geometry_paused():
        body.hide_viewport=False
        for f in range(217,361):
            scene.frame_set(f);bpy.context.view_layer.update()
            errors.append(max(abs(body.data.shape_keys.key_blocks[n].value-blink(f)) for n in ('eyeBlinkLeft','eyeBlinkRight')))
    if max(errors)>1e-5:
        (out/'failure.json').write_text(json.dumps({'errors':errors},indent=2)+'\n')
        raise ValueError('Blink driver transfer failed')
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath='//'+os.path.relpath(bpy.path.abspath(m.filepath),out)
    scene.frame_set(360)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),check_existing=False)
    scene.frame_set(360);bpy.context.view_layer.update()
    camera = scene.camera;matrix=camera.matrix_world.copy();lens=camera.data.lens
    camera.animation_data_clear();camera.data.animation_data_clear();camera.matrix_world=matrix;camera.data.lens=lens
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    for f in range(310,316):
        scene.frame_set(f);bpy.context.view_layer.update()
        scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,
        'native_sha256':base.digest(out/'scene.blend'),'max_driver_error':max(errors),
        'timing':'Authored .5-frame closure and 1.5-frame reopening; no hold',
        'geometry_material_and_other_performance_unchanged':True,
        'frames':{str(f):blink(f) for f in range(309,316)},'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
