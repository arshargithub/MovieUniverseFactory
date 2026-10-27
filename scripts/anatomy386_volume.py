"""Numeric positive-volume authoring outside Blender; no executable asset payload.

Fixed source is original80 sampled by the reviewed native exporter. A supported
thoracic/pectoral volume is joined to moving proximal foreleg capsules. This is
an authored anatomical hypothesis, not physical muscle simulation or approval.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.csgraph import connected_components

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def ellipsoid(p,c,r):
 q=p-np.array(c);r=np.array(r);k0=np.linalg.norm(q/r,axis=-1);k1=np.linalg.norm(q/(r*r),axis=-1)
 return k0*(k0-1)/np.maximum(k1,1e-8)

def capsule(p,a,b,r0,r1):
 v=b-a;u=np.clip(((p-a)*v).sum(-1)/np.dot(v,v),0,1)
 return np.linalg.norm(p-a-u[:,None]*v,axis=-1)-(r0+(r1-r0)*u)

def union(a,b,k):
 h=np.clip(.5+.5*(b-a)/k,0,1);return b*(1-h)+a*h-k*h*(1-h)

def field(p,bones):
 # Ellipsoids overlap into one supported chest: no disjoint breast spheres.
 d=ellipsoid(p,(0,-.25,1.43),(.325,.61,.37))
 d=union(d,ellipsoid(p,(0,-.685,1.395),(.245,.215,.255)),.055)
 for side in [0,1]:
  a=bones[5+side,0];b=bones[7+side,0]
  d=union(d,capsule(p,a,b,.105,.073),.045)
 return d

def author(src,dest):
 q=np.load(src,allow_pickle=False);rest=q['rest'];source=q['source'];ed=q['edges'];N=len(rest)
 adj=coo_matrix((np.ones(len(ed)*2),(np.r_[ed[:,0],ed[:,1]],np.r_[ed[:,1],ed[:,0]])),shape=(N,N)).tocsr()
 _,labels=connected_components(adj);counts=np.bincount(labels);skin=labels==counts.argmax()
 x,y,z=rest.T
 mask=skin*smooth(-1.12,-1.02,y)*(1-smooth(-.53,-.30,y))*smooth(.98,1.14,z)*(1-smooth(1.58,1.76,z))*(1-smooth(.28,.36,abs(x)))
 ids=np.flatnonzero(mask);A=diags(1/np.maximum(1,np.array(adj.sum(1)).ravel()))@adj
 target=source.copy();metrics=[]
 for i,p in enumerate(source):
  v=p[ids].astype(float).copy();B=q['bones'][i]
  for _ in range(14):
   f=field(v,B);eps=.0004
   grad=np.column_stack([(field(v+np.eye(3)[j]*eps,B)-field(v-np.eye(3)[j]*eps,B))/(2*eps) for j in range(3)])
   step=f[:,None]*grad/np.maximum((grad*grad).sum(1)[:,None],.1)
   norm=np.linalg.norm(step,axis=1);step*=np.minimum(1,.035/np.maximum(norm,1e-8))[:,None];v-=step
  delta=np.zeros_like(p);delta[ids]=(v-p[ids])*mask[ids,None]
  for _ in range(5):delta=.65*delta+.35*(A@delta);delta*=mask[:,None]
  target[i]+=delta
  metrics.append(float(np.linalg.norm(delta,axis=1).max()))
 np.savez_compressed(dest,source=source,target=target,rest=rest,mask=mask.astype(np.float32),times=q['times'])
 return dict(method='connected supported thorax/pectoral envelope plus actual proximal-limb capsules',vertices=int(len(ids)),max_delta=max(metrics),samples=len(source),outside_exact=bool(np.array_equal(target[:,mask==0],source[:,mask==0])),scope='Authored hypothesis; actual multi-view native proof required. No anatomy or motion PASS.')

if __name__=='__main__':
 print(json.dumps(author(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
