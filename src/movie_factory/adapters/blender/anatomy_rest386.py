"""Closed, hash-bound depth-only rest-form correction on the live inherited rig."""
import hashlib,json
from pathlib import Path
import numpy as np
try:
 from .anatomy_domain386 import preserve_forelegs,main_skin,preserve_pectoral_interfaces,evaluated_preservation
except ImportError:
 import importlib.util
 _spec=importlib.util.spec_from_file_location("rest386_domain",Path(__file__).with_name("anatomy_domain386.py"));_mod=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_mod);preserve_forelegs=_mod.preserve_forelegs;main_skin=_mod.main_skin;preserve_pectoral_interfaces=_mod.preserve_pectoral_interfaces;evaluated_preservation=_mod.evaluated_preservation


def load(root,binding,*,depth_only=True):
 p=(root/binding['path']).resolve()
 if not p.is_relative_to(root.resolve()) or p.stat().st_size>8*1024*1024 or hashlib.sha256(p.read_bytes()).hexdigest()!=binding['sha256']:raise ValueError('REST386_STALE')
 with np.load(p,allow_pickle=False) as q:
  if set(q.files)!={'rest','target','mask'}:raise ValueError('REST386_KEYS')
  v={k:q[k].copy() for k in q.files}
 if v['rest'].shape!=(22514,3) or v['target'].shape!=(22514,3) or v['mask'].shape!=(22514,):raise ValueError('REST386_SHAPE')
 if not all(np.isfinite(a).all() for a in v.values()) or (v['mask']<0).any() or (v['mask']>1).any():raise ValueError('REST386_FINITE_MASK')
 d=v['target']-v['rest'];changed=np.any(d!=0,axis=1);r=v['rest'][changed]
 if not changed.any() or np.linalg.norm(d,axis=1).max()>.18:raise ValueError('REST386_DISPLACEMENT')
 if depth_only and (abs(d[:,[0,2]]).max()>1e-7 or d[:,1].min()<-1e-7):raise ValueError('REST386_DEPTH_SCOPE')
 if np.any(abs(r[:,0])>.36) or np.any((r[:,1]<-1.2)|(r[:,1]>-.25)|(r[:,2]<.95)|(r[:,2]>1.75)):raise ValueError('REST386_REGION')
 if not np.array_equal(v['rest'][v['mask']==0],v['target'][v['mask']==0]):raise ValueError('REST386_OUTSIDE')
 return v



def pose_samples(bpy,horse,helpers):
 scene=bpy.context.scene;rig=bpy.data.objects['horse.rig'];saved=(scene.frame_current,scene.frame_subframe);mods=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];surface=[];rigstate=[]
 try:
  for m,_ in mods:m.show_viewport=False
  for f in [283,333,339]:
   scene.frame_set(f);bpy.context.view_layer.update();points,_=helpers('nihang_cache376').evaluated(bpy,horse)
   if points.shape!=(22514,3):raise ValueError('REST386_POSE_CAGE_SHAPE')
   surface.append(points)
   rigstate.append(np.array([[list(row) for row in horse.matrix_world]]+[[list(row) for row in rig.matrix_world@pb.matrix] for pb in rig.pose.bones]))
 finally:
  for m,v in mods:m.show_viewport=v
  scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
 return np.array(surface),np.array(rigstate)

def apply(bpy,out,binding,helpers,*,depth_only=True,allow_proximal=False,proximal_limit=.06):
 root=Path(__file__).resolve().parents[4];q=load(root,binding,depth_only=depth_only);horse=bpy.data.objects['horse'];keys=horse.data.shape_keys.key_blocks
 if horse.get('cache376') or [k.name for k in keys]!=['Basis','corr.neck','corr.chin','corr.neck.2'] or len(horse.data.vertices)!=22514:raise ValueError('REST386_LIVE_SOURCE_REQUIRED')
 before=np.array([[p.co[:] for p in k.data] for k in keys],dtype=np.float32)
 if not np.array_equal(before[0],q['rest']):raise ValueError('REST386_SOURCE_MISMATCH')
 names=[g.name for g in horse.vertex_groups];w=np.zeros((22514,len(names)),dtype=np.float32)
 for vertex in horse.data.vertices:
  for g in vertex.groups:w[vertex.index,g.group]=g.weight
 domain=preserve_pectoral_interfaces(q['rest'],q['target'],q['rest'],w,names,max_proximal=proximal_limit) if allow_proximal else preserve_forelegs(q['rest'],q['target'],w,names)
 geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy);raw=np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32)
 arm=[(m.name,m.show_viewport,m.show_render,getattr(m,'use_deform_preserve_volume',None)) for m in horse.modifiers if m.type=='ARMATURE']
 if not arm or not all(v and r for _,v,r,_ in arm):raise ValueError('REST386_ARMATURE_NOT_LIVE')
 d=q['target']-q['rest']
 pose_before,rig_before=pose_samples(bpy,horse,helpers)
 for k,co in zip(keys,before):k.data.foreach_set('co',(co+d).ravel())
 horse.data.update();bpy.context.view_layer.update()
 after=np.array([[p.co[:] for p in k.data] for k in keys],dtype=np.float32);error=float(abs((after-after[0])-(before-before[0])).max())
 other=helpers('nihang_prep367').frozen(bpy);geometry.pop('horse');other.pop('horse')
 if geometry!=other or actions!=helpers('nihang_padsolve370').actions(bpy) or error>1e-6 or not np.array_equal(raw,np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32)):raise ValueError('REST386_PRESERVATION')
 pose_after,rig_after=pose_samples(bpy,horse,helpers);pose_report=evaluated_preservation(pose_before,pose_after,~np.any(d!=0,axis=1),rig_before,rig_after)
 np.savez_compressed(out/'anatomy386-pose-preservation.npz',before=pose_before,after=pose_after,rig_before=rig_before,rig_after=rig_after)
 result=dict(binding=binding,pose_preservation=pose_report,mode='depth_only' if depth_only else 'bounded_3d_form',changed_vertices=int(np.any(d!=0,axis=1).sum()),max_delta=float(np.linalg.norm(d,axis=1).max()),relative_corrective_error=error,domain_preservation=domain,raw_actions_other_geometry_unchanged=True,original_armature_live=arm,scope='Rest-form shape hypothesis on original live rig, no new cache/motion/identity. Native neutral/raised/landing anatomical proof still required.')
 (out/'anatomy386-rest.json').write_text(json.dumps(result,indent=2)+'\n');return result
