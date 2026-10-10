"""Pinned existing horse rest geometry for anonymous distant mounted guards."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 from wardrobe_riding_fit import HORSE,HORSE_SHA
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'guard04'}:raise ValueError('Closed mounted guard source export')
 out=base.BASE/'entrance206-guard04'
 if out.exists() or base.digest(HORSE)!=HORSE_SHA:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(HORSE),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;scene.frame_set(0)
 rig=bpy.data.objects['horse.rig'];rig.data.pose_position='REST';bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get();arrays={};rows=[]
 for name in ('horse','saddle','saddle.pad','bridle','bridle.body','Full Bushy Flowing Horse Tail'):
  ob=bpy.data.objects.get(name)
  if ob is None:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
  try:
   a=np.array([ev.matrix_world@v.co for v in me.vertices]);tri=np.array([t.vertices[:] for t in me.loop_triangles]);idx=len(rows)
   arrays[f'v{idx}']=a;arrays[f'f{idx}']=tri
   rows.append(dict(name=name,bounds=[a.min(0).tolist(),a.max(0).tolist()],vertices=len(a),triangles=len(tri)))
  finally:ev.to_mesh_clear()
 np.savez_compressed(out/'horse.npz',**arrays)
 (out/'result.json').write_text(json.dumps(dict(source_sha256=HORSE_SHA,geometry_sha256=base.digest(out/'horse.npz'),objects=rows,visual_gate='NOT_RUN'),indent=2)+'\n')

if __name__=='__main__':main()
