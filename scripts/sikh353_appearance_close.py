"""Close actual appearance67 failure without consuming another allowance."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-supporting-appearance';s=c.state(t)
assert s['cycle']==s['max_corrections']==67
observations={
 'leader_front':'All283/288/327/350 inspected. Waist projecting strips remain removed and layered crown visible. Face/beard remain simplified, sash visibly kinks and does not read like convincingly supported cloth; whole costume remains below same-film bar. Source spear/right-hand pose does not establish performance. No artistic pass.',
 'leader_reverse':'All283/288/327/350 inspected. Waist breakthrough is improved, but sash lower edge still has a jagged/floating return and back cloth is too uniform. Horse/hem region partly occluded; cannot qualify it. No whole-interface pass.'}
for step,observation in observations.items():
 run=pk.read_json(r,f'results/sikh353/{step}-run-c67.json')
 v=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=run['artifacts'],observation=observation,comparison='Original supporting-actor same-film floor, not improvement over rejected predecessors.',open_defects=['Sash form/support','Whole face/costume/tack fidelity unqualified','Continuous motion not proven'])
 path=r/f'results/sikh353/{step}-visual-c67.json'
 if path.exists():assert json.loads(path.read_text())==v
 else:
  Bridge(c).record_review(t,step,v);path.write_text(json.dumps(v,indent=2)+'\n')
ev={step:dict(path=f'results/sikh353/{step}-visual-c67.json',sha256=pk.file_hash(r/f'results/sikh353/{step}-visual-c67.json')) for step in observations}
c.retrospective(t,'outcome',dict(attempt='353-c67-final-appearance',role='diagnostic',origin='actual-front-reverse-images',observations=[dict(requirement='form',status='FAIL',observation='Narrow waist/crown fixes do not qualify whole actor; sash and face/costume remain below floor.',foundation=True)],evidence=ev),'sikh353-c67-final-failure')
print(c.replan(t,'GROUNDING','Six authorized appearance corrections62–67 exhausted; actual front/reverse fail. Retain narrow improvements, no crowd propagation or ready handoff. Motion13–16 continues independently.','sikh353-appearance-exhausted')['stage'])
