"""Shot-scoped attached pectoral reconstruction. Closed native handler, no code payload.

A sculpted sternal arch has a fixed medial attachment and rotating lateral limb
insertion. Interpolated rotations avoid the collapsing linear blend used by the
legacy skin. This is an authored form hypothesis, not a muscle simulation.
"""
import importlib.util,json
from pathlib import Path
import numpy as np


def mod(name):
 s=importlib.util.spec_from_file_location('forequarter381_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def validate(e):
 if isinstance(e,dict) and e.get('kind')=='mounted_forequarter381_donor_inspect':
  b=e.get('source')
  if set(e)!={'kind','target','source'} or e['target']!='horse' or not isinstance(b,dict) or set(b)!={'path','sha256'} or b['path']!='.runtime/assets/demonstrator-01/horse.blend' or not isinstance(b['sha256'],str) or len(b['sha256'])!=64:raise ValueError('FOREQUARTER381_DONOR_FIELDS')
  return e
 if e!={'kind':'mounted_forequarter381','target':'horse','profile':'attached_arch'}:raise ValueError('FOREQUARTER381_FIELDS')
 return e


def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)


def sculpt(raw):
 """Positive rest form: preserve upper pectoral curvature, arch lower sternum.

 The lowest medial pectoral tissue is lifted toward the sternum while lateral
 roots retain their descent into the upper legs. No whole-region planar fairing.
 """
 p=np.asarray(raw,dtype=float);q=p.copy();low=smooth((1.48-p[:,2])/.32);front=smooth((-.40-p[:,1])/.25)
 medial=np.exp(-(p[:,0]/.155)**2);q[:,2]+=.145*low*medial*front
 q[:,1]+=.045*low*front;q[:,0]*=1-.07*low*front
 return q


def rotate_partial(p,R,alpha):
 """Shortest rotation interpolation, preserving radius about the anchor."""
 U,_,V=np.linalg.svd(R);rot=U@V
 if np.linalg.det(rot)<0:raise ValueError('FOREQUARTER381_REFLECTION')
 angle=np.arccos(np.clip((np.trace(rot)-1)/2,-1,1))
 if angle<1e-8:return p.copy()
 if np.pi-angle<1e-5:raise ValueError('FOREQUARTER381_AMBIGUOUS_ROTATION')
 axis=np.array([rot[2,1]-rot[1,2],rot[0,2]-rot[2,0],rot[1,0]-rot[0,1]])/(2*np.sin(angle))
 a=np.asarray(alpha)*angle;c=np.cos(a)[:,None];s=np.sin(a)[:,None]
 return p*c+np.cross(axis,p)*s+axis[None,:]*(p@axis)[:,None]*(1-c)


def attached(source,rest,template,weights,names,transforms,heads):
 p=np.asarray(source,dtype=float);d=np.zeros_like(p);names=list(names);mask=np.zeros(len(p))
 for side in ('L','R'):
  name='DEF-breast.'+side;w=weights[:,names.index(name)];mask+=w
  body=transforms[name];arm=transforms['DEF-upper_arm.'+side];relative=np.linalg.inv(body)@arm;pivot=heads[side]
  # Medial sternum and high neck attachment remain thorax-owned. The lower,
  # lateral insertion progressively participates in proximal foreleg rotation.
  alpha=smooth((np.abs(rest[:,0])-.035)/.205)*smooth((1.57-rest[:,2])/.31)
  local=rotate_partial(template-pivot,relative[:3,:3],alpha)+pivot
  moved=pivot@relative[:3,:3].T+relative[:3,3];local+=alpha[:,None]*(moved-pivot)
  new=local@body[:3,:3].T+body[:3,3];old=rest@body[:3,:3].T+body[:3,3]
  d+=w[:,None]*(new-old)
 if np.linalg.norm(d,axis=1).max()>.45 or not np.isfinite(d).all():raise ValueError('FOREQUARTER381_BOUND')
 return p+d,mask


def run(bpy,out,e):
 validate(e)
 if e['kind']=='mounted_forequarter381_donor_inspect':return donor_inspect(bpy,out,e)
 horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];names=[g.name for g in horse.vertex_groups];w=np.zeros((len(horse.data.vertices),len(names)))
 for v in horse.data.vertices:
  for g in v.groups:w[v.index,g.group]=g.weight
 raw=np.array([v.co[:] for v in horse.data.vertices]);template=sculpt(raw);base=mod('nihang_cache376')
 def target(p,rest,edges,breast,t):
  B=np.array(horse.matrix_world.inverted()@rig.matrix_world);Bi=np.linalg.inv(B);Ts={};heads={}
  for side in ('L','R'):
   arm='DEF-upper_arm.'+side
   for name in ('DEF-breast.'+side,arm):
    pb=rig.pose.bones[name];Ts[name]=B@np.array(pb.matrix@pb.bone.matrix_local.inverted())@Bi
   head=np.array(rig.data.bones[arm].head_local);heads[side]=head@B[:3,:3].T+B[:3,3]
  result,mask=attached(p,rest,template,w,names,Ts,heads);return result-p,mask
 result=base.run(bpy,out,dict(kind='mounted_horse_cache376',target='horse'),target_function=target)
 result.update(method='381 positive medial sternal arch, fixed thoracic origin and spatially rotating lateral humeral insertion; source residual and distal motion retained',profile=e['profile'],artistic_pass=False)
 (out/'forequarter381.json').write_text(json.dumps(result,indent=2)+'\n');return result


def donor_inspect(bpy,out,e):
 """Read the already-local donor without linking/evaluating its objects/scripts."""
 import hashlib
 root=Path(__file__).resolve().parents[4];b=e['source'];path=root/b['path']
 if hashlib.sha256(path.read_bytes()).hexdigest()!=b['sha256']:raise ValueError('FOREQUARTER381_DONOR_HASH')
 horse=bpy.data.objects['horse'];before=mod('nihang_prep367').frozen(bpy);actions=mod('nihang_padsolve370').actions(bpy);oldobjects=set(bpy.data.objects);oldactions=set(bpy.data.actions)
 try:
  with bpy.data.libraries.load(str(path),link=False) as (available,loaded):
   if 'horse' not in available.objects:raise ValueError('FOREQUARTER381_DONOR_OWNER')
   loaded.objects=['horse']
  donor=loaded.objects[0];mesh=donor.data
  if donor.type!='MESH' or len(mesh.vertices)!=len(horse.data.vertices):raise ValueError('FOREQUARTER381_DONOR_TOPOLOGY')
  names=[g.name for g in donor.vertex_groups];w=np.zeros((len(mesh.vertices),len(names)))
  for v in mesh.vertices:
   for g in v.groups:w[v.index,g.group]=g.weight
  raw=np.array([v.co[:] for v in mesh.vertices]);keys=mesh.shape_keys.key_blocks;shape=np.array([[v.co[:] for v in k.data] for k in keys]);edges=np.array([ed.vertices[:] for ed in mesh.edges]);current=np.array([v.co[:] for v in horse.data.vertices]);base=np.array([v.co[:] for v in horse.data.shape_keys.key_blocks[0].data]);np.savez_compressed(out/'donor381.npz',raw=raw,shape=shape,shape_names=np.array([k.name for k in keys]),weights=w,names=np.array(names),edges=edges)
  report=dict(source=b,vertices=len(raw),same_edges=np.array_equal(edges,np.array([ed.vertices[:] for ed in horse.data.edges])),same_group_names=names==[g.name for g in horse.vertex_groups],raw_difference=float(np.linalg.norm(raw-current,axis=1).max()),basis_difference=float(np.linalg.norm(shape[0]-base,axis=1).max()),shape_names=[k.name for k in keys],scales=list(donor.scale),scope='Unlinked data-only donor inspection; no reference/geometry/rig/visual qualification.')
 finally:
  for ob in set(bpy.data.objects)-oldobjects:bpy.data.objects.remove(ob,do_unlink=True)
  for a in set(bpy.data.actions)-oldactions:
   if a.users==0:bpy.data.actions.remove(a)
 if before!=mod('nihang_prep367').frozen(bpy) or actions!=mod('nihang_padsolve370').actions(bpy):raise ValueError('FOREQUARTER381_DONOR_READONLY_DRIFT')
 (out/'donor381.json').write_text(json.dumps(report,indent=2)+'\n');return report
