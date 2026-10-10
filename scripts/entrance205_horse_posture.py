"""Climb-specific horse neck articulation, preserving solved hoof motion."""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def protected_files():
 from wardrobe_riding_fit import BODY,BODY_SHA,HORSE,HORSE_SHA
 from wardrobe_motion178 import BASE
 for p,h in ((BODY,BODY_SHA),(HORSE,HORSE_SHA),(BASE/'natural152-seal-16/natural-hair.blend','9a204ec2e3951274aeff52aeb554de6b8bc7fa169933e27bfea7073bb62f323f')):
  if base.digest(p)!=h:raise ValueError('Protected source changed')


def verify():
 import bpy
 from source_gallop_math import LEGS
 out=base.BASE/'entrance205-verify27'
 if out.exists():raise ValueError('Retain previous evidence')
 protected_files();samples={};sources={}
 for label in ('horse07','horse27'):
  p=base.BASE/('entrance205-'+label)/'horse-route.blend';r=json.loads((p.parent/'result.json').read_text())
  if base.digest(p)!=r['native_sha256']:raise ValueError('Native changed')
  sources[label]=r['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);scene=bpy.context.scene
  horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];groups={horse.vertex_groups[v[1]].index for v in LEGS.values()}
  ids=[v.index for v in horse.data.vertices if any(g.group in groups and g.weight>.5 for g in v.groups)];rows=[]
  for f in (0,72,108,144,216,288):
   scene.frame_set(f);bpy.context.view_layer.update();ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
   try:feet=np.array([ev.matrix_world@me.vertices[i].co for i in ids])
   finally:ev.to_mesh_clear()
   rows.append((feet,np.array(rig.matrix_world@rig.pose.bones['DEF-head'].head)))
  samples[label]=rows
 controls=[]
 for f,a,b in zip((0,72,108,144,216,288),samples['horse07'],samples['horse27']):
  e=float(abs(a[0]-b[0]).max());controls.append({'frame':f,'hoof_world_delta_m':e,'head_world_change_m':(b[1]-a[1]).tolist()})
  if e>1e-5:raise ValueError('Hoof action changed')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'result.json').write_text(json.dumps({'sources':sources,'controls':controls,'status':'FRESH_OPEN_HOOF_PRESERVATION_PASS','recovery':'horse27 saved successfully then used character-scene-only guard in horse-only file. This independent file guard and mesh check recover that technical result; original failed job retained. Visual NOT_RUN.'},indent=2)+'\n');protected_files()


def main():
 import bpy
 from mathutils import Matrix
 from worker import action_channels
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job=={'operation':'verify27'}:return verify()
 if job!={'operation':'horse27'}:raise ValueError('Closed horse posture')
 src=base.BASE/'entrance205-horse07/horse-route.blend';out=base.BASE/'entrance205-horse27';r=json.loads((src.parent/'result.json').read_text())
 if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 with np.load(src.parent/'route.npz') as z:data={k:z[k] for k in z.files}
 scene=bpy.context.scene;rig=bpy.data.objects['horse.rig'];horse=bpy.data.objects['horse'];controls=('neck','head');poses=[];original=[]
 def feet():
  ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
  try:
   p=np.array([v.co[:] for v in me.vertices]);return p[p[:,2]<.45]
  finally:ev.to_mesh_clear()
 # Capture old control transforms before introducing keys. No feedback from
 # interpolated new keys into the original source action.
 for f in range(289):
  scene.frame_set(f);bpy.context.view_layer.update();poses.append({n:rig.pose.bones[n].matrix.copy() for n in controls})
  if f in (0,72,108,144,216,288):original.append((f,feet()))
 rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='205 climb neck reach with solved hoof action retained'
 rows=[]
 for f in range(289):
  scene.frame_set(f);m=poses[f]['neck'];pivot=m.translation
  angle=.75*math.atan(float(data['grade'][f*8]));rot=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'X')@Matrix.Translation(-pivot)
  for n in controls:
   b=rig.pose.bones[n];b.matrix=rot@poses[f][n];bpy.context.view_layer.update()
   loc,q,scale=b.matrix_basis.decompose();b.rotation_mode='QUATERNION';b.location=loc;b.rotation_quaternion=q;b.scale=scale
   for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(prop,frame=f)
  if f%24==0:print('205 horse posture',f,flush=True)
 for fc in action_channels(rig.animation_data.action):
  if any(fc.data_path.startswith(rig.pose.bones[n].path_from_id()) for n in controls):
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 for f,prior in original:
  scene.frame_set(f);bpy.context.view_layer.update();now=feet()
  if now.shape!=prior.shape:raise ValueError('Lower mesh selection changed')
  e=float(np.max(abs(now-prior)));rows.append({'frame':f,'lower_mesh_max_delta_m':e})
  if e>1e-5:raise ValueError('Neck articulation changed solved lower mesh')
 np.savez_compressed(out/'route.npz',**data);scene.frame_set(0)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'horse-route.blend'),compress=True)
 (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_sha256':base.digest(out/'horse-route.blend'),'route_sha256':base.digest(out/'route.npz'),'max_neck_counterpitch_degrees':math.degrees(.75*math.atan(.48)),'lower_mesh_controls':rows,'visual_gate':'NOT_RUN'},indent=2)+'\n');protected_files()


if __name__=='__main__':main()
