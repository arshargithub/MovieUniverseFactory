"""Preserve the exhausted346 correction record without passing production."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk, production_workflow as wf
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE)
out=r/'results/sikh335/closure346';out.mkdir(exist_ok=True)
def write(name,value):
 p=out/name;text=json.dumps(value,indent=2)+'\n'
 if p.exists():assert p.read_text()==text
 else:p.write_text(text)
states={}
for task,limit in [('sikh335-supporting-appearance',47),('sikh335-continuous-performance',12)]:
 s=c.state(task);assert s['stage']=='REPLAN_REQUIRED' and s['cycle']==s['max_corrections']==limit
 states[task]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
write('controller-state.json',states)
paths=['results/sikh335/REASSESSMENT_346.md','results/sikh335/LEARNINGS_346.md',
 'results/sikh335/look01/rejection-c47.json']
paths += [f'results/sikh335/look01/{v}-visual-review-c47.json' for v in ('leader_front','leader_reverse','leader_contact','render')]
evidence=[dict(path=p,sha256=pk.file_hash(r/p)) for p in paths]
packet=pk.read_json(r,'.runtime/knowledge-pilot213/sikh346-current.json')
checks=[dict(id=o['id'],kind=o['check_kind'],status='FAIL' if o['id'] in
 {'construction_interfaces','visual_gate','au_contact','au_surface','au_deformation'} else 'NOT_RUN',
 action_taken='Preserved five corrections, rejected final actual four-view controls and withheld production/crowd handoff.',
 observation='Regional layer and beard repairs advanced; final coupled arm exposes sleeve pinch. Whole actor and production horse remain below established finish. No complete passage or audiovisual qualification.',
 evidence=evidence) for o in packet['obligations']]
write('knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Exhausted correction closure, not media admission',checks=checks,
 hypotheses=[dict(prediction='Correct bone-frame roll alone removes the visible wrist fold.',result='failed',
 observation='46 actual contact images still fail.47 coupling removes the worst fold but exposes sleeve deformation.',
 response='Whole mounted actor and genuine garment form must constrain the next package from its first proof.',evidence=evidence)],
 adjacent_regressions=dict(status='FAIL',observation='New elbow pose pinches sleeve; face/crown/coat/saddle and horse finish remain unqualified.',evidence=evidence),
 stopping_reason='Five shared346 corrections consumed at appearance47. No artistic pass or AV queue. Renewed correction authority required.'))
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh346-*/runner-status.json')):
 d=json.loads(p.read_text());jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=d.get('elapsed'),exit_code=d.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),
 summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),
 scope='Serial native process occupancy including failed startup; not total agent work or Director idle time.'))
log=r/'.runtime/context-hygiene/runs/sikh346-tests-final/stdout.log'
write('verification.json',dict(tests=53,test_log=str(log.relative_to(r)),test_log_sha256=pk.file_hash(log),
 scope='Focused geometry and admission regressions, not artistic or audiovisual qualification.'))
print(json.dumps(states))
