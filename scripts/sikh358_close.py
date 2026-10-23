"""Record allowance-boundary evidence; never certify artistic completion."""
import json
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as retro
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger,timestamp
r=Path(__file__).resolve().parents[1];o=r/'results/sikh358';c=wf.Controller(r,DATABASE)
def write(name,value):
    p=o/name;t=json.dumps(value,indent=2)+'\n'
    if p.exists():assert p.read_text()==t,name
    else:p.write_text(t)
def bind(path):return dict(path=path,sha256=pk.file_hash(r/path))
states={};retros={}
for t in ('sikh335-supporting-appearance','sikh335-continuous-performance'):
    s=c.state(t);states[t]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
    with c.connect() as con:events=retro.events(con,t)
    retros[t]=dict(counts=dict(Counter(x['kind'] for x in events)),projection=c.retrospective_packet(t))
assert states['sikh335-supporting-appearance']['cycle']==87
assert states['sikh335-continuous-performance']['stage']=='REPLAN_REQUIRED'
assert states['sikh335-continuous-performance']['cycle']==21
write('controller-close.json',states);write('retro-close.json',retros)
images=[]
for view in ('horse_head','horse_head_reverse'):
    run=pk.read_json(r,f'results/sikh358/appearance-c86-{view}-run.json')
    images.extend(v for k,v in run['artifacts'].items() if k.startswith('frame_'))
write('appearance86-component-audit.json',dict(status='COMPONENT_IMPROVEMENT_NOT_WHOLE_PASS',evidence=images,observation='Both sides283327350 inspected: supported crown/brow/cheeks/noseband and mouth rings improve anatomical tack; old rein interface remains unresolved. Whole actor, original rearing fidelity and full-speed AV are not qualified.',unexecuted=['86 production view','integrated full passage','Director AV']))
paths=['CLOSEOUT.md','LEARNINGS.md','CHECKPOINT_86.md','appearance86-component-audit.json','motion-c17-horse_head-review.json','motion-c18-inspect-technical.json','motion-c19-save-review.json','motion-c20-save-review.json','motion-c21-save-review.json']
evidence=[bind('results/sikh358/'+p) for p in paths]
passed={'authority','versioning','stopping','economics','current_state','sikh_scope'}
failed={'visual_gate','look','construction_interfaces','au_contact','anticipation','au_reuse'}
for label in ('appearance','motion'):
    packet=pk.read_json(r,f'results/sikh358/{label}-knowledge-packet.json')
    checks=[dict(id=x['id'],kind=x['check_kind'],status='PASS' if x['id'] in passed else 'FAIL' if x['id'] in failed else 'NOT_RUN',action_taken='Preserve exact five-per-task authority and previous unused appearance cycle. Internal candidate/technical reviews and causal replans retain failures. Motion exhausted21; appearance87 preserved.',observation='86 headstall useful;17 visible rein penetration;19–21 actual construction guards reject before save. No accepted integrated unit, full-speed AV or fresh off-device backup.',evidence=evidence) for x in packet['obligations']]
    write(f'{label}-knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Allowance-boundary audit, not production-media admission',checks=checks,hypotheses=[dict(prediction='Correct endpoints and a smoothly corrected old span can establish rein contact.',result='failed',observation='17 actual renders violate contact despite zero endpoint error;19–21 alternative routes remain unqualified.',response='Whole curve and thickness must be checked against actual animated surface; preserve failed controls and original limits.',evidence=evidence)],adjacent_regressions=dict(status='FAIL',observation='84 unsupported crown,85 cast failure,17 neck penetration and19–21 clearance failures preserved. Known failures block AV queue.',evidence=evidence),stopping_reason='Motion21/max21 exhausted; appearance87 remains for integrated proof after a separately authorized motion extension. No technical method approval requested.'))
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh358-*/runner-status.json')):
    v=json.loads(p.read_text());jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=v.get('elapsed'),exit_code=v.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),scope='Serial native occupancy overlaps work; not additive.'))
log=r/'.runtime/context-hygiene/runs/sikh358-tests-final/stdout.log';assert '261 passed' in log.read_text()
write('verification.json',dict(tests=261,**bind(str(log.relative_to(r))),scope='Software tests; not artistic or actual horse route qualification. Three closed-obstacle controls pass while actual native construction fails.'))
source='.runtime/factory-native/sikh358-appearance-c86-save/scene.blend'
write('retained-native.json',dict(**bind(source),status='WORKING_NOT_ACCEPTED',appearance_attempted=list(range(82,87)),appearance_remaining=[87],motion_attempted=list(range(17,22)),motion_limit=21,rejected_integration=bind('.runtime/factory-native/sikh358-motion-c17-save/scene.blend')))
ledger=Ledger(r/'.runtime/experiment-ops.sqlite3');events=ledger.events();start=next(e for e in events if e['event_id']=='sikh358-work-start');end=next((e for e in events if e['event_id']=='sikh358-work-end'),None)
if end is None:
    end=dict(event_id='sikh358-work-end',experiment_id='sikh335',episode_id='leader358',phase='construction',event_type='work_ended',activity_id='sikh358-work',utc=datetime.now(timezone.utc).isoformat(),note='Headstall86 retained; motion21 exhausted with actual rein-route clearance failure. Appearance87 unused; no production/media handoff.')
    ledger.append(end)
write('operating-interval.json',dict(events=[start,end],elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),verified_director_idle_seconds=0,lifecycle='OPEN',scope='Active work includes render waits; not additive.',gaps=['Bootstrap before work-start','Final records/commit/handoff after work-end']))
export=r/'.runtime/operating-sikh358-export';export.mkdir(exist_ok=True);p=export/'events.json';p.write_text(json.dumps([e for e in ledger.events() if e['experiment_id']=='sikh335'],indent=2)+'\n')
write('operating-export.json',dict(**bind(str(p.relative_to(r))),scope='Current experiment events; lifecycle OPEN.'))
print(states)
