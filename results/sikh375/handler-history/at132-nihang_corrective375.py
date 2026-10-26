"""Closed local rest-bound chest deformation trial, never primary choreography."""
import json,importlib.util
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('corrective375_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(edit):
 if edit not in ({'kind':'mounted_horse_corrective375','target':'horse','phase':'body'}, {'kind':'mounted_horse_corrective375','target':'horse','phase':'coat'}):raise ValueError('CORRECTIVE375_FIELDS')
 return edit


def support(points):
 p=np.asarray(points,dtype=float)
 if p.ndim!=2 or p.shape[1]!=3 or not np.isfinite(p).all():raise ValueError('CORRECTIVE375_POINTS')
 def s(x):
  x=np.clip(x,0,1);return x*x*(3-2*x)
 # Anterior chest/limb-root only; back, seat, lower legs and high neck fixed.
 return s((p[:,2]-.98)/.20)*s((1.94-p[:,2])/.26)*s((-.28-p[:,1])/.30)


def evaluated(bpy,ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 try:
  co=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',co);return co.reshape(-1,3).copy()
 finally:ev.to_mesh_clear()


def operator(bpy,ob,name,modifier):
 # Fixed built-in operator names only, no recipe strings or executable payload.
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 if name=='corrective':return bpy.ops.object.correctivesmooth_bind(modifier=modifier)
 if name=='surface':return bpy.ops.object.surfacedeform_bind(modifier=modifier)
 raise ValueError('CORRECTIVE375_OPERATOR')


def run(bpy,out,edit):
 validate(edit);scene=mod('nihang_support').select_production_scene(bpy);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];nap=bpy.data.objects['317 rig-bound short horse nap'];saved=scene.frame_current;position=rig.data.pose_position
 geometry=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy)
 if edit['phase']=='body':
  if horse.get('corrective375') or horse.get('deform375_weights'):raise ValueError('CORRECTIVE375_SOURCE_REAPPLY')
  arm=[m for m in horse.modifiers if m.type=='ARMATURE'];subs=[m for m in horse.modifiers if m.type=='SUBSURF']
  if len(arm)!=1 or not subs:raise ValueError('CORRECTIVE375_STACK')
  points=np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[0].data]);mask=support(points);group=horse.vertex_groups.new(name='375 anterior chest deformation support')
  for i in np.flatnonzero(mask):group.add([int(i)],float(mask[i]),'REPLACE')
  rig.data.pose_position='REST';bpy.context.view_layer.update();before=evaluated(bpy,horse)
  relax=horse.modifiers.new('375 rest-bound anterior chest corrective','CORRECTIVE_SMOOTH');relax.factor=1.;relax.iterations=80;relax.smooth_type='LENGTH_WEIGHTED';relax.rest_source='BIND';relax.vertex_group=group.name;relax.use_only_smooth=False
  while horse.modifiers.find(relax.name)>horse.modifiers.find(arm[0].name)+1:
   bpy.context.view_layer.objects.active=horse;bpy.ops.object.modifier_move_up(modifier=relax.name)
  bpy.context.view_layer.update();operator(bpy,horse,'corrective',relax.name)
  if not relax.is_bind:raise ValueError('CORRECTIVE375_BIND')
  bpy.context.view_layer.update();after=evaluated(bpy,horse);error=float(np.max(np.linalg.norm(after-before,axis=1)))
  if error>1e-5:raise ValueError('CORRECTIVE375_REST_DRIFT:'+str(error))
  # Skin-only diagnostic is explicitly incomplete. Coat cannot obscure a failed
  # body and is re-enabled only after its admitted deformation binding proof.
  nap['375 previous hide_render']=nap.hide_render;nap['375 previous hide_viewport']=nap.hide_viewport;nap.hide_render=True;nap.hide_viewport=True
  horse['corrective375']='rest-bound80-lengthweighted';report=dict(phase='body',rest_maximum_delta=error,affected_vertices=int((mask>0).sum()),modifier=relax.name,iterations=80,coat='hidden for incomplete skin diagnostic; final coat required')
 else:
  if not horse.get('corrective375') or nap.get('corrective375'):raise ValueError('CORRECTIVE375_COAT_SOURCE')
  rig.data.pose_position='REST';nap.hide_viewport=False;nap.hide_render=False
  # Bind final evaluated target topology; render/viewport must remain identical.
  for m in horse.modifiers:
   if m.type=='SUBSURF':m.levels=m.render_levels;m.show_viewport=True
  arm=[m for m in nap.modifiers if m.type=='ARMATURE']
  if len(arm)!=1:raise ValueError('CORRECTIVE375_NAP_ARMATURE')
  arm[0].show_viewport=False;arm[0].show_render=False;bpy.context.view_layer.update();before=evaluated(bpy,nap)
  follow=nap.modifiers.new('375 coat follows corrected final skin','SURFACE_DEFORM');follow.target=horse;follow.falloff=4.;bpy.context.view_layer.update();operator(bpy,nap,'surface',follow.name)
  if not follow.is_bound:raise ValueError('CORRECTIVE375_COAT_BIND')
  bpy.context.view_layer.update();after=evaluated(bpy,nap);error=float(np.max(np.linalg.norm(after-before,axis=1)))
  if error>1e-5:raise ValueError('CORRECTIVE375_COAT_REST_DRIFT:'+str(error))
  nap['corrective375']='surface-bound-final-skin';report=dict(phase='coat',rest_maximum_delta=error,bound=True,old_armature_disabled=True,scope='Rest binding only; posed root contact and all final views still required.')
 rig.data.pose_position=position;scene.frame_set(saved);bpy.context.view_layer.update()
 if geometry!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('CORRECTIVE375_PRIMARY_OR_GEOMETRY_DRIFT')
 report.update(geometry_actions_unchanged=True,artistic_status='NOT_TESTED',primary_motion='accepted source exact');(out/('horse-corrective375-'+edit['phase']+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report
