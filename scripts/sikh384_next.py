"""Explicit same-task scoped revision; no correction refund or automatic art loop."""
import copy,json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep,planning_pipeline as pp
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh384';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle']+1
assert cy<=s['max_corrections']
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
cfg=pk.read_json(r,sys.argv[1]);b=copy.deepcopy(s.get('brief') or pk.read_json(r,f'results/sikh384/revised{s["cycle"]}-brief.json'));src=copy.deepcopy(s['direction']['context_sources'])
changed=['src/movie_factory/adapters/blender/warhorse384.py','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/adapters/blender/nihang_control.py','tests/test_warhorse384.py','scripts/sikh384_next.py']+cfg.get('reviewed_changes',[])
for key,v in b['source_bindings'].items():
 if pk.file_hash(r/v['path'])!=v['sha256']:
  assert v['path'] in changed,('UNREVIEWED384_DRIFT',v['path']);b['source_bindings'][key]=bind(v['path'])
for p in changed+cfg['sources']+[sys.argv[1]]:b['source_bindings'][p]=bind(p)
b['work_unit'].update(cfg.get('unit_changes',{}));b['work_unit']['edit_kinds']=list({e['kind'] for step in cfg['steps'] for e in step['recipe'].get('edits',[])})
for ref in cfg.get('new_references',[]):
 b['references'].append(ref);b['reference_plan'][ref['id']]=dict(reference_digest=pk.digest(ref),application=ref['scope']+' '+ref['fidelity'])
 b['source_bindings'][ref['binding']['path']]=ref['binding']
for need, additions in cfg.get('readiness_additions',{}).items():
 b['reference_readiness']['decisions'][need]['references']+=additions
 b['reference_readiness']['scope']['needs'][next(i for i,n in enumerate(b['reference_readiness']['scope']['needs']) if n['id']==need)]['coverage']+=list({k for a in additions for k in a['coverage']})
for need in cfg.get('historical_reference_needs',[]):
 b['reference_readiness']['scope']['needs']=[n for n in b['reference_readiness']['scope']['needs'] if n['id']!=need]
 b['reference_readiness']['decisions'].pop(need)
 for rid,needs in b['reference_mapping'].items():
  b['reference_mapping'][rid]=[n for n in needs if n!=need];assert b['reference_mapping'][rid]
for q in b['requirements']:
 if q['id'] in cfg.get('criteria',{}):q['criterion']=cfg['criteria'][q['id']]
for rid,m in b['expert_plan']['realizations'].items():
 m.update(method=cfg['method'],early_proof=cfg['proof'],failure_condition=cfg['failure'])
 if rid in cfg.get('criteria',{}):m['derivation']=cfg['criteria'][rid]
 for need in b['reference_mapping'][rid]:
  for q in b['reference_readiness']['decisions'][need]['references']:
   if q['id'] not in m['reference_ids']:m['reference_ids'].append(q['id'])
t=pk.read_json(r,s['direction']['knowledge_task']);t.update(id=f'sikh384-native{cy}',inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()});write(f'task{cy}.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write(f'packet{cy}.json',packet);b.update(knowledge_task=f'results/sikh384/task{cy}.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind(f'results/sikh384/task{cy}.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings'][f'results/sikh384/task{cy}.json']=bind(f'results/sikh384/task{cy}.json');b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write(f'revised{cy}-brief.json',b)
cfg['brief_path']=f'results/sikh384/revised{cy}-brief.json';write(f'appearance-c{cy}.json',cfg)
ch=pk.read_json(r,f'results/sikh384/appearance-c{s["cycle"]}-challenge.json');ch['checks']['method']['observation']=cfg['method']+' '+cfg['proof'];ch['strongest_counterexample']=cfg['counterexample'];write(f'appearance-c{cy}-challenge.json',ch)
ch['reference_challenge']['readiness_digest']=pk.digest(b['reference_readiness'])
for need in cfg.get('historical_reference_needs',[]):ch['reference_challenge']['checks'].pop(need)
for need,additions in cfg.get('readiness_additions',{}).items():
 ch['reference_challenge']['checks'][need]['evidence'] += [x for a in additions for x in a['evidence']]
 ch['reference_challenge']['checks'][need]['observation']+=' Actual existing near-frontal bare horse head inspected for bridge/eye/muzzle planes, supplementing side anatomy; no source-pixel adoption.'
write(f'appearance-c{cy}-challenge.json',ch)
pp.source_context(r,dict(context_sources=src))
c.revise(task,b,bind('results/sikh384/REQUEST.md'),cfg['cause'],f'sikh384-revise{cy}',grounding=dict(context_sources=src,reason=cfg['reconciliation'],evidence={p:bind(p) for p in cfg['retrospective_evidence']}));print('Revised',c.state(task)['cycle'])
