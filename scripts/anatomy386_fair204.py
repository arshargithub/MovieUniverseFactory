"""Connected constrained surface fairing; directional study is not a mesh result.

Unlike earlier displacement masks, this minimizes absolute surface curvature
over the complete connected forequarter. Hard exterior/distal coordinates and
soft anatomical section handles constrain the solve. Actual native views veto it.
"""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve
from scipy.sparse.csgraph import dijkstra
from movie_factory.adapters.blender.anatomy_domain386 import main_skin, pectoral_domains, preserve_pectoral_interfaces


def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1)
    return t*t*(3-2*t)


def fair(rest, edges, weights, names):
    r=rest.astype(float); n=len(r); x,y,z=r.T
    skin=main_skin(edges,n); frozen,proximal=pectoral_domains(r,weights,names)
    a,b=edges.T
    adj=coo_matrix((np.ones(2*len(a)),(np.r_[a,b],np.r_[b,a])),shape=(n,n)).tocsr()
    # Connected geometric domain, independent of irregular blendweight values.
    domain=skin&~frozen&(abs(x)<.355)&(y> -1.19)&(y<-.26)&(z>.995)&(z<1.72)
    ids=np.flatnonzero(domain); outside=np.flatnonzero(~domain)
    lap=diags(np.asarray(adj.sum(1)).ravel())-adj
    # Biharmonic absolute fairing smooths inherited corrugations, instead of
    # preserving them as differential coordinates or painting a displacement.
    rows=np.flatnonzero(np.asarray(adj[:,ids].sum(1)).ravel()>0)
    L=lap[rows]; A=L[:,ids]; B=L[:,outside]@r[outside]
    local=r[ids]; xx,yy,zz=local.T
    front=1-smooth(-.96,-.60,yy)
    central=1-smooth(.22,.35,abs(xx))
    vertical=smooth(1.01,1.10,zz)*(1-smooth(1.57,1.70,zz))
    handles=front*central*vertical
    # A continuous lower-neck-to-sternum envelope replaces the hollow/lobe
    # pair. These are proposed local construction handles, not measured anatomy.
    envelope=np.interp(zz,[1.,1.10,1.22,1.36,1.5,1.65,1.72],[-.70,-.77,-.86,-.94,-1.005,-1.10,-1.18])
    envelope+=.13*(np.minimum(abs(xx),.3)/.3)**2
    goal=local.copy(); goal[:,1]=envelope
    fidelity=.015+4.0*handles
    rhs=-A.T@B+fidelity[:,None]*goal
    target=r.copy(); target[ids]=spsolve((A.T@A+diags(fidelity)).tocsc(),rhs)
    # Smooth geodesic transition to protected boundaries, not a skinweight mask.
    lengths=np.linalg.norm(r[a]-r[b],axis=1)
    graph=coo_matrix((np.r_[lengths,lengths],(np.r_[a,b],np.r_[b,a])),shape=(n,n)).tocsr()
    distance=dijkstra(graph,directed=False,indices=outside,min_only=True)
    fade=smooth(0,.10,distance)
    delta=(target-r)*fade[:,None]
    # Existing technical guardrails are retained exactly; saturation is reported.
    length=np.linalg.norm(delta,axis=1); limit=np.where(proximal,.059,.179)
    scale=np.minimum(1,limit/np.maximum(length,1e-12)); delta*=scale[:,None]
    target=r+delta; target[~domain]=r[~domain]
    mask=np.any(target!=r,axis=1).astype(np.float32)
    return target,mask,dict(domain_vertices=len(ids),saturated_vertices=int(np.sum(scale<1)),max_delta=float(np.linalg.norm(delta,axis=1).max()),method='absolute_biharmonic_surface_with_continuous_anatomical_section_handles')


def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False)
    target,mask,report=fair(q['rest'],q['edges'],q['weights'],q['group_names'])
    report['interfaces']=preserve_pectoral_interfaces(q['rest'],target,q['rest'],q['weights'],q['group_names'])
    dest=root/'.runtime/art-direction/anatomy386-targets/rest204.npz'
    np.savez_compressed(dest,rest=q['rest'],target=target,mask=mask)
    report['qualification']='Numeric construction proposal only. Native neutral and accepted raised pose family NOT_RUN; generated study is directional, real photographs govern anatomical plausibility.'
    (root/'results/sikh386/rest204-numeric.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    build(Path(__file__).resolve().parents[1])
