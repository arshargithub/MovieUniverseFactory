"""Scoped source-history-aware chest skin ownership repair; draft until admitted."""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np

def mod(name):
 s=importlib.util.spec_from_file_location('weight375_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)

def validate(edit):
 if set(edit)!={'kind','target','strength'} or edit['kind']!='mounted_horse_deform375_weights' or edit['target']!='horse':raise ValueError('DEFORM375_WEIGHT_FIELDS')
 if type(edit['strength']) not in (int,float) or not np.isfinite(edit['strength']) or not 0<=edit['strength']<=1:raise ValueError('DEFORM375_WEIGHT_STRENGTH')
 return edit

def remap(points,raw,weights,names,edges,strength):
 p=np.asarray(points);raw=np.asarray(raw);w=np.asarray(weights,dtype=float);e=np.asarray(edges);names=list(names)
 if p.shape!=raw.shape or p.shape!=(len(w),3) or not np.isfinite(w).all():raise ValueError('DEFORM375_WEIGHT_ARRAYS')
 sides={side:dict(target=names.index('DEF-upper_arm.'+side),anchor=names.index('DEF-breast.'+side),distal=[i for i,n in enumerate(names) if n.startswith('DEF-forearm.'+side) or (n.startswith('DEF-upper_arm.'+side) and n.endswith('.001'))]) for side in ('L','R')}
 breast=w[:,[v['anchor'] for v in sides.values()]].sum(1);shift=p[:,1]-raw[:,1]
 spatial=smooth((p[:,2]-1.01)/.15)*smooth((1.68-p[:,2])/.18)*smooth((-.35-p[:,1])/.25)*smooth((breast-.05)/.15)
 mask=smooth((shift-.003)/.035)*spatial
 # Smooth ownership through the same local graph, with distal leg/outside
 # anatomy fixed. This changes weights, never mesh positions or action curves.
 count=np.bincount(e.ravel(),minlength=len(p));fixed=(spatial==0)|(breast<.05)
 for _ in range(4):
  total=np.zeros(len(p));np.add.at(total,e[:,0],mask[e[:,1]]);np.add.at(total,e[:,1],mask[e[:,0]]);mask=.8*mask+.2*total/np.maximum(count,1);mask[fixed]=0
 mask*=strength;result=w.copy();mass=np.zeros(len(p))
 for row in sides.values():
  ids=row['distal'];take=w[:,ids]*mask[:,None];result[:,ids]-=take;amount=take.sum(1);result[:,row['target']]+=amount;mass+=amount
  # Keep the sternum anchored; lateral pectoral tissue shares proximal-limb
  # motion instead of becoming a rigid torso flap. Fractions are a bounded
  # artistic hypothesis, not a claim of physiological muscle simulation.
  lateral=smooth((np.abs(p[:,0])-.025)/.22);attach=w[:,row['anchor']]*mask*.7*lateral;result[:,row['anchor']]-=attach;result[:,row['target']]+=attach;mass+=attach
 if result.min()< -1e-8 or np.max(np.abs(result.sum(1)-w.sum(1)))>1e-7 or mass.max()>.85:raise ValueError('DEFORM375_MASS_CONSERVATION')
 return result,mask,mass

def run(bpy,out,edit):
 validate(edit);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig']
 if horse.get('deform375_weights'):raise ValueError('DEFORM375_WEIGHT_REAPPLY')
 geom=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);p=np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[0].data]);raw=np.array([v.co[:] for v in horse.data.vertices])
 if np.max(np.linalg.norm(p-raw,axis=1))<.1:raise ValueError('DEFORM375_LEGACY_SOURCE_REQUIRED')
 names=[g.name for g in horse.vertex_groups];w=np.zeros((len(p),len(names)))
 for v in horse.data.vertices:
  for g in v.groups:w[v.index,g.group]=g.weight
 proposed,mask,mass=remap(p,raw,w,names,np.array([e.vertices[:] for e in horse.data.edges]),edit['strength']);changed=np.abs(proposed-w)>1e-10
 for i,g in enumerate(horse.vertex_groups):
  for idx in np.flatnonzero(changed[:,i]):
   value=float(proposed[idx,i])
   if value<1e-10:g.remove([int(idx)])
   else:g.add([int(idx)],value,'REPLACE')
 bpy.context.view_layer.update();actual=np.zeros_like(w)
 for v in horse.data.vertices:
  for g in v.groups:actual[v.index,g.group]=g.weight
 if np.max(np.abs(actual-proposed))>2e-7 or np.max(np.abs(actual.sum(1)-w.sum(1)))>2e-6:raise ValueError('DEFORM375_STORED_WEIGHT_MISMATCH')
 # The317 coat consists of disjoint three-vertex nap triangles carrying
 # sampled body-vertex weights. Match root position AND old weights; update
 # the whole follicle together rather than giving its tip a different owner.
 from mathutils import Vector
 from mathutils.kdtree import KDTree
 nap=bpy.data.objects.get('317 rig-bound short horse nap')
 if nap is None or len(nap.data.vertices)!=3*len(nap.data.polygons):raise ValueError('DEFORM375_NAP_TOPOLOGY')
 if any(n not in nap.vertex_groups for n,a in zip(names,changed.T) if a.any()):raise ValueError('DEFORM375_NAP_GROUPS')
 kd=KDTree(len(p))
 for idx,point in enumerate(p):kd.insert(Vector(point),idx)
 kd.balance();tohorse=horse.matrix_world.inverted()@nap.matrix_world;nap_names={g.index:g.name for g in nap.vertex_groups};updated=0;unmapped=0;maximum_root_distance=0.
 for poly in nap.data.polygons:
  ids=list(poly.vertices)
  if len(ids)!=3:raise ValueError('DEFORM375_NAP_TRIANGLE')
  root=tohorse@((nap.data.vertices[ids[0]].co+nap.data.vertices[ids[1]].co)*.5);old=np.zeros(len(names))
  for g in nap.data.vertices[ids[0]].groups:
   name=nap_names[g.group]
   if name in names:old[names.index(name)]=g.weight
  candidates=kd.find_n(root,8);chosen=None
  for tries in (candidates,kd.find_n(root,32)):
   matches=[(distance,index) for _,index,distance in tries if distance<.02 and np.max(np.abs(w[index]-old))<1e-4]
   if matches:distance,index=min(matches);chosen=(distance,index);break
  if chosen is None:
   if any(mass[index]>1e-6 for _,index,_ in candidates):unmapped+=1
   continue
  distance,index=chosen
  if mass[index]<1e-9:continue
  for j in np.flatnonzero(changed[index]):
   g=nap.vertex_groups[names[j]];value=float(actual[index,j])
   if value<1e-10:
    for vertex in ids:
     if any(row.group==g.index for row in nap.data.vertices[vertex].groups):g.remove([vertex])
   else:g.add(ids,value,'REPLACE')
  updated+=1;maximum_root_distance=max(maximum_root_distance,float(distance))
 if geom!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('DEFORM375_GEOMETRY_ACTION_DRIFT')
 if names!=[g.name for g in horse.vertex_groups]:raise ValueError('DEFORM375_GROUP_DRIFT')
 horse['deform375_weights']=json.dumps(dict(strength=edit['strength'],source_weights=hashlib.sha256(w.astype('<f4').tobytes()).hexdigest()))
 np.savez_compressed(out/'horse-weights375.npz',before=w,after=actual,mask=mask,mass=mass,names=np.array(names))
 report=dict(changed_vertices=int(np.any(changed,axis=1).sum()),changed_groups=[n for n,a in zip(names,changed.T) if a.any()],maximum_remapped_mass=float(mass.max()),maximum_sum_drift=float(np.max(np.abs(actual.sum(1)-w.sum(1)))),nap_updated_triangles=updated,nap_unmapped_near_changed=unmapped,maximum_matched_root_distance=maximum_root_distance,geometry_actions_unchanged=True,scope='Candidate only: source-history-local sternum-to-proximal-limb ownership gradient; not rigid torso donation; not a causal or anatomical PASS. Actual339 opposite+283333, affected nap/contact and complete motion must be revalidated.')
 (out/'horse-weights375.json').write_text(json.dumps(report,indent=2)+'\n');return report
