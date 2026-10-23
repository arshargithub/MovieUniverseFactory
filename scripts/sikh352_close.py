"""Close four authorized corrections with scoped evidence, never media approval."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

r=Path(__file__).resolve().parents[1];out=r/'results/sikh352'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
s=c.state(task);assert s['cycle']==s['max_corrections']==61
def write(name,value):
 p=out/name;content=json.dumps(value,indent=2)+'\n'
 if p.exists():assert p.read_text()==content
 else:p.write_text(content)
if s['stage']=='EXECUTING':
 observations={
  'leader_front':('FAIL','All four front samples283/288/327/350 inspected: prior elbow poke absent but waist band projects as rigid strips with lobed lower edge.'),
  'leader_reverse':('FAIL','Only reverse327 inspected at closure: long waist strips visible on both sides. Other rendered samples not claimed reviewed.'),
  'leader_contact':('NOT_RUN','Only contact327 inspected at closure: closed spear grip maintained, irregular/open cuff edge visible. Full contact set not reviewed; whole interface remains unqualified.')}
 for step,(verdict,observation) in observations.items():
  run=pk.read_json(r,f'results/sikh352/{step}-run-c61.json')
  v=dict(verdict=verdict,run_digest=pk.digest(run),evidence=run['artifacts'],observation=observation,
   comparison='Retained59 bare-arm scaffold and60 fabric volume; no improvement waives interface regression or whole-actor quality.',
   open_defects=['Projecting waist band','Whole garment and actor appearance unqualified','Full-speed performance not qualified by static controls'])
  Bridge(c).record_review(task,step,v);write(f'{step}-visual-c61.json',v)
 ev={p:dict(path=p,sha256=pk.file_hash(r/p)) for p in ['results/sikh352/DIAGNOSIS61.md','results/sikh352/EVIDENCE_SCOPE_NOTES.md']}
 c.retrospective(task,'outcome',dict(attempt='c61-final-form-failure',role='diagnostic',origin='actual-native-review',
  observations=[dict(requirement='form',status='FAIL',observation='Scoped59 bare anatomy does not qualify whole actor.61 waist regression remains an actual visible failure.',foundation=True)],evidence=ev),'sikh352-c61-final-form-failure')
 c.replan(task,'GROUNDING','Four approved corrections58–61 consumed. Final waist regression rejected; preserve59 arm/60 fabric. More construction requires new cycle authority.','sikh352-exhausted61')
states={}
for t,limit in [(task,61),('sikh335-continuous-performance',12)]:
 st=c.state(t);assert st['cycle']==st['max_corrections']==limit
 states[t]={k:st[k] for k in ('stage','cycle','max_corrections','planning_step')}
write('controller-close.json',states)
paths=['results/sikh352/'+p for p in ['CLOSEOUT.md','LEARNINGS.md','EVIDENCE_SCOPE_NOTES.md','DIAGNOSIS58.md','DIAGNOSIS60.md','DIAGNOSIS61.md','leader_front-visual-c61.json','leader_reverse-visual-c61.json']]
ev=[dict(path=p,sha256=pk.file_hash(r/p)) for p in paths]
packet=pk.read_json(r,'results/sikh352/knowledge-packet.json')
failed={'anatomy','visual_gate','au_deformation','construction_interfaces','au_contact','au_surface','look','anticipation','au_reuse'}
passed={'authority','strategy','versioning','stopping','economics','current_state','cache_safety','render_profile'}
checks=[dict(id=o['id'],kind=o['check_kind'],status='FAIL' if o['id'] in failed else 'PASS' if o['id'] in passed else 'NOT_RUN',
 action_taken='Four retained cycles, paired controls and actual native review; retain59 scoped anatomy and60 garment source, reject61. No crowd propagation or production handoff.',
 observation='Whole deliverable fails garment/appearance, despite sampled bare-arm progress. Procedural PASS only covers preserved authority/evidence/local resource scope; no AV pass.',evidence=ev) for o in packet['obligations']]
write('knowledge-review.json',dict(packet_digest=packet['packet_digest'],scope='Exhaustion audit, not media admission',checks=checks,
 hypotheses=[dict(prediction='Whole garment ray queries produce a coherent waist band.',result='failed',observation='61 rigid projecting strips; source suggests sleeve hits. Existing semantic surface rule was not applied.',response='Torso-owned geometry and radial negative control proposed, not executed.',evidence=ev)],
 adjacent_regressions=dict(status='FAIL',observation='Elbow clearance improvement accompanied by waist regression; retained and rejected.',evidence=ev),
 stopping_reason='Appearance61/max61 exhausted; motion12 unchanged. No new authority or known-defect waiver.'))
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh352-*/runner-status.json')):
 d=json.loads(p.read_text());jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=d.get('elapsed'),exit_code=d.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),scope='Serial native occupancy including failures, overlaps active work; not additive or model-only time.'))
log=r/'.runtime/context-hygiene/runs/sikh352-tests-final/stdout.log'
write('verification.json',dict(tests=97,path=str(log.relative_to(r)),sha256=pk.file_hash(log),scope='Focused software tests, not artistic or audiovisual qualification.'))
print(states)
