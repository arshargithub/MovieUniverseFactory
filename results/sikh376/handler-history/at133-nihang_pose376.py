"""Read-only local deformer response qualification for shot-space sculpting."""
import importlib.util,json
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('pose376_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(edit):
 if edit!={'kind':'mounted_horse_pose376_inspect','target':'horse'}:raise ValueError('POSE376_FIELDS')
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
 validate(edit);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];saved=scene.frame_current
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
