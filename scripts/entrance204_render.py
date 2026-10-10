"""Complete native story proof from pinned derivatives and one edit clock.

No generated code, synthetic interpolation, new render assets or paid calls.
All-frame visual admission is separate; process success never grants it.
"""
import json,sys,time,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance204_story import shot_frame
SOURCES={'opening':'opening06','recognition':'recognition04','route':'route05'}
OPS={'opening08':('opening',tuple(range(0,144,2))),'recognition09':('recognition',tuple(range(144,192,2))),'route10':('route',tuple(range(192,432,2))),
     'opening14':('opening',tuple(range(1,144,2))),'recognition15':('recognition',tuple(range(145,192,2))),'route16':('route',tuple(range(193,432,2))),
     'openverify11':('opening',(0,78,133,143)),'recognitionverify12':('recognition',(144,167,191)),'routeverify13':('route',(192,239,240,304,360,394,413,431))}
def main():
 import bpy
 from entrance204_build import camera_pose
 from entrance189_groom import read_mdd
 from entrance198_terrain import fingerprint
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Fixed render operation')
 op=job['operation'];kind,indices=OPS[op];src=base.BASE/('entrance204-'+SOURCES[kind])/'scene.blend';out=base.BASE/('entrance204-'+op)
 r=json.loads((src.parent/'result.json').read_text());gate=json.loads((src.parent/'internal-review.json').read_text())
 if out.exists() or base.digest(src)!=r['native_sha256'] or gate.get('status')!='PROCEED_TO_FULL_MOTION' or gate.get('source_sha256')!=r['native_sha256']:raise ValueError('Source/output/admission mismatch')
 for row in r['caches']:
  p=(src.parent/row['path']).resolve()
  if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 scene.frame_set(217 if kind=='opening' else 289 if kind=='recognition' else 361);bpy.context.view_layer.update();struct=fingerprint(scene)
 # Source/native remains fully editable; only evaluation previews are disabled.
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type=='MESH_CACHE':
    a=read_mdd(bpy.path.abspath(m.filepath))
    if a.shape[1]!=len(ob.data.vertices) or list(ob.modifiers).index(m)!=0:raise ValueError('Cache topology/order')
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=False
 rows=[];rig=bpy.data.objects['MF_body156_fit_rig'];bones=('pelvis','chest','MF185_neck','MF185_head','hand.L','hand.R','foot.L','foot.R')
 for index in indices:
  started=time.monotonic();_,shot,f=shot_frame(index);whole=math.floor(f);scene.frame_set(whole,subframe=f-whole);bpy.context.view_layer.update()
  camera=None if kind=='opening' else camera_pose(scene,shot,f)
  path=out/f'frame-{index:04d}.png';scene.render.filepath=str(path)
  if bpy.ops.render.render(write_still=True)!={'FINISHED'} or not path.is_file():raise ValueError('Incomplete native frame')
  rows.append({'frame':index,'source_frame':f,'shot':shot,'sha256':base.digest(path),'seconds':time.monotonic()-started,'camera':camera,
    'pose':{n:np.array(rig.matrix_world@rig.pose.bones[n].matrix).tolist() for n in bones}})
  (out/'progress.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'complete':False,'frames':rows},indent=2)+'\n')
  print('204 FRAME',op,index,'seconds',round(rows[-1]['seconds'],2),flush=True)
 base.check_protected();(out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,'fingerprint':struct,'cache_hashes':[x['sha256'] for x in r['caches']],
  'fps':24,'resolution':[288,512],'samples':8,'persistent_data':False,'kind':kind,'visual_gate':'NOT_RUN','limits':'Complete choreography preview, not final render or motion-dependent finishing; fixed one-clock retiming evaluated natively'},indent=2)+'\n')
if __name__=='__main__':main()
