"""Regular-cell cage replaces irregular sliver tetrahedra; numeric geometry only."""
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import anatomy386_volume185 as base

def regular(lo,hi,spacing=.09):
 axes=[np.linspace(lo[j],hi[j],int(np.ceil((hi[j]-lo[j])/spacing))+1) for j in range(3)];shape=tuple(map(len,axes));points=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3);index=np.arange(len(points)).reshape(shape);t=[]
 # Six tetrahedra around one consistent body diagonal: conforming grid, no slivers.
 pattern=np.array([[0,1,3,7],[0,3,2,7],[0,2,6,7],[0,6,4,7],[0,4,5,7],[0,5,1,7]])
 for i in range(shape[0]-1):
  for j in range(shape[1]-1):
   for k in range(shape[2]-1):
    v=index[i:i+2,j:j+2,k:k+2].ravel();t.extend(v[pattern])
 return points,np.array(t,dtype=int)

def cage(q,triangles):
 p=q['source'][14].astype(float);edges=q['edges'];N=len(p);adj=coo_matrix((np.ones(len(edges)*2),(np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(N,N));_,lab=connected_components(adj);main=lab==np.bincount(lab).argmax();faces=triangles[np.all(main[triangles],axis=1)];tri=p[faces]
 lo=np.array([-.44,-1.26,.84]);hi=np.array([.44,.12,1.86]);points,t=regular(lo,hi);center=points[t].mean(1);near=cKDTree(p[main]).query(center)[0];keep=base.inside(center,tri)|(near<.025);t=t[keep];used=np.unique(t);remap=np.full(len(points),-1);remap[used]=np.arange(len(used));rest=points[used];tets=remap[t]
 _,labels=connected_components(coo_matrix((np.ones(len(tets)*12),(np.repeat(tets,3,axis=1).ravel(),tets[:,[[1,2,3],[0,2,3],[0,1,3],[0,1,2]]].reshape(-1))),shape=(len(rest),len(rest))))
 if len(np.unique(labels))!=1:raise ValueError(('GRID189_DISCONNECTED',len(np.unique(labels))))
 fixed=np.flatnonzero((abs(rest[:,1]-lo[1])<.001)|(abs(rest[:,1]-hi[1])<.001)|(abs(rest[:,2]-lo[2])<.001)|(abs(rest[:,2]-hi[2])<.001))
 ids=np.flatnonzero(main&np.all((p>lo)&(p<hi),axis=1));centers=rest[tets].mean(1);_,candidates=cKDTree(centers).query(p[ids],k=min(50,len(tets)));tv=rest[tets[candidates]];M=np.transpose(tv[:,:,1:]-tv[:,:,0,None],(0,1,3,2));uvw=np.linalg.solve(M,(p[ids,None]-tv[:,:,0])[...,None])[...,0];weights=np.concatenate([1-uvw.sum(-1,keepdims=True),uvw],axis=-1);score=np.minimum(weights,0)**2;score=score.sum(-1)+1e-5*np.sum((p[ids,None]-centers[candidates])**2,axis=-1);which=score.argmin(1);cell=candidates[np.arange(len(ids)),which];bary=weights[np.arange(len(ids)),which]
 if bary.min()<-.65 or bary.max()>1.65:raise ValueError(('GRID189_BINDING',float(bary.min()),float(bary.max())))
 mask=base.smooth(lo[1],lo[1]+.12,p[ids,1])*(1-base.smooth(hi[1]-.14,hi[1],p[ids,1]))*base.smooth(lo[2],lo[2]+.12,p[ids,2])*(1-base.smooth(hi[2]-.12,hi[2],p[ids,2]))
 D=np.transpose(rest[tets[:,1:]]-rest[tets[:,0,None]],(0,2,1));vol=abs(np.linalg.det(D))/6;condition=np.linalg.cond(D)
 if condition.max()>10 or len(fixed)<8:raise ValueError('GRID189_QUALITY_OR_CUT')
 return dict(rest=rest,tets=tets,fixed=fixed,skinids=ids,cell=cell,bary=bary,mask=mask,p0=p,stats=dict(nodes=len(rest),tets=len(tets),fixed=len(fixed),skin=len(ids),min_barycentric=float(bary.min()),max_barycentric=float(bary.max()),min_tet_volume=float(vol.min()),max_tet_condition=float(condition.max())))
