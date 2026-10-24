"""Fixed rein-hand MCP closure and corrective-shape discriminating report."""
import json,math,importlib.util
from pathlib import Path
import numpy as np

def run(bpy,out):
 from mathutils import Vector,Quaternion
 def module(name):
  spec=importlib.util.spec_from_file_location('hand363_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 support=module('nihang_support');scene=bpy.context.scene;rig=bpy.data.objects['MF coherent Nihang rig'];horse=bpy.data.objects['horse']
 if rig.get('hand363'):raise ValueError('HAND363_PARENT')
 keys=horse.data.shape_keys;drivers=[]
 if keys.animation_data:
  for fc in keys.animation_data.drivers:
   drivers.append(dict(path=fc.data_path,expression=fc.driver.expression,type=fc.driver.type,variables=[dict(name=v.name,type=v.type,targets=[dict(bone=t.bone_target,path=t.data_path,id=t.id.name if t.id else None) for t in v.targets]) for v in fc.driver.variables]))
 correctives=[]
 for f in [283,327]:
  scene.frame_set(f);bpy.context.view_layer.update();values=[dict(name=k.name,value=k.value,mute=k.mute) for k in keys.key_blocks]
  def evaluated():
   ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();a=np.array([v.co[:] for v in me.vertices]);ev.to_mesh_clear();return a
  before=evaluated();states=[k.mute for k in keys.key_blocks]
  for k in list(keys.key_blocks)[1:]:k.mute=True
  bpy.context.view_layer.update();muted=evaluated();delta=np.linalg.norm(muted-before,axis=1);worst=int(delta.argmax())
  for k,state in zip(keys.key_blocks,states):k.mute=state
  bpy.context.view_layer.update()
  correctives.append(dict(frame=f,values=values,maximum_muting_delta=float(delta.max()),worst_position=before[worst].tolist()))
 rest=rig.data.bones;suffix='.R';wrest=rest['wrist.R'];across=(rest['finger2-1.R'].head_local-rest['finger5-1.R'].head_local).normalized()
 a=rest['finger3-1.R'];b=rest['finger3-2.R'];d1=(a.tail_local-a.head_local).normalized();d2=(b.tail_local-b.head_local).normalized();sign=1 if across.cross(d1).dot(d2-d1)>0 else -1
 reins=sorted([ob for ob in bpy.data.objects if ob.name.startswith('leader supported rein292')],key=lambda ob:ob.name);capture={}
 for f in range(252,442):
  scene.frame_set(f);bpy.context.view_layer.update();capture[f]=dict(wrist=rig.pose.bones['wrist.R'].matrix.copy(),reins=[[ob.matrix_world@Vector(p.co[:3]) for p in ob.data.splines[0].points] for ob in reins])
 rows=[]
 def set_bone(pb,matrix,frame):
  pb.rotation_mode='QUATERNION';pb.matrix=matrix
  for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=frame)
  bpy.context.view_layer.update()
 for f,row in capture.items():
  scene.frame_set(f);bpy.context.view_layer.update();hand=row['wrist']@wrest.matrix_local.inverted();rotation=hand.to_3x3();axis=(rotation@across).normalized()
  for digit in range(2,6):
   previous=None;total=0
   for j,angle in enumerate((1.32,1.18,.55),1):
    pb=rig.pose.bones[f'finger{digit}-{j}.R'];total+=angle
    rot=Quaternion(axis,sign*total).to_matrix()@rotation@pb.bone.matrix_local.to_3x3();m=rot.to_4x4();m.translation=hand@pb.bone.head_local if previous is None else previous
    set_bone(pb,m,f);previous=pb.tail.copy()
  inward=(rotation@(Quaternion(across,sign*.3)@d1-d1)).normalized();dorsal=-inward
  thumb=[rig.pose.bones[f'finger1-{j}.R'] for j in [1,2,3]];index=rig.pose.bones['finger2-1.R'];base=hand@thumb[0].bone.head_local
  first=base+(index.head-base).normalized()*thumb[0].bone.length;target=(index.head+index.tail)*.5+dorsal*.010
  distance=(target-first).length;lengths=[p.bone.length for p in thumb[1:]]
  if not abs(lengths[0]-lengths[1])+.0001<distance<sum(lengths)-.001:raise ValueError('HAND363_THUMB_REACH:'+str(distance))
  joint=Vector(support.bend_joint(first,target,*lengths,tuple(dorsal)));points=[base,first,joint,target]
  for pb,start,end in zip(thumb,points,points[1:]):
   rot=rotation@pb.bone.matrix_local.to_3x3();rot=rot.col[1].normalized().rotation_difference((end-start).normalized()).to_matrix()@rot;m=rot.to_4x4();m.translation=start;set_bone(pb,m,f)
  grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5)
  for ob,path in zip(reins,row['reins']):
   shift=grip-path[-1];inv=ob.matrix_world.inverted()
   for i,(p,old) in enumerate(zip(ob.data.splines[0].points,path)):
    u=max(0,min(1,(i/(len(path)-1)-.65)/.35));w=u*u*(3-2*u);p.co=(*(inv@(old+shift*w)),1);p.keyframe_insert('co',frame=f)
  wrist_error=max(abs(rig.pose.bones['wrist.R'].matrix[i][j]-row['wrist'][i][j]) for i in range(4) for j in range(4))
  if wrist_error>1e-5:raise ValueError('HAND363_WRIST_DRIFT')
  rows.append(dict(frame=f,grip=list(grip),wrist_error=wrist_error,thumb_error=(thumb[-1].tail-target).length))
 rig['hand363']=1;scene.frame_set(283);bpy.context.view_layer.update()
 report=dict(correctives=correctives,drivers=drivers,hand_rows=rows,scope='Hand candidate and reversible corrective diagnosis; muted corrective state restored. Actual closed silhouette, rein contact and adjacent neck/chest review required. No appearance or motion acceptance.')
 (out/'hand363.json').write_text(json.dumps(report,indent=2)+'\n');return report
