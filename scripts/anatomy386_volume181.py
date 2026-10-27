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
 # Continuous sternum keel and pectoral fans, with actual humeral insertion.
 # The paired masses are high/lateral; their lower tips are not the silhouette.
 shift=[]
 baseline=[np.array([.207,-.768,1.362]),np.array([-.207,-.768,1.362])]
 for side in [0,1]:
  insert=.5*(bones[5+side,0]+bones[5+side,1]);shift.append(insert-baseline[side])
 mean=.20*(shift[0]+shift[1])/2
 d=ellipsoid(p,(0,-.235,1.48),(.305,.565,.30))
 d=union(d,ellipsoid(p,np.array([0,-.72,1.425])+mean,(.104,.197,.235)),.055)
 for side in [0,1]:
  sign=1 if side==0 else -1
  center=np.array([sign*.134,-.705,1.49])+.6*shift[side]
  d=union(d,ellipsoid(p,center,(.146,.175,.178)),.065)
  d=union(d,capsule(p,bones[5+side,0],bones[7+side,0],.104,.073),.055)
 return d


def author(src,dest):
 q=np.load(src,allow_pickle=False);rest=q['rest'];source=q['source'];ed=q['edges'];N=len(rest)
 adj=coo_matrix((np.ones(len(ed)*2),(np.r_[ed[:,0],ed[:,1]],np.r_[ed[:,1],ed[:,0]])),shape=(N,N)).tocsr()
 _,labels=connected_components(adj);counts=np.bincount(labels);skin=labels==counts.argmax()
 x,y,z=rest.T
 mask=skin*smooth(-1.12,-1.02,y)*(1-smooth(-.53,-.30,y))*smooth(1.00,1.12,z)*(1-smooth(1.46,1.63,z))*(1-smooth(.28,.36,abs(x)))
 ids=np.flatnonzero(mask);A=diags(1/np.maximum(1,np.array(adj.sum(1)).ravel()))@adj
 target=source.copy();metrics=[];checks=[]
 triangles=np.load(Path(src).parents[1]/'sikh374-appearance-c124-inspect/horse-form374.npz')['triangles']
 triangles=triangles[np.any(mask[triangles]>0,axis=1)]
 for i,p in enumerate(source):
  B=q['bones'][i];center=np.array([0,-.62,1.50]);ray=p[ids].astype(float)-center
  ray/=np.maximum(np.linalg.norm(ray,axis=1)[:,None],1e-8)
  lo=np.zeros(len(ids));hi=np.full(len(ids),1.2)
  for _ in range(27):
   mid=(lo+hi)/2;outside=field(center+mid[:,None]*ray,B)>0
   hi=np.where(outside,mid,hi);lo=np.where(outside,lo,mid)
  v=center+((lo+hi)/2)[:,None]*ray
  delta=np.zeros_like(p);delta[ids]=(v-p[ids])*mask[ids,None]
  for _ in range(8):delta=.65*delta+.35*(A@delta)
  delta*=mask[:,None]
  # Preserve orientation before expensive native proofs. This does not approve form.
  old=p[triangles];norm0=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);area0=np.linalg.norm(norm0,axis=1)
  scale=np.ones(N);limited=np.zeros(N,dtype=bool);initial_flips=None
  for iteration in range(45):
   new=(p+delta*scale[:,None])[triangles];norm=np.cross(new[:,1]-new[:,0],new[:,2]-new[:,0]);area=np.linalg.norm(norm,axis=1)
   cosine=(norm*norm0).sum(1)/np.maximum(area*area0,1e-12)
   bad=(area0>1e-9)&((cosine<.15)|(area<area0*.12)|(area>area0*5))
   if initial_flips is None:initial_flips=int((cosine<0).sum())
   if not bad.any():break
   badids=np.unique(triangles[bad]);scale[badids]*=.72;limited[badids]=True
   scale=np.minimum(scale,.75*scale+.25*(A@scale))
  if bad.any():raise ValueError(('orientation_limit_failed',i,int(bad.sum())))
  delta*=scale[:,None]
  checks.append(dict(initial_flips=initial_flips,limited_vertices=int(limited.sum()),minimum_scale=float(scale[ids].min()),final_bad_triangles=int(bad.sum())))
  target[i]+=delta
  metrics.append(float(np.linalg.norm(delta,axis=1).max()))
 np.savez_compressed(dest,source=source,target=target,rest=rest,mask=mask.astype(np.float32),times=q['times'])
 return dict(method='central supported sternum with high pectoral fans tied to actual proximal-arm insertion; radial orientation control',vertices=int(len(ids)),orientation=checks,max_delta=max(metrics),samples=len(source),outside_exact=bool(np.array_equal(target[:,mask==0],source[:,mask==0])),scope='Authored hypothesis; actual multi-view native proof required. No anatomy or motion PASS.')

if __name__=='__main__':
 print(json.dumps(author(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
