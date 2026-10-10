"""Closed205 integration stages; visual admission remains explicit and separate."""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def camera(scene,f):
    import bpy
    from mathutils import Vector
    from entrance205_camera import route_camera
    from entrance205_scene import FLOOR
    rig=bpy.data.objects['MF_body156_fit_rig'];head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation)
    loc,target,lens,shot=route_camera((f-361)/24,(head-FLOOR)/8.3)
    cam=scene.camera;cam.location=Vector(FLOOR+8.3*loc);cam.rotation_euler=(Vector(FLOOR+8.3*target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    return {'location':list(cam.location),'target':(FLOOR+8.3*target).tolist(),'lens':lens,'shot':shot}


def main():
    import bpy
    from entrance205_actor import save
    from entrance205_support import source_caches,clothes,groom,downhill_look
    from entrance205_scene import actor,environment,checkpoint,reverse_backdrop
    from entrance201_dust import wake
    from entrance205_camera import glance
    from wardrobe_motion178_controls import render_geometry_paused
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'support09'},{'operation':'scene10'},{'operation':'support21'},{'operation':'scene22'}):raise ValueError('Fixed205 integration operation')
    revised=job['operation'] in ('support21','scene22');support=job['operation'].startswith('support')
    folder=('entrance205-fitted20' if support else 'entrance205-support21') if revised else ('entrance205-fitted08' if support else 'entrance205-support09')
    src=base.BASE/folder/'scene.blend';out=base.BASE/('entrance205-'+job['operation']);r=json.loads((src.parent/'result.json').read_text())
    if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    riderfolder='entrance205-rider19' if revised else 'entrance205-rider05'
    with np.load(base.BASE/riderfolder/'rig.npz') as z:data={k:z[k] for k in z.files}
    with np.load(base.BASE/riderfolder/'route.npz') as z:route={k:z[k] for k in z.files}
    record={'source_sha256':r['native_sha256']}
    if support:
        record['downhill_look']=downhill_look(scene,data)
        np.savez_compressed(out/'support-rig.npz',**data)
        caches=source_caches();record['cloth']=clothes(scene,out,data,caches);record['groom']=groom(scene,out,data,caches)
        with render_geometry_paused():
            for side in ('Left','Right'):
                eye=bpy.data.objects['MF_aimable_eye_'+side];scene.frame_set(360);bpy.context.view_layer.update();rest=eye.rotation_euler.copy()
                if eye.animation_data and eye.animation_data.action:eye.animation_data.action.use_fake_user=True;eye.animation_data.action=eye.animation_data.action.copy()
                for i in range(289):
                    g=glance(i/24);eye.rotation_euler=rest.copy();eye.rotation_euler.z+=math.radians(12)*g
                    eye.keyframe_insert('rotation_euler',frame=361+i)
        scene.frame_set(361)
    else:
        # Environment first freezes the previous straight scrolling origin.
        record['environment']=environment(scene,route);record['checkpoint']=checkpoint(scene)
        record['reverse_backdrop']=reverse_backdrop(scene)
        record['actor']=actor(scene,route);record['dust']=wake(scene,range(361,650),route)
        # Old emitted straight-road debris cannot be held in midair on a new
        # trajectory. Fine path-aware debris belongs to stage-two finishing.
        for o in scene.objects:
            if o.name.startswith(('MF196_debris','MF196_pebble','MF189_pebble')):o.hide_render=True
        cam=scene.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.rotation_mode='XYZ';cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36;cam.data.clip_start=.1;cam.data.clip_end=12000
        # Native camera keys use continuous real-time action. Explicit cuts
        # are review edit boundaries, not hidden source-clock retiming.
        with render_geometry_paused():
            for f in range(361,650):
                scene.frame_set(f);bpy.context.view_layer.update();camera(scene,f)
                cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
        scene.frame_set(361);record['limits']='Choreography proof; transported cloth/groom requires full visual review and later inertial finishing. Background coverage still requires actual-camera controls.'
    save(scene,out,record)


if __name__=='__main__':main()
