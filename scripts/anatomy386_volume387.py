"""Inert local volumetric ARAP compatibility experiment, not native authoring."""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import Delaunay,cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,foreleg_ownership

def inside(points,rest,faces):
    # Ray +X against actual closed source skin. No convexhull substitutes for
    # chest/foreleg concavity. Non-axis grid avoids edge double-count in setup.
    tri=rest[faces];a=tri[:,0];v=tri[:,1]-a;w=tri[:,2]-a;den=v[:,1]*w[:,2]-v[:,2]*w[:,1];valid=abs(den)>1e-12
    a=a[valid];v=v[valid];w=w[valid];den=den[valid];out=[]
    for start in range(0,len(points),48):
        p=points[start:start+48];dy=p[:,None,1]-a[None,:,1];dz=p[:,None,2]-a[None,:,2]
        u=(dy*w[None,:,2]-dz*w[None,:,1])/den;vv=(dz*v[None,:,1]-dy*v[None,:,2])/den
        x=a[None,:,0]+u*v[None,:,0]+vv*w[None,:,0]
        hit=(u>=0)&(vv>=0)&(u+vv<1)&(x>p[:,None,0]+1e-9)
        out.extend((hit.sum(1)%2)==1)
    return np.array(out,bool)

def solve_arap(rest,initial,edges,w,free,iterations=48):
    n=len(rest);a,b=edges.T;e=rest[a]-rest[b];deg=np.bincount(np.r_[a,b],weights=np.r_[w,w],minlength=n)
    L=coo_matrix((np.r_[deg,-w,-w],(np.r_[np.arange(n),a,b],np.r_[np.arange(n),b,a])),shape=(n,n)).tocsr();ids=np.flatnonzero(free);fix=np.flatnonzero(~free);solve=factorized(L[ids][:,ids].tocsc());bc=L[ids][:,fix]@initial[fix];x=initial.copy();changes=[]
    for k in range(iterations):
        d=x[a]-x[b];cov=np.zeros((n,3,3));v=d[:,:,None]*e[:,None,:]*w[:,None,None];np.add.at(cov,a,v);np.add.at(cov,b,v)
        U,_,V=np.linalg.svd(cov);U[:,:,-1]*=np.linalg.det(U@V)[:,None];R=U@V;rhsedge=.5*np.einsum('nij,nj->ni',R[a]+R[b],e)*w[:,None];rhs=np.zeros((n,3));np.add.at(rhs,a,rhsedge);np.add.at(rhs,b,-rhsedge)
        y=x.copy();y[ids]=solve(rhs[ids]-bc);change=float(np.linalg.norm(y[ids]-x[ids],axis=1).max());x=y;changes.append(change)
        if change<3e-6:break
    return x,changes

def determinants(v,tets):
    t=v[tets];return np.linalg.det(np.stack([t[:,1]-t[:,0],t[:,2]-t[:,0],t[:,3]-t[:,0]],axis=-1))

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz');rest=q['rest'].astype(float);source=q['source'];edges=q['edges'];skin=main_skin(edges,len(rest));own=foreleg_ownership(q['weights'],q['group_names'])
    free=skin&(rest[:,1]<-.22)&(rest[:,1]>-1.31)&(rest[:,2]>.97)&(rest[:,2]<1.91)&(own<.35)
    a,b=edges.T;boundary=np.zeros(len(rest),bool);cross=free[a]!=free[b];boundary[a[cross]]=True;boundary[b[cross]]=True;free&=~boundary
    selected=free|boundary;ids=np.flatnonzero(selected);v=rest[ids];fs=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz')['triangles'];fs=fs[np.all(skin[fs],axis=1)]
    grid=np.stack(np.meshgrid(np.arange(-.33,.35,.065),np.arange(-1.28,-.23,.065),np.arange(1.005,1.9,.065),indexing='ij'),-1).reshape(-1,3);grid=grid[inside(grid,rest,fs)]
    allrest=np.r_[v,grid];tets=Delaunay(allrest,qhull_options='QJ').simplices;det=determinants(allrest,tets);keep=abs(det)>1e-8;tets=tets[keep];det=det[keep]
    center=allrest[tets].mean(1);tets=tets[inside(center,rest,fs)];det=determinants(allrest,tets)
    pairs=np.array([[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]);ee=np.sort(tets[:,pairs].reshape(-1,2),axis=1);vol=np.repeat(abs(det)/6,6);ee,inv=np.unique(ee,axis=0,return_inverse=True);w=np.bincount(inv,weights=vol)/np.maximum(np.sum((allrest[ee[:,0]]-allrest[ee[:,1]])**2,axis=1),1e-8)
    # Remove isolated tetrahedral grid points; source surface points retained.
    degree=np.bincount(ee.ravel(),minlength=len(allrest));live=(degree>0);assert live[:len(ids)].all();remap=np.cumsum(live)-1;ee=remap[ee];tets=remap[tets];allrest=allrest[live]
    freeall=np.r_[free[ids],np.ones(len(grid),bool)][live]
    nearest=cKDTree(rest[skin]);_,nearestids=nearest.query(allrest[len(ids):],k=12);skinids=np.flatnonzero(skin);near=skinids[nearestids];dist=np.linalg.norm(allrest[len(ids):,None,:]-rest[near],axis=2);ww=1/np.maximum(dist,.02)**2;ww/=ww.sum(1)[:,None]
    control,cc=solve_arap(allrest,allrest.copy(),ee,w,freeall,2);assert abs(control-allrest).max()<1e-9
    target=source.copy();audit=[]
    for f in [283,333,339]:
        i=int((f-276)*2);p=source[i].astype(float);internal=allrest[len(ids):]+np.sum((p[near]-rest[near])*ww[:,:,None],axis=1);initial=np.r_[p[ids],internal];result,changes=solve_arap(allrest,initial,ee,w,freeall)
        target[i,ids[free[ids]]]=result[:len(ids)][free[ids]].astype(np.float32)
        ratio=determinants(result,tets)/determinants(allrest,tets);audit.append(dict(frame=f,max_delta=float(np.linalg.norm(target[i]-source[i],axis=1).max()),tet_volume_ratio_p01_p50_p99=np.percentile(ratio,[1,50,99]).tolist(),inverted_tets=int((ratio<=0).sum()),iterations=changes));print('solved',f,audit[-1]['max_delta'],flush=True)
    assert np.linalg.norm(target-source,axis=2).max()<.45;assert np.array_equal(target[:,own>=.35],source[:,own>=.35]);mask=np.any(target!=source,axis=(0,2)).astype(np.float32)
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/volume387-229.npz',source=source,target=target,rest=q['rest'],mask=mask,times=q['times'])
    report=dict(surface_vertices=len(ids),internal_vertices=len(allrest)-len(ids),tetrahedra=len(tets),edges=len(ee),neutral_control_error=float(abs(control-allrest).max()),poses=audit,scope='Volumetric scaffold causal diagnostic at threeposes; deformationvalidity and actualnative positive anatomy remain distinct. No motionready/finalactor claim.')
    (root/'results/sikh387/numeric229.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':build(Path(__file__).resolve().parents[1])
