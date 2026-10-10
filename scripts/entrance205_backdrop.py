"""Fixed matte-distance correction; preserve its angular artwork scale.

Camera translation matters as well as ray direction. Moving the distant art
twice as far away (scaling its height equally) clears the full swept frustum
without moving artwork with the camera or changing character/geography.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
 import bpy
 from entrance205_actor import save
 from entrance198_terrain import fingerprint
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'backdrop24'}:raise ValueError('Closed backdrop operation')
 src=base.BASE/'entrance205-scene22/scene.blend';out=base.BASE/'entrance205-backdrop24'
 record=json.loads((src.parent/'result.json').read_text())
 if out.exists() or base.digest(src)!=record['native_sha256']:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 for name in ('MF188_distant_art_arc','MF205_fixed_reverse_matte'):
  ob=bpy.data.objects[name]
  if ob.parent or max(abs(ob.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))>1e-6:raise ValueError('Backdrop not world-centred')
  ob.data=ob.data.copy()
  for v in ob.data.vertices:v.co.x*=2;v.co.y*=2;v.co.z=-20.931+2*(v.co.z+20.931)
  ob.data.update()
 save(scene,out,{'source_sha256':record['native_sha256'],'change':'Only two static matte meshes scaled2x about world floor; UVs, images, actor, terrain, camera and actions unchanged',
  'matte_radius_native':8000,'visual_gate':'NOT_RUN'})


if __name__=='__main__':main()
