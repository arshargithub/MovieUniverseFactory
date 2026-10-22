"""Continue the authorized appearance trial without resetting its counters."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/look01'
c=wf.Controller(root,DATABASE);task='sikh335-supporting-appearance'
assert c.state(task)['cycle']==5 and c.state(task)['max_corrections']==8
art={s:pk.read_json(root,f'results/sikh335/look01/{s.lower()}-c4.json')['artifact'] for s in pp.STEPS[:3]}
brief=art['STRATEGIZING']['brief']
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
def save(name,data):
    p=out/name
    if p.exists():assert json.loads(p.read_text())==data
    else:p.write_text(json.dumps(data,indent=2)+'\n')
for p in list(brief['source_bindings']):
    if p.startswith(('src/movie_factory/adapters/blender/nihang_','tests/test_nihang337')):
        brief['source_bindings'][p]=bind(p)
for p in ('results/sikh335/look01/STRATEGY_C5.md','results/sikh335/look01/allowance-338.json',
          'results/sikh335/REASSESSMENT_337.md',
          'scripts/sikh338_look_plan.py','scripts/sikh338_look_dispatch.py'):
    brief['source_bindings'][p]=bind(p)
art['GROUNDING']['reconciliation']+=' Director338 extends only this appearance task by four corrections. Prior4 failed on standalone import before cloth ran; fixed loader now tested. Preserve all earlier visual vetoes and exact source roles. Fresh knowledge packet retains obligations, manually reconciled in STRATEGY_C5.'
brief['expert_plan']['challenge']['scope_tradeoff']='Correction5/max8, two-actor supported-drape proof first. No face/headwear pass inferred from cloth success; motion retains separate allowance and pending Director AV.'
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
art['STRATEGIZING']['resource_scope']='Appearance correction5/max8, serial native save and revealing evidence images. No new spending or providers; original authority and failures retained.'
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,'sikh338-look-c5-'+stage)
    save(stage.lower()+'-c5.json',response)
p=c.packet(task);p.pop('ticket',None);save('challenge-input-c5.json',p)
print(c.state(task)['planning_step'])
