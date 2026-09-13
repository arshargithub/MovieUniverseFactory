"""Source-centred whole-control gallop and contact projection, fixed local fixture."""
from pathlib import Path
import json,math,time
import bpy
from mathutils import Matrix,Vector
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
SHA='37594a7ef2d59e5dcc9af42c332f28ab41e86e78f78a60e6bd5ff9e2a7ca961e'
FPS=24;FRAMES=144;SPEED=12.;HZ=2.2;PERIOD=FPS/HZ
LEGS={'LH':('hind_foot_ik.L','DEF-r_hoof.L',9.125,12.46875,0.,.64579),'RH':('hind_foot_ik.R','DEF-r_hoof.R',1.34375,3.375,.14,.97284),'LF':('forefoot_ik.L','DEF-f_hoof.L',2.4375,5.46875,.32,.75438),'RF':('forefoot_ik.R','DEF-f_hoof.R',3.5,7.3125,.48,.81897)}
def hermite(a,b,m,u,span):return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*span*m+(-2*u**3+3*u*u)*b+(u**3-u*u)*span*m

def source_phase(phase,leg):
 _,_,a,b,td,stroke=LEGS[leg];d=stroke/(SPEED/HZ);p=(phase-td)%1;v=(b-a)/d;w=(10-b+a)/(1-d);slope=2*v*w/(v+w)
 return (hermite(a,b,slope,p/d,d) if p<=d else hermite(b,a+10,slope,(p-d)/(1-d),1-d))%10

def leg_for(name):
 for leg,(ctrl,_,_,_,_,_) in LEGS.items():
  side=ctrl[-2:];front=leg.startswith('L') if False else leg.endswith('F')
  if name.endswith(side) and ((front and name.startswith(('forefoot_','f_hoof','f_toe_'))) or (not front and name.startswith(('hind_foot_','r_hoof','r_toe_')))):return leg
 return None

def run(mf,out,job,helper):
 if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_source_gallop_probe','demo_source_gallop_build') or job['profile']!={}:raise ValueError('Fixed source gallop job required')
 out=Path(out)
 if BASE.resolve() not in out.resolve().parents:raise ValueError('Invalid output')
 helper._file(BASE/'realism-motion/scene.blend',SHA);bpy.ops.wm.open_mainfile(filepath=str(BASE/'realism-motion/scene.blend'),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;horse=bpy.data.objects['horse.rig'];rider=bpy.data.objects['rig'];path=bpy.data.objects['horse diagnostic path'];scene.frame_start=0;scene.frame_end=143;scene.render.fps=FPS
 for tr in horse.animation_data.nla_tracks:
  if tr.name.startswith('HoofContactOverlay'):tr.mute=True
 # Preserve original rig settings and authored Euler modes. Cache source before mutation.
 roots=[bpy.data.objects[n] for n in ('rider normalization','saddle','saddle.pad','saddle.stirrup.strap','saddle.stirrup','Torus.002','repaired rein L','repaired rein R')]
 cache={o.name:[] for o in roots}
 for tick in range(81):
  sf=tick/8;helper._refresh(scene,mf,sf)
  for obj in roots:
   m=obj.matrix_world.copy();m.translation.y+=6.47*sf/FPS;cache[obj.name].append(m)
 def interpolate(name,sf):
  x=sf*8;i=min(int(x),79);return cache[name][i].lerp(cache[name][i+1],x-i)
 def retime(owner,original,horse_controls=False):
  if not original:return
  action=original.copy();owner.animation_data.action=action
  original_curves=list(mf.action_channels(original));curves=list(mf.action_channels(action))
  for src,fc in zip(original_curves,curves):
   fc.keyframe_points.clear();name=src.data_path.split('"')[1] if src.data_path.startswith('pose.bones[') else '';leg=leg_for(name) if horse_controls else None
   for tick in range(FRAMES*4+1):
    f=tick/4;phase=f/PERIOD%1;sf=source_phase(phase,leg) if leg else phase*10;k=fc.keyframe_points.insert(f,src.evaluate(sf));k.interpolation='LINEAR'
  return action
 source=bpy.data.actions['horse.gallop']
 for tr in horse.animation_data.nla_tracks:tr.mute=True
 mf.assign_character_action(horse,source.copy());retime(horse,source,True)
 retime(rider,rider.animation_data.action)
 for obj in roots:
  if obj.type=='CURVE' and obj.data.animation_data and obj.data.animation_data.action:retime(obj.data,obj.data.animation_data.action)
 # One world locomotion owner. Moving assembly roots have periodic local transforms.
 helper._refresh(scene,mf,0)
 path.animation_data_clear();path.location=(0,0,0);path.keyframe_insert('location',frame=0);path.location.y=-SPEED*FRAMES/FPS;path.keyframe_insert('location',frame=FRAMES)
 for fc in mf.action_channels(path.animation_data.action):
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 for obj in roots:
  obj.animation_data_clear();obj.parent=path;obj.matrix_parent_inverse=Matrix.Identity(4);obj.rotation_mode='QUATERNION'
  for tick in range(FRAMES*4+1):
   f=tick/4;sf=f/PERIOD%1*10;m=interpolate(obj.name,sf);obj.matrix_basis=m
   for prop in ('location','rotation_quaternion','scale'):obj.keyframe_insert(prop,frame=f)
  for fc in mf.action_channels(obj.animation_data.action):
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 # Fit stable world anchors from the uncorrected candidate, separately per stance.
 raw=[]
 for tick in range(math.ceil(PERIOD*32)+1):
  f=tick/32;helper._refresh(scene,mf,f);raw.append((f,helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())))
 anchors={}
 for leg,(_,group,a,b,td,stroke) in LEGS.items():
  duration=stroke/SPEED*FPS;start=td*PERIOD;points=[h[group]['center'] for f,h in raw if start<=f<=start+duration]
  anchors[leg]=[.5*(min(p[i] for p in points)+max(p[i] for p in points)) for i in (0,1)]+[.003]
 records=[];maxcorr=0.;base_action=horse.animation_data.action
 # Cache current unprojected channels and apply correction only as a separate location overlay.
 for tick in range(FRAMES*4+1):
  f=tick/4;helper._refresh(scene,mf,f);hooves=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get())
  for leg,(ctrl,group,a,b,td,stroke) in LEGS.items():
   start=td*PERIOD;duration=stroke/SPEED*FPS;cycle=math.floor((f-start)/PERIOD);local=f-(start+cycle*PERIOD);margin=.075*PERIOD
   if local>duration+margin:cycle+=1;local-=PERIOD
   weight=1.
   if local<0:weight=max(0,1+local/margin)
   elif local>duration:weight=max(0,1-(local-duration)/margin)
   weight=weight*weight*(3-2*weight)
   current=hooves[group];anchor=Vector(anchors[leg]);anchor.y-=SPEED*cycle/HZ
   delta=Vector((anchor.x-current['center'][0],anchor.y-current['center'][1],.003-current['min_z']))*weight
   if not(-margin<=local<=duration+margin):delta=Vector()
   maxcorr=max(maxcorr,delta.length);pb=horse.pose.bones[ctrl];mat=pb.matrix.copy();mat.translation+=horse.matrix_world.inverted().to_3x3()@delta;pb.matrix=mat;bpy.context.view_layer.update();records.append((f,ctrl,tuple(pb.location)))
 # Replace the four location channels with the evaluated projected result; preserve Euler/scale/other controls.
 channels=list(mf.action_channels(base_action))
 for ctrl in [v[0] for v in LEGS.values()]:
  for axis in range(3):
   fc=next(x for x in channels if x.data_path==horse.pose.bones[ctrl].path_from_id('location') and x.array_index==axis);fc.keyframe_points.clear()
   for f,n,loc in records:
    if n==ctrl:k=fc.keyframe_points.insert(f,loc[axis]);k.interpolation='LINEAR'
 stats={'speed_target_mps':SPEED,'frequency_hz':HZ,'stride_m':SPEED/HZ,'frames':FRAMES,'fps':FPS,'source_scene_sha256':SHA,'max_contact_projection_m':maxcorr,'anchors':anchors,'controls_phase_mapped':[fc.data_path for fc in mf.action_channels(source) if leg_for(fc.data_path.split('"')[1])],'samples':[]}
 for tick in range(FRAMES*4+1):
  f=tick/4;helper._refresh(scene,mf,f);h=helper.hoof_surfaces(bpy.context.evaluated_depsgraph_get());stats['samples'].append({'frame':f,'hooves':h,'torso':list(horse.matrix_world@horse.pose.bones['torso'].head)})
 stats['max_penetration_m']=max(0,max(-h['min_z'] for r in stats['samples'] for h in r['hooves'].values()))
 # Near-floor travel, independent from authored support schedule.
 spans={};slip=0
 for r in stats['samples']:
  for n,h in r['hooves'].items():
   if h['min_z']<=.025:
    spans.setdefault(n,h['center']);p=spans[n];slip=max(slip,math.hypot(p[0]-h['center'][0],p[1]-h['center'][1]))
   else:spans.pop(n,None)
 stats['max_near_floor_travel_m']=slip
 mf.write_json(out/'motion.json',stats)
 bpy.data.objects['diagnostic road'].scale.y=130
 scene.render.resolution_x=640;scene.render.resolution_y=360;scene.cycles.samples=12;scene.cycles.use_denoising=True
 if job['mode']=='demo_source_gallop_probe':
  for name in ('lateral','threequarter'):
   scene.camera=bpy.data.objects[name];folder=out/name;folder.mkdir(exist_ok=True)
   for f in (0,2,4,6,8,10):helper._refresh(scene,mf,f);scene.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
 else:
  bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),check_existing=False)
 return ['motion.json']
