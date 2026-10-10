"""Closed camera-side control: no actor, terrain, or timing edits.

The former named right vector was actually rider-left. Test screen evidence
before rebuilding any geometry or making compensating grooming changes.
"""
import json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def candidate(t,head):
 from entrance205_motion import sample,smooth
 d=sample(t);p=d['position'];y=d['heading'];h=np.asarray(head)
 f=np.array([np.sin(y),-np.cos(y),0.]);r=np.array([np.cos(y),np.sin(y),0.])
 if t<4.6:
  return p+f*5.2+r*2.2+[0,0,2+5.2*d['grade']],p+[0,0,1.35],44.
 # Above and just behind, seeing the downhill checkpoint past the shoulder.
 # Continue the same take around the outside into the forward face hold.
 w=float(smooth((t-7.2)/1.7))
 loc=h+f*(-2.0*(1-w)+.45*w)+r*(-.65*(1-w)+2.5*w)+[0,0,1.25*(1-w)+.65*w]
 return loc,h+[0,0,-.08],32*(1-w)+46*w


def main():
 import bpy
 from mathutils import Vector
 from entrance205_scene import FLOOR
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'coverage26'}:raise ValueError('Closed coverage control')
 src=base.BASE/'entrance205-scene22/scene.blend';out=base.BASE/'entrance205-coverage26'
 record=json.loads((src.parent/'result.json').read_text())
 if out.exists() or base.digest(src)!=record['native_sha256']:raise ValueError('Source/output')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene
 cam=scene.camera;cam.animation_data_clear();cam.data.animation_data_clear()
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
 scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
 rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
 for f in (445,469,505,529,577,648):
  scene.frame_set(f);bpy.context.view_layer.update();head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation)
  loc,target,lens=candidate((f-361)/24,(head-FLOOR)/8.3)
  cam.location=Vector(FLOOR+loc*8.3);cam.rotation_euler=(Vector(FLOOR+target*8.3)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
  scene.render.filepath=str(out/f'frame-{f-217:04d}.png');bpy.ops.render.render(write_still=True)
  rows.append({'frame':f,'location':list(cam.location),'target':list(FLOOR+target*8.3),'lens':lens})
  print('205 coverage',f,flush=True)
 (out/'result.json').write_text(json.dumps({'source_sha256':record['native_sha256'],'frames':rows,'visual_gate':'NOT_RUN'},indent=2)+'\n');base.check_protected()


if __name__=='__main__':main()
