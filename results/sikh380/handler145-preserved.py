"""Scoped pectoral ownership control; real rig evaluation, no pose cache or code payload."""
import importlib.util,json
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('chest380_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(edit):
 if edit!={'kind':'mounted_horse_chest380','target':'horse'}:raise ValueError('CHEST380_FIELDS')
 return edit


def ownership(weights,names):
 """Transfer whole pectoral group, including midline, to each proximal humerus.

 Existing breast weights already express anatomical falloff. An extra lateral
 or height gate leaves a stationary island and can fold the central lower edge.
 This is a falsifiable skin-binding hypothesis, not anatomical force simulation.
 """
 w=np.asarray(weights,dtype=float);names=list(names)
 if w.ndim!=2 or w.shape[1]!=len(names) or not np.isfinite(w).all() or (w<0).any():raise ValueError('CHEST380_WEIGHTS')
 q=w.copy()
 for side in ('L','R'):
  a=names.index('DEF-breast.'+side);b=names.index('DEF-upper_arm.'+side)
  q[:,b]+=w[:,a];q[:,a]=0
 if np.max(np.abs(q.sum(1)-w.sum(1)))>1e-7:raise ValueError('CHEST380_MASS')
 return q


def run(bpy,out,edit):
 validate(edit);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse']
 if horse.get('chest380') or horse.get('deform375_weights') or horse.get('cache376'):raise ValueError('CHEST380_ORIGINAL_SOURCE')
 before=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);keys=horse.data.shape_keys.key_blocks
 basis=np.array([v.co[:] for v in keys[0].data]);raw=np.array([v.co[:] for v in horse.data.vertices]);delta=raw-basis
 changed=np.linalg.norm(delta,axis=1)>1e-6
 if not changed.any() or np.linalg.norm(delta,axis=1).max()>.18 or np.any((basis[changed,2]<.85)|(basis[changed,2]>1.8)|(basis[changed,1]>-.1)):raise ValueError('CHEST380_SOURCE_DELTA_SCOPE')
 names=[g.name for g in horse.vertex_groups];w=np.zeros((len(raw),len(names)))
 for v in horse.data.vertices:
  for g in v.groups:w[v.index,g.group]=g.weight
 proposed=ownership(w,names);changes=np.abs(proposed-w)>1e-10
 # Undo only the historically accumulated rest sculpt, preserving all relative
 # corrective deltas and their action values. Raw geometry remains untouched.
 for key in keys:
  q=np.empty(len(raw)*3,dtype=np.float32);key.data.foreach_get('co',q);key.data.foreach_set('co',(q.reshape(-1,3)+delta).astype(np.float32).ravel())
 for i,g in enumerate(horse.vertex_groups):
  for idx in np.flatnonzero(changes[:,i]):
   value=float(proposed[idx,i])
   if value<1e-10:g.remove([int(idx)])
   else:g.add([int(idx)],value,'REPLACE')
 actual=np.zeros_like(w)
 for v in horse.data.vertices:
  for g in v.groups:actual[v.index,g.group]=g.weight
 if np.max(np.abs(actual-proposed))>2e-7:raise ValueError('CHEST380_STORED_WEIGHTS')
 nap=bpy.data.objects.get('317 rig-bound short horse nap')
 if nap:nap.hide_render=True;nap.hide_viewport=True
 horse.data.update();bpy.context.view_layer.update();after=mod('nihang_prep367').frozen(bpy)
 if any(before[n]!=after.get(n) for n in before if n!='horse') or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('CHEST380_PROTECTED_DRIFT')
 horse['chest380']='raw-rest + bilateral full pectoral/proximal-humeral ownership; diagnostic no coat'
 rows=[];levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];saved=scene.frame_current;arrays={'raw':raw,'before':basis,'weights_before':w,'weights_after':actual,'names':np.array(names)}
 try:
  for m,_ in levels:m.show_viewport=False
  for f in [283,333,339,342,367]:
   scene.frame_set(f);bpy.context.view_layer.update();ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
   try:arrays['posed_'+str(f)]=np.array([v.co[:] for v in me.vertices])
   finally:ev.to_mesh_clear()
 finally:
  for m,v in levels:m.show_viewport=v
  scene.frame_set(saved);bpy.context.view_layer.update()
 np.savez_compressed(out/'chest380.npz',**arrays)
 report=dict(restored_vertices=int(changed.sum()),maximum_rest_delta=float(np.linalg.norm(delta,axis=1).max()),changed_weight_vertices=int(changes.any(1).sum()),weight_sum_error=float(np.abs(actual.sum(1)-w.sum(1)).max()),actions_unchanged=True,other_geometry_unchanged=True,coat='hidden diagnostic; integration NOT_RUN',method=horse['chest380'],scope='Candidate only; five poses/front/reverse/side and coat/contact/full-motion still require actual review.')
 (out/'chest380.json').write_text(json.dumps(report,indent=2)+'\n');return report
