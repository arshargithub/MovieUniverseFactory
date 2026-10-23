"""Actual354 evidence closure; preserves failed gate and open production."""
import json
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as retro
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger,timestamp
r=Path(__file__).resolve().parents[1];o=r/'results/sikh354';c=wf.Controller(r,DATABASE)
def write(name,v):
 p=o/name;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,name
 else:p.write_text(t)
states={};retros={}
for t,limit in [('sikh335-supporting-appearance',72),('sikh335-continuous-performance',16)]:
 s=c.state(t);assert s['cycle']==s['max_corrections']==limit and s['stage']=='REPLAN_REQUIRED'
 states[t]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
 with c.connect() as con:
  events=retro.events(con,t)
 retros[t]=dict(counts=dict(Counter(x['kind'] for x in events)),projection=c.retrospective_packet(t))
write('controller-close.json',states);write('retro-close.json',retros)
paths=['CLOSEOUT.md','LEARNINGS.md','RETRO_AUDIT.md','leader_face-visual-c68.json','save-visual-c69.json','production-visual-c70.json','leader_front-visual-c71.json','leader_face-visual-c72.json']
evidence=[dict(path='results/sikh354/'+p,sha256=pk.file_hash(o/p)) for p in paths]
packet=pk.read_json(r,'results/sikh354/appearance-knowledge-packet.json')
passed={'authority','versioning','stopping','economics','current_state','sikh_scope'}
failed={'visual_gate','look','strategy','au_surface','construction_interfaces','anatomy','au_deformation','au_contact','anticipation','au_reuse'}
checks=[dict(id=x['id'],kind=x['check_kind'],status='PASS' if x['id'] in passed else 'FAIL' if x['id'] in failed else 'NOT_RUN',action_taken='Five appearance corrections on original task; preserve motion16, inspect actual multi-view proofs and reject final facial regression.',observation='Sash/tack sampled improvements retained in71,72 face regresses. No whole leader/horse or AV qualification; crowd deferred and no external actions.',evidence=evidence) for x in packet['obligations']]
write('appearance-knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Exhaustion audit, not production-media admission',checks=checks,hypotheses=[dict(prediction='Changed beard lengths and face projection produce believable integrated hair.',result='failed',observation='72 exposes unnatural jaw/neck band.',response='Retain71; next true anatomical root domain and sparse guides before density.',evidence=evidence)],adjacent_regressions=dict(status='FAIL',observation='72 facial regression retained;70/71 useful sash/tack not overwritten as continuation base.',evidence=evidence),stopping_reason='Five corrections68–72 exhausted; no known-defect review-ready media handoff.'))
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh354-*/runner-status.json')):
 v=json.loads(p.read_text());jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=v.get('elapsed'),exit_code=v.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),scope='Serial native occupancy overlaps active interval, not additive; includes failures.'))
ledger=Ledger(r/'.runtime/experiment-ops.sqlite3');events=ledger.events();start=next(e for e in events if e['event_id']=='sikh354-work-start')
end=next((e for e in events if e['event_id']=='sikh354-work-end'),None)
if not end:
 end=dict(event_id='sikh354-work-end',experiment_id='sikh335',episode_id='leader354',phase='construction',event_type='work_ended',activity_id='sikh354-work',utc=datetime.now(timezone.utc).isoformat(),note='Five corrections exhausted, two useful interface subproofs; final facial regression rejected. Production open.')
 ledger.append(end)
interval=dict(events=[start,end],elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),verified_director_idle_seconds=0,lifecycle='OPEN',scope='Active interval includes native waits; no additive model time claim.',gaps=['Initial bootstrap before start','Final closure/commit/handoff after end'])
if (o/'operating-interval.json').exists():
 old=json.loads((o/'operating-interval.json').read_text());assert old['elapsed_seconds']==interval['elapsed_seconds']
 assert [(x['event_id'],x['utc']) for x in old['events']]==[(x['event_id'],x['utc']) for x in interval['events']]
else:write('operating-interval.json',interval)
log=r/'.runtime/context-hygiene/runs/sikh354-tests-final/stdout.log';assert '77 passed' in log.read_text()
write('verification.json',dict(tests=77,path=str(log.relative_to(r)),sha256=pk.file_hash(log),scope='Software tests, not art/AV.'))
export=r/'.runtime/operating-sikh354-export';export.mkdir(exist_ok=True)
ep=export/'events.json';et=json.dumps([e for e in ledger.events() if e['experiment_id']=='sikh335'],indent=2)+'\n'
if ep.exists():assert ep.read_text()==et
else:ep.write_text(et)
write('operating-export.json',dict(path=str(ep.relative_to(r)),sha256=pk.file_hash(ep),scope='Retained experiment events; current production lifecycle remains OPEN.'))
gate=r/'.runtime/knowledge-pilot213/sikh354-appearance-gate.json'
if gate.exists():write('appearance-knowledge-gate.json',dict(path=str(gate.relative_to(r)),sha256=pk.file_hash(gate),result=json.loads(gate.read_text()),scope='Exit2 retained; no media admission.'))
print(states)
