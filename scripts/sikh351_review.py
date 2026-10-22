"""Persist actual manual frame findings, never infer artistic approval from exit."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
cycle=int(sys.argv[1]);assert c.state(task)['cycle']==cycle
assert cycle in (56,57)
for view in ('back','front'):
 step='anatomy_custom_'+view
 run=pk.read_json(r,f'results/sikh351/{step}-run-c{cycle}.json')
 paths=[f'.runtime/factory-native/sikh351-c{cycle}-{step}/{name}' for name in ('frame-0283.png','frame.png','frame-0350.png')]
 evidence=dict(run['artifacts']);evidence.update({p:dict(path=p,sha256=pk.file_hash(r/p)) for p in paths})
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 diagnostics=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert not diagnostics['blocked_drivers'] and not diagnostics['known_source_defects']
 value=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=evidence,
  observation='All three actual poses inspected. Sharp rear elbow slit reduced, but spear-side upper arm remains flattened/tucked behind torso with abrupt shoulder junction. Front hides much of upper arm; not a plausible bare anatomical proof.',
  comparison='55 rest/native bend retain more plausible segment shape.56 plane transport improves local crease but does not establish a plausible integrated arm configuration.',
  open_defects=['Spear-side upper-arm/shoulder configuration remains implausible; garment construction blocked.'])
 if cycle==57:
  value.update(observation='All six front/back283/327/350 images inspected. Rear elbow is rounder and separated from torso, but front shows a severe shelf/crease where the upper arm joins shoulder, plus abrupt wrist transition. Adjacent regression is an unequivocal failure.',
   comparison='56 retained tucked arm;57 improves rear silhouette but worsens visible front shoulder. Neither passes matched native-bend control. Contact error below1e-6m is not anatomical validity.',
   open_defects=['Severe front shoulder crease across all three poses.','Wrist/forearm continuity remains unnatural.','Garment transfer, whole actor and crowd remain unqualified.'])
 Bridge(c).record_review(task,step,value)
 p=r/f'results/sikh351/{step}-visual-c{cycle}.json';assert not p.exists();p.write_text(json.dumps(value,indent=2)+'\n')
if cycle==56:
 print(c.replan(task,'GROUNDING','56 plane transport improves crease but preserves implausible elbow behind shoulder.57 tests anatomical down/out elbow placement with same wrist contact and hinge-plane method; no clothing concealment.','sikh351-c57-causal-replan')['cycle'])
else:
 s=c.replan(task,'GROUNDING','57 front shoulder regression and wrist discontinuity fail. Five351 corrections exhausted; preserve history. Next proposed proof must coordinate shoulder/elbow/wrist, diagnose skinning/weights against native pose controls before cloth. No further construction authority.','sikh351-exhausted')
 print({k:s[k] for k in ('stage','cycle','max_corrections')})
