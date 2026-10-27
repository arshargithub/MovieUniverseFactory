"""Minimum-change connected neutral support control from original raw184.

205 absolute fairing erased good curvature. Keep the original cross-sectional
curvature, gently taper the entire lower mass, and explicitly test posed response.
This is an anatomy hypothesis, never an artistic PASS from a depth formula.
"""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from movie_factory.adapters.blender.anatomy_domain386 import main_skin, pectoral_domains, preserve_pectoral_interfaces

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False)
    r=q['rest'];x,y,z=r.T;edges=q['edges'];skin=main_skin(edges,len(r));frozen,prox=pectoral_domains(r,q['weights'],q['group_names'])
    a,b=edges.T;length=np.linalg.norm(r[a]-r[b],axis=1)
    graph=coo_matrix((np.r_[length,length],(np.r_[a,b],np.r_[b,a])),shape=(len(r),len(r))).tocsr()
    dist=dijkstra(graph,directed=False,indices=np.flatnonzero(skin&frozen),min_only=True)
    envelope=skin*smooth(.95,1.02,z)*(1-smooth(1.48,1.72,z))*(1-smooth(.24,.36,abs(x)))*smooth(-1.2,-1.12,y)*(1-smooth(-.43,-.25,y))*smooth(0,.18,dist)
    # Broad monotone taper below the neck, not a narrow dent above a retained tip.
    depth=.095*np.exp(-((z-1.10)/.28)**2)*envelope
    delta=np.zeros_like(r);delta[:,1]=depth
    # Tiny common underside lift supports the sternum rather than leaving a lip.
    delta[:,2]=.025*(1-smooth(1.12,1.37,z))*envelope
    delta[:,0]=-.05*x*envelope
    length=np.linalg.norm(delta,axis=1);scale=np.minimum(1,np.where(prox,.059,.179)/np.maximum(length,1e-12));delta*=scale[:,None]
    target=r+delta;mask=np.any(delta!=0,axis=1).astype(np.float32)
    report=preserve_pectoral_interfaces(r,target,r,q['weights'],q['group_names']);report.update(max_delta=float(np.linalg.norm(delta,axis=1).max()),changed_vertices=int(mask.sum()),saturated_vertices=int(np.sum(scale<1)),scope='Minimum-change raw neutral control. Posed tissue response is independently unresolved; native neutral/raised tests required. No new action/cache.')
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/rest206.npz',rest=r,target=target,mask=mask)
    (root/'results/sikh386/rest206-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
