"""Prepare one explicit same-task next correction from a scoped config."""
from pathlib import Path
import json,copy,sys
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh381';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle']+1;cfg=p.read_json(r,sys.argv[1]);assert cy<=s['max_corrections']
bind=lambda q:dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):
 dest=o/n;t=json.dumps(v,indent=2)+'\n'
 if dest.exists():assert dest.read_text()==t,('PRESERVE',n)
 else:dest.write_text(t)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources']);reviewed=set(cfg['sources'])
for k,v in b['source_bindings'].items():
 if p.file_hash(r/v['path'])!=v['sha256']:
  assert v['path'] in reviewed,('UNREVIEWED_DRIFT',v['path'])
  b['source_bindings'][k]=bind(v['path'])
for q in cfg['sources']:b['source_bindings'][q]=bind(q)
if cfg.get('reference_supplement'):
 for spec in cfg['reference_supplement']:
  ref=spec['reference'];b['references'].append(ref);b['reference_plan'][ref['id']]=dict(reference_digest=p.digest(ref),application=ref['fidelity']+' Internal study only; not film pixels or motion authority.')
  b['reference_readiness']['decisions']['junction']['references'].append(spec['selected'])
  for rid,needs in b['reference_mapping'].items():
   if 'junction' in needs:b['expert_plan']['realizations'][rid]['reference_ids'].append(ref['id'])
 for need in b['reference_readiness']['scope']['needs']:
  if need['id']=='junction' and 'frontal_rear' not in need['coverage']:need['coverage'].append('frontal_rear')
 b['reference_readiness']['decisions']['junction']['reason']='379 gross form sources retained;381 inspected near-frontal posed photographs supplement the previously ambiguous front chest/foreleg interface.'
 src.append(dict(id='target381',category='references',binding=bind('results/sikh381/REFERENCE_SUPPLEMENT.md'),lines=[11,15],status='adopted',required=True,statement='Actual near-frontal rearing photographs supplement physical chest/foreleg continuity; no film pixels, style or choreography authority.',scope='381 physical-form comparison only'))
b['work_unit']['edit_kinds']=cfg['edit_kinds'];b['expert_plan']['realizations']['form']['derivation']=cfg['cause'];b['work_unit']['appearance_proof']['poses']=[283,333,339,342,346,367]
t=p.read_json(r,s['direction']['knowledge_task']);t.update(id=f'sikh381-native{cy}',inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()});write(f'task{cy}.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write(f'packet{cy}.json',packet);b.update(knowledge_task=f'results/sikh381/task{cy}.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind(f'results/sikh381/task{cy}.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings'][f'results/sikh381/task{cy}.json']=bind(f'results/sikh381/task{cy}.json');b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write(f'revised{cy}-brief.json',b);cfg['brief_path']=f'results/sikh381/revised{cy}-brief.json';write(f'appearance-c{cy}.json',cfg)
ch=p.read_json(r,f'results/sikh381/appearance-c{s["cycle"]}-challenge.json');ch['checks']['method']['observation']=cfg['cause']+' '+cfg['method'];ch['checks']['interfaces']['observation']=cfg['proof'];ch['strongest_counterexample']=cfg['counterexample'];ch['reference_challenge']['readiness_digest']=p.digest(b['reference_readiness'])
if cfg.get('reference_supplement'):
 ch['reference_challenge']['checks']['junction'].update(status='PASS',observation='Actual near-frontal rear sources inspected; form continuity scope only, all prior role exclusions retained.',counterexample='Static photos do not validate animation or exact hidden anatomy.',evidence=[v for x in b['reference_readiness']['decisions']['junction']['references'] for v in x['evidence']])
write(f'appearance-c{cy}-challenge.json',ch)
c.revise(task,b,bind('results/sikh381/REQUEST.md'),cfg['cause'],f'sikh381-replan{cy}',grounding=dict(context_sources=src,reason='Actual preceding failed evidence preserved before source change. New in-scope construction/control sources explicitly reviewed; same original direction/reference roles, authority and allowance.',evidence={q:bind(q) for q in cfg['retrospective_evidence']}));print(c.state(task)['cycle'])
