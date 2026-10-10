"""Actual-silhouette framing and explicit glance coverage control.

Keep scene41 geometry, timing and performance. Do not manufacture a visual
pass when the face/checkpoint composition still requires a creative choice.
"""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def fit_camera(points,location,initial_target,maximum_lens=44):
 """Two centering iterations followed by a fixed 10% screen margin."""
 from mathutils import Vector
 p=np.asarray(points);loc=np.asarray(location);target=np.asarray(initial_target)
 for _ in range(3):
  q=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y');rot=np.array(q.to_matrix());v=(p-loc)@rot
  if np.any(v[:,2]>=-.01):raise ValueError('Camera inside fitted subject')
  projected=v[:,:2]/-v[:,2,None];mid=(projected.min(0)+projected.max(0))*.5
  target+=rot[:,:2]@(mid*np.median(-v[:,2]))
 q=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y');v=(p-loc)@np.array(q.to_matrix())
 lens=min(maximum_lens,.8*10.125/np.max(abs(v[:,0]/v[:,2])),.8*18/np.max(abs(v[:,1]/v[:,2])))
 return target,float(lens)


def main():
 import bpy
 from mathutils import Vector
 from entrance205_actor import save
 from entrance205_camera import route_camera
 from entrance205_motion import sample
 from entrance205_scene import FLOOR
 from entrance189_groom import read_mdd
 from wardrobe_motion178_controls import render_geometry_paused
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'framing43'},{'operation':'framing49'}):raise ValueError('Closed camera operation')
 src=base.BASE/'entrance205-scene41/scene.blend';out=base.BASE/('entrance205-'+job['operation']);r=json.loads((src.parent/'result.json').read_text())
 if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
 for row in r['caches']:
  if base.digest((src.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Changed cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene
 rig=bpy.data.objects['MF_body156_fit_rig'];horse=bpy.data.objects['MF185_gait_horse'];root=bpy.data.objects['MF205_shared_route_actor'];cam=scene.camera
 if horse.parent!=root:raise ValueError('Horse coordinate interface changed')
 cache=next(m for m in horse.modifiers if m.type=='MESH_CACHE');hp=read_mdd(Path(bpy.path.abspath(cache.filepath)))
 cam.animation_data.action=cam.animation_data.action.copy();cam.data.animation_data.action=cam.data.animation_data.action.copy();cam.data.shift_x=0;cam.data.shift_y=0
 rows=[]
 with render_geometry_paused():
  for f in range(361,650):
   scene.frame_set(f);bpy.context.view_layer.update();t=(f-361)/24;head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation)
   loc,target,lens,shot=route_camera(t,(head-FLOOR)/8.3);loc=FLOOR+loc*8.3;target=FLOOR+target*8.3
   if shot=='ots':
    # A wider shoulder offset leaves the whole checkpoint clear of headfall.
    loc[0]+=(.28-.18)*8.3
   if shot=='front_maneuver':
    matrix=np.array(root.matrix_world@horse.matrix_parent_inverse@horse.matrix_basis)
    p=np.asarray(hp[f-361]);world=p@matrix[:3,:3].T+matrix[:3,3]
    # Include the rider's crown and both shoulders/feet, not only horse bounds.
    landmarks=[head+[0,0,2.3]]
    for n in ('upperarm.L','upperarm.R','foot.L','foot.R'):
     landmarks.append(np.array((rig.matrix_world@rig.pose.bones[n].matrix).translation))
    target,lens=fit_camera(np.vstack((world,np.array(landmarks))),loc,target)
   cam.location=Vector(loc);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
   cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
   rows.append({'frame':f,'location':loc.tolist(),'target':target.tolist(),'lens':lens,'shot':shot})
  # One lens for this action shot: avoid a gait-driven automatic zoom pulse.
  fixed_lens=min(row['lens'] for row in rows if row['shot']=='front_maneuver')
  for row in rows:
   if row['shot']=='front_maneuver':
    cam.data.lens=fixed_lens;cam.data.keyframe_insert('lens',frame=row['frame']);row['lens']=fixed_lens
 scene.frame_set(361);save(scene,out,{'source_sha256':r['native_sha256'],'change':'Actual full-horse/rider silhouette centering and10percent frame margin during frontal maneuver; wider OTS offset. Other cameras remain scene41, NOT admitted.','camera_samples':rows})
 # Deliberate controls, not a claim of full-motion admission.
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
 scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
 for f in ((361,384) if job['operation']=='framing49' else (361,409,427)):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True)
 if job['operation']=='framing49':base.check_protected();return
 # Explicit alternate: readable face from downhill side; checkpoint leaves
 # the close frame. Retain this consequence as a Director-owned tradeoff.
 cam.animation_data_clear();cam.data.animation_data_clear()
 for f in (505,577):
  scene.frame_set(f);bpy.context.view_layer.update();t=(f-361)/24;d=sample(t);y=d['heading'];forward=np.array([np.sin(y),-np.cos(y),0]);outward=np.array([np.cos(y),np.sin(y),0])
  h=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation);loc=h+8.3*(forward*.65+outward*2.1+[0,0,.55]);target=h+[0,0,.3]
  cam.location=Vector(loc);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=50
  scene.render.filepath=str(out/f'outboard-{f}.png');bpy.ops.render.render(write_still=True)
 base.check_protected()


if __name__=='__main__':main()
