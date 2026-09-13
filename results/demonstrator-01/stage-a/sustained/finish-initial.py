"""Fixed checkpoint validation, effects/look, and bounded frame rendering."""
from pathlib import Path
import json,math,time,importlib.util,bpy
from mathutils import Vector
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
ROOT=BASE.parents[1]
def run(mf,out,job,helper):
 if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_sustained_check','demo_sustained_fx','demo_sustained_render'):raise ValueError('Fixed finish operation required')
 out=Path(out).resolve()
 if BASE.resolve() not in out.parents:raise ValueError('Invalid output')
 profile=job['profile']
 if job['mode']!='demo_sustained_render' and profile!={}:raise ValueError('Empty profile required')
 if job['mode']=='demo_sustained_render' and (set(profile)!={'view','start','end'} or profile['view'] not in ('hero','contact') or type(profile['start']) is not int or type(profile['end']) is not int or not 0<=profile['start']<profile['end']<=144):raise ValueError('Invalid render bounds')
 receipt=json.loads((ROOT/'results/demonstrator-01/stage-a/sustained/current-scene.json').read_text());path=Path(receipt['path']).resolve()
 if BASE.resolve() not in path.parents or path.name!='scene.blend':raise ValueError('Invalid scene receipt')
 helper._file(path,receipt['sha256']);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];rider=bpy.data.objects['rig']
 if job['mode']=='demo_sustained_check':
  result={'input_sha256':receipt['sha256'],'samples':[]};spans={};slip=0;penetration=0;reingap=0;previous=None;maxstep=0;finite=True
  for tick in range(144*8+1):
   f=tick/8;helper._refresh(scene,mf,f);deps=bpy.context.evaluated_depsgraph_get();hooves=helper.hoof_surfaces(deps)
   for name,h in hooves.items():
    penetration=max(penetration,-h['min_z'])
    if h['min_z']<=.04:
     spans.setdefault(name,h['center']);p=spans[name];slip=max(slip,math.hypot(h['center'][0]-p[0],h['center'][1]-p[1]))
    else:spans.pop(name,None)
   for side in ('L','R'):
    hand=rider.pose.bones['hand_fk.'+side];grip=rider.matrix_world@hand.matrix@Vector((0,hand.length*.55,0));obj=bpy.data.objects['repaired rein '+side];end=obj.matrix_world@Vector(obj.data.splines[0].points[-1].co[:3]);reingap=max(reingap,(grip-end).length)
   if tick%8==0:
    obj=bpy.data.objects['horse'];ev=obj.evaluated_get(deps);mesh=ev.to_mesh();points=[v.co.copy() for v in mesh.vertices];ev.to_mesh_clear();finite=finite and all(math.isfinite(x) for p in points for x in p)
    if previous:maxstep=max(maxstep,math.sqrt(sum((p-q).length_squared for p,q in zip(points,previous))/len(points)))
    previous=points
    for name in ('Man','Helmet','saddle'):helper._bbox(bpy.data.objects[name],deps)
   result['samples'].append({'frame':f,'hooves':hooves,'horse_origin':list(horse.matrix_world.translation)})
  start=result['samples'][0]['horse_origin'];end=result['samples'][-1]['horse_origin'];result.update(max_near_floor_travel_m=slip,max_penetration_m=penetration,max_rein_gap_m=reingap,max_integer_mesh_rms_step_local_m=maxstep,finite=finite,actual_horse_travel_m=math.dist(start,end),contact_screens_pass=slip<=.05 and penetration<=.02 and reingap<=.01 and finite)
  mf.write_json(out/'reopen.json',result);return ['reopen.json']
 if job['mode']=='demo_sustained_fx':
  spec=importlib.util.spec_from_file_location('sustained_fx',Path(__file__).with_name('sustained_fx.py'));fx=importlib.util.module_from_spec(spec);spec.loader.exec_module(fx)
  tail=fx.tail(scene,horse,helper,mf,2.2,frames=145)
  motion=json.loads((BASE/'source-gallop-build/motion.json').read_text());anchors=motion['anchors'];tds={'LH':0.,'RH':.14,'LF':.32,'RF':.48};events=[]
  for cycle in range(-4,15):
   for leg,td in tds.items():
    t=(cycle+td)/2.2;p=anchors[leg];events.append({'time':t,'leg':leg,'anchor':[p[0],p[1]-12*cycle/2.2,0]})
  objects,dust=fx.dust(scene,events,helper,frames=145)
  # Broaden ground so its finite boundary cannot cut diagonally behind the subject.
  road=bpy.data.objects['diagnostic road'];road.scale.x=200;road.scale.y=250
  mat=bpy.data.materials.new('dry road fine soil');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bsdf=n.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.92
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.4;tex.inputs['Detail'].default_value=3;coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.13,.067,.026,1);ramp.color_ramp.elements[1].color=(.46,.29,.12,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bsdf.inputs['Base Color']);fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=70;l.new(coord.outputs['Object'],fine.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25;bump.inputs['Distance'].default_value=.025;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bsdf.inputs['Normal']);road.data.materials.clear();road.data.materials.append(mat)
  for obj in scene.objects:
   if obj.type=='MESH' and any(m and m.name=='diagnostic ridge' for m in obj.data.materials):obj.hide_render=True
  target=bpy.data.objects['camera target'];hero=bpy.data.objects['lateral'];hero.data.lens=42;hero.location.y+=1.0
  hero.name='hero';contact=bpy.data.objects['threequarter'];contact.name='contact';contact.data.lens=43
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
