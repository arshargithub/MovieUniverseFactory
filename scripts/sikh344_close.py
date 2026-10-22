"""Preserve the five shared corrections and their incomplete production result."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk,production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);out=r/'results/sikh335/closure344';out.mkdir(exist_ok=True)
def write(path,value):
    text=json.dumps(value,indent=2)+'\n'
    if path.exists():assert path.read_text()==text
    else:path.write_text(text)
task='sikh335-continuous-performance';s=c.state(task)
assert s['cycle']==s['max_corrections']==12
if s['stage']!='REPLAN_REQUIRED':
    reason='Motion12 narrowly corrects actual preimpact endpoint slowdown. Complete original performance remains unqualified and is blocked on rejected mounted appearance37 and crowd; no full-speed or integrated pass. Preserve successful trajectory evidence while replanning the remaining integrated proof; no additional correction authority.'
    write(r/'results/sikh335/motion01/incomplete-c12.json',dict(status='INCOMPLETE',narrow_trajectory='CORRECTED',reason=reason,evidence='results/sikh335/motion01/landing-review-c12.md'))
    d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,'sikh344-motion12-integrated-incomplete')
states={}
for name in ('sikh335-supporting-appearance','sikh335-continuous-performance'):
    state=c.state(name);assert state['stage']=='REPLAN_REQUIRED' and state['cycle']==state['max_corrections']
    states[name]={k:state[k] for k in ('stage','cycle','max_corrections','planning_step')}
assert states['sikh335-supporting-appearance']['cycle']==37
write(out/'controller-state.json',states)
packet=pk.read_json(r,'.runtime/knowledge-pilot213/sikh344-current.json')
paths=['results/sikh335/REASSESSMENT_344.md','results/sikh335/LEARNINGS_344.md',
 'results/sikh335/look01/rejection-c37.json','results/sikh335/look01/leader_front-visual-review-c37.json',
 'results/sikh335/look01/leader_reverse-visual-review-c37.json','results/sikh335/look01/render-visual-review-c37.json',
 'results/sikh335/motion01/landing-review-c12.md','results/sikh335/motion01/impact-metrics-c12.json']
evidence=[dict(path=p,sha256=pk.file_hash(r/p)) for p in paths]
checks=[dict(id=o['id'],kind=o['check_kind'],status='FAIL' if o['id'] in {'construction_interfaces','visual_gate'} else 'NOT_RUN',
 action_taken='Preserved actual scoped successes and known failures; withheld production handoff and ensemble propagation.',
 observation='Actual hoof arrival improves and garment coverage/ownership defects are repaired. Appearance37 whole actor and original isolated passage remain unqualified. Complete obligation status is not inferred from narrow tests.',evidence=evidence) for o in packet['obligations']]
write(out/'knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Exhausted shared correction closure, not media admission.',checks=checks,
 hypotheses=[dict(prediction='Layer binding alone will preserve visual clothing validity.',result='unresolved',observation='34 disproved sufficiency;35-37 body-aligned support recovered coverage, but whole mounted actor remains failed.',response='Preserve body-first dependency proof; finish remaining actual interfaces before crowd.',evidence=evidence)],
 adjacent_regressions=dict(status='FAIL',observation='Belt visibility recovered after36 skirt overlap regression; hand and complete film-level finish remain blocking.',evidence=evidence),
 stopping_reason='All five shared344 additions consumed. No further construction authority; no known-defect waiver or AV queue.'))
log=r/'.runtime/context-hygiene/runs/sikh344-final-nihang-tests/stdout.log'
write(out/'verification.json',dict(tests=90,test_log=str(log.relative_to(r)),test_log_sha256=pk.file_hash(log),scope='Focused native/geometry tests, not artistic or AV acceptance.'))
print(json.dumps(states))
