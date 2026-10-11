"""Read-only, hash-bound207 motion inspection; closed operation only."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCES={'opening':('entrance206-opening20','f0f9b685bb522743aa417921b42e8461fde0347bdb297954d8556e2371f65c47'),
 'route':('entrance206-route32','0ed75ceed4473f64c0fdc5884646cb16b36ffd9bd52204426dd1dd2d11d3aef8')}
def validate(job):
 if job!={'operation':'inspect01'}:raise ValueError('Closed207 inspection')
def main():
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance189_groom import read_mdd
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job)
 out=base.BASE/'entrance207-inspect01'
 if out.exists():raise ValueError('Preserve evidence')
 out.mkdir();result={}
 for kind,(folder,sha) in SOURCES.items():
  src=base.BASE/folder/'scene.blend'
  if base.digest(src)!=sha:raise ValueError('Source changed')
  bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
  rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body'];names=['pelvis','spine','chest','MF185_neck','MF185_head','hand.L','hand.R','foot.L','foot.R']
  frames=list(range(217,361)) if kind=='opening' else list(range(361,649));matrices=[];bases=[];world=[];cameras=[]
  with render_geometry_paused():
   for f in frames:
    scene.frame_set(f);bpy.context.view_layer.update();matrices.append([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in names]);bases.append([np.array(rig.pose.bones[n].matrix_basis) for n in names]);world.append(np.array(rig.matrix_world));cameras.append(np.array(scene.camera.matrix_world))
  verts=np.array([v.co[:] for v in body.data.vertices]);weights=np.zeros((len(verts),3))
  for j,n in enumerate(('chest','MF185_neck','MF185_head')):
   g=body.vertex_groups.get(n)
   if g:
    for v in body.data.vertices:
     weights[v.index,j]=next((w.weight for w in v.groups if w.group==g.index),0)
  np.savez_compressed(out/(kind+'.npz'),frames=frames,names=names,matrices=matrices,bases=bases,world=world,cameras=cameras,body_vertices=verts,weights=weights,body_world=np.array(body.matrix_world))
  record={'source_sha256':sha,'bones':{n:dict(head=list(rig.data.bones[n].head_local),tail=list(rig.data.bones[n].tail_local),parent=rig.data.bones[n].parent.name if rig.data.bones[n].parent else None) for n in names},'modifiers':[(m.name,m.type,m.show_render) for m in body.modifiers],'grooms':{}}
  for n in ('MF188_flowing_mane','MF185_gait_Full Bushy Flowing Horse Tail'):
   ob=bpy.data.objects[n];m=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath));ids=[0,len(a)//2,len(a)-1]
   record['grooms'][n]=dict(shape=list(a.shape),start=m.frame_start,path=bpy.path.abspath(m.filepath),bounds=[[np.min(a[i],axis=0).tolist(),np.max(a[i],axis=0).tolist()] for i in ids],parent=ob.parent.name if ob.parent else None)
   np.savez_compressed(out/(kind+('-mane.npz' if 'mane' in n else '-tail.npz')),samples=np.array(a[ids]),indices=ids)
  result[kind]=record
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
