"""Record actual inspected final controls, without an artistic admission."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1]
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
assert c.state(task)['cycle']==47
observations={
 'leader_contact':'283/327/350 actual close views reduce the severe wrist fold versus46, with visible fingers around shaft. Finger/skin finish remains simplified; all-frame wrist bend peaks53.28deg. Cuff and arm cannot pass independently of the reverse sleeve failure.',
 'leader_front':'283/327/350 front: beard cards remain attached and belt continuous. Face/eyes remain generic and smooth, turban reads as a regular shell, chola as a fitted body shell with inflated shoulders. Accepted Pashtun actual-450 has substantially richer integrated surfaces and anatomy.',
 'leader_reverse':'283/327/350 reverse: sash and waistband remain attached. New folded-arm pose reveals deep pinching and a dark pocket in sleeve elbow, especially327/350; shoulder form remains inflated. Reverse evidence vetoes whole-contact admission.',
 'render':'Actual production camera283/327/350: mounted assembly is readable but actor and saddle remain simplified. Horse surface still glossy/statue-like. No whole-shot same-film quality pass; these three stills cannot qualify rearing fluidity or audio.'
}
for step,observation in observations.items():
 run=pk.read_json(r,f'results/sikh335/look01/{step}-run-c47.json')
 assert run['status']=='RETURNED'
 evidence=dict(run['artifacts'])
 ref='.runtime/art-direction/series01-finish248/opening08/actual-450.png'
 evidence['accepted_co_star']={'path':ref,'sha256':pk.file_hash(r/ref)}
 verdict=dict(verdict='FAIL',run_digest=pk.digest(run),evidence=evidence,
  observation=observation,
  comparison='Actual images inspected at all three returned poses; accepted co-star is finish control, not identity. Improved predecessor is not acceptance. Full-speed AV remains NOT_RUN.',
  open_defects=['Whole actor same-film appearance unqualified','Sleeve elbow pinch in changed arm pose','Complete hand/cuff anatomy and all-frame performance unqualified','Horse/crowd and integrated isolated passage remain open'])
 Bridge(c).record_review(task,step,verdict)
 path=r/f'results/sikh335/look01/{step}-visual-review-c47.json'
 assert not path.exists();path.write_text(json.dumps(verdict,indent=2)+'\n')
print('Four actual-image FAIL reviews recorded; no artistic or AV pass.')
