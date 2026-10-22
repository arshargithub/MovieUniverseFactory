"""Same-task correction with explicit evidence/method amendment and frozen source."""
import json,sys,shutil
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory import planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';prior=int(sys.argv[1]);cycle=prior+1
amend=pk.read_json(r,f'results/sikh335/look01/amendment-c{cycle}.json')
s=c.state(task)
if s['cycle']==prior:
    d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],amend['reason'],f'sikh340-c{cycle}-reground')
assert c.state(task)['cycle']==cycle and cycle<=17 and c.state(task)['max_corrections']==17
art={x:pk.read_json(r,f'results/sikh335/look01/{x.lower()}-c{prior}.json')['artifact'] for x in pp.STEPS[:3]}
b=art['STRATEGIZING']['brief']
for ref in b['source_bindings'].values():
    actual=pk.file_hash(r/ref['path'])
    if actual!=ref['sha256']:
        assert ref['path'].startswith(('src/movie_factory/adapters/blender/nihang_','tests/test_nihang340'))
        ref['sha256']=actual
for path in (f'results/sikh335/look01/save-run-c{prior}.json',f'results/sikh335/look01/amendment-c{cycle}.json','scripts/sikh340_continue.py'):
    b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
art['GROUNDING']['reconciliation']+=' '+amend['reason']
for name,method in amend['methods'].items():
    b['expert_plan']['realizations'][name]['method']=method
    art['DERIVING']['derivations'][name]={f:b['expert_plan']['realizations'][name][f] for f in pp.DERIVATION_FIELDS}
b['expert_plan']['challenge']['scope_tradeoff']=f'Same appearance task{cycle}/17, all failure history and quality requirements retained.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
art['STRATEGIZING']['resource_scope']=f'Correction{cycle}/17. '+amend['reason']
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,f'sikh340-c{cycle}-{stage}')
    (out/f'{stage.lower()}-c{cycle}.json').write_text(json.dumps(response,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None);(out/f'challenge-input-c{cycle}.json').write_text(json.dumps(p,indent=2)+'\n')
v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{prior}.json')
v['checks']['grounding']['observation']=amend['reason']
v['checks']['method']['observation']=amend['challenge']
v['checks']['authority']['observation']=f'Same appearance task{cycle}/17 under340. No spend or motion allowance change.'
v['strongest_counterexample']=amend['counterexample']
(out/f'challenge-verdict-c{cycle}.json').write_text(json.dumps(v,indent=2)+'\n')
freeze=out/f'source-c{cycle}';freeze.mkdir(exist_ok=False);manifest={}
for path in sorted((r/'src/movie_factory/adapters/blender').glob('*.py')):
    shutil.copy2(path,freeze/path.name);manifest[path.name]=pk.file_hash(path)
(freeze/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(c.state(task)['planning_step'])
