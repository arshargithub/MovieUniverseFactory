"""Close the approved five-cycle continuation without an artistic admission."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE)
out=r/'results/sikh335/closure345';out.mkdir(exist_ok=True)
def write(name,value):
    p=out/name;text=json.dumps(value,indent=2)+'\n'
    if p.exists():assert p.read_text()==text
    else:p.write_text(text)
states={}
for task,limit in [('sikh335-supporting-appearance',42),('sikh335-continuous-performance',12)]:
    s=c.state(task);assert s['stage']=='REPLAN_REQUIRED' and s['cycle']==s['max_corrections']==limit
    states[task]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
write('controller-state.json',states)
packet=pk.read_json(r,'.runtime/knowledge-pilot213/sikh345-current.json')
paths=['results/sikh335/REASSESSMENT_345.md','results/sikh335/LEARNINGS_345.md',
       'results/sikh335/look01/rejection-c42.json','results/sikh335/look01/leader_front-visual-review-c41.json',
       'results/sikh335/look01/leader_contact-visual-review-c41.json','results/sikh335/look01/save-run-c39.json',
       'results/sikh335/look01/save-run-c40.json','results/sikh335/look01/save-run-c42.json']
evidence=[dict(path=p,sha256=pk.file_hash(r/p)) for p in paths]
checks=[dict(id=o['id'],kind=o['check_kind'],status='FAIL' if o['id'] in {'construction_interfaces','visual_gate','au_contact'} else 'NOT_RUN',
    action_taken='Preserved five attempts, actual visual failures and three technical/admission failures; withheld production handoff.',
    observation='Waist origin and shaft grip improve narrowly.41 still fails beard attachment, belt edge and wrist interface;42 combined repair fails before save. Complete original obligations remain unqualified.',evidence=evidence) for o in packet['obligations']]
write('knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Exhausted correction closure; not media admission',checks=checks,
    hypotheses=[dict(prediction='A single torso-only surface filter is sufficient for both belt and shoulder sash.',result='unresolved',
        observation='40 and42 missing surface rays disprove current implementation;41 removes arm strip but deforms waist edge.',
        response='Region-specific support and complete surface preflight before animation, within renewed authority.',evidence=evidence)],
    adjacent_regressions=dict(status='FAIL',observation='Restored beard detach and belt edge deformation remain; final proposed fixes lack saved image proof.',evidence=evidence),
    stopping_reason='Five shared345 additions consumed; no new authority, artistic pass or Director AV queue.'))
log=r/'.runtime/context-hygiene/runs/sikh345-final-tests/stdout.log'
write('verification.json',dict(tests=67,test_log=str(log.relative_to(r)),test_log_sha256=pk.file_hash(log),
    scope='Focused geometry and admission regression tests only; not native artistic or motion qualification.'))
print(json.dumps(states))
