"""Read-only local deformer response qualification for shot-space sculpting."""
import importlib.util,json
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('pose376_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(edit):
 if edit not in ({'kind':'mounted_horse_pose376_inspect','target':'horse'},{'kind':'mounted_horse_pose376_correct','target':'horse'}):raise ValueError('POSE376_FIELDS')
 return edit


def fair(points,rest,edges,iterations=80):
 """Offline/proposed posed-surface smoothing control; not anatomy or a repair."""
 points=np.asarray(points,dtype=float);rest=np.asarray(rest,dtype=float);edges=np.asarray(edges,dtype=int)
 if points.shape!=rest.shape or points.ndim!=2 or points.shape[1]!=3 or not np.isfinite(points).all():raise ValueError('POSE376_ARRAY')
 s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
 # Lower neck/chest; limb ends, poll and back fixed. Pose-only control avoids
 # smoothing the standing accepted form as previous rest fairing did.
 mask=s((rest[:,2]-1.00)/.16)*s((1.85-rest[:,2])/.22)*s((-.28-rest[:,1])/.3)
 q=points.copy();count=np.bincount(edges.ravel(),minlength=len(q))
 for _ in range(iterations):
  total=np.zeros_like(q);np.add.at(total,edges[:,0],q[edges[:,1]]);np.add.at(total,edges[:,1],q[edges[:,0]]);q+=(total/np.maximum(count,1)[:,None]-q)*mask[:,None]*.5
 return q-points,mask


def cage(bpy,horse):
 ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 try:
  co=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',co);return co.reshape(-1,3).copy()
 finally:ev.to_mesh_clear()


def run(bpy,out,edit):
 validate(edit)
 if edit['kind']=='mounted_horse_pose376_correct':return correct(bpy,out,edit)
 scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];saved=scene.frame_current
 if horse.get('corrective375') or horse.get('deform375_weights'):raise ValueError('POSE376_ORIGINAL_SOURCE_REQUIRED')
 frozen=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);key=horse.data.shape_keys.key_blocks[0];rest=np.array([v.co[:] for v in key.data],dtype=np.float32);levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];eps=.001
 try:
  for m,_ in levels:m.show_viewport=False
  scene.frame_set(339);bpy.context.view_layer.update()
  if any(abs(k.value)>1e-8 for k in horse.data.shape_keys.key_blocks[1:]):raise ValueError('POSE376_ACTIVE_CORRECTIVE')
  posed=cage(bpy,horse);J=np.zeros((len(rest),3,3),dtype=np.float64)
  for axis in range(3):
   shifted=rest.copy();shifted[:,axis]+=eps;key.data.foreach_set('co',shifted.ravel());horse.data.update();bpy.context.view_layer.update();J[:,:,axis]=(cage(bpy,horse)-posed)/eps
  key.data.foreach_set('co',rest.ravel());horse.data.update();bpy.context.view_layer.update();reset=cage(bpy,horse);reset_error=float(np.max(np.abs(reset-posed)))
  edges=np.array([e.vertices[:] for e in horse.data.edges]);target,mask=fair(posed,rest,edges);probe=np.tile([.00042,-.00106,.00142],(len(rest),1))*mask[:,None];key.data.foreach_set('co',(rest+probe).astype(np.float32).ravel());horse.data.update();bpy.context.view_layer.update();actual=cage(bpy,horse)-posed;predicted=np.einsum('nij,nj->ni',J,probe);err=np.linalg.norm(actual-predicted,axis=1);condition=np.linalg.cond(J[mask>.001])
  np.savez_compressed(out/'horse-pose376.npz',rest=rest,posed=posed,jacobian=J,edges=edges,target_control=target,mask=mask,probe_error=err)
  report=dict(frame=339,epsilon=eps,reset_error=reset_error,probe_max_error=float(err.max()),probe_p95_error=float(np.percentile(err,95)),condition_p50_p95_max=np.percentile(condition,[50,95,100]).tolist(),source='Original80 via129, no failed375weight/modifier stack.',scope='Read-only actual finite deformer response, not anatomical positive target or artistic acceptance.')
  (out/'horse-pose376.json').write_text(json.dumps(report,indent=2)+'\n')
 finally:
  key.data.foreach_set('co',rest.ravel());horse.data.update()
  for m,v in levels:m.show_viewport=v
  scene.frame_set(saved);bpy.context.view_layer.update()
 if frozen!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('POSE376_READONLY_DRIFT')
 if reset_error>1e-6 or err.max()>.00015:raise ValueError('POSE376_RESPONSE_UNQUALIFIED')
 return report


def posed_target(posed,rest,edges,breast):
 # Local corrective sculpt in the actual descent pose. Relax stretched folds,
 # gather pendant pectoral tissue up/back into the supported chest. This is a
 # bounded artistic target, not a claim of muscle/soft-body simulation.
 delta,mask=fair(posed,rest,edges,40)
 s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
 tuck=s(np.asarray(breast)/.6)*s((rest[:,2]-1.02)/.13)*s((1.65-rest[:,2])/.20)*s((-.36-rest[:,1])/.30)
 delta[:,1]+=.10*tuck;delta[:,2]+=.08*tuck
 if not np.isfinite(delta).all() or np.max(np.linalg.norm(delta,axis=1))>.30:raise ValueError('POSE376_TARGET_BOUND')
 return delta,np.maximum(mask,tuck)


def correct(bpy,out,edit):
 if edit!={'kind':'mounted_horse_pose376_correct','target':'horse'}:raise ValueError('POSE376_CORRECT_FIELDS')
 scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];nap=bpy.data.objects['317 rig-bound short horse nap'];saved=scene.frame_current
 if horse.get('pose376_corrective') or horse.get('corrective375') or horse.get('deform375_weights'):raise ValueError('POSE376_CORRECT_SOURCE')
 root=Path(__file__).resolve().parents[4];q=np.load(root/'.runtime/factory-native/sikh376-appearance-c133-inspect/horse-pose376.npz',allow_pickle=False);rest=q['rest'];posed=q['posed'];J=q['jacobian'];edges=q['edges'];keys=horse.data.shape_keys.key_blocks
 if not np.array_equal(np.array([v.co[:] for v in keys[0].data],dtype=np.float32),rest):raise ValueError('POSE376_REST_SOURCE_MISMATCH')
 original={k.name:np.array([v.co[:] for v in k.data],dtype=np.float32) for k in keys};geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices];breast=np.array([sum(v for n,v in row.items() if n.startswith('DEF-breast.')) for row in rows]);target,mask=posed_target(posed,rest,edges,breast);desired=posed+target
 for m,_ in levels:m.show_viewport=False
 scene.frame_set(339);bpy.context.view_layer.update()
 if np.max(np.abs(cage(bpy,horse)-posed))>1e-5:raise ValueError('POSE376_POSED_SOURCE_MISMATCH')
 key=horse.shape_key_add(name='376 descent pectoral corrective',from_mix=False);key.value=1.;dr=np.zeros_like(rest,dtype=float);errors=[]
 # Fixed target, bounded numeric inversion iterations; not extra artistic trials.
 for _ in range(8):
  actual=cage(bpy,horse);error=desired-actual;maximum=float(np.max(np.linalg.norm(error,axis=1)));errors.append(maximum)
  if maximum<.001:break
  update=np.linalg.solve(J,error[...,None])[...,0];dr+=update
  if not np.isfinite(dr).all() or np.max(np.linalg.norm(dr,axis=1))>.55:raise ValueError('POSE376_INVERSE_BOUND')
  key.data.foreach_set('co',(rest+dr).astype(np.float32).ravel());horse.data.update();bpy.context.view_layer.update()
 actual=cage(bpy,horse);error=np.linalg.norm(actual-desired,axis=1)
 np.savez_compressed(out/'horse-corrective376.npz',rest=rest,posed=posed,target=desired,actual=actual,delta_rest=dr,mask=mask)
 report=dict(frame=339,target_maximum_delta=float(np.max(np.linalg.norm(target,axis=1))),maximum_rest_delta=float(np.max(np.linalg.norm(dr,axis=1))),actual_fit_error_max=float(error.max()),actual_fit_error_p95=float(np.percentile(error,95)),inverse_iterations=errors,scope='One posed sculpt target; actual surface fit only, not anatomy PASS or future arbitrary-motion qualification.')
 (out/'horse-corrective376.json').write_text(json.dumps(report,indent=2)+'\n')
 if error.max()>.001:raise ValueError('POSE376_TARGET_FIT_FAILED')
 path=key.path_from_id('value')
 for f,v in [(276,0),(293,0),(315,.35),(333,.8),(339,1),(346,.4),(358,.05),(367,0)]:key.value=v;key.keyframe_insert(data_path='value',frame=f)
 anim=horse.data.shape_keys.animation_data;action=anim.action
 curves=[]
 for layer in action.layers:
  for strip in layer.strips:
   for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
 for fc in curves:
  if fc.data_path==path:
   for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
 ignored={action.name:[path]};after=mod('nihang_padsolve370').actions(bpy,ignore=ignored)
 if any(after.get(n)!=v for n,v in actions.items()):raise ValueError('POSE376_OLD_ACTION_DRIFT')
 for name,co in original.items():
  if not np.array_equal(np.array([v.co[:] for v in keys[name].data],dtype=np.float32),co):raise ValueError('POSE376_OLD_SHAPE_DRIFT')
 aftergeo=mod('nihang_prep367').frozen(bpy)
 if any(aftergeo.get(n)!=v for n,v in geometry.items() if n!=horse.name):raise ValueError('POSE376_OTHER_GEOMETRY_DRIFT')
 for m,v in levels:m.show_viewport=v
 nap['376 previous hide_render']=nap.hide_render;nap['376 previous hide_viewport']=nap.hide_viewport;nap.hide_render=True;nap.hide_viewport=True
 scene.frame_set(saved);bpy.context.view_layer.update();horse['pose376_corrective']=key.name;report.update(existing_shapes_unchanged=True,existing_actions_unchanged=True,other_geometry_unchanged=True,coat='hidden only for incomplete body diagnostic',key=key.name,curve_scope='Shot-specific276..367, arbitrary later poses NOT_QUALIFIED');(out/'horse-corrective376.json').write_text(json.dumps(report,indent=2)+'\n');return report
