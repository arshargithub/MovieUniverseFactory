"""Closed shot-specific multi-pose chest corrective, not primary animation."""
import importlib.util,json
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('multiform376_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(e):
 if e!={'kind':'mounted_horse_multiform376','target':'horse'}:raise ValueError('MULTIFORM376_FIELDS')
 return e


def envelopes():
 return {333:[(276,0),(293,0),(315,.35),(333,1),(339,0),(346,0),(367,0)],339:[(276,0),(333,0),(339,1),(346,0),(367,0)],346:[(276,0),(333,0),(339,0),(346,1),(358,.1),(367,0)]}


def run(bpy,out,edit):
 validate(edit);base=mod('nihang_pose376');scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];nap=bpy.data.objects['317 rig-bound short horse nap'];saved=scene.frame_current
 if any(horse.get(n) for n in ('pose376_corrective','corrective375','deform375_weights','multiform376')):raise ValueError('MULTIFORM376_ORIGINAL_SOURCE')
 keys=horse.data.shape_keys.key_blocks;original={k.name:np.array([v.co[:] for v in k.data],dtype=np.float32) for k in keys};rest=original[keys[0].name];raw=np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32);geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices];breast=np.array([sum(v for n,v in row.items() if n.startswith('DEF-breast.')) for row in rows]);edges=np.array([e.vertices[:] for e in horse.data.edges]);created=[];records=[];arrays={'rest':rest};eps=.001
 try:
  for m,_ in levels:m.show_viewport=False
  for frame,amount in [(333,1.),(339,1.),(346,.5)]:
   scene.frame_set(frame);bpy.context.view_layer.update()
   if any(abs(keys[n].value)>1e-8 for n in original if n!=keys[0].name):raise ValueError('MULTIFORM376_ACTIVE_SOURCE_KEY')
   posed=base.cage(bpy,horse);J=np.empty((len(rest),3,3),dtype=float)
   for axis in range(3):
    shifted=rest.copy();shifted[:,axis]+=eps;keys[0].data.foreach_set('co',shifted.ravel());horse.data.update();bpy.context.view_layer.update();J[:,:,axis]=(base.cage(bpy,horse)-posed)/eps
   keys[0].data.foreach_set('co',rest.ravel());horse.data.update();bpy.context.view_layer.update()
   if np.max(np.abs(base.cage(bpy,horse)-posed))>1e-6:raise ValueError('MULTIFORM376_RESPONSE_RESTORE')
   target,mask=base.posed_target(posed,rest,edges,breast);target*=amount;desired=posed+target;key=horse.shape_key_add(name='376 pectoral posed '+str(frame),from_mix=False);key.data.foreach_set('co',rest.ravel());key.value=1.;horse.data.update();bpy.context.view_layer.update();dr=np.zeros_like(rest,dtype=float);iterations=[]
   for _ in range(8):
    actual=base.cage(bpy,horse);err=desired-actual;maximum=float(np.max(np.linalg.norm(err,axis=1)));iterations.append(maximum)
    if maximum<.001:break
    dr+=np.linalg.solve(J,err[...,None])[...,0]
    if not np.isfinite(dr).all() or np.max(np.linalg.norm(dr,axis=1))>.55:raise ValueError('MULTIFORM376_INVERSE_BOUND:'+str(frame))
    key.data.foreach_set('co',(rest+dr).astype(np.float32).ravel());horse.data.update();bpy.context.view_layer.update()
   actual=base.cage(bpy,horse);error=np.linalg.norm(actual-desired,axis=1);record=dict(frame=frame,amount=amount,error_max=float(error.max()),error_p95=float(np.percentile(error,95)),maximum_rest_delta=float(np.linalg.norm(dr,axis=1).max()),inverse_iterations=iterations);records.append(record);arrays['delta_'+str(frame)]=dr;arrays['target_'+str(frame)]=desired;arrays['actual_'+str(frame)]=actual
   (out/'horse-multiform376.json').write_text(json.dumps(dict(poses=records,complete=False),indent=2)+'\n')
   if error.max()>.001:raise ValueError('MULTIFORM376_TARGET_FIT:'+str(frame))
   key.value=0.;created.append((frame,key));horse.data.update();bpy.context.view_layer.update()
 finally:
  keys[0].data.foreach_set('co',rest.ravel());horse.data.update()
  for m,v in levels:m.show_viewport=v
  scene.frame_set(saved);bpy.context.view_layer.update()
 paths=[]
 for frame,key in created:
  for f,v in envelopes()[frame]:key.value=v;key.keyframe_insert(data_path='value',frame=f)
  paths.append(key.path_from_id('value'))
 action=horse.data.shape_keys.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for bag in getattr(strip,'channelbags',[]):
    for fc in bag.fcurves:
     if fc.data_path not in paths:continue
     pts=list(fc.keyframe_points)
     for i,k in enumerate(pts):
      x,y=k.co;left=x-pts[i-1].co.x if i else 1.;right=pts[i+1].co.x-x if i+1<len(pts) else 1.;k.interpolation='BEZIER';k.handle_left_type='FREE';k.handle_right_type='FREE';k.handle_left=(x-left/3,y);k.handle_right=(x+right/3,y)
 after=mod('nihang_padsolve370').actions(bpy,ignore={action.name:paths})
 if any(after.get(n)!=v for n,v in actions.items()):raise ValueError('MULTIFORM376_OLD_ACTION_DRIFT')
 for name,co in original.items():
  if not np.array_equal(np.array([v.co[:] for v in keys[name].data],dtype=np.float32),co):raise ValueError('MULTIFORM376_OLD_SHAPE_DRIFT')
 if not np.array_equal(np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32),raw):raise ValueError('MULTIFORM376_RAW_DRIFT')
 aftergeo=mod('nihang_prep367').frozen(bpy)
 if any(aftergeo.get(n)!=v for n,v in geometry.items() if n!=horse.name):raise ValueError('MULTIFORM376_OTHER_GEOMETRY_DRIFT')
 nap.hide_render=True;nap.hide_viewport=True;horse['multiform376']=json.dumps([k.name for _,k in created]);scene.frame_set(saved);bpy.context.view_layer.update();np.savez_compressed(out/'horse-multiform376.npz',**arrays)
 report=dict(poses=records,complete=True,existing_shapes_actions_unchanged=True,raw_geometry_unchanged=True,other_geometry_unchanged=True,coat='Hidden for incomplete body diagnostic; mandatory finalcoupling separate.',scope='Shot-specific333/339/346 corrective shapes, C1 zero-slope complementary envelopes. Original primarychoreography exact. Actual anatomy/movingforms and arbitraryfuturemotion NOT_QUALIFIED.');(out/'horse-multiform376.json').write_text(json.dumps(report,indent=2)+'\n');return report
