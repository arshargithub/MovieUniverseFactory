"""Fit the complete OTS option corridor; retain all actor and guard work."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 from entrance206_checkpoint import camera
 from entrance205_actor import save
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'route27'},{'operation':'route28'}):raise ValueError('Closed composition fit')
 src=base.BASE/'entrance206-route26';out=base.BASE/('entrance206-'+job['operation']);sha='59644e0ea19237f53de6bec63cc1ae81a8748b34f36efa0a0e091617af78d80b'
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 for row in json.loads((src/'result.json').read_text())['caches']:
  if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Source cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'entrance206_checkpoint.py').write_bytes((ROOT/'scripts/entrance206_checkpoint.py').read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
 record=dict(source_sha256=sha,change='OTS actual landmark corridor fit only; frontal turn and all actor/cache work retained',camera=camera(scene));scene.frame_set(361);save(scene,out,record)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 for f in (361,372,384,390,409,472,487,529,577,648):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 COMPOSITION',f,flush=True)
 base.check_protected()

if __name__=='__main__':main()
