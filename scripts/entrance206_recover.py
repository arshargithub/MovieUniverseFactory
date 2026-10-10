"""Recover a saved native after JSON float serialization failed; no rebake."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 from entrance205_actor import save
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'opening08'}:raise ValueError('Closed serialization recovery')
 src=base.BASE/'entrance206-opening06';sha='d0d6c451a37df17e7a26290c5a6f4ef03922c5628ba76b5585d740346dee408d';out=base.BASE/'entrance206-opening08'
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 p=np.load(src/'performance.npz');hair=[]
 for label in ('main','strands'):
  z=np.load(src/f'hair-{label}-metrics.npz');hair.append(dict(label=label,maximum_tip_displacement_native=float(z['metrics'][:,0].max()),maximum_edge_error_native=float(z['metrics'][:,1].max()),root_error=float(z['metrics'][:,2].max()),metrics_sha256=base.digest(src/f'hair-{label}-metrics.npz')))
 record=dict(source_sha256=sha,recovered_from='opening06 saved native; process failed only serializing np.float32 contact error; failure retained',performance=dict(protected_contact_error=float(p['protected_error'].max()),evidence_sha256=base.digest(src/'performance.npz')),hair=hair,original_handler_sources={x.name:base.digest(x) for x in src.glob('*.py')})
 scene.frame_set(217);save(scene,out,record)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 for f in (299,311,325,339,350,360):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 RECOVERED CONTROL',f,flush=True)
 base.check_protected()

if __name__=='__main__':main()
