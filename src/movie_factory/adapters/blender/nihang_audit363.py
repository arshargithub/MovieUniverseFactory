"""Fixed read-only horse-chest, hand and animation-consumer diagnosis."""
import json,hashlib
import numpy as np

def run(bpy,out):
 scene=bpy.context.scene;horse=bpy.data.objects['horse'];hr=bpy.data.objects['horse.rig'];rider=bpy.data.objects['MF coherent Nihang rig']
 base=np.array([v.co[:] for v in horse.data.vertices]);sections=[]
 for axis in range(3):
  lo,hi=base[:,axis].min(),base[:,axis].max()
  for center in np.linspace(lo,hi,17):
   mask=abs(base[:,axis]-center)<(hi-lo)/32
   if mask.any():sections.append(dict(axis=axis,center=float(center),count=int(mask.sum()),low=base[mask].min(0).tolist(),high=base[mask].max(0).tolist()))
 records=[]
 for f in [276,283,298,307,327,350,356]:
  scene.frame_set(f);bpy.context.view_layer.update();evaluated=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();co=np.array([v.co[:] for v in mesh.vertices]);evaluated.to_mesh_clear()
  records.append(dict(frame=f,horse_bounds=[co.min(0).tolist(),co.max(0).tolist()],horse_controls={n:dict(head=list(hr.pose.bones[n].head),tail=list(hr.pose.bones[n].tail),basis=[list(x) for x in hr.pose.bones[n].matrix_basis]) for n in ['chest','neck','head','hips'] if n in hr.pose.bones},hands={side:{n:dict(rest_head=list(b.head_local),rest_tail=list(b.tail_local),head=list(rider.pose.bones[n].head),tail=list(rider.pose.bones[n].tail),matrix=[list(x) for x in rider.pose.bones[n].matrix]) for n,b in rider.data.bones.items() if n.endswith('.'+side) and n.startswith(('finger','wrist','lowerarm01','upperarm01'))} for side in ['L','R']}))
 nearby=[]
 for ob in bpy.data.objects:
  if any(k in ob.name.lower() for k in ['spear','flag','rein','coherent','hind support','horse','headstall','saddle']):
   nearby.append(dict(name=ob.name,type=ob.type,parent=ob.parent.name if ob.parent else None,parent_bone=ob.parent_bone,location=list(ob.location),rotation_mode=ob.rotation_mode,scale=list(ob.scale),modifiers=[dict(name=m.name,type=m.type) for m in ob.modifiers],action=ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None,shape_keys=len(ob.data.shape_keys.key_blocks) if ob.type=='MESH' and ob.data.shape_keys else 0))
 actions=[]
 for action in bpy.data.actions:
  actions.append(dict(name=action.name,range=list(action.frame_range),users=action.users,slots=[s.identifier for s in action.slots]))
 report=dict(subframes=subframe_interfaces(bpy),stage_interfaces=stage_interfaces(bpy),hand_owner=hand_owner(bpy,rider),horse=dict(vertices=len(base),base_sha256=hashlib.sha256(base.astype('<f4').tobytes()).hexdigest(),bounds=[base.min(0).tolist(),base.max(0).tolist()],modifiers=[dict(name=m.name,type=m.type,preserve_volume=getattr(m,'use_deform_preserve_volume',None),object=getattr(getattr(m,'object',None),'name',None)) for m in horse.modifiers],shape_keys=[k.name for k in horse.data.shape_keys.key_blocks] if horse.data.shape_keys else [],groups=[g.name for g in horse.vertex_groups],sections=sections),samples=records,objects=nearby,actions=actions,scope='Read-only diagnosis, no anatomical or performance approval.')
 (out/'audit363.json').write_text(json.dumps(report,indent=2)+'\n');scene.frame_set(283);return report


def hand_owner(bpy,rig):
 from mathutils import Vector
 from collections import Counter
 body=bpy.data.objects['MF coherent Nihang body'];root=bpy.data.objects['mounted leader'];target=rig.matrix_world@rig.pose.bones['finger3-1.R'].head
 states=[(m,m.show_viewport) for m in body.modifiers]
 for m,_ in states:m.show_viewport=False
 bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mx=rig.matrix_world.inverted()@body.matrix_world
 if len(mesh.vertices)!=len(body.data.vertices):raise ValueError('HAND_OWNER_SOURCE_INDEX')
 shaped=[mx@v.co for v in mesh.vertices];ev.to_mesh_clear()
 for m,on in states:m.show_viewport=on
 bpy.context.view_layer.update();helpers={}
 for group in body.vertex_groups:
  if not group.name.startswith(('joint-r-finger','joint-r-hand')):continue
  ids=[v.index for v in body.data.vertices if any(g.group==group.index and g.weight>.5 for g in v.groups)]
  if ids:helpers[group.name]=list(sum((shaped[i] for i in ids),Vector())/len(ids))
 joints={}
 for n,b in rig.data.bones.items():
  if not n.endswith('.R') or not n.startswith(('finger','wrist','metacarpal')):continue
  closest=sorted([(float((Vector(p)-b.head_local).length),key,p) for key,p in helpers.items()])[:2]
  joints[n]=dict(rest_head=list(b.head_local),nearest_helpers=closest)
 close=[]
 for ob in root.children_recursive:
  if ob.type!='MESH' or ob.hide_render:continue
  corners=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=Vector(tuple(min(p[i] for p in corners) for i in range(3)));hi=Vector(tuple(max(p[i] for p in corners) for i in range(3)))
  distance=sum(max(lo[i]-target[i],target[i]-hi[i],0)**2 for i in range(3))**.5
  if distance>.15:continue
  close.append(dict(name=ob.name,parent=ob.parent.name if ob.parent else None,vertices=len(ob.data.vertices),distance=distance,modifiers=[dict(name=m.name,type=m.type,viewport=m.show_viewport,render=m.show_render,object=getattr(getattr(m,'object',None),'name',None)) for m in ob.modifiers]))
 groups=Counter();sample=[]
 for v in body.data.vertices:
  row=[(body.vertex_groups[g.group].name,g.weight) for g in v.groups]
  if any(n.endswith('.R') and n.startswith(('finger','wrist','metacarpal')) and w>.01 for n,w in row):
   for n,w in row:groups[n]+=w
   if len(sample)<30:sample.append(dict(index=v.index,rest=list(v.co),weights=row))
 return dict(morphed_helpers=helpers,rest_joint_comparison=joints,nearby_visible=close,hand_group_weight_totals=dict(groups),sample=sample,shape_keys=[dict(name=k.name,value=k.value) for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else [],bone_deform={n:dict(deform=b.use_deform,parent=b.parent.name if b.parent else None) for n,b in rig.data.bones.items() if n.endswith('.R') and n.startswith(('finger','wrist','metacarpal'))})

def stage_interfaces(bpy):
 from mathutils import Vector,Matrix,Quaternion
 from bpy_extras.object_utils import world_to_camera_view
 scene=bpy.context.scene;actor=bpy.data.objects['MF coherent Nihang rig'];horse=bpy.data.objects['horse.rig'];shaft=bpy.data.objects['LEADER spear world contact owner'];camera=scene.camera;records=[]
 for f in (283,300,306,310,314,317,322,327,333):
  scene.frame_set(f);bpy.context.view_layer.update();grip=actor.matrix_world@((actor.pose.bones['finger3-1.R'].head+actor.pose.bones['finger3-2.R'].head)*.5);head=horse.matrix_world@horse.pose.bones['DEF-head'].matrix@horse.data.bones['DEF-head'].matrix_local.inverted();anchors=json.loads(horse['tack358_anchors']);reins=[]
  for label,ob in zip(('R','L'),sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)):
   pts=[ob.matrix_world@Vector(p.co[:3]) for p in ob.data.splines[0].points];anchor=head@Vector(anchors[label]);reins.append(dict(name=ob.name,hidden=ob.hide_render,grip_error=(pts[-1]-grip).length,bit_center_error=(pts[0]-anchor).length,start=list(pts[0]),end=list(pts[-1]),grip=list(grip),anchor=list(anchor)))
  eyes=[actor.matrix_world@actor.pose.bones['eye.'+s].head for s in ('L','R')];face=(eyes[0]+eyes[1])*.5-Vector((0,0,.03));base=shaft.matrix_world@Vector((0,0,0));tip=shaft.matrix_world@Vector((0,0,3.91));original=camera.matrix_world.copy();center=bpy.data.objects['mounted leader'].matrix_world.translation+Vector((0,0,.5));angles=[]
  for angle in (-25,-15,-8,0,8,15,25):
   q=Quaternion((0,0,1),angle*3.141592653589793/180).to_matrix().to_4x4();camera.matrix_world=Matrix.Translation(center)@q@Matrix.Translation(-center)@original
   a,b,p=[world_to_camera_view(scene,camera,v) for v in (base,tip,face)];av=Vector((a.x*432,a.y*768));bv=Vector((b.x*432,b.y*768));pv=Vector((p.x*432,p.y*768));u=max(0,min(1,(pv-av).dot(bv-av)/(bv-av).length_squared));gap=(pv-av-(bv-av)*u).length;angles.append(dict(angle=angle,face_pole_pixels=gap,tip_ndc=list(b),face_ndc=list(p)))
  camera.matrix_world=original;records.append(dict(frame=f,reins=reins,cameras=angles))
 scene.frame_set(283);bpy.context.view_layer.update();return records

def subframe_interfaces(bpy):
 from mathutils import Vector
 scene=bpy.context.scene;rig=bpy.data.objects['MF coherent Nihang rig'];b=rig.pose.bones['finger3-1.R'];names=[b.name]+[p.name for p in b.parent_recursive];rows=[];action=rig.animation_data.action;curves=[]
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     if any(n in fc.data_path for n in names):curves.append(dict(path=fc.data_path,index=fc.array_index,modifiers=[dict(type=m.type,muted=m.mute) for m in fc.modifiers],samples=[(t,fc.evaluate(t)) for t in (340,340.25,340.5,340.75,341)],keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in fc.keyframe_points if 339<=k.co.x<=342]))
 for t in (313,313.5,314,314.5,315,340,340.25,340.5,340.75,341):
  scene.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update();grip=rig.matrix_world@((rig.pose.bones['finger3-1.R'].head+rig.pose.bones['finger3-2.R'].head)*.5);rows.append(dict(time=t,world=[list(r) for r in rig.matrix_world],grip=list(grip),bones={n:dict(mode=rig.pose.bones[n].rotation_mode,basis=[list(r) for r in rig.pose.bones[n].matrix_basis],matrix=[list(r) for r in rig.pose.bones[n].matrix],location=list(rig.pose.bones[n].location),quaternion=list(rig.pose.bones[n].rotation_quaternion),scale=list(rig.pose.bones[n].scale),constraints=[c.type for c in rig.pose.bones[n].constraints]) for n in names}))
 objects=[];ob=rig
 while ob:objects.append(ob);ob=ob.parent
 objectrows=[];objectcurves=[]
 for t in (340,340.25,340.5,340.75,341):
  scene.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update();objectrows.append(dict(time=t,objects={ob.name:dict(world=[list(r) for r in ob.matrix_world],basis=[list(r) for r in ob.matrix_basis],mode=ob.rotation_mode,location=list(ob.location),quaternion=list(ob.rotation_quaternion),euler=list(ob.rotation_euler),constraints=[c.type for c in ob.constraints]) for ob in objects}))
 for ob in objects:
  ad=ob.animation_data
  if not ad or not ad.action:continue
  for layer in ad.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:objectcurves.append(dict(owner=ob.name,path=fc.data_path,index=fc.array_index,modifiers=[m.type for m in fc.modifiers],samples=[(t,fc.evaluate(t)) for t in (340,340.25,340.5,340.75,341)],keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in fc.keyframe_points if 339<=k.co.x<=342]))
 scene.frame_set(283);bpy.context.view_layer.update();return dict(object_chain=objectrows,object_curves=objectcurves,action=action.name,chain=names,rows=rows,curves=curves,nla=[dict(name=t.name,strips=[dict(name=s.name,action=s.action.name if s.action else None,frame_start=s.frame_start,frame_end=s.frame_end,action_frame_start=s.action_frame_start,action_frame_end=s.action_frame_end) for s in t.strips]) for t in rig.animation_data.nla_tracks])
