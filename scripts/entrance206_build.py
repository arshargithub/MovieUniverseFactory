"""Closed206 integrated derivatives, protected205 turn and accepted masters."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance206_inspect import SOURCES
OPS={'composition05':'route','composition18':'route'}

def main():
 import bpy
 from entrance205_actor import save
 from entrance206_checkpoint import build,camera
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed206 build')
 op=job['operation'];kind=OPS[op];folder,sha=SOURCES[kind];src=base.BASE/folder/'scene.blend';out=base.BASE/('entrance206-'+op)
 if op=='composition18':src=base.BASE/'entrance206-composition05/scene.blend';sha='07c3f73df59bedf50a823b5683f866bf960b123ac1e2c0e7d42ea4e6b8694bf1'
 if out.exists() or base.digest(src)!=sha:raise ValueError('Source/output')
 r=json.loads((src.parent/'result.json').read_text())
 for row in r['caches']:
  if base.digest((src.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Cache source changed')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);base.check_protected()
 scene=bpy.context.scene;scene.frame_set(361);bpy.context.view_layer.update()
 result=dict(source_sha256=sha,checkpoint=build(scene) if op=='composition05' else r['checkpoint'],ots=camera(scene));scene.frame_set(361);save(scene,out,result)
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.use_persistent_data=False
 for f in (361,384,472,487):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 CONTROL',f,flush=True)
 base.check_protected()

if __name__=='__main__':main()
