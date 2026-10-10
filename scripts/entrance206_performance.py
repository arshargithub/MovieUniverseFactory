"""Recognition then a decisive escape-route look; retained turn/contact keys."""
import math
import numpy as np
from entrance205_motion import smooth

def escape_weight(f):
 return float(smooth((f-346)/14)*(1-smooth((f-363)/17)))

def expression(f):
 # A visible change from concentration, through acquisition, into resolve.
 acquire=float(smooth((f-322)/5)*(1-smooth((f-331)/7)))
 resolve=float(smooth((f-331)/13))
 return dict(eyeSquintLeft=.06+.42*resolve,eyeSquintRight=.06+.39*resolve,
   browDownLeft=.035+.53*resolve,browDownRight=.03+.46*resolve,
   browInnerUp=.025+.40*acquire,browOuterUpLeft=.03+.24*acquire,browOuterUpRight=.03+.21*acquire,
   mouthPressLeft=.035+.40*resolve,mouthPressRight=.035+.40*resolve,
   jawOpen=.075*(1-resolve)+.006,cheekSquintLeft=.025+.10*resolve,cheekSquintRight=.025+.10*resolve)

def apply(scene,out,kind):
 import bpy
 from mathutils import Quaternion
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance189_groom import read_mdd,write_mdd,attach_cache
 from worker import action_channels
 frames=list(range(217,361)) if kind=='opening' else list(range(361,649))
 rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body'];keys=body.data.shape_keys
 rig.animation_data.action.use_fake_user=True;rig.animation_data.action=rig.animation_data.action.copy()
 controls={}
 for n in expression(217):
  ds=[d for d in keys.animation_data.drivers if d.data_path==keys.key_blocks[n].path_from_id('value')]
  if len(ds)!=1 or len(ds[0].driver.variables)!=1:raise ValueError('Unexpected face driver')
  t=ds[0].driver.variables[0].targets[0]
  if t.id_type!='KEY':raise ValueError('Unexpected face controller')
  controls[n]=t.id.key_blocks[n]
 for d in set(k.id_data for k in controls.values()):d.animation_data.action.use_fake_user=True;d.animation_data.action=d.animation_data.action.copy()
 for k in controls.values():
  for fc in action_channels(k.id_data.animation_data.action):
   if fc.data_path==k.path_from_id('value'):fc.keyframe_points.clear()
 before=[];after=[];world=[];basis=[];protected=[]
 shawl=bpy.data.objects['MF185_moving_shawl']
 with render_geometry_paused():
  for f in frames:
   scene.frame_set(f);bpy.context.view_layer.update();before.append(np.array(rig.matrix_world@rig.pose.bones['MF185_head'].matrix))
   basis.append([rig.pose.bones[n].rotation_quaternion.copy() for n in ('MF185_neck','MF185_head')])
   world.append(np.array(shawl.parent.matrix_world@shawl.matrix_parent_inverse@shawl.matrix_basis if shawl.parent else shawl.matrix_world))
   protected.append([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in ('pelvis','chest','hand.L','hand.R','foot.L','foot.R')])
  errors=[]
  for i,f in enumerate(frames):
   scene.frame_set(f);g=escape_weight(f)
   for j,(n,deg) in enumerate((('MF185_neck',-7),('MF185_head',-23))):
    b=rig.pose.bones[n];b.rotation_mode='QUATERNION';b.rotation_quaternion=basis[i][j]@Quaternion((0,1,0),math.radians(deg)*g);b.keyframe_insert('rotation_quaternion',frame=f)
   for n,v in expression(f).items():controls[n].value=v;controls[n].keyframe_insert('value',frame=f)
   bpy.context.view_layer.update();after.append(np.array(rig.matrix_world@rig.pose.bones['MF185_head'].matrix))
   errors.append(max(np.max(abs(np.array(rig.matrix_world@rig.pose.bones[n].matrix)-p)) for n,p in zip(('pelvis','chest','hand.L','hand.R','foot.L','foot.R'),protected[i])))
 before=np.array(before);after=np.array(after);world=np.array(world)
 if max(errors)>1e-5:raise ValueError('Protected contact/body changed')
 m=next(m for m in shawl.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath));offset=int(m.frame_start)
 def rows():
  for i,f in enumerate(frames):
   p=np.array(a[f-offset],float);wmat=world[i];inv=np.linalg.inv(wmat);q=p@wmat[:3,:3].T+wmat[:3,3];h=np.linalg.inv(before[i]);local=q@h[:3,:3].T+h[:3,3]
   weight=smooth((local[:,1]+1.2)/1.8);weight[2501:]=0
   delta=after[i]@h;moved=q@delta[:3,:3].T+delta[:3,3];q+=(moved-q)*weight[:,None]
   yield (q@inv[:3,:3].T+inv[:3,3]).astype(np.float32)
 path=out/'headfall.mdd';write_mdd(path,len(frames),len(shawl.data.vertices),rows());attach_cache(shawl,path,frames[0])
 np.savez_compressed(out/'performance.npz',frames=frames,head_before=before,head_after=after,protected_error=errors)
 return dict(recognition_frames=[322,344],escape_glance_frames=[346,380],head_neck_yaw_degrees=-30,contact_matrix_max_error=float(max(errors)),headfall='Existing support weights transported with actual head change; wrap courses retained',visual_gate='NOT_RUN')

def earlier_face_camera(scene):
 import bpy
 from mathutils import Vector
 from wardrobe_motion178_controls import render_geometry_paused
 cam=scene.camera;rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
 with render_geometry_paused():
  for f in range(217,361):
   scene.frame_set(f);bpy.context.view_layer.update();h=(rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation
   w=float(smooth((f-285)/36));old=cam.matrix_world.copy();oldpos=old.translation;axis=old.to_3x3()@Vector((0,0,-1));depth=(h-oldpos).dot(axis)
   if depth<=0:raise ValueError('Face coverage behind camera')
   loc=oldpos.lerp(h+Vector((-8,-19.12,2.5)),w);target=(oldpos+axis*depth).lerp(h+Vector((0,-.4,-.4)),w);rot=(target-loc).to_track_quat('-Z','Y')
   rows.append((f,loc,rot,cam.data.lens*(1-w)+62*w))
  cam.animation_data.action.use_fake_user=True;cam.animation_data_clear();cam.data.animation_data_clear();cam.rotation_mode='QUATERNION'
  for f,loc,rot,lens in rows:
   cam.location=loc;cam.rotation_quaternion=rot;cam.data.lens=lens;cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f);cam.data.keyframe_insert('lens',frame=f)
 return dict(close_coverage_reached=321,recognition_begins=322,cut=False,reason='Original recognition occurred before readable facial coverage')
