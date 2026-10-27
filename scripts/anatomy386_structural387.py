"""Bound inert-source posed ARAP experiment. No native or provider dispatch."""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,foreleg_ownership

def arap(rest,initial,edges,free,iterations=36):
    n=len(rest);a,b=edges.T
    active=free[a]|free[b];a=a[active];b=b[active];e=rest[a]-rest[b]
    # Uniform edge weights avoid magnifying tiny imported poles. Source topology
    # remains intact. Exact Dirichlet boundary instead of arbitrary soft springs.
    w=np.ones(len(a));deg=np.bincount(np.r_[a,b],weights=np.r_[w,w],minlength=n)
    L=coo_matrix((np.r_[deg,-w,-w],(np.r_[np.arange(n),a,b],np.r_[np.arange(n),b,a])),shape=(n,n)).tocsr()
    ids=np.flatnonzero(free);fixed=np.flatnonzero(~free);solve=factorized(L[ids][:,ids].tocsc());bc=L[ids][:,fixed]@initial[fixed]
    x=initial.astype(float).copy();energies=[]
    for iteration in range(iterations):
        d=x[a]-x[b];cov=np.zeros((n,3,3));v=d[:,:,None]*e[:,None,:]*w[:,None,None];np.add.at(cov,a,v);np.add.at(cov,b,v)
        U,_,V=np.linalg.svd(cov);U[:,:,-1]*=np.linalg.det(U@V)[:,None];R=U@V
        rhsedge=.5*np.einsum('nij,nj->ni',R[a]+R[b],e)*w[:,None];rhs=np.zeros((n,3));np.add.at(rhs,a,rhsedge);np.add.at(rhs,b,-rhsedge)
        y=x.copy();y[ids]=solve(rhs[ids]-bc);change=float(np.linalg.norm(y[ids]-x[ids],axis=1).max());x=y
        energies.append(change)
        if change<2e-6:break
    return x,energies

def self_test():
    r=np.array([[0.,0,0],[1,0,0],[1,1,0],[0,1,0],[.5,.5,.2]])
    e=np.array([[0,1],[1,2],[2,3],[3,0],[0,4],[1,4],[2,4],[3,4]])
    free=np.array([0,0,0,0,1],bool);theta=.7;R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
    a,_=arap(r,r,e,free);expected=r@R.T+np.array([2,3,1]);b,_=arap(r,expected,e,free)
    assert abs(a-r).max()<1e-10 and abs(b-expected).max()<1e-10
    return dict(neutral_error=float(abs(a-r).max()),rigid_error=float(abs(b-expected).max()))

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);rest=q['rest'].astype(float);src=q['source'];edges=q['edges'];n=len(rest)
    skin=main_skin(edges,n);ownership=foreleg_ownership(q['weights'],q['group_names'])
    # Connected forequarter patch, including both shoulder/neck-base interfaces;
    # exact rest-coordinate boundary. Protected35distal policy retained for first
    # causal trial. Group label does not define free anatomical tissue.
    free=skin&(rest[:,1]<-.22)&(rest[:,1]>-1.31)&(rest[:,2]>.97)&(rest[:,2]<1.91)&(ownership<.35)
    # A one-ring boundary collar is fixed, so an abrupt patch seam cannot be
    # mistaken for anatomical success.
    a,b=edges.T;boundary=np.zeros(n,bool);cross=free[a]!=free[b];boundary[a[cross]]=True;boundary[b[cross]]=True;free&=~boundary
    assert 200<free.sum()<6000
    target=src.copy();audit=[]
    for frame in [283,333,339]:
        i=int((frame-276)*2);posed=src[i].astype(float);result,iterations=arap(rest,posed,edges,free)
        delta=np.linalg.norm(result-posed,axis=1); target[i,free]=result[free].astype(np.float32)
        use=free[a]&free[b];base=np.linalg.norm(rest[a[use]]-rest[b[use]],axis=1);old=np.linalg.norm(posed[a[use]]-posed[b[use]],axis=1)/np.maximum(base,1e-9);new=np.linalg.norm(result[a[use]]-result[b[use]],axis=1)/np.maximum(base,1e-9)
        audit.append(dict(frame=frame,max_delta=float(delta.max()),iterations=iterations,source_edge_ratio_p05_p95=np.percentile(old,[5,95]).tolist(),target_edge_ratio_p05_p95=np.percentile(new,[5,95]).tolist()))
        print('solved',frame,'free',int(free.sum()),'maxdelta',delta.max(),flush=True)
    assert abs(target-src).max()<.45 and np.array_equal(target[:,ownership>=.35],src[:,ownership>=.35])
    out=root/'.runtime/art-direction/anatomy386-targets/posed387-227.npz';np.savez_compressed(out,source=src,target=target,rest=q['rest'],mask=free.astype(np.float32),times=q['times'])
    report=dict(self_test=self_test(),free_vertices=int(free.sum()),source_skin_vertices=int(skin.sum()),boundary_vertices=int(boundary.sum()),poses=audit,scope='Three isolated diagnostic posed reconstructions only; intervening source unchanged. No motion-ready derivative or artisticpass.')
    (root/'results/sikh387/numeric227.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':build(Path(__file__).resolve().parents[1])
