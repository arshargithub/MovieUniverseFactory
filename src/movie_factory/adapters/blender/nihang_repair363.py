"""Fixed363 hand frame proof and bounded horse pectoral contour correction.

No arbitrary payloads. Source masters stay untouched; actual desired/evaluated
bone matrices, not only lengths, must agree after action evaluation.
"""
import json,math,importlib.util
from pathlib import Path
import numpy as np

def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)

def chest_delta(points,weights):
 p=np.asarray(points,dtype=float);w=np.asarray(weights,dtype=float)
 window=smooth((p[:,2]-.93)/.15)*smooth((1.66-p[:,2])/.20)
 target=-.68-.40*smooth((p[:,2]-1.0)/.65)+.05*(p[:,0]/.30)**2
 excess=np.maximum(0,target-p[:,1]);amount=.18*np.tanh(excess/.18)
 d=np.zeros_like(p);d[:,1]=amount*window*smooth(w/.65)
 return d

def run(bpy,out):
 from mathutils import Vector,Quaternion,Matrix
 def module(name):
  spec=importlib.util.spec_from_file_location('repair363_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 motion=module('nihang_motion');support=module('nihang_support');scene=bpy.context.scene
 rig=bpy.data.objects['MF coherent Nihang rig'];bones=rig.data.bones;frames=list(range(252,442));capture={}
 if rig.get('repair363'):raise ValueError('REPAIR363_ALREADY_APPLIED')
 names=[f'finger{i}-{j}.R' for i in range(1,6) for j in range(1,4)]
 reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();capture[f]=dict(world=rig.matrix_world.copy(),bones={p.name:p.matrix.copy() for p in rig.pose.bones},paths=[[ob.matrix_world@Vector(p.co[:3]) for p in ob.data.splines[0].points] for ob in reins])
 across=(bones['finger2-1.R'].head_local-bones['finger5-1.R'].head_local).normalized();a=bones['finger3-1.R'];long=(a.head_local-bones['wrist.R'].head_local).normalized();normal=-across.cross(long).normalized()
 # Explicit right-hand palm frame; all matrices are solved before mutation.
 local={};identity=Matrix.Identity(4);deform=identity
 for digit in range(2,6):
  previous=None;total=0
  for j,angle in enumerate((1.35,1.40,.55),1):
   bone=bones[f'finger{digit}-{j}.R'];total+=angle;d=(bone.tail_local-bone.head_local).normalized();sign=1 if across.cross(d).dot(normal)>0 else -1
   rotation=Quaternion(across,sign*total).to_matrix()@bone.matrix_local.to_3x3();mat=rotation.to_4x4();mat.translation=bone.head_local if previous is None else previous;local[bone.name]=mat;previous=mat.translation+rotation.col[1]*bone.length
 thumb=[bones[f'finger1-{j}.R'] for j in (1,2,3)];base=thumb[0].head_local.copy();index=local['finger2-2.R'];idxend=index.translation+index.to_3x3().col[1]*bones['finger2-2.R'].length
 target=(index.translation+idxend)*.5-normal*.009;first=base+(target-base).normalized()*thumb[0].length;distance=(target-first).length;l1,l2=[b.length for b in thumb[1:]]
 if not abs(l1-l2)+.0001<distance<l1+l2-.0001:raise ValueError('REPAIR363_THUMB_REACH')
 joint=Vector(support.bend_joint(first,target,l1,l2,tuple(-normal)));pts=[base,first,joint,target]
 for bone,start,end in zip(thumb,pts,pts[1:]):
  rot=bone.matrix_local.to_3x3();rot=rot.col[1].normalized().rotation_difference((end-start).normalized()).to_matrix()@rot;m=rot.to_4x4();m.translation=start;local[bone.name]=m
 values={n:[] for n in names};desired_all={}
 for f,row in capture.items():
  hand=row['bones']['wrist.R']@bones['wrist.R'].matrix_local.inverted();desired={n:hand@m for n,m in local.items()};desired_all[f]=desired
  for n in names:
   bone=bones[n];parent=bone.parent;parent_matrix=desired.get(parent.name,row['bones'][parent.name])
   basis=bone.convert_local_to_pose(desired[n],bone.matrix_local,parent_matrix=parent_matrix,parent_matrix_local=parent.matrix_local,invert=True);loc,q,scale=basis.decompose();q.normalize()
   if values[n] and q.dot(values[n][-1][1])<0:q.negate()
   values[n].append((loc,q,scale))
 for n in names:rig.pose.bones[n].rotation_mode='QUATERNION'
 count=0
 for fc in motion.curves(rig):
  for n in names:
   prefix=rig.pose.bones[n].path_from_id()+'.'
   if not fc.data_path.startswith(prefix):continue
   prop=fc.data_path[len(prefix):];slot={'location':0,'rotation_quaternion':1,'scale':2}.get(prop)
   if slot is None:continue
   co=np.array([tuple(k.co) for k in fc.keyframe_points],dtype=np.float32);mask=(co[:,0]>=252)&(co[:,0]<=441);data=[v[slot][fc.array_index] for v in values[n]];co[mask,1]=np.interp(co[mask,0],frames,data);fc.keyframe_points.foreach_set('co',co.ravel())
   for key in fc.keyframe_points:key.interpolation='LINEAR'
   fc.update();count+=1;break
 if count!=150:raise ValueError('REPAIR363_CHANNEL_COVERAGE')
 records=[];newpaths={ob.name:[] for ob in reins}
 for f,row in capture.items():
  scene.frame_set(f);bpy.context.view_layer.update()
  matrix_error=max(abs(rig.pose.bones[n].matrix[i][j]-desired_all[f][n][i][j]) for n in names for i in range(4) for j in range(4))
  if matrix_error>2e-4:raise ValueError('REPAIR363_EVALUATED_POSE:'+str((f,matrix_error)))
  grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5)
  for ob,path in zip(reins,row['paths']):
   delta=grip-path[-1];inv=ob.matrix_world.inverted();newpaths[ob.name].append([[*(inv@(p+delta*float(smooth((i/(len(path)-1)-.65)/.35)))),1.] for i,p in enumerate(path)])
  records.append(dict(frame=f,matrix_error=matrix_error,grip=list(grip)))
 for ob in reins:
  data=np.asarray(newpaths[ob.name])
  for fc in motion.curves(ob.data):
   if fc.array_index==3:continue
   i=int(fc.data_path.split('points[')[1].split(']')[0]);co=np.array([tuple(k.co) for k in fc.keyframe_points],dtype=np.float32);mask=(co[:,0]>=252)&(co[:,0]<=441);co[mask,1]=np.interp(co[mask,0],frames,data[:,i,fc.array_index]);fc.keyframe_points.foreach_set('co',co.ravel());fc.update()
 # Lower front pectoral excess only. Preserve bone ownership and foreleg shape.
 horse=bpy.data.objects['horse'];points=np.array([v.co[:] for v in horse.data.vertices]);weights=np.array([sum(g.weight for g in v.groups if horse.vertex_groups[g.group].name in {'DEF-breast.L','DEF-breast.R','DEF-chest'}) for v in horse.data.vertices]);delta=chest_delta(points,weights)
 for block in horse.data.shape_keys.key_blocks:
  coords=np.empty(len(block.data)*3,dtype=np.float32);block.data.foreach_get('co',coords);block.data.foreach_set('co',(coords.reshape(-1,3)+delta).ravel())
 # Short nap is bound to the same surface: transfer the same local displacement.
 nap=bpy.data.objects.get('317 rig-bound short horse nap')
 if nap and nap.type=='MESH':
  from mathutils.kdtree import KDTree
  kd=KDTree(len(points))
  for i,p in enumerate(points):kd.insert(Vector(p),i)
  kd.balance();tohorse=horse.matrix_world.inverted()@nap.matrix_world;tonap=tohorse.inverted().to_3x3()
  for v in nap.data.vertices:
   p=tohorse@v.co;_,i,_=kd.find(p);v.co+=tonap@Vector(delta[i])
 rig['repair363']=1;scene.frame_set(283);bpy.context.view_layer.update()
 report=dict(hand=dict(frames=records,channels=count,method='Explicit desired armature-space matrices converted through actual parent rest/pose frames before bulk action bake; actual evaluated matrices checked.'),chest=dict(vertices=int((np.linalg.norm(delta,axis=1)>1e-8).sum()),max_displacement=float(np.max(np.linalg.norm(delta,axis=1))),method='Smooth weighted lower-pectoral anterior contour; bones/weights/foreleg domain unchanged, nap transferred.'),scope='Candidate only; close grip and front/side/crest horse images veto numeric success.')
 (out/'repair363.json').write_text(json.dumps(report,indent=2)+'\n');return report
