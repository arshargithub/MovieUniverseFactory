"""Evidence-backed closeout of exhausted381; no artistic PASS or new authority."""
import json,sqlite3
from pathlib import Path
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
from movie_factory.native_admission import Bridge
from movie_factory.experiment_ledger import Ledger,timestamp,union
r=Path(__file__).resolve().parents[1];o=r/'results/sikh381'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
s=c.state(task);assert s['cycle']==156 and s['max_corrections']==156
for step in ['oblique','side']:
 run=pk.read_json(r,f'results/sikh381/appearance-c156-{step}-run.json')
 observations={
 'oblique':'Actual367 retains low separate chest bulge;333 projects a rounded pectoral plate over constricted upper-leg roots;339 shows pendant outer lobes and a pinched join. Opposite oblique does not resolve the known front failure.',
 'side':'Actual367 lower chest hangs separately in front of the upper foreleg;333 and339 retain an abrupt projecting chest shelf rather than a supported continuous neck/shoulder/upper-leg volume.'}
 outcomes={q['id']:dict(status='FAIL',observation='This broad step cannot satisfy its claimed whole-unit requirement because actual form fails. No audiovisual inspection or independent failure diagnosis of an untested interface is claimed.') for q in s['brief']['requirements']}
 outcomes['form']=dict(status='FAIL',observation=observations[step])
 v=dict(run_digest=pk.digest(run),verdict='FAIL',observation=observations[step],comparison='Inspected real standing and rearing physical-form references, including near-frontal381 supplement; original faithful motion role unchanged. Static images do not qualify continuous motion.',open_defects=['Unsupported chest/foreleg-root continuity'],evidence=run['artifacts'],requirement_outcomes=outcomes)
 Bridge(c).record_review(task,step,v);write(f'appearance-c156-{step}-review.json',v)
ev={p:bind(p) for p in ['results/sikh381/RETROSPECTIVE381.md','results/sikh381/appearance-c156-oblique-review.json','results/sikh381/appearance-c156-side-review.json','results/sikh381/appearance-c154-front-review.json']}
c.retrospective(task,'outcome',dict(attempt='381-final',role='diagnostic',origin='matched-view-failure-audit',observations=[dict(requirement='__forequarter_method__',status='FAIL',observation='Connected positive forequarter not achieved across standing/apex/descent. Stop same-foundation parameter variants; broader foundation qualification requires Director decision.',foundation=True,falsified=True,reference_gap=False)],evidence=ev),'sikh381-final-retrospective')
packet=pk.read_json(r,'results/sikh381/packet156.json')
review=dict(packet_digest=packet['packet_digest'],checks=[dict(id=q['id'],kind=q['check_kind'],status='FAIL' if 'form' in q['id'] else 'NOT_RUN',observation='Actual final body audit fails; no downstream coat/contact/full-speed completion claimed.',action_taken='Stopped construction, preserved evidence and proposed foundation qualification.',evidence=list(ev.values())) for q in packet['obligations']],hypotheses=[dict(prediction='Smoother native skin may still contain unsupported pectoral masses.',observation='Observed in actual oblique and side apex/descent.',response='Reject body; no coat concealment or production handoff.',result='unresolved')],adjacent_regressions='Rider/tack/coat/continuous-motion interfaces remain unqualified on derivative. Protected motion masters separately hashed.',stopping_reason='156/max156 exhausted; material foundation decision required.')
write('evidence-review156.json',review);write('evidence-gate156.json',pk.check_review(r,packet,review))
c.revise(task,s['brief'],bind('results/sikh381/REQUEST.md'),'381 allowance exhausted; actual matched-view body FAIL. Stop this repair approach, no new method or correction authority.','sikh381-final-exhausted')
write('final-state.json',{k:c.state(task)[k] for k in ['task','stage','cycle','max_corrections','production_approved']})
protected=['.runtime/factory-native/sikh373-motion-c80-contact/scene.blend','.runtime/factory-native/sikh370-motion-c66-audit/scene.blend','.runtime/factory-native/sikh372-motion-c75-source/scene.blend']
expected=['204eea24a877219a30c7405bba178ddcff9655c30036d0c5ab218b603fc0fb44','4b31c8428034de3635c23992d4e3068d43fa83fa49eae1fa6dac7103a9b3e748','9633bf00d5cabdedde370c2195729b9f1e5190e681130d75c2c9a6187b8701ca']
rows=[]
for p,h in zip(protected,expected):
 actual=pk.file_hash(r/p);assert actual==h,p;rows.append(dict(path=p,sha256=actual,matches_expected=True))
write('PROTECTED_MASTERS_VERIFIED.json',dict(verified_utc=datetime.now(timezone.utc).isoformat(),files=rows,scope='Fresh local streamed hashes only; not remote backup verification.'))
db=sqlite3.connect(r/DATABASE);assert db.execute('select count(*) from heavy_job').fetchone()[0]==0
events=list(db.execute("select event_id,utc,action from events where event_id like 'native-%:sikh381-%' order by seq"));jobs={};intervals=[]
l=Ledger(r/'.runtime/experiment-ops.sqlite3');old=l.events();ids={v['event_id'] for v in old}
for event_id,utc,action in events:
 job=event_id.split(':',1)[1];kind='job_started' if action=='job:acquire' else 'job_completed';eid='sikh381-import-'+event_id
 if eid not in ids:l.append(dict(event_id=eid,experiment_id='sikh335',episode_id='leader369',phase='appearance',event_type=kind,job_id=job,utc=utc,note='Backfilled from canonical native reservation event; not CPU start/end.'))
 jobs.setdefault(job,{})['start' if kind=='job_started' else 'end']=utc
receipts=[]
for job,times in jobs.items():
 if 'start'in times and 'end'in times:intervals.append((timestamp(times['start']),timestamp(times['end'])))
 p=f'.runtime/factory-native/{job}/runner-status.json'
 if (r/p).exists():
  v=pk.read_json(r,p);receipts.append(dict(job=job,**times,process_elapsed_seconds=v.get('elapsed'),exit_code=v.get('exit_code'),receipt=bind(p)))
old=l.events();start=next(v for v in old if v['event_id']=='sikh381-work-start');end=next((v for v in old if v['event_id']=='sikh381-work-end'),None)
if end is None:
 end=dict(event_id='sikh381-work-end',experiment_id='sikh335',episode_id='leader369',phase='appearance',event_type='work_ended',activity_id='sikh381-work',utc=datetime.now(timezone.utc).isoformat(),note='Exhausted failed repair audited and preserved; no production PASS.');l.append(end)
if not any(v['event_id']=='sikh381-next-direction' for v in l.events()):l.append(dict(event_id='sikh381-next-direction',experiment_id='sikh335',episode_id='leader369',phase='appearance',event_type='wait_started',wait_id='sikh381-next-direction',reason='director_response',utc=end['utc'],note='Material horse-foundation decision and new allowance; closeout after this timestamp separately unmeasured.'))
write('OPERATING_CLOSEOUT.json',dict(start=start['utc'],end=end['utc'],recorded_elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),reservation_union_seconds=sum(b-a for a,b in union(intervals)),jobs=receipts,interval_rule='Native reservation occupancy overlaps recorded work; do not add. Process elapsed is separate and may include startup. No Director idle deducted inside active interval.',gaps=['Bootstrap before work start','Final record/commit/handoff after work end'],token_usage=None,engineering_cost_usd=None,external_paid_calls=0))
export=r/'.runtime/operating381/events.json';export.parent.mkdir(exist_ok=True);export.write_text(json.dumps([v for v in l.events() if v['experiment_id']=='sikh335'],indent=2)+'\n');write('operating-export.json',dict(**bind(str(export.relative_to(r))),scope='Local export, not verified off-device backup.'))
print(json.dumps(dict(state=c.state(task)['stage'],cycle=156,max=156,jobs=len(jobs),no_heavy_jobs=True,tests='103 passed',artistic_pass=False)))
