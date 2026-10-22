"""Explicit same-task replan after recorded failure; counters never reset."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/look01'
c=wf.Controller(root,DATABASE);task='sikh335-supporting-appearance'
prior=int(sys.argv[1]);cycle=prior+1;reason=sys.argv[2]
s=c.state(task)
if s['cycle']==prior:
    d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,f'sikh338-look-c{cycle}-reground')
assert c.state(task)['cycle']==cycle and c.state(task)['max_corrections']==8
art={s:pk.read_json(root,f'results/sikh335/look01/{s.lower()}-c{prior}.json')['artifact'] for s in pp.STEPS[:3]}
brief=art['STRATEGIZING']['brief']
for key,b in brief['source_bindings'].items():
    actual=pk.file_hash(root/b['path'])
    if actual!=b['sha256']:
        assert b['path'].startswith(('src/movie_factory/adapters/blender/nihang_','tests/test_nihang338','scripts/sikh338_'))
        b['sha256']=actual
for p in ('scripts/sikh338_continue_plan.py',f'results/sikh335/look01/save-run-c{prior}.json'):
    brief['source_bindings'][p]={'path':p,'sha256':pk.file_hash(root/p)}
art['GROUNDING']['reconciliation']+=' '+reason
if cycle==8:
    real=brief['expert_plan']['realizations']
    real['form']['method']='Measure the common supported central torso domain in the evaluated stance. Settle two regular quad cloth panels against the contracted torso proxy, with pinned boundaries. Transfer only bounded depth displacement to original garment topology and all207 leader caches. Weld crown duplicates, lower collar, refit outer layers. This is a static method proof, not animated cloth qualification.'
    art['DERIVING']['derivations']['form']={f:real['form'][f] for f in pp.DERIVATION_FIELDS}
    brief['strategy']='Supported regular-panel cloth proof on a measured torso domain, preserving garment topology and cached poses; revealing stance/crest/front/reverse controls before replication or artistic admission.'
    art['STRATEGIZING']['method_choice']['chosen']=brief['strategy']
brief['expert_plan']['challenge']['scope_tradeoff']=f'Correction{cycle}/max8 on same existing task. No extra spending or authority; preserved failures and artistic vetoes.'
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
art['STRATEGIZING']['resource_scope']=f'Appearance correction{cycle}/max8; serial local native proof, no new spending. '+reason
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);r={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],r,f'sikh338-look-c{cycle}-'+stage)
    dest=out/(stage.lower()+f'-c{cycle}.json');assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None)
(out/f'challenge-input-c{cycle}.json').write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['planning_step'])
