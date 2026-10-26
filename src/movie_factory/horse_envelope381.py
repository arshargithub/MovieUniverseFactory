"""Positive forequarter envelope study in body coordinates; not anatomy simulation."""
import numpy as np


def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)


def ellipsoid(p,center,radii):
 r=np.asarray(radii);q=p-center
 # Continuous implicit field, including the centre; not an exact distance.
 return (np.linalg.norm(q/r,axis=1)-1)*float(r.min())


def capsule(p,a,b,r):
 v=b-a;t=np.clip(((p-a)@v)/max(float(v@v),1e-8),0,1)
 return np.linalg.norm(p-a-t[:,None]*v,axis=1)-r


def union(a,b,k):
 h=np.clip(.5+.5*(b-a)/k,0,1);return b*(1-h)+a*h-k*h*(1-h)


def field(p,limbs):
 # Thoracic breast, lower neck and anterior barrel are a single rounded form.
 d=ellipsoid(p,np.array([0,-.63,1.49]),np.array([.265,.32,.255]))
 d=union(d,ellipsoid(p,np.array([0,-.69,1.70]),np.array([.205,.255,.31])),.075)
 d=union(d,ellipsoid(p,np.array([0,-.17,1.35]),np.array([.325,.67,.395])),.065)
 for a,b,c in limbs:
  d=union(d,capsule(p,a,b,.108),.065)
  d=union(d,capsule(p,b,c,.079),.035)
 return d


def anchors(rest,posed,weights,names):
 names=list(names);out=[]
 for side in ('L','R'):
  points=[]
  for n in ['DEF-upper_arm.'+side,'DEF-upper_arm.'+side+'.001','DEF-forearm.'+side]:
   w=weights[:,names.index(n)]**6;points.append((posed*w[:,None]).sum(0)/w.sum())
  a,b,c=points
  # Extend along measured source centres so the capsule spans the actual roots.
  out.append((a+.6*(a-b),b+.6*(b-c),c+1.0*(c-b)))
 return out


def support(rest,weights,names):
 r=rest;names=list(names)
 distal=weights[:,[i for i,n in enumerate(names) if n.startswith('DEF-hand.')]].sum(1)
 m=smooth((r[:,2]-.60)/.25)*smooth((1.86-r[:,2])/.19)*smooth((-.24-r[:,1])/.24)*smooth((r[:,1]+1.24)/.16)
 m*=1-smooth((distal-.05)/.35)
 return m


def target(rest,source,weights,names,edges,*,steps=70):
 m=support(rest,weights,names);ids=np.flatnonzero(m>0);q=source.astype(float).copy();limbs=anchors(rest,source,weights,names);eps=.0003
 degree=np.bincount(edges.ravel(),minlength=len(rest));i,j=edges.T
 for _ in range(steps):
  p=q[ids];d=field(p,limbs);grad=np.empty_like(p)
  for k in range(3):
   e=np.zeros(3);e[k]=eps;grad[:,k]=(field(p+e,limbs)-field(p-e,limbs))/(2*eps)
  n=np.sum(grad*grad,axis=1);move=grad*(np.clip(d,-.008,.008)/np.maximum(n,.15))[:,None]
  q[ids]-=move*(.65*m[ids,None])
  total=np.zeros_like(q);np.add.at(total,i,q[j]);np.add.at(total,j,q[i]);q+=(total/np.maximum(degree,1)[:,None]-q)*(.32*m)[:,None]
  q[m==0]=source[m==0]
 delta=q-source
 if not np.isfinite(delta).all() or np.linalg.norm(delta,axis=1).max()>.45:raise ValueError('ENVELOPE381_BOUND')
 return q,m
