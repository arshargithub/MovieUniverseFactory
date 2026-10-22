"""Preserve exhausted correction evidence without admitting failed media."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk, production_workflow as wf
from movie_factory.task_router import DATABASE

root=Path(__file__).resolve().parents[1]
out=root/'results/sikh335/closure343'
out.mkdir(exist_ok=True)
def write(name,value):
    p=out/name
    text=json.dumps(value,indent=2)+'\n'
    if p.exists(): assert p.read_text()==text
    else: p.write_text(text)

c=wf.Controller(root,DATABASE)
states={}
for task in ('sikh335-supporting-appearance','sikh335-continuous-performance'):
    s=c.state(task)
    assert s['stage']=='REPLAN_REQUIRED' and s['cycle']==s['max_corrections']
    states[task]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
write('controller-state.json',states)
packet=pk.read_json(root,'.runtime/knowledge-pilot213/sikh343-current.json')
paths=['results/sikh335/REASSESSMENT_343.md',
       'results/sikh335/look01/rejection-c33.json',
       'results/sikh335/look01/leader_front-visual-review-c33.json',
       'results/sikh335/look01/leader_reverse-visual-review-c33.json',
       'results/sikh335/motion01/rejection-c11.json']
evidence=[{'path':p,'sha256':pk.file_hash(root/p)} for p in paths]
checks=[]
for item in packet['obligations']:
    checks.append(dict(id=item['id'],kind=item['check_kind'],
        status='FAIL' if item['id'] in {'construction_interfaces','visual_gate'} else 'NOT_RUN',
        action_taken='Preserved scoped prerequisites and actual failures; withheld integrated production handoff.',
        observation='Appearance33 front/reverse have garment intersections and unqualified anatomy/style. Motion11 actual hoof arrival still slows before impact. Other complete obligation checks are not established by this closure.',
        evidence=evidence))
write('knowledge-review.json',dict(packet_digest=packet['packet_digest'],
    scope='Exhausted production closure, not media admission or global knowledge calibration.',
    checks=checks,
    hypotheses=[dict(prediction='One shared body/garment armature will preserve layer coherence.',
        result='unresolved',observation='33 actual renders disprove sufficiency: rest-space support plus independent weights and modifiers do not preserve clearance.',
        response='Require actual posed layer/contact proof before full animation bake or crowd propagation.',evidence=evidence)],
    adjacent_regressions=dict(status='FAIL',observation='Crown recovered but cuffs, belt and sash remain visibly broken.',evidence=evidence),
    stopping_reason='All five shared additions consumed; both tasks REPLAN_REQUIRED. No known-failure waiver or AV queue.'))
write('verification.json',dict(tests=84,test_log='.runtime/context-hygiene/runs/sikh343-all-nihang-tests/stdout.log',
    test_log_sha256=pk.file_hash(root/'.runtime/context-hygiene/runs/sikh343-all-nihang-tests/stdout.log'),
    scope='Focused existing Nihang tests only; not artistic or performance acceptance.'))
print(json.dumps(states))
