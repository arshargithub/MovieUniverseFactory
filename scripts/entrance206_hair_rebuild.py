"""Isolated contact-energy correction, preserving reviewed camera/performance."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
 import bpy
 from entrance206_hair import install
 from entrance205_actor import save
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'opening20'}:raise ValueError('Closed206 hair correction')
 src=base.BASE/'entrance206-opening17';sha='27e4af54c4e097c520fa0878e9993889bcd3de5478a086830d1f70cef8f1444c';out=base.BASE/'entrance206-opening20'
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 r=json.loads((src/'result.json').read_text())
 for row in r['caches']:
  if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Source cache changed')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());(out/'entrance206_hair.py').write_bytes((ROOT/'scripts/entrance206_hair.py').read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected();removed=[]
 for ob in scene.objects:
  if ob.type=='CURVES' and ob.name.startswith('MF_natural147_hair_long hair'):
   mods=[m for m in ob.modifiers if m.name=='206 root-pinned guide simulation']
   if len(mods)!=1:raise ValueError('Expected one old guide cache interface')
   ob.modifiers.remove(mods[0]);removed.append(ob.name)
 if len(removed)!=2:raise ValueError('Unexpected hair source')
 for name in ('MF206_main_guide_dynamics','MF206_strands_guide_dynamics'):bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 record=dict(source_sha256=sha,change='Only hair contact energy handling; camera, facial performance, rig and headfall unchanged',hair=install(scene,out,'opening'))
 scene.frame_set(217);save(scene,out,record)
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 for f in (311,321,327,339,350,360):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('206 HAIR CONTACT',f,flush=True)
 base.check_protected()

if __name__=='__main__':main()
