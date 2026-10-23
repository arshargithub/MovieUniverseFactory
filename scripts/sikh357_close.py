"""Scoped authority-boundary close; never converts technical evidence into art pass."""
import json
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as retro
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger,timestamp
r=Path(__file__).resolve().parents[1];o=r/'results/sikh357';c=wf.Controller(r,DATABASE)
def write(name,value):
    p=o/name;text=json.dumps(value,indent=2)+'\n'
    if p.exists():assert p.read_text()==text,name
    else:p.write_text(text)
states={};retros={}
for t in ('sikh335-supporting-appearance','sikh335-continuous-performance'):
    s=c.state(t);states[t]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
    with c.connect() as con:events=retro.events(con,t)
    retros[t]=dict(counts=dict(Counter(x['kind'] for x in events)),projection=c.retrospective_packet(t))
assert states['sikh335-supporting-appearance']['cycle']==82
assert states['sikh335-continuous-performance']['max_corrections']==16
write('controller-close.json',states);write('retro-close.json',retros)
paths=['CLOSEOUT.md','LEARNINGS.md','CHECKPOINT_77.md','leader_face-visual-c73.json','leader_face-visual-c74.json','leader_face-visual-c75.json','leader_face-visual-c76.json','leader_front-visual-c77.json','leader_reverse-visual-c78.json','leader_reverse-visual-c79.json','horse_head-visual-c80.json','horse_head-visual-c81.json']
evidence=[dict(path='results/sikh357/'+p,sha256=pk.file_hash(o/p)) for p in paths]
packet=pk.read_json(r,'results/sikh357/appearance-knowledge-packet.json')
passed={'authority','versioning','stopping','economics','current_state','sikh_scope'}
failed={'visual_gate','look','construction_interfaces','au_contact','anticipation','au_reuse'}
checks=[dict(id=x['id'],kind=x['check_kind'],status='PASS' if x['id'] in passed else 'FAIL' if x['id'] in failed else 'NOT_RUN',action_taken='Nine actual candidates73–81 reviewed; checkpoint77 retained;82 remains unused while integrated tack/rein repair needs separate motion allowance.',observation='Face/cloth/coat component improvements retained; new inherited tack attachment defect blocks whole unit. Motion16 unchanged, no direct AV or production pass.',evidence=evidence) for x in packet['obligations']]
write('appearance-knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Authority-boundary audit, not production-media admission',checks=checks,hypotheses=[dict(prediction='Complete visible horse surface can be qualified with shader/shape refinements.',result='failed',observation='Close head control additionally exposes inherited tack attachment error, while80 regressed authored texture reuse.',response='Retain81 surface, repair actual headstall and consuming rein trajectory together under correct authority.',evidence=evidence)],adjacent_regressions=dict(status='FAIL',observation='74 ribbons,75 sheet and80 glossy/reuse regression retained as failures;81 is working source, not artistic approval.',evidence=evidence),stopping_reason='One appearance cycle remains; integrated contact repair needs motion extension beyond16/16, requested but not assumed.'))
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh357-*/runner-status.json')):
    v=json.loads(p.read_text());jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=v.get('elapsed'),exit_code=v.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),scope='Serial native occupancy overlaps active work interval; not additive.'))
ledger=Ledger(r/'.runtime/experiment-ops.sqlite3');events=ledger.events();start=next(e for e in events if e['event_id']=='sikh357-work-start');end=next((e for e in events if e['event_id']=='sikh357-work-end'),None)
if end is None:
    end=dict(event_id='sikh357-work-end',experiment_id='sikh335',episode_id='leader357',phase='construction',event_type='work_ended',activity_id='sikh357-work',utc=datetime.now(timezone.utc).isoformat(),note='Nine appearance candidates complete; one unused. Integrated tack/rein repair needs separate motion extension; no production handoff.')
    ledger.append(end)
write('operating-interval.json',dict(events=[start,end],elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),verified_director_idle_seconds=0,lifecycle='OPEN',scope='Active work includes render waits, not additive.',gaps=['Initial bootstrap before work-start','Final closure/commit/handoff after work-end']))
log=r/'.runtime/context-hygiene/runs/sikh357-tests-final/stdout.log';assert '203 passed' in log.read_text()
write('verification.json',dict(tests=203,path=str(log.relative_to(r)),sha256=pk.file_hash(log),scope='Software checks only, not visual/AV.'))
source=r/'.runtime/factory-native/sikh357-c81-save/scene.blend'
write('retained-native.json',dict(path=str(source.relative_to(r)),sha256=pk.file_hash(source),status='WORKING_NOT_ACCEPTED',appearance_completed=list(range(73,82)),appearance_remaining=[82],motion_limit=16))
export=r/'.runtime/operating-sikh357-export';export.mkdir(exist_ok=True);p=export/'events.json';p.write_text(json.dumps([e for e in ledger.events() if e['experiment_id']=='sikh335'],indent=2)+'\n')
write('operating-export.json',dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),scope='Current experiment event export; lifecycle OPEN.'))
print(states)
