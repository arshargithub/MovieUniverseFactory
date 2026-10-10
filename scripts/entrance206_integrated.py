"""Closed performance/hair controls. Technical success is not visual admission."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OPS={
 'opening06':('opening','entrance205-opening45','f63e6fb06268f32ecfb691b836b9fed4b21b00dd9e49f90893531da54cb8446a'),
 'opening09':('opening','entrance205-opening45','f63e6fb06268f32ecfb691b836b9fed4b21b00dd9e49f90893531da54cb8446a'),
 'opening15':('opening','entrance205-opening45','f63e6fb06268f32ecfb691b836b9fed4b21b00dd9e49f90893531da54cb8446a'),
 'opening17':('opening','entrance205-opening45','f63e6fb06268f32ecfb691b836b9fed4b21b00dd9e49f90893531da54cb8446a'),
 'route07':('route','entrance206-geography19','0e2b4752779873de15befd1012f88fb8b1ff83a0e64140c5d3d4775f8b8fff49'),
 'route21':('route','entrance206-geography19','0e2b4752779873de15befd1012f88fb8b1ff83a0e64140c5d3d4775f8b8fff49'),
 'route22':('route','entrance206-geography19','0e2b4752779873de15befd1012f88fb8b1ff83a0e64140c5d3d4775f8b8fff49')}

def validate(job):
 if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed206 integrated operation')

def main():
 import bpy
 from entrance205_actor import save
 from entrance206_performance import apply,earlier_face_camera
 from entrance206_hair import install
 from entrance206_checkpoint import camera
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job)
 op=job['operation'];kind,folder,sha=OPS[op];src=base.BASE/folder/'scene.blend';out=base.BASE/('entrance206-'+op)
 if out.exists() or base.digest(src)!=sha:raise ValueError('Source/output')
 r=json.loads((src.parent/'result.json').read_text())
 for row in r['caches']:
  if base.digest((src.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Changed cache')
 out.mkdir();bindings={}
 for p in sorted((ROOT/'scripts').glob('entrance206_*.py')):(out/p.name).write_bytes(p.read_bytes());bindings[p.name]=base.digest(p)
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene
 integration={}
 if kind=='route':
  from entrance206_integration import guard_bindings,matte
  from wardrobe_motion178_controls import render_geometry_paused
  with render_geometry_paused():integration=dict(guards=guard_bindings(scene),matte=matte(scene))
 result=dict(source_sha256=sha,handler_sources=bindings,performance=apply(scene,out,kind));print('206 PERFORMANCE BUILT',op,flush=True)
 result['integration']=integration
 if op in ('opening09','opening15','opening17'):result['camera']=earlier_face_camera(scene)
 result['hair']=install(scene,out,kind);print('206 HAIR BUILT',op,flush=True)
 if kind=='route':result['ots']=camera(scene)
 scene.frame_set(217 if kind=='opening' else 361);save(scene,out,result)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 frames=(311,321,327,339,350,360) if kind=='opening' else (361,372,384,390,409,472,487,529,577,648)
 evidence=[]
 for f in frames:
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 CONTROL',op,f,flush=True)
  if kind=='route' and f in (361,384,472,487):
   from entrance206_visibility import inspect
   evidence.append(inspect(scene,f))
 (out/'composition-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 base.check_protected()

if __name__=='__main__':main()
