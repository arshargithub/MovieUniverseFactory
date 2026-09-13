"""Fixed checkpoint validation, effects/look, and bounded frame rendering."""
from pathlib import Path
import json,math,time,importlib.util,bpy
from mathutils import Vector
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
ROOT=BASE.parents[1]
def run(mf,out,job,helper):
 if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_sustained_check','demo_sustained_fx','demo_sustained_render','demo_sustained_look','demo_sustained_contact_control'):raise ValueError('Fixed finish operation required')
 out=Path(out).resolve()
 if BASE.resolve() not in out.parents:raise ValueError('Invalid output')
 profile=job['profile']
 if job['mode']!='demo_sustained_render' and profile!={}:raise ValueError('Empty profile required')
 if job['mode']=='demo_sustained_render' and (set(profile)!={'view','start','end'} or profile['view'] not in ('hero','contact') or type(profile['start']) is not int or type(profile['end']) is not int or not 0<=profile['start']<profile['end']<=144):raise ValueError('Invalid render bounds')
 receipt_name='fx-scene.json' if job['mode']=='demo_sustained_look' else 'current-scene.json'
 receipt=json.loads((ROOT/'results/demonstrator-01/stage-a/sustained'/receipt_name).read_text());path=Path(receipt['path']).resolve()
 if BASE.resolve() not in path.parents or path.name!='scene.blend':raise ValueError('Invalid scene receipt')
 helper._file(path,receipt['sha256']);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];rider=bpy.data.objects['rig']
 if job['mode']=='demo_sustained_contact_control':
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
 if job['mode']=='demo_sustained_look':
  try:scene.render.engine='BLENDER_EEVEE'
  except TypeError:scene.render.engine='BLENDER_EEVEE_NEXT'
  scene.render.resolution_x=960;scene.render.resolution_y=540
  target=bpy.data.objects['camera target'];target.location.y=4.5;target.location.z=1.35
  hero=bpy.data.objects['hero'];hero.location=(9,4.5,3.1);hero.data.lens=40
  contact=bpy.data.objects['contact'];contact.location=(8,-3,3.0);contact.data.lens=46
  material=bpy.data.materials['dry road fine soil'];nodes=material.node_tree.nodes;links=material.node_tree.links;geo=nodes.new('ShaderNodeNewGeometry')
  for node in nodes:
   if node.bl_idname=='ShaderNodeTexNoise':links.new(geo.outputs['Position'],node.inputs['Vector'])
  dust=bpy.data.materials['Soft Warm Contact Dust Volume']
  # The final density gain is the multiply node feeding Volume Density.
  volume=next(n for n in dust.node_tree.nodes if n.bl_idname=='ShaderNodeVolumePrincipled')
  gain=volume.inputs['Density'].links[0].from_node;gain.inputs[1].default_value=30
  volume.inputs['Color'].default_value=(.55,.37,.18,1)
  scene.camera=hero;helper._refresh(scene,mf,50);scene.render.filepath=str(out/'look.png');start=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-start
  mf.write_json(out/'look.json',{'input_sha256':receipt['sha256'],'renderer':scene.render.engine,'seconds':elapsed,'projected_hero_seconds':elapsed*144,'resolution':[960,540],'camera_target':list(target.location)})
  bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),check_existing=False);return ['look.png','look.json','scene.blend']
 if job['mode']=='demo_sustained_check':
  result={'input_sha256':receipt['sha256'],'samples':[]};spans={};slip=0;penetration=0;reingap=0;previous=None;maxstep=0;finite=True;selected=None;material_spans={};material_slip=0;topology=None
  for tick in range(144*8+1):
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
 if job['mode']=='demo_sustained_fx':
  spec=importlib.util.spec_from_file_location('sustained_fx',Path(__file__).with_name('sustained_fx.py'));fx=importlib.util.module_from_spec(spec);spec.loader.exec_module(fx)
  tail=fx.tail(scene,horse,helper,mf,2.2,frames=145)
  motion=json.loads((path.parent/'motion.json').read_text());events=list(motion['contact_events'])
  first=[e for e in events if e['cycle']==0]
  for cycle in (-4,-3,-2,-1):
   for e in first:events.append({'time':e['time']+cycle/2.2,'leg':e['leg'],'anchor':[e['anchor'][0],e['anchor'][1]-12*cycle/2.2,0.]})
  objects,dust=fx.dust(scene,events,helper,frames=145)
  # Broaden ground so its finite boundary cannot cut diagonally behind the subject.
  road=bpy.data.objects['diagnostic road'];road.scale.x=200;road.scale.y=250
  mat=bpy.data.materials.new('dry road fine soil');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bsdf=n.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.92
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.4;tex.inputs['Detail'].default_value=3;coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.13,.067,.026,1);ramp.color_ramp.elements[1].color=(.46,.29,.12,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bsdf.inputs['Base Color']);fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=70;l.new(coord.outputs['Object'],fine.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25;bump.inputs['Distance'].default_value=.025;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bsdf.inputs['Normal']);road.data.materials.clear();road.data.materials.append(mat)
  for obj in scene.objects:
   if obj.type=='MESH' and any(m and m.name=='diagnostic ridge' for m in obj.data.materials):obj.hide_render=True
  geo=n.new('ShaderNodeNewGeometry');l.new(geo.outputs['Position'],tex.inputs['Vector']);l.new(geo.outputs['Position'],fine.inputs['Vector'])
  target=bpy.data.objects['camera target'];target.location.y=4.1;target.location.z=1.4;hero=bpy.data.objects['lateral'];hero.data.lens=40;hero.location=(8.5,4.1,2.8)
  hero.name='hero';contact=bpy.data.objects['threequarter'];contact.name='contact';contact.data.lens=36
  try:scene.render.engine='BLENDER_EEVEE'
  except TypeError:scene.render.engine='BLENDER_EEVEE_NEXT'
  scene.frame_end=143;scene.render.resolution_x=960;scene.render.resolution_y=540;scene.cycles.samples=24;scene.cycles.use_denoising=True
  scene.camera=hero;helper._refresh(scene,mf,50);scene.render.filepath=str(out/'look.png');start=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-start
  mf.write_json(out/'fx.json',{'source_scene_sha256':receipt['sha256'],'tail':tail,'dust':dust,'representative_render_seconds':elapsed,'frames':144,'fps':24,'forecast_hero_seconds':elapsed*144})
  bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),check_existing=False)
  return ['fx.json','look.png','scene.blend']
 # Fully baked scene, separately bounded frame interval. No time-dependent simulation.
 scene.camera=bpy.data.objects[profile['view']]
 if profile['view']=='contact':
  for collection in bpy.data.collections:
   if collection.name.startswith('FX Contact Dust'):collection.hide_render=True
  scene.render.resolution_x=640;scene.render.resolution_y=360;scene.cycles.samples=12
 else:scene.render.resolution_x=960;scene.render.resolution_y=540;scene.cycles.samples=24
 times=[]
 for f in range(profile['start'],profile['end']):
  helper._refresh(scene,mf,f);scene.render.filepath=str(out/f'{f:04d}.png');start=time.monotonic();bpy.ops.render.render(write_still=True);times.append({'frame':f,'seconds':time.monotonic()-start});mf.write_json(out/'render-times.json',{'scene_sha256':receipt['sha256'],'view':profile['view'],'frames':times})
 return ['render-times.json']
