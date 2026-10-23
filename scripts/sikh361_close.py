"""Preserve actual boundary evidence, including failed gates; no artistic pass."""
import json
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as retro
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger,timestamp
r=Path(__file__).resolve().parents[1];o=r/'results/sikh361';c=wf.Controller(r,DATABASE)
def bind(path):return dict(path=path,sha256=pk.file_hash(r/path))
def write(name,value):
    path=o/name;text=json.dumps(value,indent=2)+'\n'
    if path.exists():assert path.read_text()==text,name
    else:path.write_text(text)
states={};retros={}
for task in ('sikh335-supporting-appearance','sikh335-continuous-performance'):
    s=c.state(task);states[task]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
    with c.connect() as con:events=retro.events(con,task)
    retros[task]=dict(counts=dict(Counter(e['kind'] for e in events)),projection=c.retrospective_packet(task))
assert states['sikh335-supporting-appearance']['stage']=='REPLAN_REQUIRED'
assert states['sikh335-supporting-appearance']['cycle']==97
assert states['sikh335-continuous-performance']['cycle']==25
with c.connect() as con:assert not con.execute('SELECT 1 FROM heavy_job').fetchone()
write('controller-close.json',states);write('retro-close.json',retros)
write('retained-native.json',dict(status='WORKING_COMPONENT_NOT_WHOLE_ACCEPTANCE',native=bind('.runtime/factory-native/sikh361-motion-c24-save/scene.blend'),rejected_appearance=bind('.runtime/factory-native/sikh361-appearance-c95-save/scene.blend'),appearance_native_attempts=list(range(87,97)),appearance97='PLANNING_REJECTION_NO_WORKER',motion_attempts=[22,23,24],motion_remaining=list(range(25,32)),prepared_seam_repair='NOT_RUN_NATIVELY',continuous_template='NOT_ADMITTED_NOT_RENDERED'))
jobs=[]
for path in sorted((r/'.runtime/factory-native').glob('sikh361-*/runner-status.json')):
    value=json.loads(path.read_text());jobs.append(dict(**bind(str(path.relative_to(r))),elapsed=value.get('elapsed'),exit_code=value.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,count=len(jobs),summed_process_seconds=sum(j['elapsed'] for j in jobs if isinstance(j['elapsed'],(int,float))),scope='Serial native occupancy overlaps active work; not additive or complete turn time.'))
paths=['CLOSEOUT.md','LEARNINGS.md','CHECKPOINT_91.md','PREFLIGHT_97.md','MOTION24_REVIEW.md','controller-close.json','retained-native.json','appearance-c95-leader_reverse-review.json','appearance-c96-save-review.json','appearance-c97-challenge.json']
evidence=[bind('results/sikh361/'+p) for p in paths]
passed={'authority','strategy','stopping','versioning','economics','current_state','sikh_scope','reuse_envelope'}
failed={'construction_interfaces','visual_gate','anticipation','look','au_contact','au_surface','au_reuse'}
for label in ('appearance','motion'):
    packet=pk.read_json(r,f'results/sikh361/{label}-knowledge-packet.json')
    checks=[dict(id=item['id'],kind=item['check_kind'],status='PASS' if item['id'] in passed else 'FAIL' if item['id'] in failed else 'NOT_RUN',action_taken='Retain original authority/history, reject known source/frame failures and preflight-invalid97. Preserve useful motion24 and prepare unexecuted seam fix; no media handoff.',observation='Rein component improves; dressed-layer appearance remains unqualified. Appearance97 exhausted, motion25..31 retained. No full-speed AV/audio or new backup qualification.',evidence=evidence) for item in packet['obligations']]
    write(label+'-knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Allowance-boundary failure audit, not production-media admission',checks=checks,hypotheses=[dict(prediction='Coat contact and a supported band suffice for the dressed waist.',result='failed',observation='95 numerical coat contact succeeds but actual blue skirt occlusion remains;96 identifies the additional consumers.',response='Compile layer interfaces before fitting; prepare97 support-domain repair without dispatch beyond limit.',evidence=evidence)],adjacent_regressions=dict(status='FAIL',observation='Rejected lock groom, proxy/cap/projection failures and skirt/band occlusion preserved. Known failures prohibit an AV queue.',evidence=evidence),stopping_reason='Original appearance task at97/max97 after preflight rejection; request four further appearance corrections. Motion allowance retained, no cap reset or new authority assumed.'))
log='.runtime/context-hygiene/runs/sikh361-final-controls/stdout.log';assert '229 passed' in (r/log).read_text()
write('verification.json',dict(tests=229,**bind(log),scope='Software controls only; seam and whole character NOT_RUN/unqualified.'))
ledger=Ledger(r/'.runtime/experiment-ops.sqlite3');events=ledger.events();start=next(e for e in events if e['event_id']=='sikh361-work-start');end=next((e for e in events if e['event_id']=='sikh361-work-end'),None)
if end is None:
    end=dict(event_id='sikh361-work-end',experiment_id='sikh335',episode_id='leader361',phase='construction',event_type='work_ended',activity_id='sikh361-work',utc=datetime.now(timezone.utc).isoformat(),note='Rein24 retained; appearance97 limit reached. Prepared code not run. No production-media handoff.')
    ledger.append(end)
write('operating-interval.json',dict(events=[start,end],elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),verified_director_idle_seconds=0,lifecycle='OPEN',scope='Active work includes render waits; exact full-turn net time UNKNOWN.',gaps=['Bootstrap before recorded work start','Final gate checks, commit and handoff after recorded work end']))
export=r/'.runtime/operating-sikh361-export';export.mkdir(exist_ok=True);path=export/'events.json';path.write_text(json.dumps([e for e in ledger.events() if e['experiment_id']=='sikh335'],indent=2)+'\n');write('operating-export.json',dict(**bind(str(path.relative_to(r))),scope='Current experiment remains OPEN; not archive or backup verification.'))
print(states);print('Native jobs:',len(jobs))
