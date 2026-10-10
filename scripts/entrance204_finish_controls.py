"""Fixed shot-domain corrections; retains accepted character and prior trials."""
import json,sys,os,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance204_build import camera_pose,facial
from entrance204_inspect import SOURCES
def main():
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance204_contact import apply
 from entrance204_story import smooth,glance
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'route05'},{'operation':'recognition04'},{'operation':'opening06'}):raise ValueError('Fixed stage')
 op=job['operation'];kind='route' if op=='route05' else 'recognition' if op=='recognition04' else 'opening';folder='entrance204-route03' if kind=='route' else SOURCES['opening'][0]
 src=base.BASE/folder/'scene.blend';record=json.loads((src.parent/'result.json').read_text());sha=record['native_sha256'];out=base.BASE/('entrance204-'+op)
 if out.exists() or base.digest(src)!=sha:raise ValueError('Source/output')
 for row in record['caches']:
  p=(src.parent/row['path']).resolve()
  if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected();result={'source_sha256':sha}
 scene.frame_set(361 if kind=='route' else 289);bpy.context.view_layer.update()
 if kind=='recognition':result['face']=facial(scene,kind)
 if kind=='route':
  art=bpy.data.objects['MF188_distant_art_arc'];art.rotation_euler.z=math.radians(-140)
  land=bpy.data.objects['AS_valley_landform'];land.data=land.data.copy();q=np.array([v.co[:] for v in land.data.vertices]);world=np.array(land.matrix_world);p=q@world[:3,:3].T+world[:3,3]
  mask=(1-smooth((abs(p[:,0])-30)/60))*smooth((-p[:,1]-390)/70)*(1-smooth((-p[:,1]-650)/100));p[:,2]=-20.931+(p[:,2]+20.931)*(1-.65*mask)
  inv=np.linalg.inv(world);q=p@inv[:3,:3].T+inv[:3,3];land.data.vertices.foreach_set('co',q.astype(np.float32).ravel());land.data.update()
  result['environment']={'matte_rotation_degrees':-140,'terrain_change':'Soften main-road shoulders near checkpoint only, outside traversed branch; road bed unchanged','affected_vertices':int((mask>0).sum())}
 # Separate editable eye aim from facial muscle controls. Source eye geometry
 # and attachment are unchanged; modest shared gaze accompanies the head.
 if kind!='opening':
  frames=range(361,554) if kind=='route' else range(289,337)
  with render_geometry_paused():
   for side in ('Left','Right'):
    eye=bpy.data.objects['MF_aimable_eye_'+side];original=float(eye.rotation_euler.z)
    if eye.animation_data and eye.animation_data.action:eye.animation_data.action.use_fake_user=True;eye.animation_data.action=eye.animation_data.action.copy()
    for f in frames:
     t=(f-(361 if kind=='route' else 289))/24;g=glance(t)*12 if kind=='route' else 3*float(smooth(t/.25))
     eye.rotation_euler.z=original+math.radians(g);eye.keyframe_insert(data_path='rotation_euler',index=2,frame=f)
 result['mane_contact']=apply(scene,out,361 if kind=='route' else 217,193 if kind=='route' else 144)
 if kind!='opening':scene.camera.animation_data_clear();scene.camera.data.animation_data_clear()
 caches=[]
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type=='MESH_CACHE':
    p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
 scene.render.use_persistent_data=False;scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
 scene.frame_set(361 if kind=='route' else 289 if kind=='recognition' else 217)
 if kind!='opening':camera_pose(scene,'ots' if kind=='route' else 'recognition',scene.frame_current)
 bpy.context.preferences.filepaths.save_version=0
 for relative in (False,True):
  if relative:bpy.ops.file.make_paths_relative()
  if bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)!={'FINISHED'}:raise ValueError('Save did not finish')
  if not (out/'scene.blend').is_file():raise ValueError('Save missing')
 result.update(native_sha256=base.digest(out/'scene.blend'),caches=caches,visual_gate='NOT_RUN');(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('204 SEALED CONTROL',out.name,result['native_sha256'],flush=True)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 tests=[('ots',361),('ots',395),('final',493),('final',511),('final',535),('final',552)] if kind=='route' else [('recognition',f) for f in (289,300,312,336)] if kind=='recognition' else [('opening',f) for f in (325,350,360)]
 rows=[]
 for shot,f in tests:
  scene.frame_set(f);bpy.context.view_layer.update()
  if kind!='opening':camera_pose(scene,shot,f)
  path=out/f'{shot}-{f:04d}.png';scene.render.filepath=str(path)
  if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Incomplete frame')
  rows.append({'shot':shot,'frame':f,'sha256':base.digest(path)});(out/'review-frames.json').write_text(json.dumps(rows,indent=2)+'\n')
 base.check_protected()
if __name__=='__main__':main()
