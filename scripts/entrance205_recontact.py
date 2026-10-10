"""Reuse unchanged fitted lower assembly; renew changed horse/rein interfaces.

Requires full-array rider pose, saddle and stirrup parity, not a visual guess.
Old lower collision envelopes are NOT requalified for the changed horse neck.
"""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
 import bpy
 from entrance189_groom import attach_cache,read_mdd
 from entrance205_actor import save
 from wardrobe185_grip import rein_channel
 from wardrobe185_mount_fit import rein_points
 from wardrobe_motion178_controls import render_geometry_paused
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
 if job!={'operation':'fitted36'}:raise ValueError('Closed reuse operation')
 src=base.BASE/'entrance205-fitted20/scene.blend';out=base.BASE/'entrance205-fitted36';r=json.loads((src.parent/'result.json').read_text())
 if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
 parity={}
 with np.load(base.BASE/'entrance205-rider19/rig.npz') as a,np.load(base.BASE/'entrance205-rider35/rig.npz') as b:
  for k in ('source_frames','before','after','world'):
   e=float(abs(a[k]-b[k]).max());parity[k]=e
   if e>1e-5:raise ValueError('Body dependency changed: '+k)
 old=base.BASE/'entrance205-export03';new=base.BASE/'entrance205-export29';nr=json.loads((new/'result.json').read_text())
 for n in ('saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap'):
  p=new/(n+'.mdd')
  if base.digest(p)!=nr['caches'][n]:raise ValueError('Export changed')
  e=float(abs(read_mdd(old/(n+'.mdd'))-read_mdd(p)).max());parity[n]=e
  if e>1e-4:raise ValueError('Lower tack dependency changed')
 with np.load(new/'contacts.npz') as z:bits=z['bit_points'].copy()
 if base.digest(new/'contacts.npz')!=nr['contacts_sha256']:raise ValueError('Contacts changed')
 out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene
 for n in ('horse','bridle','bridle.body','bit','Torus.002'):
  p=new/(n+'.mdd')
  if base.digest(p)!=nr['caches'][n]:raise ValueError('Changed horse export')
  attach_cache(bpy.data.objects['MF185_gait_'+n],p,361)
 rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
 for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].data.animation_data_clear()
 with render_geometry_paused():
  for i in range(289):
   f=361+i;scene.frame_set(f);bpy.context.view_layer.update()
   for j,side in enumerate(('L','R')):
    channel=rein_channel(rig,side);bit=bits[i,j]+[0,0,-1.05];points=rein_points(bit,channel);ob=bpy.data.objects['MF185_rein_'+side]
    if len(points)!=len(ob.data.splines[0].points):raise ValueError('Rein topology')
    for point,co in zip(ob.data.splines[0].points,points):point.co=(*co,1);point.keyframe_insert(data_path='co',frame=f)
   if i%24==0:print('205 recontact',f,flush=True)
 scene.frame_set(361);save(scene,out,{'source_sha256':r['native_sha256'],'new_horse_source':nr['source_sha256'],'reuse_parity':parity,'reuse':'Unchanged fitted pants, stirrups and leather caches retained after all-frame dependency parity; reins rebuilt to new bit','limits':'Old lower collision envelope not qualified for changed horse neck; stage-two simulation requires renewal'})


if __name__=='__main__':main()
