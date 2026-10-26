"""Boundary-supported front-cap reconstruction; outer Python only, no native launch."""
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import connected_components


class FrontCap:
 def __init__(self,rest,edges,weights,names,relief=.045):
  r=np.asarray(rest,dtype=float);self.rest=r;self.relief=relief;names=list(names)
  distal=weights[:,[i for i,n in enumerate(names) if n.startswith('DEF-forearm.')]].sum(1)
  n=len(r);ei,ej=edges.T;G=coo_matrix((np.ones(len(ei)*2),(np.r_[ei,ej],np.r_[ej,ei])),shape=(n,n)).tocsr();_,labels=connected_components(G);body=labels==int(np.bincount(labels).argmax())
  active=body&(r[:,1]<-.70)&(r[:,2]>.99)&(r[:,2]<1.80)&(np.abs(r[:,0])<.34)&(distal<.55)
  self.ids=np.flatnonzero(active);self.fixed=np.flatnonzero(~active);self.mask=active.astype(float)
  if not 30<len(self.ids)<2000:raise ValueError('CAP381_DOMAIN')
  n=len(r);i,j=edges.T;degree=np.bincount(edges.ravel(),minlength=n).astype(float)
  L=diags(degree)-coo_matrix((np.ones(len(i)*2),(np.r_[i,j],np.r_[j,i])),shape=(n,n)).tocsr();B=(L.T@L).tocsr();self.cross=B[self.ids][:,self.fixed];self.solve=splu(B[self.ids][:,self.ids].tocsc()).solve
  # A positive smooth bubble provides muscle relief; squared bubble has zero
  # slope at the fixed boundary. The base is a boundary-supported C1 cap.
  bubble=splu(L[self.ids][:,self.ids].tocsc()).solve(np.ones(len(self.ids)));bubble/=bubble.max();self.bubble=bubble*bubble
  self.lobes=.65+.35*np.exp(-((np.abs(r[self.ids,0])-.12)/.09)**2)

 def fit(self,source):
  q=np.asarray(source,dtype=float).copy();q[self.ids]=self.solve(-self.cross@q[self.fixed]);q[self.ids,1]-=self.relief*self.bubble*self.lobes
  if not np.isfinite(q).all() or np.linalg.norm(q-source,axis=1).max()>.45:raise ValueError('CAP381_TARGET_BOUND')
  return q
