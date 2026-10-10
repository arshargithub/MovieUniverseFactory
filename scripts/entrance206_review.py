"""Source-bound native motion/reopen review; no retiming or synthetic frames."""
import json,sys,time,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
ATTENTION=tuple(range(309,361,2));HAIR=tuple(range(505,602,2))
def overview_first(frames):
 overview=tuple(f for f in frames if (f-217)%12==0)
 return overview+tuple(f for f in frames if f not in overview)
OPS={
 'opening10':('opening20',overview_first(tuple(f for f in range(217,361) if f not in ATTENTION)),True),
 'route11':('route32',overview_first(tuple(f for f in range(361,649) if f not in HAIR)),True),
 'reopen12':('opening20',(217,321,327,339,360),False),
 'reopen13':('route32',(361,384,409,487,529,577,648),False),
 'hair14':('route28',HAIR,False),
 'hair31':('route32',HAIR,False),
 'attention16':('opening20',ATTENTION,False)}

def validate(job):
 if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed206 review')

def main():
 import bpy
 from entrance198_terrain import fingerprint
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job)
 op=job['operation'];folder,frames,full=OPS[op];src=base.BASE/('entrance206-'+folder);out=base.BASE/('entrance206-'+op);r=json.loads((src/'result.json').read_text())
 if out.exists() or base.digest(src/'scene.blend')!=r['native_sha256']:raise ValueError('Source/output')
 if full:
  gate=json.loads((src/'internal-review.json').read_text())
  if gate.get('status')!='PROCEED_TO_FULL_MOTION' or gate.get('source_sha256')!=r['native_sha256']:raise ValueError('Missing source-bound visual controls admission')
 for row in r['caches']:
  p=(src/row['path']).resolve()
  if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed/foreign cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 scene.frame_set(frames[0]);bpy.context.view_layer.update();structure=fingerprint(scene)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type=='MESH_CACHE':
    with Path(bpy.path.abspath(m.filepath)).open('rb') as stream:count,n=struct.unpack('>ii',stream.read(8))
    if n!=len(ob.data.vertices) or list(ob.modifiers).index(m)!=0:raise ValueError('Cache topology/order '+ob.name)
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
 rig=bpy.data.objects['MF_body156_fit_rig'];bones=('pelvis','chest','MF185_neck','MF185_head','hand.L','hand.R','foot.L','foot.R');rows=[]
 tree=None
 if folder.startswith('route'):
  from mathutils import Vector
  from mathutils.bvhtree import BVHTree
  land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles();tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],[tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True)
 for f in frames:
  start=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update();p=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(p)
  geography=None
  if tree is not None:
   eye=bpy.data.objects['MF_aimable_eye_Left'].matrix_world.translation;target=Vector((0,-900,-9.5));delta=target-eye;hit=tree.ray_cast(eye,delta.normalized(),delta.length)
   geography=dict(eye_world=list(eye),checkpoint_target=list(target),eye_to_checkpoint_land_occlusion=None if hit[0] is None else list(hit[0]))
   if 505<=f<=553 and hit[0] is not None:raise ValueError('Uphill checking glance blocked by terrain: '+repr(geography))
  if bpy.ops.render.render(write_still=True)!={'FINISHED'} or not p.is_file():raise ValueError('Native render incomplete')
  row=dict(index=f-217,source_frame=f,sha256=base.digest(p),seconds=time.monotonic()-start,camera=np.array(scene.camera.matrix_world).tolist(),lens=scene.camera.data.lens,pose={n:np.array(rig.matrix_world@rig.pose.bones[n].matrix).tolist() for n in bones});rows.append(row)
  row['geography']=geography
  (out/'progress.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,complete=False),indent=2)+'\n');print('206 FRAME',op,f,round(row['seconds'],2),flush=True)
 base.check_protected();(out/'result.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,fingerprint=structure,fps=24,resolution=[432,768],samples=8,visual_gate='NOT_RUN',limits='Silent native chronological preview; not release-resolution or final secondary-motion finishing'),indent=2)+'\n')

if __name__=='__main__':main()
