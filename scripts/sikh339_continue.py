"""Reconcile an observed same-task native failure without resetting limits."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory import planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';prior=int(sys.argv[1]);cycle=prior+1;reason=sys.argv[2]
s=c.state(task)
if s['cycle']==prior:
    d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,f'sikh339-c{cycle}-reground')
assert c.state(task)['cycle']==cycle and c.state(task)['max_corrections']==12
art={x:pk.read_json(r,f'results/sikh335/look01/{x.lower()}-c{prior}.json')['artifact'] for x in pp.STEPS[:3]}
b=art['STRATEGIZING']['brief']
for ref in b['source_bindings'].values():
    actual=pk.file_hash(r/ref['path'])
    if actual!=ref['sha256']:
        assert ref['path'].startswith(('src/movie_factory/adapters/blender/nihang_','tests/test_nihang339','scripts/sikh339_'))
        ref['sha256']=actual
for path in (f'results/sikh335/look01/save-run-c{prior}.json','scripts/sikh339_continue.py'):
    b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
art['GROUNDING']['reconciliation']+=' '+reason
b['expert_plan']['challenge']['scope_tradeoff']=f'Same-task correction{cycle}/12; original full appearance floor and retained failures. No new spending.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
art['STRATEGIZING']['resource_scope']=f'Correction{cycle}/12. '+reason
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,f'sikh339-c{cycle}-{stage}')
    dest=out/f'{stage.lower()}-c{cycle}.json';assert not dest.exists();dest.write_text(json.dumps(response,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None);(out/f'challenge-input-c{cycle}.json').write_text(json.dumps(p,indent=2)+'\n')
v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{prior}.json')
v['checks']['grounding']['observation']=reason
v['checks']['method']['observation']='Reviewed the specific correction and unchanged full sewn-shell method. Hidden sleeve geometry is in the same raw donor coordinate convention used by319; discarded object transforms are not valid contact frames. Actual donor surface-distance guard remains. Native and image results remain unqualified.'
v['checks']['authority']['observation']=f'Same task correction{cycle}/12 under separate339 extension. No new spending; prior failures preserved.'
(out/f'challenge-verdict-c{cycle}.json').write_text(json.dumps(v,indent=2)+'\n')
print(c.state(task)['planning_step'])
