"""Local anatomical-template fitting with observed source deformation transfer.

Inert licensed geometry supplies gross spatial form, not identity/material/rig.
Only a bounded original-horse skin region changes; actual native views decide.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def closest(p,v,f):
 tri=v[f];tree=cKDTree(tri.mean(1));_,idx=tree.query(p,k=min(48,len(f)))
 idx=np.asarray(idx).reshape(len(p),-1);t=tri[idx];P=p[:,None,:];a=t[:,:,0];ab=t[:,:,1]-a;ac=t[:,:,2]-a;n=np.cross(ab,ac);nn=(n*n).sum(-1)
 proj=P-(((P-a)*n).sum(-1)/np.maximum(nn,1e-14))[:,:,None]*n
 v2=proj-a;d00=(ab*ab).sum(-1);d01=(ab*ac).sum(-1);d11=(ac*ac).sum(-1);d20=(v2*ab).sum(-1);d21=(v2*ac).sum(-1);den=d00*d11-d01*d01
 u=(d11*d20-d01*d21)/np.maximum(den,1e-14);w=(d00*d21-d01*d20)/np.maximum(den,1e-14);inside=(u>=0)&(w>=0)&(u+w<=1)&(nn>1e-14)
 best=proj.copy();dist=np.where(inside,((proj-P)**2).sum(-1),np.inf)
 for j,k in [(0,1),(1,2),(2,0)]:
  a=t[:,:,j];e=t[:,:,k]-a;alpha=np.clip(((P-a)*e).sum(-1)/np.maximum((e*e).sum(-1),1e-14),0,1);q=a+alpha[:,:,None]*e;d=((q-P)**2).sum(-1);take=d<dist;best=np.where(take[:,:,None],q,best);dist=np.minimum(dist,d)
 pick=dist.argmin(1);return best[np.arange(len(p)),pick],np.sqrt(dist[np.arange(len(p)),pick])

def rotations(p0,p,edges,ids,N):
 a,b=edges.T;old=p0[b]-p0[a];new=p[b]-p[a];outer=new[:,:,None]*old[:,None,:];cov=np.zeros((N,3,3))
 np.add.at(cov,a,outer);np.add.at(cov,b,outer)
 U,S,V=np.linalg.svd(cov[ids]);sign=np.linalg.det(U@V);U[:,:,-1]*=sign[:,None];return U@V

def author(source_path,reference_path,dest):
 q=np.load(source_path,allow_pickle=False);source=q['source'];r=q['rest'];edges=q['edges'];N=len(r);p0=source[int((283-276)*2)]
 ref=np.load(reference_path,allow_pickle=False);v=ref['vertices'].astype(float).copy();f=ref['faces']
 # Provisional anatomical registration, explicitly NOT a breed/identity match.
 v[:,0]*=.72+.13*smooth(1.2,1.65,v[:,2]);v[:,1]=v[:,1]*.68-.34;v[:,2]=v[:,2]*.93+.10
 centers=v[f].mean(1);f=f[(centers[:,1]<-.18)&(centers[:,2]>.82)&(centers[:,2]<1.85)]
 adj=coo_matrix((np.ones(len(edges)*2),(np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(N,N)).tocsr();_,labels=connected_components(adj);skin=labels==np.bincount(labels).argmax();A=diags(1/np.maximum(1,np.asarray(adj.sum(1)).ravel()))@adj
 x,y,z=r.T;mask=skin*smooth(-1.20,-1.08,y)*(1-smooth(-.38,-.15,y))*smooth(.98,1.13,z)*(1-smooth(1.53,1.75,z))*(1-smooth(.34,.42,abs(x)));ids=np.flatnonzero(mask)
 goal,distance=closest(p0[ids],v,f);d0=np.zeros_like(p0);d0[ids]=(goal-p0[ids])*mask[ids,None]
 for _ in range(10):d0=.7*d0+.3*(A@d0)
 d0*=mask[:,None]
 tri=np.load(Path(source_path).parents[1]/'sikh374-appearance-c124-inspect/horse-form374.npz')['triangles'];tri=tri[np.any(mask[tri]>0,axis=1)]
 target=source.copy();audit=[]
 for i,p in enumerate(source):
  R=rotations(p0,p,edges,ids,N);delta=np.zeros_like(p);delta[ids]=np.einsum('nij,nj->ni',R,d0[ids])
  if i==14:delta=d0.copy()
  old=p[tri];n0=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);area0=np.linalg.norm(n0,axis=1);scale=np.ones(N);limited=np.zeros(N,dtype=bool)
  for k in range(50):
   new=(p+delta*scale[:,None])[tri];n=np.cross(new[:,1]-new[:,0],new[:,2]-new[:,0]);area=np.linalg.norm(n,axis=1);cos=(n*n0).sum(1)/np.maximum(area*area0,1e-12);bad=(area0>1e-9)&((cos<.12)|(area<area0*.12)|(area>area0*5))
   if not bad.any():break
   b=np.unique(tri[bad]);limited[b]=True;scale[b]*=.72;scale=np.minimum(scale,.75*scale+.25*(A@scale))
  if bad.any():raise ValueError(('TEMPLATE183_ORIENTATION',i,int(bad.sum())))
  delta*=scale[:,None];target[i]+=delta;audit.append(dict(frame=float(q['times'][i]),limited_vertices=int(limited.sum()),max_delta=float(np.linalg.norm(delta,axis=1).max()),bad_triangles=int(bad.sum())))
 np.savez_compressed(dest,source=source,target=target,rest=r,mask=mask.astype(np.float32),times=q['times'])
 report=dict(method='registered anatomical3Dguide localclosest-surface fit plus actual one-ring deformation rotation transfer',vertices=len(ids),max_delta=max(a['max_delta'] for a in audit),orientation=audit,fit_distance_percentiles=np.percentile(distance,[0,50,90,100]).tolist(),outside_exact=bool(np.array_equal(target[:,mask==0],source[:,mask==0])),qualification='Hypothesis only; provisional registration and native standing/raised multiview proof required. No new horse identity/rig/material/action adoption.')
 return report

if __name__=='__main__':print(json.dumps(author(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3])),indent=2))
