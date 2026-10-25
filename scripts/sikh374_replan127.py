import copy,json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path.cwd();o=r/'results/sikh374';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==126
def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
fail=dict(status='FAIL',cause='126 source report: expanded-neighbour source9.403mm versus candidate9.408mm, so absolute25mm guard rejected an unchanged interface. Replace invalid global threshold with2mm floor and twice local two-ring displacement bound, retain source-contact mask and all92frame checks; no candidate yet or artistic acceptance.',run=bind('results/sikh374/appearance-c126-sculpt-run.json'),stderr=bind('.runtime/factory-native/sikh374-appearance-c126-sculpt/stderr.log'),scope='Method repair, original task/cap retained; not artistic acceptance.')
write('REJECT126.json',fail)
c.retrospective(task,'outcome',dict(attempt='sikh374-form126',role='diagnostic',origin='native-clearance-rejection',observations=[dict(requirement='interfaces',status='FAIL',observation=fail['cause'])],evidence={'failure':bind('results/sikh374/REJECT126.json')}),'sikh374-form126-guard-fail')
t=p.read_json(r,'results/sikh374/task126.json');t['id']='sikh374-horseform127'
new=['tests/test_horse_sculpt374.py','src/movie_factory/adapters/blender/nihang_sculpt374.py','results/sikh374/REJECT126.json','.runtime/context-hygiene/runs/sikh374-local-clearance-tests/stdout.log']
for q in new:t['inputs'][q]=p.file_hash(r/q)
write('task127.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet127.json',packet)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources'])
for x in src:
 if x['id']=='controls':x['binding']=bind('results/sikh374/task127.json')
for x in src:b['source_bindings'][x['id']]=x['binding']
for q in new:b['source_bindings'][q]=bind(q)
b['source_bindings']['results/sikh374/task127.json']=bind('results/sikh374/task127.json');b.update(knowledge_task='results/sikh374/task127.json',knowledge_digest=packet['packet_digest']);b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised127-brief.json',b)
cfg=p.read_json(r,'results/sikh374/appearance-c126.json');cfg.update(cause=fail['cause'],method='Actual Basis-local upper pectoral/central sternum sculpt with source cloth-owned65..150mm exclusion, unchangedback/seat/weights/actions, same relative corrective deltas and nap transfer. All92frame local influence/contact check:2mm floor plus twice two-ring displacement bound; source9.4mm unchanged-neighbour falsepositive explicitly corrected.',sources=cfg['sources']+new,retrospective_evidence=['results/sikh374/appearance-c127.json','results/sikh374/appearance-c127-challenge.json','results/sikh374/REQUEST.md','results/sikh374/REJECT126.json']);write('appearance-c127.json',cfg)
ch=p.read_json(r,'results/sikh374/appearance-c125-challenge.json');ch['checks']['interfaces']['observation']='126 global threshold rejected unchanged9.4mm neighbour.127 tests actual local-deformation bound and2mm floor with source-contact exclusion, exact motion/back/seat, all92frames. No continuous surface or artistic certification from this diagnostic.';ch['strongest_counterexample']='Contact exclusion can leave an ugly flat boundary or erase too much of the positive sculpt. Check actual resulting continuous chest/shoulder form, not merely cleared distance; no gap relaxation or old image reuse.';write('appearance-c127-challenge.json',ch)
c.revise(task,b,bind('results/sikh374/REQUEST.md'),'126 rejected unchanged neighbour with invalid global margin;127 corrects local-influence guard without new authority or erasing failures.','sikh374-replan127',grounding=dict(context_sources=src,reason='Reviewed actual126 failure and39tests of local influence model; replace invalid global assumption with bounded contact-sensitive guard, no new authority.',evidence={'failure':bind('results/sikh374/REJECT126.json'),'tests':bind('.runtime/context-hygiene/runs/sikh374-local-clearance-tests/stdout.log')}));print(c.state(task)['cycle'])
q=Path('scripts/sikh374_plan125.py').read_text().replace('revised125-brief.json','revised127-brief.json').replace('scripts/sikh374_plan125.py','scripts/sikh374_plan127.py');Path('scripts/sikh374_plan127.py').write_text(q)
