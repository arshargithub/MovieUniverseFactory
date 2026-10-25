import copy,json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path.cwd();o=r/'results/sikh374';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==125
def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
fail=dict(status='FAIL',cause='Post-sculpt guard rejected expanded torso-neighbour/cache gap2.778mm at276 before save. The broad field reached cloth-owned surface; current code now derives a source-contact exclusion BEFORE sculpt, retains25mm guard and records failure coordinates. No new candidate or weakened clearance claim.',run=bind('results/sikh374/appearance-c125-sculpt-run.json'),stderr=bind('.runtime/factory-native/sikh374-appearance-c125-sculpt/stderr.log'),scope='Method repair, original task/cap retained; not artistic acceptance.')
write('REJECT125.json',fail)
c.retrospective(task,'outcome',dict(attempt='sikh374-form125',role='diagnostic',origin='native-clearance-rejection',observations=[dict(requirement='interfaces',status='FAIL',observation=fail['cause'])],evidence={'failure':bind('results/sikh374/REJECT125.json')}),'sikh374-form125-guard-fail')
t=p.read_json(r,'results/sikh374/task125.json');t['id']='sikh374-horseform126'
new=['src/movie_factory/adapters/blender/nihang_sculpt374.py','results/sikh374/REJECT125.json','.runtime/context-hygiene/runs/sikh374-contact-mask-tests/stdout.log']
for q in new:t['inputs'][q]=p.file_hash(r/q)
write('task126.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet126.json',packet)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources'])
for x in src:
 if x['id']=='controls':x['binding']=bind('results/sikh374/task126.json')
for x in src:b['source_bindings'][x['id']]=x['binding']
for q in new:b['source_bindings'][q]=bind(q)
b['source_bindings']['results/sikh374/task126.json']=bind('results/sikh374/task126.json');b.update(knowledge_task='results/sikh374/task126.json',knowledge_digest=packet['packet_digest']);b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised126-brief.json',b)
cfg=p.read_json(r,'results/sikh374/appearance-c125.json');cfg.update(cause=fail['cause'],method=cfg['method']+' Before mutation, actual five-pose source cache distance freezes cloth-owned skin with65..150mm smooth exclusion; unchanged25mm all92frame guard.',sources=cfg['sources']+new,retrospective_evidence=['results/sikh374/appearance-c126.json','results/sikh374/appearance-c126-challenge.json','results/sikh374/REQUEST.md','results/sikh374/REJECT125.json']);write('appearance-c126.json',cfg)
ch=p.read_json(r,'results/sikh374/appearance-c125-challenge.json');ch['checks']['interfaces']['observation']='125 source failed a prospective cache guard before save;126 excludes cloth-owned source surface before sculpt and retains unchanged all92frame clearance threshold, exact motion and back/seat source. Positive anatomy still needs new actual matrix.';ch['strongest_counterexample']='Contact exclusion can leave an ugly flat boundary or erase too much of the positive sculpt. Check actual resulting continuous chest/shoulder form, not merely cleared distance; no gap relaxation or old image reuse.';write('appearance-c126-challenge.json',ch)
c.revise(task,b,bind('results/sikh374/REQUEST.md'),'125 source rejected before save;126 protects actual cloth-owned source domain before sculpt, original five total cycles only.','sikh374-replan126',grounding=dict(context_sources=src,reason='Reviewed source-contact mask and19tests, failure evidence retained; no weakened guard or new authority.',evidence={'failure':bind('results/sikh374/REJECT125.json'),'tests':bind('.runtime/context-hygiene/runs/sikh374-contact-mask-tests/stdout.log')}));print(c.state(task)['cycle'])
q=Path('scripts/sikh374_plan125.py').read_text().replace('revised125-brief.json','revised126-brief.json').replace('scripts/sikh374_plan125.py','scripts/sikh374_plan126.py');Path('scripts/sikh374_plan126.py').write_text(q)
