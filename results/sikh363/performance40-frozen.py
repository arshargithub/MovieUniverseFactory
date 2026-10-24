"""Fixed363 phased edit, explicit permission hoist and exchange eyeline.

Reviewed fixed implementation candidate; never accepts code/paths from recipe.
"""
import math,json,importlib.util
from pathlib import Path
import numpy as np

OLD=[252,283,300,307,323,331,350,356]
NEW=[252,283,300,306,314,317,327,333]
def edit_time(x):
 if x<=252:return x
 if x>=356:return x-23
 i=next(i for i in range(7) if OLD[i]<=x<OLD[i+1]);h=OLD[i+1]-OLD[i];t=(x-OLD[i])/h;ds=[(NEW[j+1]-NEW[j])/(OLD[j+1]-OLD[j]) for j in range(7)]
 def slope(j):
  if j in (0,7):return 1.
  if OLD[j]==350:return .5
  a=OLD[j]-OLD[j-1];b=OLD[j+1]-OLD[j];w1=2*b+a;w2=b+2*a;return (w1+w2)/(w1/ds[j-1]+w2/ds[j])
 return (2*t**3-3*t*t+1)*NEW[i]+(t**3-2*t*t+t)*h*slope(i)+(-2*t**3+3*t*t)*NEW[i+1]+(t**3-t*t)*h*slope(i+1)
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)

def run(bpy,out):
 from mathutils import Vector,Matrix,Quaternion
 def load(name):
  spec=importlib.util.spec_from_file_location('performance363_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 motion=load('nihang_motion');support=load('nihang_support');scene=bpy.context.scene;rig=bpy.data.objects['MF coherent Nihang rig'];shaft=bpy.data.objects['LEADER spear world contact owner'];root=bpy.data.objects['mounted leader'];bones=rig.data.bones
 if scene.get('performance363'):raise ValueError('PERFORMANCE363_REAPPLY')
 owned=[bpy.data.objects[n] for n in ('HORSE hind support pivot','mounted leader','horse.rig','MF coherent Nihang rig','LEADER spear world contact owner')]
 owned += [ob for ob in rig.children_recursive if not ob.hide_render and ob.name.startswith(('MF Nihang wrapped crown','MF Nihang overlapped cloth','MF Nihang gathered crown','eyeball.','iris.','pupil.','brow.','MF347 integrated beard'))];source_integers={}
 def anchors():
  hr=bpy.data.objects['horse.rig'];return dict(worlds={o.name:[list(r) for r in o.matrix_world] for o in owned},horse_head=list(hr.matrix_world@hr.pose.bones['DEF-head'].head),right_grip=list(rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5)))
 for f in range(252,442):scene.frame_set(f);bpy.context.view_layer.update();source_integers[f]=anchors()
 removed=[];visited=set()
 for owner in owned:
  for fc in motion.curves(owner):
   if fc.as_pointer() in visited or not fc.keyframe_points:continue
   visited.add(fc.as_pointer());values=[float(fc.evaluate(f)) for f in range(252,442)]
   fractional=[tuple(k.co) for k in fc.keyframe_points if 252<=k.co.x<=441 and abs(k.co.x-round(k.co.x))>=1e-5]
   outside=[dict(co=tuple(k.co),left=tuple(k.handle_left),right=tuple(k.handle_right),interpolation=k.interpolation,left_type=k.handle_left_type,right_type=k.handle_right_type) for k in fc.keyframe_points if k.co.x<252 or k.co.x>441]
   coords=sorted([r['co'] for r in outside]+list(zip(range(252,442),values)));oldrows={round(r['co'][0],5):r for r in outside};fc.keyframe_points.clear();fc.keyframe_points.add(len(coords));fc.keyframe_points.foreach_set('co',np.asarray(coords,dtype=np.float32).ravel())
   for key in fc.keyframe_points:
    row=oldrows.get(round(float(key.co.x),5))
    if row:
     key.interpolation=row['interpolation'];key.handle_left_type=row['left_type'];key.handle_right_type=row['right_type'];key.handle_left=row['left'];key.handle_right=row['right']
    else:key.interpolation='LINEAR'
   fc.update()
   if fractional:removed.append(dict(owner=owner.name,path=fc.data_path,index=fc.array_index,removed=fractional))
 preservation=[]
 for f in range(252,442):
  scene.frame_set(f);bpy.context.view_layer.update();now=anchors();before=source_integers[f];error=max(float(np.max(np.abs(np.array(now['worlds'][n])-np.array(before['worlds'][n])))) for n in now['worlds']);error=max(error,float(np.max(np.abs(np.array(now['horse_head'])-before['horse_head']))),float(np.max(np.abs(np.array(now['right_grip'])-before['right_grip']))));preservation.append(dict(frame=f,error=error))
  if error>1e-5:raise ValueError('PERFORMANCE363_INTEGER_POSE_CHANGED:'+str((f,error)))
 (out/'source363-key-repair.json').write_text(json.dumps(dict(removed=removed,preservation=preservation),indent=2)+'\n')
 hemisphere=[]
 for action in bpy.data.actions:
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     groups={}
     for fc in bag.fcurves:
      if fc.data_path.endswith('rotation_quaternion'):groups.setdefault(fc.data_path,{})[fc.array_index]=fc
     for path,group in groups.items():
      if set(group)!={0,1,2,3}:raise ValueError('PERFORMANCE363_QUAT_CHANNELS')
      times=[[float(k.co.x) for k in group[i].keyframe_points] for i in range(4)]
      if any(t!=times[0] for t in times[1:]):raise ValueError('PERFORMANCE363_QUAT_CLOCK_MISMATCH')
      previous=None;flips=0
      for j in range(len(times[0])):
       q=np.array([group[i].keyframe_points[j].co.y for i in range(4)])
       if np.linalg.norm(q)<1e-8:raise ValueError('PERFORMANCE363_ZERO_QUAT')
       if previous is not None and np.dot(q,previous)<0:
        q=-q;flips+=1
        for i in range(4):
         key=group[i].keyframe_points[j];y=float(key.co.y);left=float(key.handle_left.y);right=float(key.handle_right.y);key.co.y=-y;key.handle_left.y=-left;key.handle_right.y=-right
       previous=q
      if flips:hemisphere.append(dict(action=action.name,path=path,flips=flips))
      for fc in group.values():fc.update()
 # Moving sparse control keys is not equivalent to retiming a densely baked
 # world path under a nonlinear clock. Sample EVERY consumer at one inverse
 # source time instead, then evaluate the whole new scene at integer frames.
 frames=list(range(252,419));source_times=[]
 for frame in frames:
  lo,hi=252.,441.
  for _ in range(40):
   mid=(lo+hi)/2
   if edit_time(mid)<frame:lo=mid
   else:hi=mid
  source_times.append((lo+hi)/2)
 source_contacts=[]
 for f in source_times:
  scene.frame_set(math.floor(f),subframe=f-math.floor(f));bpy.context.view_layer.update();grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5);source_contacts.append(dict(time=f,grip=list(grip),errors=[(ob.matrix_world@Vector(ob.data.splines[0].points[-1].co[:3])-grip).length for ob in bpy.data.objects if ob.name.startswith('leader supported rein292')]))
 (out/'source363-preflight.json').write_text(json.dumps(source_contacts,indent=2)+'\n')
 if max(max(x['errors']) for x in source_contacts)>.008:raise ValueError('PERFORMANCE363_SOURCE_SUBFRAME_CONTACT')
 clocks=[];total_keys=0;new_key_allocation=0;original_keys=0
 for action in bpy.data.actions:
  count=0
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      if not fc.keyframe_points:continue
      values=[float(fc.evaluate(t)) for t in source_times];outside=[]
      for k in fc.keyframe_points:
       if k.co.x<252 or k.co.x>441:outside.append(dict(co=(edit_time(float(k.co.x)),float(k.co.y)),left=(edit_time(float(k.handle_left.x)),float(k.handle_left.y)),right=(edit_time(float(k.handle_right.x)),float(k.handle_right.y)),interpolation=k.interpolation,left_type=k.handle_left_type,right_type=k.handle_right_type,easing=k.easing))
      inside=list(zip(frames,values)) if max(values)-min(values)>1e-9 else [(252,values[0]),(418,values[-1])]
      coords=sorted([row['co'] for row in outside]+inside);before_count=len(fc.keyframe_points);original_keys+=before_count;total_keys+=len(coords);new_key_allocation+=max(0,len(coords)-before_count)
      if new_key_allocation>4000000:raise ValueError('PERFORMANCE363_RESAMPLE_RESOURCE_BOUND')
      fc.keyframe_points.clear();fc.keyframe_points.add(len(coords));fc.keyframe_points.foreach_set('co',np.asarray(coords,dtype=np.float32).ravel());oldrows={round(row['co'][0],5):row for row in outside}
      for key in fc.keyframe_points:
       row=oldrows.get(round(float(key.co.x),5))
       if row:
        key.interpolation=row['interpolation'];key.handle_left_type=row['left_type'];key.handle_right_type=row['right_type'];key.handle_left=row['left'];key.handle_right=row['right'];key.easing=row['easing']
       else:key.interpolation='LINEAR'
      count+=len(coords)
      fc.update()
  if count:clocks.append(dict(action=action.name,keys=count,users=action.users))
 for marker in scene.timeline_markers:marker.frame=round(edit_time(marker.frame))
 scene.frame_end=round(edit_time(scene.frame_end));capture={}
 # Visible rigid head attachments must follow the actual new head owner too.
 scene.frame_set(283);bpy.context.view_layer.update();headworld=rig.matrix_world@rig.pose.bones['head'].head;accessories=[]
 for ob in rig.children_recursive:
  if ob.type not in {'MESH','CURVE'} or ob.hide_render or any(m.type=='ARMATURE' for m in ob.modifiers):continue
  if ob.parent_type=='BONE':continue
  corners=[ob.matrix_world@Vector(p) for p in ob.bound_box];center=sum(corners,Vector())/8
  if (center-headworld).length<.48:accessories.append(ob)
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();capture[f]=dict(world=rig.matrix_world.copy(),bones={p.name:p.matrix.copy() for p in rig.pose.bones},shaft=shaft.matrix_world.copy(),camera=scene.camera.matrix_world.copy(),root=root.matrix_world.copy(),accessories={ob.name:ob.matrix_world.copy() for ob in accessories})
 # New integer frames expose previously unreviewed subframe interpolation.
 # Do not hide a retime failure by rebuilding a rope around a broken pose.
 retime_contacts=[]
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5)
  errors=[(ob.matrix_world@Vector(ob.data.splines[0].points[-1].co[:3])-grip).length for ob in bpy.data.objects if ob.name.startswith('leader supported rein292')]
  source=source_contacts[f-252];retime_contacts.append(dict(frame=f,errors=errors,source_time=source['time'],source_grip_error=(grip-Vector(source['grip'])).length))
 (out/'retime363-preflight.json').write_text(json.dumps(dict(hemisphere_unwrap=hemisphere,contacts=retime_contacts),indent=2)+'\n')
 if max(max(x['errors']) for x in retime_contacts)>.008 or max(x['source_grip_error'] for x in retime_contacts)>.0002:raise ValueError('PERFORMANCE363_RETIME_CONTACT:'+str(sorted(retime_contacts,key=lambda x:max(x['errors']))[-3:]))
 armnames=[n for n in bones.keys() if n.endswith('.L') and n.startswith(('upperarm','lowerarm','wrist','metacarpal','finger'))]
 neck=bones['neck02'];head=bones['head'];headnames=[b.name for b in bones if b==neck or neck in b.parent_recursive];changed=set(armnames+headnames)
 ua=(bones['lowerarm01.L'].head_local-bones['upperarm01.L'].head_local).length;la=(bones['wrist.L'].head_local-bones['lowerarm01.L'].head_local).length
 failed=[];solutions=None
 for height in (.48,.43,.38,.33):
  candidate={}
  try:
   for f,row in capture.items():
    amount=ease((f-302)/11);worlddelta=Vector((0,0,height*amount))+row['root'].to_quaternion()@Vector((.11,0,0));localdelta=row['world'].inverted().to_3x3()@worlddelta;old=row['bones'];s=old['upperarm01.L'].translation;w=old['wrist.L'].translation+localdelta;e=Vector(support.bend_joint(s,w,ua,la,old['lowerarm01.L'].translation-s));candidate[f]=dict(delta=worlddelta,localdelta=localdelta,elbow=e,wrist=w)
   solutions=candidate;chosen=height;break
  except ValueError as ex:failed.append(dict(height=height,error=str(ex)))
 if solutions is None:raise ValueError('PERFORMANCE363_HOIST_REACH:'+str(failed))
 targets={};shaft_targets={};head_delta={};gaze=[]
 from bpy_extras.object_utils import world_to_camera_view
 camera=scene.camera;camera_mode=camera.rotation_mode;rawcamera={f:row['camera'].copy() for f,row in capture.items()};chosen_camera=None
 for factor in (1.18,1.24,1.30,1.36):
  okay=True;candidates={}
  for f,row in capture.items():
   cam=rawcamera[f].copy()
   if 276<=f<=333:
    center=row['root'].translation+Vector((0,0,.5));q=Quaternion((0,0,1),math.radians(-25)).to_matrix().to_4x4();cam=Matrix.Translation(center)@q@Matrix.Translation(-center)@cam;cam.translation=center+(cam.translation-center)*factor;camera.matrix_world=cam
    tip=(Matrix.Translation(solutions[f]['delta'])@row['shaft'])@Vector((0,0,3.91));p=world_to_camera_view(scene,camera,tip)
    if not .03<p.x<.97 or not .03<p.y<.97:okay=False
   candidates[f]=cam
  if okay:chosen_camera=candidates;camera_factor=factor;break
 camera.matrix_world=rawcamera[283]
 if chosen_camera is None:raise ValueError('PERFORMANCE363_RAISED_TIP_FRAME')
 for f,row in capture.items():row['camera']=chosen_camera[f]
 for f,row in capture.items():
  old=row['bones'];v=solutions[f];desired={n:m.copy() for n,m in old.items()};s=old['upperarm01.L'].translation;e0=old['lowerarm01.L'].translation;w0=old['wrist.L'].translation
  for names,a,b,na,nb in [(('upperarm01.L','upperarm02.L'),s,e0,s,v['elbow']),(('lowerarm01.L','lowerarm02.L'),e0,w0,v['elbow'],v['wrist'])]:
   rot=(b-a).normalized().rotation_difference((nb-na).normalized()).to_matrix().to_4x4();delta=Matrix.Translation(na)@rot@Matrix.Translation(-a)
   for n in names:desired[n]=delta@old[n]
  for n in armnames:
   if n.startswith(('wrist','metacarpal','finger')):desired[n]=Matrix.Translation(v['localdelta'])@old[n]
  # The exchange camera is a proxy for the Sikh eyeline. Distribute a bounded
  # turn over neck and head; preserve eyes, beard and crown as one character.
  hd=old['head']@head.matrix_local.inverted();forward=row['world'].to_3x3()@(hd.to_3x3()@Vector((0,-1,0)));want=row['camera'].translation-row['world']@old['head'].translation;forward.z=0;want.z=0;forward.normalize();want.normalize();yaw=math.atan2(forward.cross(want).z,forward.dot(want));yaw=max(-math.radians(55),min(math.radians(55),yaw))*ease((f-277)/9)
  axis=row['world'].to_quaternion().inverted()@Vector((0,0,1));q=Quaternion(axis,yaw*.35).to_matrix().to_4x4();pivot=old['neck02'].translation;delta=Matrix.Translation(pivot)@q@Matrix.Translation(-pivot)
  for n in headnames:desired[n]=delta@old[n]
  q=Quaternion(axis,yaw*.65).to_matrix().to_4x4();pivot=desired['head'].translation;delta=Matrix.Translation(pivot)@q@Matrix.Translation(-pivot)
  for n in headnames:
   if n=='head' or head in bones[n].parent_recursive:desired[n]=delta@desired[n]
  targets[f]=desired;shaft_targets[f]=Matrix.Translation(v['delta'])@row['shaft'];head_delta[f]=row['world']@desired['head']@old['head'].inverted()@row['world'].inverted();gaze.append(dict(frame=f,yaw_degrees=math.degrees(yaw),lift=v['delta'].z))
 # Local-basis conversion uses desired parents, never dependency-update order.
 values={n:[] for n in changed}
 for f,row in capture.items():
  for n in changed:
   b=bones[n];parent=b.parent;basis=b.convert_local_to_pose(targets[f][n],b.matrix_local,parent_matrix=targets[f][parent.name],parent_matrix_local=parent.matrix_local,invert=True);loc,q,scale=basis.decompose();q.normalize()
   if values[n] and q.dot(values[n][-1][1])<0:q.negate()
   values[n].append((loc,q,scale))
 def bake(owner,data):
  for path,rows in data.items():
   owner.keyframe_insert(path,frame=252)
   curves={fc.array_index:fc for fc in motion.curves(owner) if fc.data_path==path}
   for index,fc in curves.items():
    outside=[tuple(k.co) for k in fc.keyframe_points if k.co.x<252 or k.co.x>418];coords=np.array(sorted(outside+[(f,rows[j][index]) for j,f in enumerate(frames)]),dtype=np.float32);fc.keyframe_points.clear();fc.keyframe_points.add(len(coords));fc.keyframe_points.foreach_set('co',coords.ravel())
    for k in fc.keyframe_points:k.interpolation='LINEAR'
    fc.update()
 data={}
 for n in changed:
  pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION'
  for slot,prop in enumerate(('location','rotation_quaternion','scale')):data[pb.path_from_id()+'.'+prop]=[r[slot] for r in values[n]]
 bake(rig,data)
 def object_bake(ob,matrices):
  rows=[]
  for f,m in zip(frames,matrices):
   if ob.parent:
    parent=capture[f]['world'] if ob.parent==rig else ob.parent.matrix_world
    m=ob.matrix_parent_inverse.inverted()@parent.inverted()@m
   loc,q,scale=m.decompose();q.normalize()
   if rows and q.dot(rows[-1][1])<0:q.negate()
   rows.append((loc,q,scale))
  ob.rotation_mode='QUATERNION';bake(ob,{prop:[r[j] for r in rows] for j,prop in enumerate(('location','rotation_quaternion','scale'))})
 object_bake(shaft,[shaft_targets[f] for f in frames])
 for ob in accessories:object_bake(ob,[head_delta[f]@capture[f]['accessories'][ob.name] for f in frames])
 if camera_mode not in {'XYZ','XZY','YXZ','YZX','ZXY','ZYX'}:raise ValueError('PERFORMANCE363_CAMERA_MODE')
 camera.rotation_mode=camera_mode;camera_rows=[];previous=None
 for f in frames:
  m=chosen_camera[f];e=m.to_euler(camera_mode,previous) if previous else m.to_euler(camera_mode);previous=e.copy();camera_rows.append((m.translation,e,m.to_scale()))
 bake(camera,{prop:[r[j] for r in camera_rows] for j,prop in enumerate(('location','rotation_euler','scale'))})
 # The spear strike stays at300 but moves outboard with the material hand.
 for ob in bpy.data.objects:
  if 'spear' not in ob.name.lower() or not ob.name.startswith(('305 hoof earth puff','305 kicked soil clod')):continue
  if ob.parent:raise ValueError('PERFORMANCE363_IMPACT_PARENT')
  delta=solutions[300]['delta']
  for fc in motion.curves(ob):
   if fc.data_path=='location':
    for k in fc.keyframe_points:k.co.y+=delta[fc.array_index];k.handle_left.y+=delta[fc.array_index];k.handle_right.y+=delta[fc.array_index]
    fc.update()
 records=[]
 for f,row in capture.items():
  scene.frame_set(f);bpy.context.view_layer.update();err=max(abs(rig.pose.bones[n].matrix[i][j]-targets[f][n][i][j]) for n in changed for i in range(4) for j in range(4));pole=max(abs(shaft.matrix_world[i][j]-shaft_targets[f][i][j]) for i in range(4) for j in range(4))
  if err>3e-4 or pole>3e-4:raise ValueError('PERFORMANCE363_BAKE_DRIFT:'+str((f,err,pole)))
  records.append(dict(frame=f,bone_error=err,pole_error=pole))
 scene['performance363']=1;scene.frame_set(314);bpy.context.view_layer.update()
 report=dict(allocation=dict(original_keys=original_keys,final_keys=total_keys,positive_new_keys=new_key_allocation),source_key_repair=dict(tracks=len(removed),keys=sum(len(x['removed']) for x in removed),maximum_integer_pose_error=max(x['error'] for x in preservation)),hemisphere_unwrap=hemisphere,retime_contacts=retime_contacts,camera=dict(orbit_degrees=-25,distance_factor=camera_factor,mode_preserved=camera_mode),clock=dict(old=OLD,new=NEW,airborne_frames=[43,21],shot=[276,333],handles=[252,357],downstream_shift=-23,consumers=clocks),hoist=dict(height=chosen,failed_preflights=failed,start=302,held_from=313,outboard=.11),gaze=gaze,accessories=[o.name for o in accessories],frames=records,scope='Actual phased timing/hoist/head ownership candidate. Flag still old rigid wave until separate final-clock CLOTH bake. Actual framing, anatomy, face/pole clearance and Director full-speed judgment mandatory.')
 (out/'performance363.json').write_text(json.dumps(report,indent=2)+'\n');return report
