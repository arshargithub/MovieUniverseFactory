"""Closed read-only comparison of distant guard source transforms and bounds."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'guard23'},{'operation':'guard25'}):raise ValueError('Closed guard diagnostic')
 src=base.BASE/('entrance206-route22' if job['operation']=='guard23' else 'entrance206-route24');record=json.loads((src/'result.json').read_text());out=base.BASE/('entrance206-'+job['operation'])
 if out.exists() or base.digest(src/'scene.blend')!=record['native_sha256']:raise ValueError('Source/output')
 out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);bpy.context.scene.frame_set(361)
 def describe(o):
  v=np.array([p.co[:] for p in o.data.vertices]);m=np.array(o.matrix_world);w=v@m[:3,:3].T+m[:3,3]
  return dict(name=o.name,basis=np.array(o.matrix_basis).tolist(),world=m.tolist(),bounds=[w.min(0).tolist(),w.max(0).tolist()],local_bounds=[v.min(0).tolist(),v.max(0).tolist()],parent=o.parent.name if o.parent else None,hide_render=o.hide_render,hide_viewport=o.hide_viewport)
 names=('MF206_guard0_horse','MF206_guard0_coat','MF206_guard0_head','MF206_guard1_horse','MF206_guard1_head');rows={n:dict(current=describe(bpy.data.objects[n])) for n in names}
 if job['operation']=='guard25':
  from bpy_extras.object_utils import world_to_camera_view
  from mathutils import Vector
  scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
  for n in names:
   o=bpy.data.objects[n];bounds=np.array(rows[n]['current']['bounds']);target=Vector(bounds.mean(0));direction=target-scene.camera.matrix_world.translation
   hit=scene.ray_cast(dg,scene.camera.matrix_world.translation,direction.normalized(),distance=direction.length+1)
   rows[n]['projection']=list(world_to_camera_view(scene,scene.camera,target));rows[n]['first_hit']=hit[4].name if hit[0] else None;rows[n]['hit_location']=list(hit[1]) if hit[0] else None
  (out/'result.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({n:{k:v for k,v in r.items() if k!='current'} for n,r in rows.items()},indent=2),flush=True);return
 source=base.BASE/'entrance206-composition05/scene.blend'
 if base.digest(source)!='07c3f73df59bedf50a823b5683f866bf960b123ac1e2c0e7d42ea4e6b8694bf1':raise ValueError('Donor source')
 with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.objects=list(names)
 for n,o in zip(names,loaded.objects):rows[n]['unlinked_donor']=describe(o)
 (out/'result.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)

if __name__=='__main__':main()
