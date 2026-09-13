"""Full-cut fixed-material contact verification, reusing the admitted six-second screens.
No imported code or arbitrary paths; the historical centroid diagnostic is retained.
"""
from pathlib import Path
import json,math,bpy
from mathutils import Vector
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
ROOT=BASE.parents[1]
def run(mf,out,job,helper):
 if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_cut_check','demo_cut_contact_control','demo_cut_final_check') or job['profile']!={}:raise ValueError('Fixed cut verification operation required')
 out=Path(out).resolve()
 if BASE.resolve() not in out.parents:raise ValueError('Invalid output')
 receipt=json.loads((ROOT/'results/demonstrator-01/rough-cut/motion-receipt.json').read_text())
 path=BASE/'cut-motion/scene.blend'
 helper._file(path,receipt['sha256']);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];rider=bpy.data.objects['rig']
 if job['mode']=='demo_cut_final_check':
  frames=[0,48,96,143,144,220,312,334,334.001,350.5,366,388,400,431,432,516,575]
  def capture():
   rows=[]
   for f in frames:
    helper._refresh(bpy.context.scene,mf,f);deps=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['horse'];ev=body.evaluated_get(deps);mesh=ev.to_mesh();pts=[tuple(ev.matrix_world@v.co) for v in mesh.vertices];ev.to_mesh_clear()
    rider=bpy.data.objects['rig'];head=list(rider.pose.bones['head'].matrix.to_quaternion());gap=0
    for side in ('L','R'):
     hand=rider.pose.bones['hand_fk.'+side];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0));obj=bpy.data.objects['repaired rein '+side];end=obj.matrix_world@Vector(obj.data.splines[0].points[-1].co[:3]);gap=max(gap,(grip-end).length)
    rows.append({'frame':f,'points':pts,'head':head,'rein_gap':gap})
   return rows
  baseline=capture();final=json.loads((ROOT/'results/demonstrator-01/rough-cut/scene-receipt.json').read_text());path=Path(final['scene_path']).resolve()
  if BASE not in path.parents:raise ValueError('Invalid final scene')
  helper._file(path,final['scene_sha256']);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);candidate=capture();rows=[];worst=0;gap=0;finite=True
  for a,b in zip(baseline,candidate):
   if len(a['points'])!=len(b['points']):raise ValueError('Horse topology changed')
   delta=max(math.dist(p,q) for p,q in zip(a['points'],b['points']));worst=max(worst,delta);gap=max(gap,b['rein_gap']);finite=finite and all(math.isfinite(x) for p in b['points'] for x in p)
   dot=abs(sum(x*y for x,y in zip(a['head'],b['head'])));angle=math.degrees(2*math.acos(min(1,dot)));rows.append({'frame':a['frame'],'max_horse_vertex_delta_m':delta,'head_rotation_delta_degrees':angle,'rein_gap_m':b['rein_gap']})
  scene=bpy.context.scene;eevee=scene.eevee
  result={'source_sha256':receipt['sha256'],'final_sha256':final['scene_sha256'],'samples':rows,'max_horse_vertex_delta_m':worst,'max_rein_gap_m':gap,'finite':finite,'pass':worst<=.00001 and gap<=.01 and finite,'render':{'engine':scene.render.engine,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'percentage':scene.render.resolution_percentage,'fps':scene.render.fps,'fps_base':scene.render.fps_base,'eevee_sample_settings':{n:getattr(eevee,n) for n in ('taa_render_samples','render_samples') if hasattr(eevee,n)}}}
  mf.write_json(out/'final-reopen.json',result);return ['final-reopen.json']
 if job['mode']=='demo_cut_contact_control':
  body=bpy.data.objects['horse'];path_owner=bpy.data.objects['horse diagnostic path'];original=path_owner.animation_data.action;groups={body.vertex_groups[n].index:n for n in ('DEF-r_hoof.L','DEF-r_hoof.R','DEF-f_hoof.L','DEF-f_hoof.R')};selected=None;results={}
  for variant in ('positive','path_speed_125pct'):
   if variant!='positive':
    changed=original.copy();path_owner.animation_data.action=changed
    for fc in mf.action_channels(changed):
     if fc.data_path=='location' and fc.array_index==1:
      for key in fc.keyframe_points:key.co.y*=1.25
   spans={};worst=0.;penetration=0.
   for tick in range(22*16+1):
    f=(tick+.5)/16;helper._refresh(scene,mf,f);deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
    if selected is None:
     selected=[]
     for v in mesh.vertices:
      if any(g.group in groups and g.weight>.5 for g in v.groups):selected.append(v.index)
    for i in selected:
     p=ev.matrix_world@mesh.vertices[i].co;penetration=max(penetration,-p.z)
     if p.z<=.015:
      spans.setdefault(i,p.copy());q=spans[i];worst=max(worst,math.hypot(p.x-q.x,p.y-q.y))
     else:spans.pop(i,None)
    ev.to_mesh_clear()
   results[variant]={'max_material_ground_band_travel_m':worst,'max_penetration_m':penetration,'samples':353,'sampling':'1/16 frame with 1/32 offset; not bake knots'}
   path_owner.animation_data.action=original
  results['input_sha256']=receipt['sha256'];results['frozen_material_travel_limit_m']=.02;results['pass']=results['positive']['max_material_ground_band_travel_m']<=.02 and results['path_speed_125pct']['max_material_ground_band_travel_m']>.02
  mf.write_json(out/'contact-control.json',results);return ['contact-control.json']
 if job['mode']=='demo_cut_check':
  result={'input_sha256':receipt['sha256'],'samples':[]};spans={};slip=0;penetration=0;reingap=0;previous=None;maxstep=0;finite=True;selected=None;material_spans={};material_slip=0;topology=None
  for tick in range(576*8+1):
   f=tick/8;helper._refresh(scene,mf,f);deps=bpy.context.evaluated_depsgraph_get()
   body=bpy.data.objects['horse'];ev=body.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
   if selected is None:
    names=['DEF-r_hoof.L','DEF-r_hoof.R','DEF-f_hoof.L','DEF-f_hoof.R'];groups={body.vertex_groups[n].index:n for n in names};selected={n:[] for n in names}
    for v in mesh.vertices:
     for g in v.groups:
      if g.group in groups and g.weight>.5:selected[groups[g.group]].append(v.index)
    topology=len(mesh.vertices)
   if len(mesh.vertices)!=topology:raise ValueError('Evaluated topology changed')
   hooves={}
   for name,ids in selected.items():
    pts=[(i,ev.matrix_world@mesh.vertices[i].co) for i in ids];pts.sort(key=lambda row:row[1].z);low=pts[:max(3,len(pts)//10)];center=sum((p for i,p in low),Vector())/len(low);hooves[name]={'center':list(center),'min_z':pts[0][1].z,'vertices':len(pts)}
    for i,p in pts:
     key=(name,i)
     if p.z<=.015:
      material_spans.setdefault(key,p.copy());q=material_spans[key];material_slip=max(material_slip,math.hypot(p.x-q.x,p.y-q.y))
     else:material_spans.pop(key,None)
   if tick%8==0:points=[v.co.copy() for v in mesh.vertices]
   ev.to_mesh_clear()
   for name,h in hooves.items():
    penetration=max(penetration,-h['min_z'])
    if h['min_z']<=.04:
     spans.setdefault(name,h['center']);p=spans[name];slip=max(slip,math.hypot(h['center'][0]-p[0],h['center'][1]-p[1]))
    else:spans.pop(name,None)
   for side in ('L','R'):
    hand=rider.pose.bones['hand_fk.'+side];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0));obj=bpy.data.objects['repaired rein '+side];end=obj.matrix_world@Vector(obj.data.splines[0].points[-1].co[:3]);reingap=max(reingap,(grip-end).length)
   if tick%8==0:
    finite=finite and all(math.isfinite(x) for p in points for x in p)
    if previous:maxstep=max(maxstep,math.sqrt(sum((p-q).length_squared for p,q in zip(points,previous))/len(points)))
    previous=points
    for name in ('Man','Helmet','saddle'):helper._bbox(bpy.data.objects[name],deps)
   result['samples'].append({'frame':f,'hooves':hooves,'horse_origin':list(horse.matrix_world.translation)})
   if tick%192==0:mf.write_json(out/'progress.json',{'frame':f,'max_slip':slip,'material_point_slip':material_slip,'rein_gap':reingap})
  start=result['samples'][0]['horse_origin'];end=result['samples'][-1]['horse_origin'];result.update(material_contact_screen_pass=material_slip<=.02 and penetration<=.02 and reingap<=.01 and finite,legacy_centroid_screen_retained=True,max_material_point_ground_band_travel_m=material_slip,max_near_floor_travel_m=slip,max_penetration_m=penetration,max_rein_gap_m=reingap,max_integer_mesh_rms_step_local_m=maxstep,finite=finite,actual_horse_travel_m=math.dist(start,end),contact_screens_pass=slip<=.05 and penetration<=.02 and reingap<=.01 and finite)
  peak=max((math.dist(a['hooves'][n]['center'],b['hooves'][n]['center'])*192,n,a['frame'],b['frame']) for a,b in zip(result['samples'],result['samples'][1:]) for n in a['hooves'])
  result['peak_hoof_centroid_speed']={'mps':peak[0],'group':peak[1],'from_frame':peak[2],'to_frame':peak[3],'role':'temporal diagnostic; centroid is not a fixed material vertex'}
  mf.write_json(out/'reopen.json',result);return ['reopen.json']
