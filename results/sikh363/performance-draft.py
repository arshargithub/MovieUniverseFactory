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
 # One edit map for every action consumer, including shape keys, FX, reins and
 # camera. Untouched source file is the retained original; no stale old cache.
 clocks=[]
 for action in bpy.data.actions:
  count=0
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:
       x=float(key.co.x);lh=float(key.handle_left.x);rh=float(key.handle_right.x);key.co.x=edit_time(x);key.handle_left.x=edit_time(lh);key.handle_right.x=edit_time(rh);count+=1
      fc.update()
  if count:clocks.append(dict(action=action.name,keys=count,users=action.users))
 for marker in scene.timeline_markers:marker.frame=round(edit_time(marker.frame))
 scene.frame_end=round(edit_time(scene.frame_end));frames=list(range(252,419));capture={}
 # Visible rigid head attachments must follow the actual new head owner too.
 scene.frame_set(283);bpy.context.view_layer.update();headworld=rig.matrix_world@rig.pose.bones['head'].head;accessories=[]
 for ob in rig.children_recursive:
  if ob.type not in {'MESH','CURVE'} or ob.hide_render or any(m.type=='ARMATURE' for m in ob.modifiers):continue
  if ob.parent_type=='BONE':continue
  corners=[ob.matrix_world@Vector(p) for p in ob.bound_box];center=sum(corners,Vector())/8
  if (center-headworld).length<.48:accessories.append(ob)
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();capture[f]=dict(world=rig.matrix_world.copy(),bones={p.name:p.matrix.copy() for p in rig.pose.bones},shaft=shaft.matrix_world.copy(),camera=scene.camera.matrix_world.copy(),root=root.matrix_world.copy(),accessories={ob.name:ob.matrix_world.copy() for ob in accessories})
 armnames=[n for n in bones.keys() if n.endswith('.L') and n.startswith(('upperarm','lowerarm','wrist','finger'))]
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
 for f,row in capture.items():
  old=row['bones'];v=solutions[f];desired={n:m.copy() for n,m in old.items()};s=old['upperarm01.L'].translation;e0=old['lowerarm01.L'].translation;w0=old['wrist.L'].translation
  for names,a,b,na,nb in [(('upperarm01.L','upperarm02.L'),s,e0,s,v['elbow']),(('lowerarm01.L','lowerarm02.L'),e0,w0,v['elbow'],v['wrist'])]:
   rot=(b-a).normalized().rotation_difference((nb-na).normalized()).to_matrix().to_4x4();delta=Matrix.Translation(na)@rot@Matrix.Translation(-a)
   for n in names:desired[n]=delta@old[n]
  for n in armnames:
   if n.startswith(('wrist','finger')):desired[n]=Matrix.Translation(v['localdelta'])@old[n]
  # The exchange camera is a proxy for the Sikh eyeline. Distribute a bounded
  # turn over neck and head; preserve eyes, beard and crown as one character.
  hd=old['head']@head.matrix_local.inverted();forward=row['world'].to_3x3()@(hd.to_3x3()@Vector((0,-1,0)));want=row['camera'].translation-row['world']@old['head'].translation;forward.z=0;want.z=0;forward.normalize();want.normalize();yaw=math.atan2(forward.cross(want).z,forward.dot(want));yaw=max(-math.radians(30),min(math.radians(30),yaw))*ease((f-277)/9)
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
 report=dict(clock=dict(old=OLD,new=NEW,airborne_frames=[43,21],shot=[276,333],handles=[252,357],downstream_shift=-23,consumers=clocks),hoist=dict(height=chosen,failed_preflights=failed,start=302,held_from=313,outboard=.11),gaze=gaze,accessories=[o.name for o in accessories],frames=records,scope='Actual phased timing/hoist/head ownership candidate. Flag still old rigid wave until separate final-clock CLOTH bake. Actual framing, anatomy, face/pole clearance and Director full-speed judgment mandatory.')
 (out/'performance363.json').write_text(json.dumps(report,indent=2)+'\n');return report
