"""Fixed local donor import/studio proof. No paths, code or downloads in recipes."""
import hashlib,json,struct
from pathlib import Path
SOURCE='.runtime/assets/warhorse383/Warhorse_Lite.glb'
SHA='745ccfa9dc9fa390496e7147d258fc390a791c914653779194a26da7e1386fcc'
VIEWS={'warhorse_front383','warhorse_side383','warhorse_reverse383'}

def validate(edit):
 if not isinstance(edit,dict) or set(edit)!={'kind','target'} or edit['kind'] not in {'warhorse_import383','warhorse_retarget383'} or edit['target']!='warhorse383':raise ValueError('WARHORSE383_FIELDS')

def validate_glb(path):
 d=Path(path).read_bytes()
 if hashlib.sha256(d).hexdigest()!=SHA:raise ValueError('WARHORSE383_HASH')
 magic,version,total=struct.unpack_from('<4sII',d)
 if magic!=b'glTF' or version!=2 or total!=len(d):raise ValueError('WARHORSE383_CONTAINER')
 n,kind=struct.unpack_from('<II',d,12)
 if kind!=0x4e4f534a:raise ValueError('WARHORSE383_JSON')
 v=json.loads(d[20:20+n])
 if v.get('extensionsRequired') or any('uri'in x for k in ['images','buffers'] for x in v.get(k,[])):raise ValueError('WARHORSE383_EXTERNAL_DEPENDENCY')
 if len(v['skins'])!=1 or len(v['meshes'])!=1 or {x['name'] for x in v['animations']}!={'rear','canter_loop','walk_loop','idle_loop'}:raise ValueError('WARHORSE383_CONTENT')
 return v

def curves(action):
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:yield from bag.fcurves

def inventory(bpy):
 rig=bpy.data.objects.get('MF383 Warhorse rig');mesh=bpy.data.objects.get('MF383 Warhorse surface')
 if rig is None or mesh is None:return None
 ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 try:
  coords=[[round(float(x),6) for x in v.co] for v in me.vertices]
  bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
 finally:ev.to_mesh_clear()
 return dict(vertices=len(mesh.data.vertices),polygons=len(mesh.data.polygons),bounds_local=bounds,
  posed_geometry_sha256=hashlib.sha256(json.dumps(coords).encode()).hexdigest(),
  bones={p.name:[[round(float(x),6) for x in row] for row in p.matrix] for p in rig.pose.bones},
  action=rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
  material_names=[m.name for m in mesh.data.materials],scope='Actual imported donor pose, not artistic qualification')

def camera(bpy,view):
 from mathutils import Vector
 if view not in VIEWS:raise ValueError('WARHORSE383_VIEW')
 s=bpy.context.scene;frame=s.frame_current;s.frame_set(283);bpy.context.view_layer.update()
 rig=bpy.data.objects['MF383 Warhorse rig'];head=rig.matrix_world@rig.pose.bones['head'].head;hip=rig.matrix_world@rig.pose.bones['pelvis'].head
 forward=head-hip;forward.z=0;forward.normalize();side=Vector((-forward.y,forward.x,0));target=Vector((0,0,1.55))
 s.frame_set(frame);bpy.context.view_layer.update();data=bpy.data.cameras.new('MF383 evidence camera');data.type='ORTHO';data.ortho_scale=4.4
 ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob)
 offset=forward*5 if view=='warhorse_front383' else side*5 if view=='warhorse_side383' else forward*4-side*4
 ob.location=target+offset+Vector((0,0,.30));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();return ob

def run(bpy,out,edit):
 from mathutils import Vector
 if edit['kind']=='warhorse_retarget383':return retarget(bpy,out,edit)
 validate(edit);root=Path(__file__).resolve().parents[4];path=root/SOURCE
 if path.is_symlink():raise ValueError('WARHORSE383_SYMLINK')
 doc=validate_glb(path)
 if bpy.data.objects.get('MF383 Warhorse rig'):raise ValueError('WARHORSE383_ALREADY_IMPORTED')
 before={x.as_pointer() for x in bpy.data.objects}
 s=bpy.data.scenes.new('MF383 Warhorse studio');bpy.context.window.scene=s
 bpy.ops.import_scene.gltf(filepath=str(path),import_pack_images=True)
 imported=[x for x in bpy.data.objects if x.as_pointer() not in before]
 rigs=[x for x in imported if x.type=='ARMATURE'];meshes=[x for x in imported if x.type=='MESH' and any(m.type=='ARMATURE' and m.object in rigs for m in x.modifiers)]
 if len(rigs)!=1 or len(meshes)!=1:raise ValueError('WARHORSE383_IMPORT_OWNERS:'+str([(x.name,x.type) for x in imported]))
 rig=rigs[0];mesh=meshes[0];rig.name='MF383 Warhorse rig';mesh.name='MF383 Warhorse surface';mesh['mf_supporting_appearance']=True
 if set(rig.pose.bones.keys())!={x['name'] for x in doc['nodes'][:39]}:raise ValueError('WARHORSE383_BONES')
 actions=[a for a in bpy.data.actions if a.name=='rear' or a.name.startswith(('rear_','rear|'))]
 if len(actions)!=1:raise ValueError('WARHORSE383_REAR_ACTION:'+str([a.name for a in bpy.data.actions if 'rear'in a.name.lower()]))
 action=actions[0];rig.animation_data_create()
 for track in rig.animation_data.nla_tracks:track.mute=True
 rig.animation_data.action=action
 if action.slots:rig.animation_data.action_slot=action.slots[0]
 old=list(action.frame_range);shift=283-old[0]
 for fc in curves(action):
  for k in fc.keyframe_points:k.co.x+=shift;k.handle_left.x+=shift;k.handle_right.x+=shift
 s.render.fps=24;s.frame_start=283;s.frame_end=343
 for ob in imported:ob.hide_render=ob.type=='MESH' and ob!=mesh
 world=bpy.data.worlds.new('MF383 neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.24,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;s.world=world
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.012));ground=bpy.context.object;ground.name='MF383 studio ground'
 mat=bpy.data.materials.new('MF383 matte ground');mat.diffuse_color=(.19,.21,.24,1);ground.data.materials.append(mat)
 for label,loc,energy,size in [('key',(4,-4,6),1100,5),('fill',(-4,1,4),800,4),('rim',(1,4,5),1000,3)]:
  data=bpy.data.lights.new('MF383 '+label,'AREA');data.energy=energy;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,1.4))-ob.location).to_track_quat('-Z','Y').to_euler()
 s.camera=camera(bpy,'warhorse_reverse383');s.view_settings.view_transform='AgX';samples={}
 for f in [283,295,307,315,323,331,343,367]:s.frame_set(f);bpy.context.view_layer.update();samples[str(f)]=inventory(bpy)
 s.frame_set(283);bpy.context.view_layer.update()
 report=dict(source=SOURCE,source_sha256=SHA,original_action_range=old,shifted_action_range=list(action.frame_range),sampled=samples,rig=rig.name,mesh=mesh.name,scope='Own rear stress test; accepted choreography not retargeted or replaced. Medieval tack present. No production pass.')
 (out/'warhorse383.json').write_text(json.dumps(report,indent=2)+'\n');return report

def retarget(bpy,out,edit):
 """Baseline-calibrated global rotational transfer, not an accepted IK/contact solve."""
 from mathutils import Matrix,Vector
 validate(edit);target=bpy.data.objects.get('MF383 Warhorse rig');source=bpy.data.objects.get('horse.rig');studio=bpy.context.scene
 if target is None or source is None or studio.name!='MF383 Warhorse studio':raise ValueError('WARHORSE383_RETARGET_OWNERS')
 owners=[s for s in bpy.data.scenes if s!=studio and source.name in s.objects]
 if len(owners)!=1:raise ValueError('WARHORSE383_SOURCE_SCENE')
 owner=owners[0];mapping=dict(pelvis='DEF-spine.001',spine_01='DEF-spine.002',spine_02='DEF-spine.004',spine_03='DEF-spine.006',neck_01='DEF-neck.001',neck_02='DEF-neck.002',neck_03='DEF-neck.004',head='DEF-head',jaw='DEF-jaw')
 for suffix,old in [('L','L'),('R','R')]:
  for name,src in [('scapula','DEF-shoulder'),('upperarm','DEF-upper_arm'),('forearm','DEF-forearm'),('hand','DEF-forefoot'),('finger','DEF-f_toe'),('thigh','DEF-thigh'),('calf','DEF-lower_leg'),('foot','DEF-hind_foot'),('toe','DEF-r_toe'),('ear','DEF-ear')]:mapping[name+'_'+suffix]=src+'.'+old
 for i in range(1,6):mapping[f'tail_{i:02d}']=f'DEF-tail.{i:03d}'
 if not set(mapping)<=set(target.pose.bones.keys()) or not set(mapping.values())<=set(source.pose.bones.keys()):raise ValueError('WARHORSE383_RETARGET_MAP')
 studio.frame_set(283);bpy.context.view_layer.update();base={p.name:p.matrix.copy() for p in target.pose.bones};tw=target.matrix_world.copy()
 bpy.context.window.scene=owner;owner.frame_set(283);bpy.context.view_layer.update();sw=source.matrix_world.copy();sb={n:(source.matrix_world@source.pose.bones[n].matrix).copy() for n in set(mapping.values())};align=tw.to_quaternion()@sw.to_quaternion().inverted()
 scale=base['pelvis'].translation.z/(source.pose.bones['DEF-spine.001'].head.z or 1)
 frames={}
 for f in range(276,368):
  owner.frame_set(f);bpy.context.view_layer.update();frames[f]={n:(source.matrix_world@source.pose.bones[n].matrix).copy() for n in sb}
 bpy.context.window.scene=studio;target.animation_data.action=bpy.data.actions.new('MF383 accepted-motion transfer diagnostic')
 for track in target.animation_data.nla_tracks:track.mute=True
 ordered=sorted(target.pose.bones,key=lambda p:len(p.parent_recursive));audit={}
 for f,values in frames.items():
  studio.frame_set(f);bpy.context.view_layer.update();desired={}
  for pb in ordered:
   parent=pb.parent;carry=desired[parent.name]@base[parent.name].inverted()@base[pb.name] if parent else base[pb.name].copy()
   if pb.name in mapping:
    sn=mapping[pb.name];dq=values[sn].to_quaternion()@sb[sn].to_quaternion().inverted();dq=align@dq@align.inverted();dq=tw.to_quaternion().inverted()@dq@tw.to_quaternion();q=dq@base[pb.name].to_quaternion();q.normalize();m=q.to_matrix().to_4x4();m.translation=carry.translation
    if pb.name=='pelvis':m.translation=base['pelvis'].translation+tw.inverted().to_3x3()@(align@(values[sn].translation-sb[sn].translation))*scale
   else:m=carry
   desired[pb.name]=m;pb.rotation_mode='QUATERNION'
   kwargs=dict(parent_matrix=desired[parent.name],parent_matrix_local=parent.bone.matrix_local) if parent else {}
   pb.matrix_basis=pb.bone.convert_local_to_pose(m,pb.bone.matrix_local,invert=True,**kwargs)
   pb.keyframe_insert('rotation_quaternion',frame=f);pb.keyframe_insert('location',frame=f);pb.keyframe_insert('scale',frame=f)
  bpy.context.view_layer.update()
  audit[str(f)]={p.name:float((p.head-desired[p.name].translation).length) for p in target.pose.bones if p.name in mapping}
 studio.frame_start=276;studio.frame_end=367;studio.frame_set(283);bpy.context.view_layer.update()
 samples={}
 for f in [283,310,320,333,339,346,367]:studio.frame_set(f);bpy.context.view_layer.update();samples[str(f)]=inventory(bpy)
 studio.frame_set(283);bpy.context.view_layer.update()
 report=dict(mapping=mapping,translation_scale=scale,maximum_assigned_head_error=max(v for x in audit.values() for v in x.values()),sampled=samples,scope='Accepted source global rotation changes transferred relative to baseline283; original source unchanged. Different limb lengths/contact may require IK and rider/tack refit. This does not qualify anatomy, foot planting or final motion.')
 (out/'warhorse383-retarget.json').write_text(json.dumps(report,indent=2)+'\n');return report
