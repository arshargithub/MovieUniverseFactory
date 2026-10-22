"""Evidence-backed exhaustion record. Not a production/AV admission."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh351';c=wf.Controller(r,DATABASE)
def write(name,value):
 p=out/name;content=json.dumps(value,indent=2)+'\n'
 if p.exists():assert p.read_text()==content
 else:p.write_text(content)
states={}
for task,limit in [('sikh335-supporting-appearance',57),('sikh335-continuous-performance',12)]:
 s=c.state(task);assert s['cycle']==s['max_corrections']==limit
 states[task]={k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
write('controller-close.json',states)
paths=['results/sikh351/CLOSEOUT.md','results/sikh351/DIAGNOSIS.md','results/sikh351/DIAGNOSIS57.md']
paths += [f'results/sikh351/anatomy_custom_{v}-visual-c{n}.json' for n in (56,57) for v in ('front','back')]
ev=[dict(path=p,sha256=pk.file_hash(r/p)) for p in paths]
packet=pk.read_json(r,'results/sikh351/knowledge-packet.json')
failed={'anatomy','visual_gate','au_deformation','construction_interfaces','au_contact','au_surface','look'}
passed={'authority','strategy','versioning','stopping','economics','current_state','cache_safety','render_profile'}
checks=[dict(id=o['id'],kind=o['check_kind'],status='FAIL' if o['id'] in failed else 'PASS' if o['id'] in passed else 'NOT_RUN',
 action_taken='Preserved limits and source masters; isolated bare anatomy before clothing; inspected all six actual poses per candidate and rejected both. No crowd propagation or production handoff.',
 observation='57/max57 exhausted. Visible shoulder and wrist defects remain. Procedural PASS is limited to preserved authority/evidence/local resource scope, never appearance or AV.',evidence=ev) for o in packet['obligations']]
write('knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Exhaustion audit, not media admission',checks=checks,
 hypotheses=[dict(prediction='Rest-plane transport with fixed hands yields credible whole arm.',result='failed',observation='56 reduces slit but upper arm remains tucked;57 elbow placement causes front shoulder shelf and wrist kink.',response='Coordinated arm/contact plus skinning control proposed; no further authority.',evidence=ev)],
 adjacent_regressions=dict(status='FAIL',observation='57 rear improvement accompanied by front shoulder regression; retained and rejected.',evidence=ev),
 stopping_reason='All five additional corrections consumed, appearance57/max57; motion12 unchanged. New authority required; no known-defect waiver.'))
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh351-*/runner-status.json')):
 d=json.loads(p.read_text());jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=d.get('elapsed'),exit_code=d.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),scope='Serial worker occupancy including failures; overlaps active work and is not additive to it. Not Director idle or model-only time.'))
log=r/'.runtime/context-hygiene/runs/sikh351-tests-qualified/stdout.log'
write('verification.json',dict(tests=102,path=str(log.relative_to(r)),sha256=pk.file_hash(log),scope='Focused software tests, not art/AV qualification.'))
print(states)
