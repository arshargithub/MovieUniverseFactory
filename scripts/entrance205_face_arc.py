"""Director-authorized face-first continuous final coverage; immutable parent.

The checkpoint is established inboard, then leaves frame during the arc.
This changes only final-shot camera keys, never the actor clock or motion.
"""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance205_motion import sample,smooth


def face_camera(t,head):
    d=sample(t);y=d['heading']
    forward=np.array([np.sin(y),-np.cos(y),0.])
    outward=np.array([np.cos(y),np.sin(y),0.])
    w=float(smooth((t-5.05)/1.45))
    a0=np.arctan2(-1.65,.8);a1=np.arctan2(2.1,.65)
    angle=a0+(a1-a0)*w
    radius=np.hypot(.8,1.65)*(1-w)+np.hypot(.65,2.1)*w
    settle=float(smooth((t-7.9)/1.1))
    f=radius*np.cos(angle)+.65*settle
    o=radius*np.sin(angle)
    height=.12*(1-w)+.55*w+.35*np.sin(np.pi*w)**2
    h=np.asarray(head,float)
    loc=h+forward*f+outward*o+np.array([0,0,height])
    target=h+np.array([0,0,-.06*(1-w)+.3/8.3*w])
    axis=target-loc;screen_right=np.cross(axis,[0,0,1]);screen_right/=np.linalg.norm(screen_right)
    target+=screen_right*.4*(1-w)**2
    return loc,target,28+22*w


def main():
    import bpy
    from mathutils import Vector
    import wardrobe_motion178 as base
    from entrance205_actor import save
    from entrance205_scene import FLOOR
    from wardrobe_motion178_controls import render_geometry_paused
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'arc52'}:raise ValueError('Closed camera operation')
    src=base.BASE/'entrance205-framing49/scene.blend';out=base.BASE/'entrance205-arc52'
    if out.exists() or base.digest(src)!='de4b5b5ee8c01aae3207444209e5b9b7732efbda4481e4faa743bb3a6fb85a2c':raise ValueError('Source/output')
    r=json.loads((src.parent/'result.json').read_text())
    for row in r['caches']:
        if base.digest((src.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Changed cache')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;cam=scene.camera;rig=bpy.data.objects['MF_body156_fit_rig']
    cam.animation_data.action=cam.animation_data.action.copy();cam.data.animation_data.action=cam.data.animation_data.action.copy()
    rows=[]
    with render_geometry_paused():
        for f in range(472,650):
            scene.frame_set(f);bpy.context.view_layer.update()
            head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation)
            loc,target,lens=face_camera((f-361)/24,(head-FLOOR)/8.3)
            loc=FLOOR+8.3*loc;target=FLOOR+8.3*target
            cam.location=Vector(loc);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
            cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
            rows.append(dict(frame=f,location=loc.tolist(),target=target.tolist(),lens=lens))
    scene.frame_set(472)
    save(scene,out,dict(source_sha256=r['native_sha256'],camera_samples=rows,
        change='Director approved checkpoint leaving frame after establishment; continuous frontward arc to readable face, sustained forward resolve. Earlier cameras and all actor motion retained.'))


if __name__=='__main__':main()
