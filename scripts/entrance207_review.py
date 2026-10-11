"""Closed207 native review and independent replay; fixed footage clock."""
import json,sys,time,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OPFRAMES=tuple(range(313,345));ROFRAMES=tuple(range(577,615))
OPS={'opening03':('opening09',OPFRAMES,False),'route04':('route02',ROFRAMES,False),
 'opening05':('opening09',tuple(f for f in range(217,361) if f not in OPFRAMES),True),
 'route06':('route02',tuple(f for f in range(361,649) if f not in ROFRAMES),True),
 'reopen07':('opening09',(313,325,337,360),False),'reopen08':('route02',(361,384,409,487,589,607,648),False)}
def validate(job):
 if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed207 review')
def main():
 import bpy
 from entrance198_terrain import fingerprint
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job);op=job['operation'];folder,frames,full=OPS[op];src=base.BASE/('entrance207-'+folder);out=base.BASE/('entrance207-'+op);r=json.loads((src/'result.json').read_text())
 if out.exists() or base.digest(src/'scene.blend')!=r['native_sha256']:raise ValueError('Source/output')
 if full:
  g=json.loads((src/'internal-review.json').read_text())
  if g.get('status')!='PROCEED_TO_FULL_MOTION' or g.get('source_sha256')!=r['native_sha256']:raise ValueError('Missing visual admission')
 for row in r['caches']:
  p=(src/row['path']).resolve()
  if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed/foreign cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type=='MESH_CACHE':
    with Path(bpy.path.abspath(m.filepath)).open('rb') as stream:nf,nv=struct.unpack('>ii',stream.read(8))
    if nv!=len(ob.data.vertices) or list(ob.modifiers).index(m)!=0:raise ValueError('Cache topology/order '+ob.name)
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
 rig=bpy.data.objects['MF_body156_fit_rig'];names=('pelvis','chest','MF185_neck','MF185_head','hand.L','hand.R','foot.L','foot.R');rows=[]
 for f in frames:
  start=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update();p=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(p)
  if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
  rows.append(dict(index=f-217,source_frame=f,sha256=base.digest(p),seconds=time.monotonic()-start,camera=np.array(scene.camera.matrix_world).tolist(),lens=scene.camera.data.lens,pose={n:np.array(rig.matrix_world@rig.pose.bones[n].matrix).tolist() for n in names}))
  (out/'progress.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,complete=False),indent=2)+'\n');print('207 FRAME',op,f,round(rows[-1]['seconds'],2),flush=True)
 base.check_protected();(out/'result.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,fingerprint=fingerprint(scene),fps=24,resolution=[432,768],visual_gate='NOT_RUN'),indent=2)+'\n')
if __name__=='__main__':main()
