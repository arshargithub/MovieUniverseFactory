"""Static chest shape proof from the volume-derived guide, not tissue simulation.

Keep the guide's chest displacement only inside the actual ownership contract.
The189 guide's limb deformation is explicitly discarded; accepted forelegs are
source-exact. No physical or temporal claim is made from this construction.
"""
from pathlib import Path
import json
import numpy as np
from movie_factory.adapters.blender.anatomy_domain386 import foreleg_ownership,preserve_forelegs
from anatomy386_volume185 import smooth


def build(root):
 src=root/'.runtime/art-direction/anatomy386-targets/volume189-static339.npz';q=np.load(src,allow_pickle=False);own=np.load(root/'.runtime/factory-native/sikh386-appearance-c186-source/anatomy386-source.npz',allow_pickle=False);top=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False)
 weights=foreleg_ownership(own['weights'],own['group_names']);mask=q['mask']*(1-smooth(.05,.35,weights));target=q['source'].copy();target[126]+=((q['target'][126]-q['source'][126])*(1-smooth(.05,.35,weights))[:,None])
 domain=preserve_forelegs(q['source'],target,own['weights'],own['group_names']);faces=top['triangles'];faces=faces[np.any(mask[faces]>0,axis=1)];p=q['source'][126,faces];b=target[126,faces];n0=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);a0=np.linalg.norm(n0,axis=1);a=np.linalg.norm(n,axis=1);valid=a0>1e-8;cos=(n*n0).sum(1)/np.maximum(a*a0,1e-20);ratio=a/np.maximum(a0,1e-20)
 bad=valid&((cos<.05)|(ratio<.1)|(ratio>8))
 report=dict(method='Volume-derived chestshape only, ownership-limited corrective; NOT fullvolume simulation.',domain_preservation=domain,affected_triangles=len(faces),bad_surface_triangles=int(bad.sum()),min_normal_cos=float(cos[valid].min()),area_ratio_extrema=[float(ratio[valid].min()),float(ratio[valid].max())],max_delta=float(np.linalg.norm(target[126]-q['source'][126],axis=1).max()),scope='Only339corrected, otherposes exactplaceholders. Numericalsurface validity cannot establish supported anatomy or animation.')
 (root/'results/sikh386/scope192-numeric.json').write_text(json.dumps(report,indent=2)+'\n')
 if bad.any():raise ValueError('SCOPE192_INTERFACE_ORIENTATION')
 np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/scope192-static339.npz',source=q['source'],target=target,rest=q['rest'],mask=mask,times=q['times']);print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
