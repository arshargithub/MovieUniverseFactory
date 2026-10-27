"""Broad connected taper with separately reviewed proximal skin boundary.

The old6cm cap was a method constraint, not a skeletal or Director constraint.
Keep exact distal geometry and original action while testing a continuous form.
"""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,pectoral_domains,preserve_pectoral_interfaces

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False)
    r=q['rest'];current=np.load(root/'.runtime/art-direction/anatomy386-targets/rest206.npz')['target']
    weights=np.load(root/'.runtime/factory-native/sikh386-appearance-c208-source/anatomy386-weights.npz')['after'];names=q['group_names'];x,y,z=r.T;edges=q['edges'];skin=main_skin(edges,len(r));frozen,prox=pectoral_domains(r,weights,names)
    a,b=edges.T;length=np.linalg.norm(r[a]-r[b],axis=1);graph=coo_matrix((np.r_[length,length],(np.r_[a,b],np.r_[b,a])),shape=(len(r),len(r))).tocsr()
    dist=dijkstra(graph,directed=False,indices=np.flatnonzero(skin&frozen),min_only=True)
    env=skin*smooth(.95,1.02,z)*(1-smooth(1.5,1.73,z))*(1-smooth(.27,.36,abs(x)))*smooth(-1.2,-1.12,y)*(1-smooth(-.43,-.25,y))*smooth(0,.24,dist)
    delta=np.zeros_like(r);delta[:,1]=.17*np.exp(-((z-1.12)/.32)**2)*env;delta[:,2]=.035*(1-smooth(1.13,1.39,z))*env;delta[:,0]=-.10*x*env
    length=np.linalg.norm(delta,axis=1);scale=np.minimum(1,np.where(prox,.149,.179)/np.maximum(length,1e-12));delta*=scale[:,None];target=r+delta
    # Current206 already has a small taper;209 authors the cumulative goal from
    # the raw original, not an accumulating per-cycle offset.
    allowed=(abs(current[:,0])<=.36)&(current[:,1]>=-1.2)&(current[:,1]<=-.25)&(current[:,2]>=.95)&(current[:,2]<=1.75)
    target[~allowed]=current[~allowed]
    mask=np.any(target!=current,axis=1).astype(np.float32)
    cumulative=preserve_pectoral_interfaces(r,target,r,weights,names,max_proximal=.15)
    incremental=preserve_pectoral_interfaces(current,target,current,weights,names,max_proximal=.15)
    report=dict(cumulative=cumulative,incremental=incremental,max_original_delta=float(np.linalg.norm(target-r,axis=1).max()),max_incremental_delta=float(np.linalg.norm(target-current,axis=1).max()),clamped_vertices=int(np.sum(scale<1)),scope='Cumulative connected form goal on208skin ownership. Numeric only; neutral and raised native shape/nap/consumer NOT_RUN.')
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/rest209.npz',rest=current,target=target,mask=mask)
    (root/'results/sikh386/rest209-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
