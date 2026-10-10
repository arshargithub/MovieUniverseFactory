"""Narrow the approach cutback; restore the inner hill behind uphill coverage."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 from entrance206_geography import terrain
 from entrance206_visibility import inspect
 from entrance205_actor import save
 from wardrobe_motion178_controls import render_geometry_paused
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'route30'},{'operation':'route32'}):raise ValueError('Closed terrain correction')
 src=base.BASE/'entrance206-route28';out=base.BASE/('entrance206-'+job['operation']);sha='6fe890c421386159227e2d4987b45b8bd56ff5c4808d81878e6da76984f8df2e'
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 for row in json.loads((src/'result.json').read_text())['caches']:
  if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Source cache')
 original=base.BASE/'entrance206-composition18/scene.blend'
 if base.digest(original)!='4a2d096656b451a24eed4932ce67883d70feddb7da411f2fa91d452abe114ef3':raise ValueError('Original terrain source')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'entrance206_geography.py').write_bytes((ROOT/'scripts/entrance206_geography.py').read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;land=bpy.data.objects['AS_valley_landform']
 with render_geometry_paused():
  matrix=np.array(land.matrix_world);v=np.array([p.co[:] for p in land.data.vertices]);previous=v@matrix[:3,:3].T+matrix[:3,3]
  with bpy.data.libraries.load(str(original),link=False) as (available,loaded):loaded.objects=['AS_valley_landform']
  donor=loaded.objects[0]
  def chain(o):
   result=[]
   while o:
    if o.constraints or o.animation_data:raise ValueError('Unexpected animated terrain hierarchy')
    result.append(np.array(o.matrix_basis));result.append(np.array(o.matrix_parent_inverse));o=o.parent
   return np.array(result)
  a,b=chain(donor),chain(land)
  if len(donor.data.vertices)!=len(land.data.vertices) or a.shape!=b.shape or np.max(abs(a-b))>1e-5:raise ValueError('Terrain stored hierarchy/topology changed')
  land.data=donor.data.copy();bpy.data.objects.remove(donor,do_unlink=True);record=dict(source_sha256=sha,original_terrain_sha256=base.digest(original),terrain=terrain(scene,previous))
 scene.frame_set(361);save(scene,out,record)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;evidence=[]
 for f in (361,372,384,390,409,472,487,505,509,511,515,517,529,577,648):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 TERRAIN',f,flush=True)
  if f in (361,384):evidence.append(inspect(scene,f))
 (out/'composition-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
