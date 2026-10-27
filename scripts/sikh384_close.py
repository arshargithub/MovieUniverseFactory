"""Close failed bounded qualification honestly; retain all original-task history."""
import json,sqlite3
from pathlib import Path
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger,timestamp,union
r=Path(__file__).resolve().parents[1];o=r/'results/sikh384';task='sikh335-supporting-appearance';c=wf.Controller(r,DATABASE)
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
s=c.state(task);assert s['cycle']==176 and s['max_corrections']==176
db=sqlite3.connect(r/DATABASE);assert db.execute('select count(*) from heavy_job').fetchone()[0]==0
runs=[json.loads(x[0]) for x in db.execute("select record from native_runs where id like 'sikh384-%'")]
write('NATIVE_RUN_SUMMARY.json',dict(jobs=len(runs),returned=sum(x['status']=='RETURNED' for x in runs),failed=sum(x['status']=='FAILED' for x in runs),runs=[{k:x.get(k) for k in ['id','cycle','step','status','error','artifacts']} for x in runs],limits='Returned worker is not an artistic pass.168 blocked pre-reservation race is separate.'))
old=pk.read_json(r,'results/sikh383/PROTECTED_MASTERS_VERIFIED.json');protected=[]
for row in old['files']:
 actual=pk.file_hash(r/row['path']);assert actual==row['sha256'];protected.append(dict(path=row['path'],sha256=actual,matches_expected=True))
original=pk.read_json(r,'results/sikh383/appearance-c166-import-run.json')['artifacts']['native'];assert pk.file_hash(r/original['path'])==original['sha256'];protected.append(dict(**original,matches_expected=True))
write('PROTECTED_MASTERS_VERIFIED.json',dict(utc=datetime.now(timezone.utc).isoformat(),files=protected,scope='Fresh local streamed checksums; no remote backup claim.'))
l=Ledger(r/'.runtime/experiment-ops.sqlite3');ids={e['event_id'] for e in l.events()};jobs={}
for eid,utc,action in db.execute("select event_id,utc,action from events where event_id like 'native-%:sikh384-%' order by seq"):
 job=eid.split(':',1)[1];kind='job_started' if action=='job:acquire' else 'job_completed';key='sikh384-import-'+eid
 if key not in ids:l.append(dict(event_id=key,experiment_id='sikh335',episode_id='leader369',phase='adaptation',event_type=kind,job_id=job,utc=utc,note='Canonical native reservation timing; not CPU-only/render-only timing.'))
 jobs.setdefault(job,{})['start' if kind=='job_started' else 'end']=utc
start=next(e for e in l.events() if e['event_id']=='sikh384-work-start');end=dict(event_id='sikh384-work-end',experiment_id='sikh335',episode_id='leader369',phase='adaptation',event_type='work_ended',activity_id='sikh384-work',utc=datetime.now(timezone.utc).isoformat(),note='Ten-slot bare-head qualification failed; no production candidate or motion queue. Creative headpiece decision and new allowance required.');l.append(end)
l.append(dict(event_id='sikh384-next-direction',experiment_id='sikh335',episode_id='leader369',phase='adaptation',event_type='wait_started',wait_id='sikh384-next-direction',reason='director_response',utc=end['utc'],note='Director-owned intact headpiece versus further bare-head reconstruction choice; current176/176 exhausted.'))
intervals=[(timestamp(v['start']),timestamp(v['end'])) for v in jobs.values() if 'start'in v and 'end'in v]
write('OPERATING_CLOSEOUT.json',dict(start=start['utc'],end=end['utc'],recorded_elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),reservation_union_seconds=sum(b-a for a,b in union(intervals)),jobs=jobs,interval_rule='Native reservations overlap active work; never add them. No verified Director idle inside interval.',gaps=['Bootstrap before recorded work start','Final closeout records, local commits and handoff after work end'],engineering_subscription_usage=None,engineering_cost_usd=None,external_paid_calls=0,model_escalation=False))
ev={p:bind(p) for p in ['results/sikh384/CLOSEOUT.md','results/sikh384/appearance-c176-after_front-review.json','results/sikh384/appearance-c176-after_side-review.json','results/sikh384/appearance-c176-whole-review.json','results/sikh384/PROTECTED_MASTERS_VERIFIED.json','results/sikh384/OPERATING_CLOSEOUT.json']}
c.retrospective(task,'outcome',dict(attempt='384-final',role='diagnostic',origin='head-tack-qualification',observations=[dict(requirement='form',status='FAIL',observation='Actual complete176 close and whole pose family retains stretched planar neck web and projecting collar; reject bare-head conversion despite closed shared loops and clean face. Original intact donor remains protected.',reference_gap=False)],evidence=ev),'sikh384-final-failure')
packet=pk.read_json(r,'results/sikh384/packet176.json');status={k:'PASS' for k in ['authority','strategy','anticipation','stopping','versioning','economics','render_profile','cache_safety','rights','sikh_scope']}
for k in ['construction_interfaces','visual_gate','representation','anatomy','look','au_deformation','au_surface','au_reuse']:status[k]='FAIL'
review=dict(packet_digest=packet['packet_digest'],checks=[dict(id=q['id'],kind=q['check_kind'],status=status.get(q['id'],'NOT_RUN'),observation=('Current scoped process/technical records are present; source preservation and bounded authority checked. This is not a production or appearance pass.' if status.get(q['id'])=='PASS' else 'Actual head-neck form fails. Full-speed AV, deferred grooming/contact and complete production integration remain NOT_RUN; no known defect waiver.'),action_taken='Preserved failures and source, stopped downstream motion, recommend a concrete Director-owned intact-head direction decision.',evidence=list(ev.values())) for q in packet['obligations']],hypotheses=[dict(prediction='A coherent head can still fail the neck/body interface despite exact weights and closed topology.',observation='176 actual side/apex/descent show stretched planar web and collar; full framing confirms it.',response='Reject candidate and stop further automatic skin reconstruction; bring intact-head costume option to Director.',result='unresolved')],adjacent_regressions='Known wrong neck surface/material and projecting collar remain; original source masters hash-match. No whole-film or temporal pass.',stopping_reason='Exact ten-slot allowance exhausted and actual neck failure persists; requires creative direction/new scoped authority.')
write('evidence-review176.json',review);write('evidence-gate176.json',pk.check_review(r,packet,review))
c.revise(task,s['brief'],bind('results/sikh384/REQUEST.md'),'384 ten-slot head/tack qualification failed; visible neck web persists. Material intact-headpiece direction/new allowance required; no automatic continuation.','sikh384-final-exhausted')
write('final-state.json',{k:c.state(task)[k] for k in ['task','stage','cycle','max_corrections','production_approved']})
p=r/'.runtime/operating384/events.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps([e for e in l.events() if e['experiment_id']=='sikh335'],indent=2)+'\n');write('operating-export.json',dict(**bind(str(p.relative_to(r))),scope='Local export only.'))
print(json.dumps(dict(jobs=len(runs),cycle=176,max_corrections=176,stage=c.state(task)['stage'],evidence_gate='FAIL',source_masters_unchanged=True)))
