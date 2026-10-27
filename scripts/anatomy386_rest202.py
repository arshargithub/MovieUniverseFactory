"""Revalidate the unchanged201 stroke after per-limb ownership classification fix."""
from pathlib import Path
import json,hashlib
import numpy as np
from movie_factory.adapters.blender.anatomy_domain386 import pectoral_domains,preserve_pectoral_interfaces
from movie_factory.adapters.blender.anatomy_rest386 import load


def build(root):
 q=np.load(root/'results/sikh386/rest201-proposal.npz',allow_pickle=False);s=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);w=s['weights'];names=[str(n) for n in s['group_names']]
 oldarm=w[:,[i for i,n in enumerate(names) if n.startswith('DEF-forearm.')]].sum(1);distal=w[:,[i for i,n in enumerate(names) if n.startswith(('DEF-forefoot.','DEF-f_toe.','DEF-f_hoof.'))]].sum(1);oldf=((oldarm>=.05)&(q['rest'][:,2]<=1.0))|(distal>=.05);newf,_=pectoral_domains(q['rest'],w,names)
 if not np.array_equal(oldf,newf):raise ValueError('REST202_FALLOFF_INPUT_CHANGED')
 protection=preserve_pectoral_interfaces(q['rest'],q['target'],q['rest'],w,names);dest=root/'.runtime/art-direction/anatomy386-targets/rest202.npz';np.savez_compressed(dest,rest=q['rest'],target=q['target'],mask=q['mask']);b=dict(path=str(dest.relative_to(root)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest());load(root,b,depth_only=False)
 report=dict(domain_preservation=protection,unchanged_201_field=True,unchanged_distal_falloff_set=True,max_delta=float(np.linalg.norm(q['target']-q['rest'],axis=1).max()),scope='Same201geometry, corrected per-limbdominanceclassification only. Actualnativeform andrig/worldproofNOT_RUN.')
 (root/'results/sikh386/rest202-numeric.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
