"""Reviewed207 integrated derivative, fixed source/output and operation enums."""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance207_inspect import SOURCES
from entrance207_motion import flexion,expression,mane_step,tail_response
from entrance189_groom import read_mdd,write_mdd,attach_cache
OPS={'opening01':'opening','opening09':'opening','route02':'route'}
def validate(job):
 if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed207 construction')
def world(ob):
 return np.array(ob.parent.matrix_world@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_world)

def performance(scene,out,kind):
 import bpy
 from mathutils import Quaternion
 from wardrobe_motion178_controls import render_geometry_paused
 from worker import action_channels
 from entrance205_motion import smooth
 data=np.load(base.BASE/'entrance207-inspect01'/(kind+'.npz'));frames=data['frames'];names=list(data['names']);rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body'];shawl=bpy.data.objects['MF185_moving_shawl']
 chest=np.array([__import__('mathutils').Matrix(m.tolist()).to_euler('XYZ').x for m in data['bases'][:,names.index('chest')]])
 offsets=flexion(chest);rig.animation_data.action.use_fake_user=True;rig.animation_data.action=rig.animation_data.action.copy()
 # Broaden the cervical articulation across the neck, retaining all rest
 # coordinates and total influence. No face or clavicle sculpting.
 groupnames=('chest','MF185_neck','MF185_head');groups=[body.vertex_groups[n] for n in groupnames];changed=0
 for v,weights in zip(body.data.vertices,data['weights']):
  x,y,z=v.co
  if not (-1.85<z<-.85 and abs(x)<1.05):continue
  mask=float(smooth((z+1.85)/.18)*smooth((-.85-z)/.16)*smooth((1.05-abs(x))/.3));t=float(smooth((z+1.85)/1.0));desired=np.array([(1-t)**2,2*t*(1-t),t*t])*sum(weights)
  w=weights*(1-mask)+desired*mask
  for g,value in zip(groups,w):g.add([v.index],float(value),'REPLACE')
  changed+=int(mask>0)
 keys=body.data.shape_keys;controls={}
 for n in expression(217):
  ds=[d for d in keys.animation_data.drivers if d.data_path==keys.key_blocks[n].path_from_id('value')]
  if len(ds)!=1:raise ValueError('Facial driver mismatch')
  t=ds[0].driver.variables[0].targets[0];controls[n]=t.id.key_blocks[n]
 for k in set(k.id_data for k in controls.values()):k.animation_data.action.use_fake_user=True;k.animation_data.action=k.animation_data.action.copy()
 after=[];transforms=[];errors=[]
 with render_geometry_paused():
  for i,f in enumerate(frames):
   scene.frame_set(int(f))
   for j,n in enumerate(('MF185_neck','MF185_head')):
    b=rig.pose.bones[n];q=__import__('mathutils').Matrix(data['bases'][i,names.index(n)].tolist()).to_quaternion();b.rotation_mode='QUATERNION'
    b.rotation_quaternion=q@Quaternion((1,0,0),float(offsets[i,j]));b.keyframe_insert('rotation_quaternion',frame=int(f))
   for n,v in expression(int(f)).items():controls[n].value=v;controls[n].keyframe_insert('value',frame=int(f))
   bpy.context.view_layer.update();after.append(np.array(rig.matrix_world@rig.pose.bones['MF185_head'].matrix));transforms.append(world(shawl))
   errors.append(max(float(abs(np.array(rig.matrix_world@rig.pose.bones[n].matrix)-data['matrices'][i,names.index(n)]).max()) for n in ('pelvis','chest','hand.L','hand.R','foot.L','foot.R')))
 if max(errors)>2e-5:raise ValueError('Protected contacts changed')
 for fc in action_channels(rig.animation_data.action):
  if 'MF185_neck' in fc.data_path or 'MF185_head' in fc.data_path:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 m=next(m for m in shawl.modifiers if m.type=='MESH_CACHE');cache=read_mdd(bpy.path.abspath(m.filepath));start=int(m.frame_start);before=data['matrices'][:,names.index('MF185_head')]
 def rows():
  for i,f in enumerate(frames):
   M=transforms[i];p=np.array(cache[int(f)-start],float);q=p@M[:3,:3].T+M[:3,3];inv=np.linalg.inv(before[i]);local=q@inv[:3,:3].T+inv[:3,3]
   weight=smooth((local[:,1]+1.2)/1.8);weight[2501:]=0;D=after[i]@inv;q+=(q@D[:3,:3].T+D[:3,3]-q)*weight[:,None];I=np.linalg.inv(M)
   yield (q@I[:3,:3].T+I[:3,3]).astype(np.float32)
 p=out/'headfall.mdd';write_mdd(p,len(frames),len(shawl.data.vertices),rows());attach_cache(shawl,p,int(frames[0]))
 np.savez_compressed(out/'performance.npz',frames=frames,offsets=offsets,head_before=before,head_after=after,contact_errors=errors)
 return dict(contact_matrix_max_error=max(errors),neck_addition_deg_range=np.rad2deg([offsets[:,0].min(),offsets[:,0].max()]).tolist(),redistributed_neck_vertices=changed,rest_coordinates_changed=False,headfall='Coherent bounded head support transport; exposed hair inherited local dynamics, renewed visual clearance required')

def groom(scene,out,kind):
 import bpy
 from wardrobe_motion178_controls import render_geometry_paused
 frames=list(range(217,361)) if kind=='opening' else list(range(361,649));records={}
 for label,name in [('mane','MF188_flowing_mane'),('tail','MF185_gait_Full Bushy Flowing Horse Tail')]:
  ob=bpy.data.objects[name];m=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath));start=int(m.frame_start);matrices=[];hands=[]
  with render_geometry_paused():
   for f in frames:
    scene.frame_set(f);bpy.context.view_layer.update();M=world(ob);matrices.append(M);inv=np.linalg.inv(M);rig=bpy.data.objects['MF_body156_fit_rig'];row=[]
    for s in ('L','R'):
     H=np.array(rig.matrix_world@rig.pose.bones['hand.'+s].matrix);p=H[:3,3]+H[:3,1]*.45;row.append(inv[:3,:3]@p+inv[:3,3])
    hands.append(row)
  matrices=np.array(matrices);hands=np.array(hands)
  if label=='mane':
   centers=np.array([np.asarray(a[f-start]).reshape(6282,12,3,3).mean(2) for f in frames],float);roots=centers[:,:,0]
   wr=np.einsum('fij,fgj->fgi',matrices[:,:3,:3],roots)+matrices[:,:3,3][:,None,:];acc=np.gradient(np.gradient(wr,axis=0)*24,axis=0)*24
   acc=np.array([np.linalg.solve(M[:3,:3],v.T).T for M,v in zip(matrices,acc)]);acc=np.clip(acc,-120,120);phase=centers[0,:,0,1]*1.1+centers[0,:,0,2]*.7+.15*np.sin(np.arange(6282)*2.399963)
   state=[np.zeros_like(centers[0]),np.zeros_like(centers[0])];metric=[]
   def rows():
    for i,f in enumerate(frames):
     rest=centers[i];d,v=mane_step(rest,*state,acc[i],phase,(f-217)/24)
     # Coherent guide attenuation near actual moving hand proxies. This
     # preserves the original clearance rather than pointwise hair chatter.
     alpha=np.ones(6282)
     for h in hands[i]:
      proposed=rest+d;dist=np.sum(((proposed-h)/np.array([.75,1.0,.85]))**2,axis=2);old=np.sum(((rest-h)/np.array([.75,1.0,.85]))**2,axis=2)
      risky=np.any((dist<1)&(dist<old-.02),axis=1);alpha[risky]=0
     d*=alpha[:,None,None];v*=alpha[:,None,None];state[:]=[d,v]
     p=np.array(a[f-start],float).reshape(6282,12,3,3);p+=d[:,:,None,:]
     metric.append([float(abs(d[:,:2]).max()),float(np.max(np.linalg.norm(d,axis=2))),int((alpha==0).sum())]);yield p.reshape(-1,3).astype(np.float32)
   p=out/'mane.mdd';write_mdd(p,len(frames),a.shape[1],rows());attach_cache(ob,p,frames[0]);records[label]=dict(root_error=max(x[0] for x in metric),max_displacement=max(x[1] for x in metric),method='Root pinned damped guide response, length projection, one-way hand-proximity attenuation; coefficients authored, not calibrated')
   np.savez_compressed(out/'mane-metrics.npz',frames=frames,metrics=metric)
  else:
   from entrance193_motion import frame_basis
   rest=np.array(a[0],float);root_ids=rest[:,1]<6.35;roots=np.array([np.asarray(a[f-start])[root_ids].mean(0) for f in frames]);centers=[roots[0]]
   for y in np.linspace(6.7,15.2,17):centers.append(np.median(rest[np.argsort(abs(rest[:,1]-y))[:700]],axis=0))
   centers=np.array(centers);u=np.interp(rest[:,1],centers[:,1],np.arange(len(centers)));lo=np.minimum(u.astype(int),len(centers)-2);w=u-lo;ref=(1-w[:,None])*centers[lo]+w[:,None]*centers[lo+1]
   axes=frame_basis(centers);B=(1-w[:,None,None])*axes[lo]+w[:,None,None]*axes[lo+1];offset=np.einsum('ni,nij->nj',rest-ref,B);chain=tail_response(centers,roots,matrices)
   def rows():
    for i,f in enumerate(frames):
     axes=frame_basis(chain[i]);B=(1-w[:,None,None])*axes[lo]+w[:,None,None]*axes[lo+1];p=(1-w[:,None])*chain[i,lo]+w[:,None]*chain[i,lo+1]+np.einsum('ni,nji->nj',offset,B)
     from entrance205_motion import smooth
     blend=smooth((rest[:,1]-6.35)/.85);original=np.array(a[f-start],float);p=original*(1-blend[:,None])+p*blend[:,None];p[root_ids]=original[root_ids]
     yield p.astype(np.float32)
   p=out/'tail.mdd';write_mdd(p,len(frames),a.shape[1],rows());attach_cache(ob,p,frames[0]);np.savez_compressed(out/'tail-chain.npz',rest=centers,frames=chain,roots=roots)
   records[label]=dict(root_error=0,method='Weighted trailing rest curve and damped root-driven length-constrained centerline, preserved bushy cross sections',max_segment_error=float(np.max(abs(np.linalg.norm(np.diff(chain,axis=1),axis=2)-np.linalg.norm(np.diff(centers,axis=0),axis=1)))))
  print('207 groom complete',kind,label,flush=True)
 return records

def guards(scene):
 import bpy
 from mathutils import Vector,Matrix
 from mathutils.bvhtree import BVHTree
 land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles();tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],[tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True);rows=[]
 for j,(oldxy,newxy) in enumerate((((-38,-790),(-32,-510)),((38,-770),(34,-555)))):
  oldhit=tree.ray_cast(Vector((*oldxy,1000)),Vector((0,0,-1)),2000)[0];hit=tree.ray_cast(Vector((*newxy,1000)),Vector((0,0,-1)),2000)[0]
  if oldhit is None or hit is None:raise ValueError('Guard not terrain grounded')
  T=Matrix.Translation(hit)@Matrix.Scale(1.10,4)@Matrix.Translation(-oldhit);count=0
  for ob in list(scene.objects):
   if ob.type!='MESH' or not ob.name.startswith(f'MF206_guard{j}_'):continue
   if ob.parent or np.max(abs(np.array(ob.matrix_world)-np.eye(4)))>1e-5:raise ValueError('Guard stored basis unexpected')
   ob.data=ob.data.copy();ob.data.transform(T);ob.data.update();count+=1
  rows.append(dict(guard=j,position=list(hit),scale=1.10,objects=count))
 return rows

def main():
 import bpy
 from entrance205_actor import save
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job);op=job['operation'];kind=OPS[op];folder,sha=SOURCES[kind];src=base.BASE/folder;out=base.BASE/('entrance207-'+op)
 if out.exists() or base.digest(src/'scene.blend')!=sha:raise ValueError('Source/output')
 r=json.loads((src/'result.json').read_text())
 for row in r['caches']:
  if base.digest((src/row['path']).resolve())!=row['sha256']:raise ValueError('Source cache changed')
 out.mkdir();bindings={}
 for p in sorted((ROOT/'scripts').glob('entrance207_*.py')):(out/p.name).write_bytes(p.read_bytes());bindings[p.name]=base.digest(p)
 bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
 result=dict(source_sha256=sha,handlers=bindings,performance=performance(scene,out,kind));print('207 performance complete',kind,flush=True)
 result['groom']=groom(scene,out,kind)
 if kind=='route':result['guards']=guards(scene)
 scene.frame_set(217 if kind=='opening' else 361);save(scene,out,result)
 for ob in scene.objects:
  for m in ob.modifiers:
   if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
 for f in ((217,277,313,319,325,331,337,343,350,360) if kind=='opening' else (361,372,384,390,409,427,472,487,577,583,589,595,601,607,648)):
  scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True);print('207 CONTROL',f,flush=True)
 base.check_protected()
if __name__=='__main__':main()
