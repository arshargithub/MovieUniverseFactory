"""Normalize one proposed sculpt stroke to the admitted regional bound.

Global scaling preserves the proposed shape ratios. This is not a per-vertex
clamp, an inversion repair, a parameter sweep or an artistic qualification.
"""
from pathlib import Path
import json
import numpy as np
from movie_factory.adapters.blender.anatomy_rest386 import load

def build(root):
 q=np.load(root/'.runtime/art-direction/anatomy386-targets/rest197.npz',allow_pickle=False);d=q['target']-q['rest'];old=float(np.linalg.norm(d,axis=1).max());scale=min(1.,.17/old);target=q['rest']+d*scale
 dest=root/'.runtime/art-direction/anatomy386-targets/rest198.npz';np.savez_compressed(dest,rest=q['rest'],target=target,mask=q['mask'])
 import hashlib
 b=dict(path=str(dest.relative_to(root)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest());load(root,b,depth_only=False)
 report=dict(source_max=old,global_scale=scale,max_delta=float(np.linalg.norm(target-q['rest'],axis=1).max()),scope='Singleproposedstroke normalizedbeforeartproof; .18mconsumerbound unchanged, no pervertexclamp/knownshapeapproval.')
 (root/'results/sikh386/rest198-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
