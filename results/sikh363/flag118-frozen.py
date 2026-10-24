"""Fixed final-clock Blender CLOTH pennant with three moving material ties.

Keep an editable isolated solver scene plus source matrices/settings and a
sampled local shape cache. Final renders use the cache, never a stale sim state.
"""
import json,math,hashlib
import numpy as np

def topology(n=22):
 points=[];lookup={};pins=[];faces=[]
 for i in range(n+1):
  for j in range(n+1-i):
   u=i/n;v=j/n;idx=len(points);lookup[i,j]=idx;points.append((.032+.004*math.sin(5*u+3*v)*u,.55*u,3.48-.54*v-.27*u))
   if i==0 and j in {0,n//2,n}:pins.append(idx)
 for i in range(n):
  for j in range(n-i):
   faces.append((lookup[i,j],lookup[i+1,j],lookup[i,j+1]))
   if i+j<n-1:faces.append((lookup[i+1,j],lookup[i+1,j+1],lookup[i,j+1]))
 return np.asarray(points),faces,pins

def _solve(bpy,out,*,wind_strength,collisions,self_collision,diagnostic=False,reinforced=False):
 from mathutils import Vector,Matrix
 scene=bpy.context.scene;shaft=bpy.data.objects['LEADER spear world contact owner']
 if not scene.get('performance363') or scene.get('flag363'):raise ValueError('FLAG363_FINAL_CLOCK_REQUIRED')
 points,faces,pins=topology();frames=list(range(230,419));matrices={}
 for f in frames:
  scene.frame_set(max(252,f));bpy.context.view_layer.update();matrices[f]=shaft.matrix_world.copy()
 temp=bpy.data.scenes.new('MF363 editable final-clock flag solver');temp.render.fps=24;temp.frame_start=230;temp.frame_end=418;temp.gravity=(0,0,-9.81)
 def obj(name,p,faces):
  data=bpy.data.meshes.new(name);data.from_pydata(p,[],faces);data.update();ob=bpy.data.objects.new(name,data);temp.collection.objects.link(ob);return ob
 def goals(ob,rows,coords):
  ob.shape_key_add(name='Basis')
  for f,p in zip(rows,coords):
   key=ob.shape_key_add(name='Goal '+str(f));key.data.foreach_set('co',np.asarray(p,dtype=np.float32).ravel())
   for ff,value in [(f-1,0.),(f,1.),(f+1,0.)]:key.value=value;key.keyframe_insert('value',frame=ff)
  for layer in ob.data.shape_keys.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
 worldgoals=[np.array([matrices[f]@Vector(p) for p in points]) for f in frames]
 cloth=obj('MF363 solver cloth with moving pin goals',worldgoals[0],faces);goals(cloth,frames,worldgoals)
 bound=[i for i,p in enumerate(points) if p[1]==0] if reinforced else pins
 pin=cloth.vertex_groups.new(name='Reinforced attached hem' if reinforced else 'Three material pole ties');pin.add(bound,1.,'REPLACE')
 excluded=[]
 if reinforced:
  excluded=[i for i,p in enumerate(points) if p[1]<=.0251]
  attachment=cloth.vertex_groups.new(name='Sewn attachment collision exclusion');attachment.add(excluded,1.,'REPLACE')
 bpy.context.window.scene=temp
 # Actual moving cylinder, isolated from unrelated production objects.
 cp=[];cf=[];segments=20
 for z in (2.84,3.58):
  cp += [(.018*math.cos(i*math.tau/segments),.018*math.sin(i*math.tau/segments),z) for i in range(segments)]
 for i in range(segments):j=(i+1)%segments;cf.append((i,j,j+segments,i+segments))
 cf += [tuple(reversed(range(segments))),tuple(range(segments,2*segments))]
 pole=obj('MF363 moving pole collider',cp,cf);pole.rotation_mode='QUATERNION'
 for f in frames:
  pole.matrix_world=matrices[f]
  for prop in ('location','rotation_quaternion','scale'):pole.keyframe_insert(prop,frame=f)
 pole.modifiers.new('Actual pole collision','COLLISION');pole.collision.thickness_outer=.001;pole.collision.thickness_inner=.001;pole.collision.cloth_friction=2
 bpy.ops.object.effector_add(type='WIND',location=matrices[252].translation)
 wind=bpy.context.object;wind.name='MF363 physical breeze';wind.rotation_euler=Vector((1,.35,.1)).to_track_quat('Z','Y').to_euler();wind.field.strength=wind_strength
 mod=cloth.modifiers.new('Actual moving-pole CLOTH363','CLOTH');s=mod.settings;s.quality=20;s.mass=.001;s.tension_stiffness=80;s.compression_stiffness=80;s.shear_stiffness=50;s.bending_stiffness=.18;s.air_damping=4;s.vertex_group_mass=pin.name;s.pin_stiffness=1
 mod.collision_settings.collision_quality=12;mod.collision_settings.use_collision=collisions;mod.collision_settings.distance_min=.002;mod.collision_settings.use_self_collision=self_collision;mod.collision_settings.self_distance_min=.003;mod.collision_settings.vertex_group_object_collisions=attachment.name if reinforced else '';mod.point_cache.frame_start=230;mod.point_cache.frame_end=418
 edges=sorted({tuple(sorted((a,b))) for face in faces for a,b in zip(face,(*face[1:],face[0]))});ei=np.asarray(edges);rest=np.linalg.norm(points[ei[:,0]]-points[ei[:,1]],axis=1);solved=[];records=[]
 try:
  for f,goal in zip(frames,worldgoals):
   temp.frame_set(f);bpy.context.view_layer.update();ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();co=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
   if len(co)!=len(points) or not np.isfinite(co).all():raise ValueError('FLAG363_NONFINITE_OR_TOPOLOGY')
   pinerror=float(np.max(np.linalg.norm(co[bound]-goal[bound],axis=1)));stretch=float(np.max(np.linalg.norm(co[ei[:,0]]-co[ei[:,1]],axis=1)/rest))
   if pinerror>.006 or stretch>1.7:
    (out/'flag363-failed-solve.json').write_text(json.dumps(dict(frame=f,pin_error=pinerror,stretch=stretch,prior=records,world_points=co.tolist(),goals=goal.tolist(),rest=points.tolist(),edges=edges,pins=pins),indent=2)+'\n')
    raise ValueError('FLAG363_SIM_GUARD:'+str((f,pinerror,stretch)))
   inv=matrices[f].inverted();solved.append(np.array([inv@Vector(p) for p in co]));records.append(dict(frame=f,pin_error=pinerror,maximum_edge_stretch=stretch))
 finally:bpy.context.window.scene=scene
 if diagnostic:
  report=dict(status='SOLVED',frames=records,wind=wind_strength,collisions=collisions,self_collision=self_collision,mass=float(s.mass),reinforced_hem=reinforced,scope='Causal control only, no production mesh/acceptance.')
  np.savez_compressed(out/'control-cache.npz',frames=frames,local_points=np.asarray(solved),pole_matrices=np.asarray([matrices[f] for f in frames]),rest=points,faces=faces,pins=pins)
  (out/'control.json').write_text(json.dumps(report,indent=2)+'\n');return report
 material=bpy.data.materials['319 worn saffron pennant'];data=bpy.data.meshes.new('363 solved attached pennant');data.from_pydata(points,[],faces);data.update();flag=bpy.data.objects.new('MF363 physically solved tied pennant',data);scene.collection.objects.link(flag);flag.parent=shaft;flag.matrix_parent_inverse=Matrix.Identity(4);flag.matrix_basis=Matrix.Identity(4);data.materials.append(material)
 goals(flag,frames,solved)
 for p in data.polygons:p.use_smooth=True
 sub=flag.modifiers.new('363 cloth continuous surface','SUBSURF');sub.levels=1;sub.render_levels=1
 solid=flag.modifiers.new('363 woven thickness','SOLIDIFY');solid.thickness=.0007
 # Source old pennant remains preserved but cannot compete with solved cloth.
 for name in ('319 supported cloth pennant','leader standard cloth'):
  if name in bpy.data.objects:bpy.data.objects[name].hide_render=True;bpy.data.objects[name].hide_viewport=True
 ties=[]
 for k,i in enumerate(pins):
  z=float(points[i,2]);curve=bpy.data.curves.new('363 pole tie '+str(k),'CURVE');curve.dimensions='3D';curve.bevel_depth=.0017;curve.bevel_resolution=2;sp=curve.splines.new('POLY');sp.points.add(11)
  for j,p in enumerate(sp.points):
   a=j/11*math.tau;p.co=(.0065+.0255*math.cos(a),.019*math.sin(a),z,1)
  ob=bpy.data.objects.new(curve.name,curve);scene.collection.objects.link(ob);ob.parent=shaft;ob.matrix_parent_inverse=Matrix.Identity(4);curve.materials.append(material);ties.append(ob.name)
 np.savez_compressed(out/'flag363-cache.npz',frames=frames,local_points=np.asarray(solved),pole_matrices=np.asarray([matrices[f] for f in frames]),rest=points,faces=faces,pins=pins)
 provenance=dict(solver='Blender CLOTH',pole_matrix_sha256=hashlib.sha256(np.asarray([matrices[f] for f in frames],dtype='<f8').tobytes()).hexdigest(),fps=24,frames=[230,418],pins=pins,settings=dict(reinforced_hem=reinforced,attachment_excluded_vertices=len(excluded),collision_iterations=int(mod.collision_settings.collision_quality),pole_outer=float(pole.collision.thickness_outer),pole_inner=float(pole.collision.thickness_inner),tie_offset=.032,quality=int(s.quality),mass=float(s.mass),discrete_total_mass=float(s.mass)*len(points),tension=80,compression=80,shear=50,bending=.18,air_damping=4,wind_strength=3),solver_scene=temp.name,cache='flag363-cache.npz',final_render='Pole-local sampled shape cache, matching exact final-clock pole matrices; solver inputs and scene retained for editing. Any pole/action edit requires rebake; this cache is not reusable on changed motion.')
 text=bpy.data.texts.new('MF363 cloth provenance DATA.json');text.write(json.dumps(provenance,indent=2));scene['flag363']=1;scene.frame_set(314);bpy.context.view_layer.update()
 report=dict(**provenance,records=records,ties=ties,free_tip_local_span=np.ptp(np.asarray(solved)[:,-1],axis=0).tolist(),scope='Actual solver/cache and pins proof; intended-framing cloth silhouette, face/pole clearance and full-speed Director judgment remain required.')
 (out/'flag363.json').write_text(json.dumps(report,indent=2)+'\n');return report


def run(bpy,out):
 return _solve(bpy,out,wind_strength=3.,collisions=True,self_collision=True,reinforced=True)

def control(bpy,out):
 reports=[]
 for name,reinforced in (('original_attachment_negative',False),('reinforced_hem',True)):
  folder=out/name;folder.mkdir()
  try:report=_solve(bpy,folder,wind_strength=3.,collisions=True,self_collision=True,diagnostic=True,reinforced=reinforced)
  except ValueError as ex:
   if not str(ex).startswith('FLAG363_SIM_GUARD:'):raise
   report=dict(status='GUARD_FAILED',error=str(ex),evidence=str((folder/'flag363-failed-solve.json').name))
  reports.append(dict(name=name,**report))
 result=dict(controls=reports,scope='Exact-final-motion attachment representation control; no production flag or artistic acceptance.')
 (out/'flag363-controls.json').write_text(json.dumps(result,indent=2)+'\n');return result
