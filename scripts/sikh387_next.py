"""Reviewed same-task revision; one charged next correction, no art auto-PASS."""
import copy,json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep,planning_pipeline as pp,retrospective as rt

r=Path(__file__).resolve().parents[1];o=r/'results/sikh387';c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task)
cfg=pk.read_json(r,sys.argv[1]);cy=s['cycle']+1;assert cy<=s['max_corrections']
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
    p=o/n;t=json.dumps(v,indent=2)+'\n'
    if p.exists():assert p.read_text()==t,n
    else:p.write_text(t)
b=copy.deepcopy(s.get('brief') or pk.read_json(r,f'results/sikh387/revised{s["cycle"]}-brief.json'))
src=copy.deepcopy(s['direction']['context_sources']);reviewed=set(cfg['reviewed_changes'])
for key,v in b['source_bindings'].items():
    if pk.file_hash(r/v['path'])!=v['sha256']:
        assert v['path'] in reviewed,('UNREVIEWED386_DRIFT',v['path']);b['source_bindings'][key]=bind(v['path'])
for row in src:
    if row['id'] in cfg.get('source_ranges',{}):row['lines']=cfg['source_ranges'][row['id']]
    if row['id']!='controls':row['binding']=bind(row['binding']['path'])
for p in list(reviewed)+cfg['sources']+[sys.argv[1],'scripts/sikh387_next.py']:b['source_bindings'][p]=bind(p)
for addition in cfg.get('reference_additions',[]):
    ref=copy.deepcopy(addition['reference']);rid=ref['id'];assert rid not in {x['id'] for x in b['references']}
    need=addition['need'];qualified=copy.deepcopy(addition['qualification']);assert qualified['id']==rid
    b['references'].append(ref);b['reference_plan'][rid]=dict(reference_digest=pk.digest(ref),application=addition['application'])
    d=b['reference_readiness']['decisions'][need];d['references'].append(qualified);d['decision']='acquire';d['reason']=addition['reason']
    for req,needs in b['reference_mapping'].items():
        if need in needs and rid not in b['expert_plan']['realizations'][req]['reference_ids']:b['expert_plan']['realizations'][req]['reference_ids'].append(rid)
    for item in [ref['binding']]+qualified['evidence']:b['source_bindings'][item['path']]=item
if 'unit_changes' in cfg:b['work_unit'].update(cfg['unit_changes'])
if 'experiment_changes' in cfg:b['work_unit']['causal_experiment'].update(cfg['experiment_changes'])
if 'criteria' in cfg:
    for q in b['requirements']:
        if q['id'] in cfg['criteria']:q['criterion']=cfg['criteria'][q['id']]
for rid,m in b['expert_plan']['realizations'].items():m.update(method=cfg['method'],early_proof=cfg['proof'],failure_condition=cfg['failure'])
t=pk.read_json(r,s['direction']['knowledge_task']);t.update(id=f'sikh387-native{cy}',intent=b['intent'],inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()})
write(f'task{cy}.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write(f'packet{cy}.json',packet)
b.update(knowledge_task=f'results/sikh387/task{cy}.json',knowledge_digest=packet['packet_digest'])
for row in src:
    if row['id']=='controls':row['binding']=bind(f'results/sikh387/task{cy}.json')
    b['source_bindings'][row['binding']['path']]=row['binding']
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write(f'revised{cy}-brief.json',b)
wf.validate_brief(r,b,'production',s['mode']);pp.source_context(r,dict(context_sources=src))
con=c.connect();projection=rt.snapshot(con,task);con.close()
if projection['engine']!=rt.engine():
    migration=dict(state_digest=pk.digest(c.state(task)),coverage='Serialization-only trigger dictionary extension; all events/findings/memberships/digests and exact counters retained. No active worker or false art closure.',
        unknowns='Anatomy and actual exporter integration unqualified; previous177failed.',evidence={p:bind(p) for p in cfg['retro_evidence']})
    write(f'policy-migration{cy}.json',migration);c.migrate_retrospective(task,bind('results/sikh387/REQUEST.md'),migration,f'sikh387-policy{cy}')
c.revise(task,b,bind('results/sikh387/REQUEST.md'),cfg['reconciliation'],f'sikh387-revise{cy}',
    grounding=dict(context_sources=src,reason=cfg['reconciliation'],evidence={p:bind(p) for p in cfg['retro_evidence']}))
assert c.state(task)['cycle']==cy
cfg['brief_path']=f'results/sikh387/revised{cy}-brief.json';write(f'appearance-c{cy}.json',cfg)
print(json.dumps(dict(cycle=cy,max=c.state(task)['max_corrections'],sources=len(b['source_bindings']))))
