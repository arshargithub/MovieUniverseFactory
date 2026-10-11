"""Fixed207 distant-sentry staging control; actor/camera/cache state retained."""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
def validate(job):
 if job!={'operation':'threat10'}:raise ValueError('Closed207 sentry control')
def main():
 import bpy
 from mathutils import Matrix,Vector
 from mathutils.bvhtree import BVHTree
 from entrance205_actor import save
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 validate(job)
 src=base.BASE/'entrance207-route02';out=base.BASE/'entrance207-threat10';r=json.loads((src/'result.json').read_text())
 if out.exists() or base.digest(src/'scene.blend')!=r['native_sha256']:raise ValueError('Source/output')
 for row in r['caches']:
  if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Changed source cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles();tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],[tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True);records=[]
 for j,(oldxy,newxy,angle) in enumerate((((-32,-510),(-32,-335),-.35),((34,-555),(30,-400),.35))):
  def ground(xy):
   hit=tree.ray_cast(Vector((*xy,1000)),Vector((0,0,-1)),2000)[0]
   if hit is None:raise ValueError('Guard outside terrain')
   return hit
  old=ground(oldxy);new=ground(newxy);T=Matrix.Translation(new)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-old)
  for ob in scene.objects:
   if ob.type=='MESH' and ob.name.startswith(f'MF206_guard{j}_'):
    ob.data=ob.data.copy();ob.data.transform(T);ob.data.update()
  records.append(dict(guard=j,anchor=list(new),added_yaw_radians=angle,scale_change=1.,reason='More legible three-quarter mounted silhouettes forward of unchanged distant barrier'))
 scene.frame_set(361);save(scene,out,dict(source_sha256=r['native_sha256'],guards=records,change='Only static mounted sentries moved/rotated; source207 performance/grooms/cameras retained'))
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 for f in (361,372,384,390,409,427,472,487,577,583,589,595,601,607,648):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('207 THREAT',f,flush=True)
 base.check_protected()
if __name__=='__main__':main()
