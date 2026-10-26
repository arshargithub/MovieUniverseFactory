"""Closed shot-space soft-tissue cache; original rig/masters stay authoritative."""
import importlib.util,json
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('cache376_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(e):
 if e!={'kind':'mounted_horse_cache376','target':'horse'}:raise ValueError('CACHE376_FIELDS')
 return e


def amplitude(t):
 rows=[(276,0),(293,0),(315,.35),(333,1),(339,1),(346,.5),(358,.05),(367,0)]
 for (a,x),(b,y) in zip(rows,rows[1:]):
  if a<=t<=b:
   f=(t-a)/(b-a);return x+(y-x)*f*f*(3-2*f)
 return 0.


def target(points,rest,edges,breast,t):
 base=mod('nihang_pose376');delta,mask=base.posed_target(points,rest,edges,breast);count=np.bincount(edges.ravel(),minlength=len(delta))
 # Smooth the sculpt displacement itself AFTER the gather stroke. This removes
 # group-boundary kinks while preserving unmodified body outside the support.
 for _ in range(20):
  total=np.zeros_like(delta);np.add.at(total,edges[:,0],delta[edges[:,1]]);np.add.at(total,edges[:,1],delta[edges[:,0]]);delta+=(total/np.maximum(count,1)[:,None]-delta)*mask[:,None]*.4;delta[mask==0]=0
 return delta*amplitude(t),mask


def evaluated(bpy,horse):
 ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 try:
  co=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',co);n=np.empty_like(co);me.vertices.foreach_get('normal',n);return co.reshape(-1,3).copy(),n.reshape(-1,3).copy()
 finally:ev.to_mesh_clear()


def at(scene,f):scene.frame_set(int(f),subframe=float(f-int(f)))


def run(bpy,out,e):
 validate(e);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];nap=bpy.data.objects['317 rig-bound short horse nap'];saved=(scene.frame_current,scene.frame_subframe)
 if any(horse.get(n) for n in ('pose376_corrective','corrective375','deform375_weights','multiform376','cache376')):raise ValueError('CACHE376_ORIGINAL_SOURCE')
 keys=horse.data.shape_keys.key_blocks;original={k.name:np.array([v.co[:] for v in k.data],dtype=np.float32) for k in keys};rest=original[keys[0].name];raw=np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32);actions=mod('nihang_padsolve370').actions(bpy);geom=mod('nihang_prep367').frozen(bpy);levels=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF'];arms=[m for m in horse.modifiers if m.type=='ARMATURE']
 if len(arms)!=1:raise ValueError('CACHE376_ARMATURE')
 rows=[{horse.vertex_groups[g.group].name:g.weight for g in v.groups} for v in horse.data.vertices];breast=np.array([sum(v for n,v in row.items() if n.startswith('DEF-breast.')) for row in rows]);edges=np.array([ed.vertices[:] for ed in horse.data.edges]);times=np.arange(552,735)/2.;sources=[];normals=[];targets=[];maxima=[]
 try:
  for m,_ in levels:m.show_viewport=False
  for f in times:
   at(scene,float(f));bpy.context.view_layer.update();p,n=evaluated(bpy,horse);delta,mask=target(p,rest,edges,breast,float(f));sources.append(p);normals.append(n);targets.append((p+delta).astype(np.float32));maxima.append(float(np.linalg.norm(delta,axis=1).max()))
   if len(sources)%24==0:(out/'horse-cache376-progress.json').write_text(json.dumps(dict(samples=len(sources),total=len(times),phase='sourceandtarget'),indent=2)+'\n')
 finally:
  for m,v in levels:m.show_viewport=v
  scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
 sources=np.array(sources);normals=np.array(normals);targets=np.array(targets);np.savez_compressed(out/'horse-cache376.npz',times=times,rest=rest,source=sources,source_normals=normals,target=targets,mask=mask)
 # A reversible derivative owns this shot window only. Source armature and all
 # original shapes/actions remain in the blend and unchanged in protected80.
 arms[0].show_viewport=False;arms[0].show_render=False
 for name in original:
  if name!=keys[0].name:keys[name].mute=True
 created=[]
 for f,co in zip(times,targets):
  k=horse.shape_key_add(name='376 chest shot sample '+str(int(round(f*2))),from_mix=False);k.data.foreach_set('co',co.ravel());k.value=0.;created.append((f,k))
 paths=[]
 for f,k in created:
  for x,y in [(f-.5,0),(f,1),(f+.5,0)]:k.value=y;k.keyframe_insert(data_path='value',frame=float(x))
  paths.append(k.path_from_id('value'))
 action=horse.data.shape_keys.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for bag in getattr(strip,'channelbags',[]):
    for fc in bag.fcurves:
     if fc.data_path in paths:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
 after=mod('nihang_padsolve370').actions(bpy,ignore={action.name:paths})
 if any(after.get(n)!=v for n,v in actions.items()):raise ValueError('CACHE376_PRIMARY_ACTION_DRIFT')
 for name,co in original.items():
  if not np.array_equal(np.array([v.co[:] for v in keys[name].data],dtype=np.float32),co):raise ValueError('CACHE376_OLD_SHAPE_DRIFT')
 if not np.array_equal(np.array([v.co[:] for v in horse.data.vertices],dtype=np.float32),raw):raise ValueError('CACHE376_RAW_DRIFT')
 aftergeom=mod('nihang_prep367').frozen(bpy)
 if any(aftergeom.get(n)!=v for n,v in geom.items() if n!=horse.name):raise ValueError('CACHE376_OTHER_GEOMETRY_DRIFT')
 audit=[];ls=[(m,m.show_viewport) for m in horse.modifiers if m.type=='SUBSURF']
 try:
  for m,_ in ls:m.show_viewport=False
  for f in [276,283,333,336,339,342,346,367]:
   at(scene,f);bpy.context.view_layer.update();p,_=evaluated(bpy,horse);index=int(round((f-276)*2));error=float(np.max(np.linalg.norm(p-targets[index],axis=1)));audit.append(dict(frame=f,error=error))
   if error>2e-6:raise ValueError('CACHE376_TARGET_PLAYBACK:'+str((f,error)))
 finally:
  for m,v in ls:m.show_viewport=v
  scene.frame_set(saved[0],subframe=saved[1]);bpy.context.view_layer.update()
 nap.hide_render=True;nap.hide_viewport=True;horse['cache376']='183half-frame shot samples276..367; outsidewindowNOTQUALIFIED; original80master remains live rig source'
 report=dict(samples=len(times),frame_window=[276,367],sample_step=.5,maximum_target_delta=max(maxima),sample_playback_audit=audit,original_raw_shapes_actions_unchanged=True,other_geometry_unchanged=True,source_armature_retained_disabled_on_derivative=True,old_correctives_retained_muted_on_derivative=True,scope='Shot-specific appearance derivative, not a general rig repair. All outside-chest sourcepoint positions exact at183sampletimes; linear interpolation between samples and fullspeed judgment remain separate. Outside276..367 unsupported; reuse original80 for otheractions. Finalcoat/contact/movie stillrequired.',coat='hidden for incompletebodydiagnostic');(out/'horse-cache376.json').write_text(json.dumps(report,indent=2)+'\n');return report
