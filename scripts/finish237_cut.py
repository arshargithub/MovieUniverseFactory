"""One-frame hard-cut repair with exact unaffected-frame reuse proof."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance205_actor import save
    from worker import action_channels
    if sys.argv[1:]:raise ValueError('Closed camera-cut repair')
    old=base.BASE/'entrance218-route13';src=base.BASE/'finish237-route04';out=base.BASE/'finish237-route05'
    for folder in (old,src):
        r=json.loads((folder/'result.json').read_text())
        if base.digest(folder/'scene.blend')!=r['native_sha256']:raise ValueError('Source changed')
        for c in r['caches']:
            if base.digest((folder/c['path']).resolve())!=c['sha256']:raise ValueError('Cache changed')
    if out.exists():raise ValueError('Preserve derivative')
    bpy.ops.wm.open_mainfile(filepath=str(old/'scene.blend'),load_ui=False,use_scripts=False)
    with render_geometry_paused():
        bpy.context.scene.frame_set(390);bpy.context.view_layer.update();camera=bpy.context.scene.camera
        intended=camera.matrix_world.copy();lens=camera.data.lens
    bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;camera=scene.camera
    if scene.render.use_motion_blur:raise ValueError('Frame reuse requires separate subframe/blur proof')
    def channels():
        return [(label,fc) for label,owner in [('object',camera),('data',camera.data)] for fc in action_channels(owner.animation_data.action)]
    frames=np.arange(415,721)
    before={(label,fc.data_path,fc.array_index):np.array([fc.evaluate(int(f)) for f in frames]) for label,fc in channels()}
    # Copy only camera actions; no actor/material/cache changes.
    for owner in (camera,camera.data):owner.animation_data.action=owner.animation_data.action.copy()
    scene.frame_set(462);camera.matrix_world=intended;camera.rotation_mode='QUATERNION';camera.rotation_quaternion=intended.to_quaternion();camera.location=intended.translation
    camera.data.lens=lens
    for field in ('location','rotation_quaternion'):camera.keyframe_insert(field,frame=462)
    camera.data.keyframe_insert('lens',frame=462)
    after={(label,fc.data_path,fc.array_index):np.array([fc.evaluate(int(f)) for f in frames]) for label,fc in channels()}
    if set(before)!=set(after):raise ValueError('Camera channel schema changed')
    delta=np.max(np.stack([abs(before[k]-after[k]) for k in before]),axis=0)
    changed=frames[delta>1e-7].tolist()
    if changed!=[462]:raise ValueError('Unexpected affected integer frames '+str(changed))
    out.mkdir();scene.frame_set(462)
    save(scene,out,dict(source_sha256=base.digest(src/'scene.blend'),change='Only frame462 camera pose/lens: hold original390 OTS before391 hard cut',
        changed_camera_frames=changed,unchanged_integer_camera_frames=int(sum(delta<=1e-7)),motion_blur=False,body_material_cache_edits=False,
        frame_reuse='Reuse route04 rendered integer frames except global245 after independent neighboring-frame parity check'))
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    for f in (461,462,463):
        scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f-217:04d}.png');bpy.ops.render.render(write_still=True)
    base.check_protected()
if __name__=='__main__':
    # Blender injects its own argv. The handler accepts no post-- payload.
    sys.argv=[sys.argv[0]]+([] if '--' not in sys.argv else sys.argv[sys.argv.index('--')+1:]);main()
