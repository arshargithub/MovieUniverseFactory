"""Correct only static distant guards; retain integrated motion and caches."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 from entrance206_integration import guard_bindings
 from entrance205_actor import save
 from wardrobe_motion178_controls import render_geometry_paused
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job not in ({'operation':'route24'},{'operation':'route26'}):raise ValueError('Closed guard repair')
 src=base.BASE/('entrance206-route22' if job['operation']=='route24' else 'entrance206-route24');out=base.BASE/('entrance206-'+job['operation']);sha='e10d68b59ccb516ff9a3133d4c3198f1d631d0c36d444d04d4c8e178ab93b04f' if job['operation']=='route24' else 'f599b68413b63b62c9cf27e1654abf0debbd06dde72491886aec9ff88254c7ae'
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 record=json.loads((src/'result.json').read_text())
 for row in record['caches']:
  if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Source cache')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'entrance206_integration.py').write_bytes((ROOT/'scripts/entrance206_integration.py').read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
 with render_geometry_paused():guards=guard_bindings(scene)
 from entrance206_checkpoint import camera
 record=dict(source_sha256=sha,change='Static guard placement and tighter OTS composition; actor motion and hair/cloth caches retained',guards=guards,camera=camera(scene));(out/'entrance206_checkpoint.py').write_bytes((ROOT/'scripts/entrance206_checkpoint.py').read_bytes());scene.frame_set(361);save(scene,out,record)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 for f in (361,372,384,390,409,472,487,529,577,648):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 GUARD REPAIR',f,flush=True)
 base.check_protected()

if __name__=='__main__':main()
