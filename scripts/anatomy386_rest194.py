"""Curvature-preserving depth correction on the coherent raw neutral chest.

A proposed22%anterior-depth correction, not a measured or Director-approved
proportion. Spatial/physical references govern supported form; native proof
must decide whether this modest rest hypothesis is an improvement.
"""
from pathlib import Path
import json
import numpy as np
from anatomy386_volume185 import smooth
from movie_factory.adapters.blender.anatomy_domain386 import foreleg_ownership,preserve_forelegs

def build(root):
 q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz');r=q['rest'];x,y,z=r.T;ownership=foreleg_ownership(q['weights'],q['group_names'])
 mask=smooth(.95,1.1,z)*(1-smooth(1.5,1.75,z))*(1-smooth(.22,.36,abs(x)))*smooth(-1.2,-1.1,y)*(1-smooth(-.45,-.25,y))*(1-smooth(.05,.35,ownership))
 # Affine depth compression of each section preserves its curvature instead
 # of projecting the front vertices onto a flat target/cap.
 target=r.copy();target[:,1]+=.22*np.maximum(0,-.35-y)*mask
 protection=preserve_forelegs(r,target,q['weights'],q['group_names']);dest=root/'.runtime/art-direction/anatomy386-targets/rest194.npz';np.savez_compressed(dest,rest=r,target=target,mask=mask.astype(np.float32))
 report=dict(domain_preservation=protection,changed_vertices=int(np.any(target!=r,axis=1).sum()),max_delta=float(np.linalg.norm(target-r,axis=1).max()),scope='Rest form only; actual native neutral/raised/landing proof on liveoriginal rig required.22%is proposed test strength, not historicalmeasurement/approval.')
 (root/'results/sikh386/rest194-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
