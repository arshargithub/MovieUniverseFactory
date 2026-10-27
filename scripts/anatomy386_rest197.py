"""Curvature-preserving depth correction on the coherent raw neutral chest.

A proposed lowerpectoralanterior-depth correction, not a measured or Director-approved
proportion. Spatial/physical references govern supported form; native proof
must decide whether this modest rest hypothesis is an improvement.
"""
from pathlib import Path
import json
import numpy as np
from anatomy386_volume185 import smooth
from movie_factory.adapters.blender.anatomy_domain386 import foreleg_ownership,preserve_forelegs,main_skin
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

def build(root):
 q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz');r=q['rest'];x,y,z=r.T;ownership=foreleg_ownership(q['weights'],q['group_names'])
 edges=q['edges'];skin=main_skin(edges,len(r));length=np.linalg.norm(r[edges[:,1]]-r[edges[:,0]],axis=1);adj=coo_matrix((np.r_[length,length],(np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(len(r),len(r))).tocsr()
 distance=dijkstra(adj,directed=False,indices=np.flatnonzero(skin&(ownership>=.35)),min_only=True)
 # Ownership gives a frozen set, not a smooth deformation weight. Surface
 # geodesic distance supplies a geometric C1 falloff without irregular skinweights.
 falloff=smooth(0,.35,distance)*skin
 mask=smooth(.95,1.08,z)*(1-smooth(1.30,1.53,z))*(1-smooth(.22,.36,abs(x)))*smooth(-1.2,-1.1,y)*(1-smooth(-.45,-.25,y))*falloff
 # Affine depth compression of each section preserves its curvature instead
 # of projecting the front vertices onto a flat target/cap.
 target=r.copy();target[:,1]+=.32*np.maximum(0,-.35-y)*mask
 target[:,0]-=.16*x*mask
 target[:,2]+=.055*smooth(.06,.25,abs(x))*mask
 protection=preserve_forelegs(r,target,q['weights'],q['group_names']);dest=root/'.runtime/art-direction/anatomy386-targets/rest197.npz';np.savez_compressed(dest,rest=r,target=target,mask=mask.astype(np.float32))
 report=dict(domain_preservation=protection,changed_vertices=int(np.any(target!=r,axis=1).sum()),max_delta=float(np.linalg.norm(target-r,axis=1).max()),scope='Rest form only; actual native neutral/raised/landing proof on liveoriginal rig required.Thedepth/taper strengths are proposed hypotheses, not historicalmeasurement/approval.')
 (root/'results/sikh386/rest197-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
