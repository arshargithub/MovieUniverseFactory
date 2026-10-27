"""Re-express the identical211rest goal against original184rest/skin source.

This is a source-preserving factorial control, not a new fitted shape.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from movie_factory.adapters.blender.anatomy_domain386 import preserve_pectoral_interfaces
from movie_factory.adapters.blender.anatomy_rest386 import load

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False)
    goal=np.load(root/'.runtime/art-direction/anatomy386-targets/rest211.npz',allow_pickle=False)['target']
    r=q['rest'];report=preserve_pectoral_interfaces(r,goal,r,q['weights'],q['group_names'],max_proximal=.15)
    path=root/'.runtime/art-direction/anatomy386-targets/rest213.npz';np.savez_compressed(path,rest=r,target=goal,mask=np.any(goal!=r,axis=1).astype(np.float32))
    binding=dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(path.read_bytes()).hexdigest());load(root,binding,depth_only=False)
    report.update(exact211target=True,max_original_delta=float(np.linalg.norm(goal-r,axis=1).max()),scope='Same actual anatomical goal as212, original raw184rest/skin mapping; only skin-attachment condition differs. No new goal/identity/action. Native factorial control NOT_RUN.')
    (root/'results/sikh386/rest213-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
