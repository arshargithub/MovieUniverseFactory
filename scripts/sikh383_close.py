"""Preserve qualification result and exhausted original task; never approve art."""
import json,sqlite3
from pathlib import Path
from datetime import datetime,timezone
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger,timestamp,union
r=Path(__file__).resolve().parents[1];o=r/'results/sikh383';task='sikh335-supporting-appearance';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
assert c.state(task)['cycle']==166 and c.state(task)['max_corrections']==166
for step in ['oblique','front','side']:
 run=pk.read_json(r,f'results/sikh383/appearance-c166-{step}-run.json')
 v=dict(run_digest=pk.digest(run),verdict='FAIL',observation='Actual7pose family reviewed. Chest/foreleg root is more connected than381; no old triangular web visible in sampled views. Full qualification remains incomplete: armor covers medial chest/head, strong frontal pectoral relief is not Director-accepted, coarse tail/reins/tack and complete contact/film integration remain open.',comparison='Real physical-form photos, original intended rear and actual381 failure controls. This supports a promising donor recommendation, not a bare-anatomy or complete production horse PASS.',open_defects=['Fused costume and hidden anatomy require adaptation proof','Full hoof/rider/tack/groom interfaces unqualified','Final film look/Director performance not accepted'],evidence=run['artifacts'])
 Bridge(c).record_review(task,step,v);write(f'appearance-c166-{step}-review.json',v)
for i in range(7):
 step=f'motion{i}';run=pk.read_json(r,f'results/sikh383/appearance-c166-{step}-run.json')
 v=dict(run_digest=pk.digest(run),verdict='PASS',observation='Actual returned timed-frame chunk/manifest bound and decoded; all92 unique frames present across chunks and encoded at24fps. Availability/coverage only, no motion-quality judgment.',comparison='Actual frames manifests versus admitted frame sets; repeated283 decoded pixels match across six duplicate controls, container metadata differs. No general replay claim.',open_defects=[],evidence=run['artifacts'],requirement_outcomes={rid:dict(status='NOT_TESTED',observation='Component byte/frame coverage only. Complete unit and direct temporal judgment not independently qualified.') for rid in ['evidence','director_form_motion']})
 Bridge(c).record_review(task,step,v);write(f'appearance-c166-{step}-review.json',v)
ev={p:bind(p) for p in ['results/sikh383/QUALIFICATION.md','results/sikh383/ENCODE_RECEIPT.json','results/sikh383/appearance-c166-front-review.json','results/sikh383/appearance-c166-side-review.json','results/sikh383/appearance-c166-oblique-review.json']}
c.retrospective(task,'outcome',dict(attempt='383-final',role='diagnostic',origin='alternative-foundation-qualification',observations=[dict(requirement='__warhorse383_qualification__',status='UNKNOWN',observation='Useful donor/body and retarget evidence; foundation not yet adopted. Fused head/tack adaptation and full contact/Director temporal judgment remain before production use.',reference_gap=False)],evidence=ev),'sikh383-final-retrospective')
packet=pk.read_json(r,'results/sikh383/packet166.json');review=dict(packet_digest=packet['packet_digest'],checks=[dict(id=q['id'],kind=q['check_kind'],status='NOT_RUN',observation='Qualification result only, known unfinished armor/contact/groom and no independent direct AV judgment; no complete production pass.',action_taken='Preserved source/candidate evidence and concrete head/tack proof recommendation; no automatic adoption.',evidence=list(ev.values())) for q in packet['obligations']],hypotheses=[dict(prediction='Cleaner body may still have uneconomic fused costume and retarget contacts.',observation='Fused main mesh and actual contact adaptation confirmed; helmet removal remains unproven.',response='Require head/tack separation proof before production commitment.',result='unresolved')],adjacent_regressions='Source transforms retained; new tail/reins/rider/forefoot/hill interfaces remain unqualified.',stopping_reason='Ten authorized slots157..166 used; integrated appearance remains unaccepted. Qualification evidence supports a material foundation decision.')
write('evidence-review166.json',review);write('evidence-gate166.json',pk.check_review(r,packet,review))
s=c.state(task);c.revise(task,s['brief'],bind('results/sikh383/REQUEST.md'),'383 ten-slot qualification completed; original appearance remains unqualified. Foundation/head-tack decision and new scope/allowance required. No silent adoption.','sikh383-final-exhausted')
write('final-state.json',{k:c.state(task)[k] for k in ['task','stage','cycle','max_corrections','production_approved']})
protected=[('.runtime/factory-native/sikh373-motion-c80-contact/scene.blend','204eea24a877219a30c7405bba178ddcff9655c30036d0c5ab218b603fc0fb44'),('.runtime/factory-native/sikh370-motion-c66-audit/scene.blend','4b31c8428034de3635c23992d4e3068d43fa83fa49eae1fa6dac7103a9b3e748'),('.runtime/factory-native/sikh372-motion-c75-source/scene.blend','9633bf00d5cabdedde370c2195729b9f1e5190e681130d75c2c9a6187b8701ca'),('.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4','1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b')]
rows=[]
for p,h in protected:
 actual=pk.file_hash(r/p);assert actual==h,p;rows.append(dict(path=p,sha256=actual,matches_expected=True))
write('PROTECTED_MASTERS_VERIFIED.json',dict(utc=datetime.now(timezone.utc).isoformat(),files=rows,scope='Fresh local streamed hash verification, not remote backup.'))
db=sqlite3.connect(r/DATABASE);assert db.execute('select count(*) from heavy_job').fetchone()[0]==0
l=Ledger(r/'.runtime/experiment-ops.sqlite3');ids={e['event_id'] for e in l.events()};jobs={}
for eid,utc,action in db.execute("select event_id,utc,action from events where event_id like 'native-%:sikh383-%' order by seq"):
 job=eid.split(':',1)[1];kind='job_started' if action=='job:acquire' else 'job_completed';key='sikh383-import-'+eid
 if key not in ids:l.append(dict(event_id=key,experiment_id='sikh335',episode_id='leader369',phase='qualification',event_type=kind,job_id=job,utc=utc,note='Backfilled canonical reservation timing, not CPU timing.'))
 jobs.setdefault(job,{})['start' if kind=='job_started' else 'end']=utc
start=next(e for e in l.events() if e['event_id']=='sikh383-work-start');end=next((e for e in l.events() if e['event_id']=='sikh383-work-end'),None)
if end is None:
 end=dict(event_id='sikh383-work-end',experiment_id='sikh335',episode_id='leader369',phase='qualification',event_type='work_ended',activity_id='sikh383-work',utc=datetime.now(timezone.utc).isoformat(),note='Alternative donor qualification evidence preserved; not production-ready or adopted.');l.append(end)
if 'sikh383-next-direction'not in ids:l.append(dict(event_id='sikh383-next-direction',experiment_id='sikh335',episode_id='leader369',phase='qualification',event_type='wait_started',wait_id='sikh383-next-direction',reason='director_response',utc=end['utc'],note='Material candidate/head-tack direction and new allowance after exhausted trial.'))
intervals=[(timestamp(v['start']),timestamp(v['end'])) for v in jobs.values() if 'start'in v and 'end'in v]
write('OPERATING_CLOSEOUT.json',dict(start=start['utc'],end=end['utc'],recorded_elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),reservation_union_seconds=sum(b-a for a,b in union(intervals)),jobs=jobs,process_receipts=bind('results/sikh383/NATIVE_RUN_SUMMARY.json'),interval_rule='Native reservations overlap active work, never add them. No verified Director idle inside interval.',gaps=['Bootstrap before work start','Closeout record/commit/handoff after work end'],token_usage=None,engineering_cost_usd=None,external_paid_calls=0))
p=r/'.runtime/operating383/events.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps([e for e in l.events() if e['experiment_id']=='sikh335'],indent=2)+'\n');write('operating-export.json',dict(**bind(str(p.relative_to(r))),scope='Local ledger export, not off-device protection.'))
print(json.dumps(dict(stage=c.state(task)['stage'],cycle=166,max=166,qualified_for_production=False,protected_sources_match=True,jobs=len(jobs))))
