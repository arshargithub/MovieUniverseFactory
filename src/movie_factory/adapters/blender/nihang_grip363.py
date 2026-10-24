"""Fixed closed right grip, constant wrist-local pose and rebased rein end."""
import json,importlib.util
from pathlib import Path
import numpy as np

def run(bpy,out):
 from mathutils import Vector,Quaternion
 spec=importlib.util.spec_from_file_location('grip363_support',Path(__file__).with_name('nihang_support.py'));support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
 spec=importlib.util.spec_from_file_location('grip363_motion',Path(__file__).with_name('nihang_motion.py'));motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
 scene=bpy.context.scene;rig=bpy.data.objects['MF coherent Nihang rig'];rest=rig.data.bones
 if rig.get('grip363') or rig.get('hand363'):raise ValueError('GRIP363_SOURCE_REQUIRES99')
 reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name);frames=list(range(252,442));capture={}
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();capture[f]=dict(wrist=rig.pose.bones['wrist.R'].matrix.copy(),paths=[[ob.matrix_world@Vector(p.co[:3]) for p in ob.data.splines[0].points] for ob in reins])
 scene.frame_set(283);bpy.context.view_layer.update();wrist=rig.pose.bones['wrist.R'];hand=wrist.matrix@wrist.bone.matrix_local.inverted();rot=hand.to_3x3()
 across=(rest['finger2-1.R'].head_local-rest['finger5-1.R'].head_local).normalized();a=rest['finger3-1.R'];b=rest['finger3-2.R'];d1=(a.tail_local-a.head_local).normalized();d2=(b.tail_local-b.head_local).normalized()
 longitudinal=(a.head_local-rest['wrist.R'].head_local).normalized()
 palm_normal=-across.cross(longitudinal).normalized()  # actual RIGHT-hand chirality
 old_sign=1 if across.cross(d1).dot(d2-d1)>0 else -1
 sign=1 if across.cross(d1).dot(palm_normal)>0 else -1
 if old_sign==sign:raise ValueError('GRIP363_EXPECTED_DORSAL_CONTROL')
 axis=(rot@across).normalized()
 names=[f'finger{i}-{j}.R' for i in range(1,6) for j in range(1,4)]
 def set_bone(pb,m):
  pb.rotation_mode='QUATERNION';pb.matrix=m
  for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=283)
  bpy.context.view_layer.update()
 for digit in range(2,6):
  previous=None;total=0.
  for j,angle in enumerate((1.45,1.60,.90),1):
   pb=rig.pose.bones[f'finger{digit}-{j}.R'];total+=angle;rotation=Quaternion(axis,sign*total).to_matrix()@rot@pb.bone.matrix_local.to_3x3();m=rotation.to_4x4();m.translation=hand@pb.bone.head_local if previous is None else previous;set_bone(pb,m);previous=pb.tail.copy()
 inward=(rot@(Quaternion(across,sign*.3)@d1-d1)).normalized();dorsal=-inward
 thumb=[rig.pose.bones[f'finger1-{j}.R'] for j in (1,2,3)];index=rig.pose.bones['finger2-2.R'];base=hand@thumb[0].bone.head_local;first=base+(index.head-base).normalized()*thumb[0].bone.length;target=(index.head+index.tail)*.5+dorsal*.008;lens=[p.bone.length for p in thumb[1:]];d=(target-first).length
 if not abs(lens[0]-lens[1])+.0001<d<sum(lens)-.001:raise ValueError('GRIP363_THUMB_REACH:'+str(d))
 joint=Vector(support.bend_joint(first,target,*lens,tuple(dorsal)));points=[base,first,joint,target]
 for pb,start,end in zip(thumb,points,points[1:]):
  rotation=rot@pb.bone.matrix_local.to_3x3();rotation=rotation.col[1].normalized().rotation_difference((end-start).normalized()).to_matrix()@rotation;m=rotation.to_4x4();m.translation=start;set_bone(pb,m)
 # The grasp is constant relative to the wrist. Freeze those local transforms
 # once, not thousands of repeated world-space solves/dependency updates.
 values={}
 for name in names:
  pb=rig.pose.bones[name]
  for prop in ('location','rotation_quaternion','scale'):values[pb.path_from_id()+'.'+prop]=tuple(getattr(pb,prop))
 count=0
 for fc in motion.curves(rig):
  if fc.data_path not in values:continue
  value=values[fc.data_path][fc.array_index]
  for key in fc.keyframe_points:key.co.y=value;key.handle_left.y=value;key.handle_right.y=value
  fc.update();count+=1
 if count!=150:raise ValueError('GRIP363_CURVE_SET:'+str(count))
 captured={ob.name:[] for ob in reins};records=[]
 for f,row in capture.items():
  scene.frame_set(f);bpy.context.view_layer.update();grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5)
  for ob,path in zip(reins,row['paths']):
   delta=grip-path[-1];inv=ob.matrix_world.inverted();new=[]
   for i,p in enumerate(path):
    u=max(0,min(1,(i/(len(path)-1)-.65)/.35));new.append([*(inv@(p+delta*u*u*(3-2*u))),1.])
   captured[ob.name].append(new)
  error=max(abs(rig.pose.bones['wrist.R'].matrix[i][j]-row['wrist'][i][j]) for i in range(4) for j in range(4));length_error=max(abs((rig.pose.bones[n].tail-rig.pose.bones[n].head).length/rest[n].length-1) for n in names)
  if error>1e-5 or length_error>1e-4:raise ValueError('GRIP363_ANATOMICAL_PRESERVATION')
  records.append(dict(frame=f,grip=list(grip),wrist_error=error,segment_length_error=length_error))
 for ob in reins:
  data=np.asarray(captured[ob.name]);curves=list(motion.curves(ob.data))
  for fc in curves:
   if fc.array_index==3:continue
   if not fc.data_path.startswith('splines[0].points[') or not fc.data_path.endswith('].co'):raise ValueError('GRIP363_REIN_PATH')
   point=int(fc.data_path.split('points[')[1].split(']')[0]);co=np.array([tuple(k.co) for k in fc.keyframe_points],dtype=np.float32);mask=(co[:,0]>=252)&(co[:,0]<=441);co[mask,1]=np.interp(co[mask,0],frames,data[:,point,fc.array_index]);fc.keyframe_points.foreach_set('co',co.ravel());fc.update()
 rig['grip363']=1;scene.frame_set(283);bpy.context.view_layer.update()
 horse=bpy.data.objects['horse'];states=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF']
 for m,_ in states:m.show_viewport=False
 bpy.context.view_layer.update();ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 if len(me.vertices)!=len(horse.data.vertices):raise ValueError('GRIP363_CHEST_INDEX')
 chest=[dict(index=v.index,rest=list(v.co),posed=list(me.vertices[v.index].co),weights=[(horse.vertex_groups[g.group].name,g.weight) for g in v.groups]) for v in horse.data.vertices if -1.3<v.co.y<-.1 and .8<v.co.z<1.8]
 ev.to_mesh_clear()
 for m,enabled in states:m.show_viewport=enabled
 bpy.context.view_layer.update()
 report=dict(frames=records,constant_local_curves=count,angles=[1.45,1.60,.90],old_curl_sign=old_sign,palm_side_curl_sign=sign,old_flex_toward_palm=old_sign*across.cross(d1).dot(palm_normal),chest_source=chest,scope='Actual fist candidate, not a grip pass from bone lengths or local-bake efficiency. Thumb/palm/finger silhouette and rein enclosure require actual images. Chest rest versus posed coordinates are source diagnosis, no sculpt yet.')
 (out/'grip363.json').write_text(json.dumps(report,indent=2)+'\n');return report
