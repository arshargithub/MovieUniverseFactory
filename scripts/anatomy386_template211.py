"""Coherent registered anatomical-surface fit in rest space, original live rig.

183 is a negative control: it projected posed samples and transported a cached
displacement. This fit instead regularizes a single rest surface, retains208's
tested tissue attachment, and must qualify all poses through the original rig.
"""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve
from scipy.sparse.csgraph import dijkstra
from anatomy386_template183 import closest
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,pectoral_domains,preserve_pectoral_interfaces

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);r=q['rest'].astype(float);edges=q['edges'];n=len(r)
    current=np.load(root/'.runtime/art-direction/anatomy386-targets/rest209.npz')['target'];weights=np.load(root/'.runtime/factory-native/sikh386-appearance-c208-source/anatomy386-weights.npz')['after'];names=q['group_names']
    ref=np.load(root/'.runtime/art-direction/anatomy386-references/lyndon-body-reference.npz');v=ref['vertices'].astype(float).copy();f=ref['faces']
    # Provisional chest/shoulder registration, not a breed/head identity match.
    v[:,0]*=.84;v[:,1]=v[:,1]*.82-.22;v[:,2]=v[:,2]*.95+.07
    centers=v[f].mean(1);f=f[(centers[:,1]<-.15)&(centers[:,2]>.86)&(centers[:,2]<1.85)]
    skin=main_skin(edges,n);frozen,prox=pectoral_domains(r,weights,names);a,b=edges.T
    lengths=np.linalg.norm(r[a]-r[b],axis=1);graph=coo_matrix((np.r_[lengths,lengths],(np.r_[a,b],np.r_[b,a])),shape=(n,n)).tocsr();dist=dijkstra(graph,directed=False,indices=np.flatnonzero(skin&frozen),min_only=True)
    x,y,z=r.T;mask=skin*smooth(.95,1.04,z)*(1-smooth(1.5,1.74,z))*(1-smooth(.27,.36,abs(x)))*smooth(-1.2,-1.10,y)*(1-smooth(-.43,-.25,y))*smooth(0,.20,dist)
    ids=np.flatnonzero(mask>1e-5);adj=coo_matrix((np.ones(2*len(a)),(np.r_[a,b],np.r_[b,a])),shape=(n,n)).tocsr();lap=diags(np.asarray(adj.sum(1)).ravel())-adj
    rows=np.flatnonzero(np.asarray(adj[:,ids].sum(1)).ravel()>0);L=lap[rows][:,ids];penalty=L.T@L;points=r[ids].copy();audit=[]
    _,before_distance=closest(points,v,f)
    for strength in [.5,2.,8.,20.]:
        goal,distance=closest(points,v,f);fidelity=strength*mask[ids]**2+.0001
        delta=spsolve((penalty+diags(fidelity)).tocsc(),fidelity[:,None]*(goal-r[ids]))
        points=r[ids]+delta;audit.append(dict(strength=strength,median_distance=float(np.median(distance)),max_displacement=float(np.linalg.norm(delta,axis=1).max())))
    delta=np.zeros_like(r);delta[ids]=points-r[ids]
    # One coherent global scale, not independent caps that make a jagged seam.
    lengths=np.linalg.norm(delta,axis=1);scale=min(1.,.179/max(float(lengths.max()),1e-12),.149/max(float(lengths[prox].max()),1e-12));target=r+delta*scale
    allowed=(abs(current[:,0])<=.36)&(current[:,1]>=-1.2)&(current[:,1]<=-.25)&(current[:,2]>=.95)&(current[:,2]<=1.75);target[~allowed]=current[~allowed]
    incremental=float(np.linalg.norm(target-current,axis=1).max());alpha=min(1.,.179/max(incremental,1e-12));target=current+alpha*(target-current)
    cumulative=preserve_pectoral_interfaces(r,target,r,weights,names,max_proximal=.15);incr=preserve_pectoral_interfaces(current,target,current,weights,names,max_proximal=.15)
    _,after_distance=closest(target[ids],v,f)
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/rest211.npz',rest=current,target=target.astype(np.float32),mask=np.any(target!=current,axis=1).astype(np.float32))
    report=dict(vertices=len(ids),registration=dict(x_scale=.84,y_scale=.82,y_offset=-.22,z_scale=.95,z_offset=.07),iterations=audit,global_scale=scale,incremental_scale=alpha,mean_guide_distance_before=float(before_distance.mean()),mean_guide_distance_after=float(after_distance.mean()),cumulative=cumulative,incremental=incr,max_original_delta=float(np.linalg.norm(target-r,axis=1).max()),max_incremental_delta=float(np.linalg.norm(target-current,axis=1).max()),scope='QualifiedCC0guide used for connected gross anatomy. Same vertex topology/rest/live rig and original action; no posed cache. Numeric fit is not natural anatomy or production approval; actual neutral/raised views required.')
    (root/'results/sikh386/rest211-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
