"""Fixed local donor import/studio proof. No paths, code or downloads in recipes."""
import hashlib,json,struct
from pathlib import Path
SOURCE='.runtime/assets/warhorse383/Warhorse_Lite.glb'
SHA='745ccfa9dc9fa390496e7147d258fc390a791c914653779194a26da7e1386fcc'
VIEWS={'warhorse_front383','warhorse_side383','warhorse_reverse383'}

def validate(edit):
 if edit!={'kind':'warhorse_import383','target':'warhorse383'}:raise ValueError('WARHORSE383_FIELDS')

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
