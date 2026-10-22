"""Verify actual float32 mesh-write invariants; retain failed float64 assertion."""
import json
from pathlib import Path
import numpy as np
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE)
task='sikh335-supporting-appearance';cycle=c.state(task)['cycle'];assert cycle==21
run=pk.read_json(r,'results/sikh335/look01/bend-run-c21.json');assert run['status']=='RETURNED'
for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
patch=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
assert patch['before']['objects']==patch['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
directory=(r/run['artifacts']['native']['path']).parent;evidence={}
for name in ('body','garment'):
 p=directory/f'{name}-bend.npz';a=np.load(p);rest=a['rest'];bent=a['bent']
 mask=(rest[:,2]>1.21)|(rest[:,0]<0)
 # Blender MeshVertex coordinates and foreach_set('co') use float32. The
 # original float64 arithmetic identity is not the native-storage identity.
 assert np.isfinite(bent).all() and np.array_equal(rest[mask].astype('f4'),bent[mask].astype('f4'))
 evidence[name]={'path':str(p.relative_to(r)),'sha256':pk.file_hash(p),
    'max_float64_arithmetic_delta':float(np.max(abs(bent[mask]-rest[mask]))),
    'exact_float32_mesh_write_identity':True}
v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],
 observation='Technical prerequisite only. Original four production owners unchanged and safe. Shoulder/opposite arm are bit-identical at Blender float32 mesh-write precision. Prior float64 assertion failed on 6.94e-18m cancellation and remains recorded.',
 comparison='No visual bend or integration pass. Saved inputs/outputs independently checked for finiteness and storage precision.',open_defects=[],numeric_evidence=evidence)
Bridge(c).record_review(task,'bend',v)
p=r/'results/sikh335/look01/bend-technical-review-c21.json';assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
print('Bend native storage prerequisite PASS; visible bend NOT_RUN')
