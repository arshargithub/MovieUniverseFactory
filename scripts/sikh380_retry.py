import json,copy
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh380';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==144 and s['max_corrections']==146;cy=145

def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):
 q=o/n;t=json.dumps(v,indent=2)+'\n'
 if q.exists():assert q.read_text()==t
 else:q.write_text(t)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources']);cfg=p.read_json(r,'results/sikh380/appearance-c144.json');new=['scripts/sikh380_retry.py','results/sikh380/REJECT144.md','.runtime/factory-native/sikh380-appearance-c144-repair/runner-status.json']
for q in new:b['source_bindings'][q]=bind(q)
t=p.read_json(r,'results/sikh380/task144.json');t['id']='sikh380-native145';t['inputs'].update({q:p.file_hash(r/q) for q in new});write('task145.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet145.json',packet);b.update(knowledge_task='results/sikh380/task145.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind('results/sikh380/task145.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings']['results/sikh380/task145.json']=bind('results/sikh380/task145.json');b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised145-brief.json',b)
cfg.update(brief_path='results/sikh380/revised145-brief.json',sources=cfg['sources']+new,retrospective_evidence=cfg['retrospective_evidence']+new);cfg['cause']='144 startup exit-11 before scene or handler. Retry unchanged ownership hypothesis through same bridge with local OS approval; no result or method failure inferred. '+cfg['cause'];write('appearance-c145.json',cfg)
ch=p.read_json(r,'results/sikh380/appearance-c144-challenge.json');ch['checks']['method']['observation']=cfg['cause'];write('appearance-c145-challenge.json',ch)
c.revise(task,b,bind('results/sikh380/SWITCH.md'),'Retain144 startup failure; same hypothesis145 with controlled local permissions. No reset.', 'sikh380-replan145',grounding=dict(context_sources=src,reason='Actual startup failure; all source,scope and authority unchanged, new failure bound.',evidence={q:bind(q) for q in new}));print(c.state(task)['cycle'])
