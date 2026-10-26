"""Same-task scoped method/source revision. No budget reset or automatic loop."""
import copy,json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep,planning_pipeline as pp
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh383';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle']+1;assert cy<=s['max_corrections']
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
cfg=pk.read_json(r,sys.argv[2] if len(sys.argv)>2 else f'results/sikh383/appearance-c{s["cycle"]}.json');b=copy.deepcopy(s.get('brief') or pk.read_json(r,f'results/sikh383/revised{s["cycle"]}-brief.json'));src=copy.deepcopy(s['direction']['context_sources']);reason=sys.argv[1]
changed=['src/movie_factory/adapters/blender/warhorse383.py','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/adapters/blender/nihang_control.py','scripts/sikh383_next.py','tests/test_warhorse383.py']
for k,v in b['source_bindings'].items():
 if pk.file_hash(r/v['path'])!=v['sha256']:
  assert v['path'] in changed,('UNREVIEWED383_DRIFT',v['path']);b['source_bindings'][k]=bind(v['path'])
for p in changed:b['source_bindings'][p]=bind(p)
if len(sys.argv)>2:b['source_bindings'][sys.argv[2]]=bind(sys.argv[2])
b['work_unit']['edit_kinds']=list({e['kind'] for step in cfg['steps'] for e in step['recipe'].get('edits',[])})
if 'poses'in cfg:b['work_unit']['appearance_proof']['poses']=cfg['poses']
t=pk.read_json(r,s['direction']['knowledge_task']);t.update(id=f'sikh383-native{cy}',inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()});write(f'task{cy}.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write(f'packet{cy}.json',packet);b.update(knowledge_task=f'results/sikh383/task{cy}.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind(f'results/sikh383/task{cy}.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings'][f'results/sikh383/task{cy}.json']=bind(f'results/sikh383/task{cy}.json');b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write(f'revised{cy}-brief.json',b)
cfg.update(brief_path=f'results/sikh383/revised{cy}-brief.json',cause=reason);cfg['sources']=list(dict.fromkeys(cfg['sources']+changed));write(f'appearance-c{cy}.json',cfg)
ch=pk.read_json(r,f'results/sikh383/appearance-c{s["cycle"]}-challenge.json');ch['checks']['method']['observation']=reason+' Actual import failure preserved; diagnose closed source only, no guarantee from file inventory.';write(f'appearance-c{cy}-challenge.json',ch)
c.revise(task,b,bind('results/sikh383/REQUEST.md'),reason,f'sikh383-revise{cy}',grounding=dict(context_sources=src,reason='Reviewed fixed-handler revision in same authorized donor qualification; failure history and limits retained.',evidence={p:bind(p) for p in ['results/sikh383/HANDLER_REVIEW.md','results/sikh383/REQUEST.md']}));print(c.state(task)['cycle'])
