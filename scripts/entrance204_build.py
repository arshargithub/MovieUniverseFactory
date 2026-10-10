"""Closed native choreography controls; derivative only, no runtime code."""
import json,sys,os,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance204_inspect import SOURCES
from entrance204_story import smooth,glance,face_values

def facial(scene,kind):
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 body=bpy.data.objects['MF_studio_adult_body'];keys=body.data.shape_keys;controls={}
 for name in face_values(0):
  key=keys.key_blocks[name];ds=[d for d in keys.animation_data.drivers if d.data_path==key.path_from_id('value')]
  if len(ds)!=1 or len(ds[0].driver.variables)!=1:raise ValueError('Unexpected facial driver')
  target=ds[0].driver.variables[0].targets[0]
  if target.id_type!='KEY' or target.data_path!=target.id.key_blocks[name].path_from_id('value'):raise ValueError('Unexpected facial source')
  controls[name]=target.id.key_blocks[name]
 # Keep unedited shape deltas; isolate all controller actions before editing.
 for data in set(k.id_data for k in controls.values()):
  if data.animation_data and data.animation_data.action:
   data.animation_data.action.use_fake_user=True;data.animation_data.action=data.animation_data.action.copy()
 from worker import action_channels
 for k in controls.values():
  for fc in action_channels(k.id_data.animation_data.action):
   if fc.data_path==k.path_from_id('value'):fc.keyframe_points.clear()
 start,end=(289,337) if kind=='recognition' else (361,554)
 with render_geometry_paused():
  for f in range(start,end):
   values=face_values((f-start)/24,kind=='recognition')
   for n,v in values.items():controls[n].value=v;controls[n].keyframe_insert(data_path='value',frame=f)
  body.hide_viewport=False;errors=[]
  for f in (start,(start+end)//2,end-1):
   scene.frame_set(f);bpy.context.view_layer.update();expected=face_values((f-start)/24,kind=='recognition');errors.append(max(abs(keys.key_blocks[n].value-v) for n,v in expected.items()))
 if max(errors)>1e-5:raise ValueError('Facial transfer failed')
 return {'transfer_max_error':max(errors),'intent':'Recognition to composed determination, no fear or grin'}

def performance(scene,out):
 import bpy
 from mathutils import Quaternion
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance189_groom import read_mdd,write_mdd,attach_cache
 rig=bpy.data.objects['MF_body156_fit_rig'];names=('MF185_neck','MF185_head');before=[];after=[];bases=[]
 with render_geometry_paused():
  for f in range(361,554):
   scene.frame_set(f);bpy.context.view_layer.update();before.append([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in names]);bases.append([rig.pose.bones[n].rotation_quaternion.copy() for n in names])
  rig.animation_data.action.use_fake_user=True;rig.animation_data.action=rig.animation_data.action.copy()
  for i,f in enumerate(range(361,554)):
   scene.frame_set(f);g=glance(i/24)
   for j,(n,deg) in enumerate(zip(names,(14,49))):
    b=rig.pose.bones[n];b.rotation_mode='QUATERNION';b.rotation_quaternion=bases[i][j]@Quaternion((0,1,0),math.radians(deg)*g);b.keyframe_insert(data_path='rotation_quaternion',frame=f)
   bpy.context.view_layer.update();after.append([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in names])
 before=np.array(before);after=np.array(after);shawl=bpy.data.objects['MF185_moving_shawl'];m=next(m for m in shawl.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath));transforms=[]
 with render_geometry_paused():
  for f in range(361,554):
   scene.frame_set(f);bpy.context.view_layer.update();world=shawl.parent.matrix_world@shawl.matrix_parent_inverse@shawl.matrix_basis;transforms.append(np.array(world))
 def rows():
  for i,row in enumerate(a):
   world=transforms[i];inv=np.linalg.inv(world);p=np.array(row,float);q=p@world[:3,:3].T+world[:3,3];local=q@np.linalg.inv(before[i,1])[:3,:3].T+np.linalg.inv(before[i,1])[:3,3]
   w=smooth((local[:,1]+.9)/1.5);w[2501:]=0
   delta=after[i,1]@np.linalg.inv(before[i,1]);moved=q@delta[:3,:3].T+delta[:3,3];q+=(moved-q)*w[:,None]
   yield (q@inv[:3,:3].T+inv[:3,3]).astype(np.float32)
 path=out/'shawl.mdd';write_mdd(path,len(a),len(shawl.data.vertices),rows());attach_cache(shawl,path,361)
 np.savez_compressed(out/'head.npz',before=before,after=after)
 return {'head_yaw_degrees':63,'method':'Head/neck authored glance with supported headfall transport; new camera/contact visual gates required','forward_return_source_time':7.2}

def guards(scene):
 import bpy
 from mathutils import Vector
 floor=-20.931
 # Keep original barrier construction, relocate along the same main road.
 for ob in scene.objects:
  if ob.name.startswith('MF190_provisional_timber_barrier'):ob.location.y-=177
 def material(name,col):
  m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.9;return m
 cloth=material('204 anonymous distant coat',(.16,.14,.12));skin=material('204 distant skin',(.27,.15,.08));dark=material('204 distant boots and equipment',(.045,.032,.025))
 def ellipsoid(name,p,s,mat):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=p);ob=bpy.context.object;ob.name=name;ob.scale=s;ob.data.materials.append(mat);return ob
 def limb(name,a,b,r,mat):
  a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r*.8,depth=(b-a).length,location=(a+b)/2);ob=bpy.context.object;ob.name=name;ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();ob.data.materials.append(mat)
 for j,(x,y) in enumerate(((-15,-556),(14,-545))):
  def p(a,b,c):return (x+a,y+b,floor+c)
  prefix=f'MF204_guard_{j}_'
  ellipsoid(prefix+'coat',p(0,0,8.8),(2,1.3,3.8),cloth);ellipsoid(prefix+'head',p(0,0,13.5),(.95,.9,1.25),skin);ellipsoid(prefix+'cap',p(0,0,14.35),(1.08,.98,.55),cloth)
  for side in (-1,1):
   limb(prefix+'leg',p(side*.95,0,6),p(side*1.2,.25,1),.64,cloth);ellipsoid(prefix+'boot',p(side*1.2,-.3,.6),(.8,1.3,.6),dark)
   limb(prefix+'upper_arm',p(side*1.8,0,10.9),p(side*2.25,-.7,8.5),.62,cloth);limb(prefix+'forearm',p(side*2.25,-.7,8.5),p(side*1.8,-1.65,7.8),.48,cloth);ellipsoid(prefix+'hand',p(side*1.8,-1.65,7.8),(.46,.45,.6),skin)
  limb(prefix+'long_equipment',p(2,-1.7,3.5),p(2,-1.7,12),.17,dark)
 return {'count':2,'checkpoint':[0,-550,floor],'status':'Distant anonymous blocking figures, not approved uniform, affiliation or weapon design'}

def camera_pose(scene,kind,f):
 import bpy
 from mathutils import Vector
 cam=scene.camera;rig=bpy.data.objects['MF_body156_fit_rig'];head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation)
 if kind=='recognition':
  loc=head+np.array([-8.,-19.12,2.50]);target=head+np.array([0,-.4,-.4]);lens=62
 else:
  t=(f-361)/24
  if kind=='ots':loc=head+[-2.0,10.,1.];target=np.array([0,-550,-9.5]);lens=42
  elif kind=='wide':
   from entrance190_perspective import camera
   with np.load(base.BASE/'entrance190-rider09/route.npz') as z:r={k:z[k] for k in z.files}
   loc,target=camera(r,t);lens=35
  else:
   danger=np.array([0,-550,-8]);d=danger-head;d[2]=0;d/=np.linalg.norm(d);cross=np.array([-d[1],d[0],0])
   loc=head-d*60+cross*10+[0,0,15];target=head+d*35+[0,0,-5];lens=45
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 return {'camera':list(cam.location),'target':np.asarray(target).tolist(),'lens':lens}

def main():
 import bpy
 sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'recognition02'},{'operation':'route03'},{'operation':'recognition04'}):raise ValueError('Fixed build operation')
 kind='recognition' if job['operation'].startswith('recognition') else 'route';source_kind='opening' if kind=='recognition' else 'route';folder,sha=SOURCES[source_kind];src=base.BASE/folder/'scene.blend';out=base.BASE/('entrance204-'+job['operation'])
 if out.exists() or base.digest(src)!=sha:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 scene.frame_set(289 if kind=='recognition' else 361);result={'source_sha256':sha,'face':facial(scene,kind)}
 if kind=='route':result.update(performance=performance(scene,out),guards=guards(scene))
 cam=scene.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36;cam.data.clip_end=12000;cam.data.clip_start=.1
 caches=[]
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type=='MESH_CACHE':
    p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
 scene.render.use_persistent_data=False;scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
 # Review cameras are deterministic named repository controls. Save native
 # before render-only evaluation flags; no embedded scripts needed to open.
 camera_pose(scene,'recognition' if kind=='recognition' else 'ots',289 if kind=='recognition' else 361)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
 print('204 SAVE CHECK',str(out),sorted(p.name for p in out.iterdir()),(out/'scene.blend').stat().st_size,flush=True)
 result.update(native_sha256=base.digest(out/'scene.blend'),caches=caches,visual_gate='NOT_RUN');(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 tests=[('recognition',f) for f in (289,300,312,325,336)] if kind=='recognition' else [('ots',361),('ots',395),('wide',433),('wide',469),('final',493),('final',511),('final',535),('final',552)]
 rows=[]
 for shot,f in tests:
  scene.frame_set(f);bpy.context.view_layer.update();row=camera_pose(scene,shot,f);p=out/f'{shot}-{f:04d}.png';scene.render.filepath=str(p)
  if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Incomplete image')
  rows.append({'shot':shot,'frame':f,**row,'sha256':base.digest(p)});(out/'review-frames.json').write_text(json.dumps(rows,indent=2)+'\n')
 base.check_protected()
 print('204 FINAL FILE CHECK',sorted(p.name for p in out.iterdir()),flush=True)
if __name__=='__main__':main()
