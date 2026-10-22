"""Source-reconciled same-task garment replacement plan, correction9 only."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory import planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
assert c.state(task)['cycle']==9 and c.state(task)['max_corrections']==12
art={s:pk.read_json(r,f'results/sikh335/look01/{s.lower()}-c8.json')['artifact'] for s in pp.STEPS[:3]}
b=art['STRATEGIZING']['brief']
for key,ref in b['source_bindings'].items():
    current=pk.file_hash(r/ref['path'])
    if current!=ref['sha256']:
        assert ref['path'] in ('src/movie_factory/adapters/blender/nihang_look.py',)
        ref['sha256']=current
for path in ('src/movie_factory/adapters/blender/nihang_garment.py','tests/test_nihang339_garment.py',
             'results/sikh335/look01/STRATEGY_C9.md','results/sikh335/look01/allowance-339.json',
             'results/sikh335/look01/leader_front-visual-review-c8.json',
             'scripts/sikh339_plan.py','scripts/sikh339_dispatch.py'):
    b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
art['GROUNDING']['reconciliation']+=' Separate339 approval extends exhausted8 to12. Actual C8 image reviews reject the patch-transfer representation. STRATEGY_C9 reconciles fresh knowledge and the replacement garment, keeping all face/headwear/appearance vetoes.'
real=b['expert_plan']['realizations']
real['form']['method']='Replace anatomical shirt display with a connected sewn low-resolution torso and sleeve shell; measured torso depth, existing elbow/cuff ownership, shoulder/waist/cuff support, isolated40-frame cloth settle against original donor. Barycentric local-normal binding transfers existing207 poses. Original donor hidden, source masters untouched. Refit sash and placket to final exterior.'
real['interfaces']['method']='Preserve original motion owners and camera. Barycentric triangle attachment plus local-normal offset carries garment through source pose caches; compare actual stance and crest, collar/armpit/cuff/belt and reverse. Static drape is not dynamic cloth qualification.'
for name in ('form','interfaces'):
    art['DERIVING']['derivations'][name]={f:real[name][f] for f in pp.DERIVATION_FIELDS}
b['strategy']='Whole sewn-shell construction proof instead of rectangular depth correction on anatomy; preserve performance and judge all visible interfaces before face/headwear continuation or propagation.'
b['expert_plan']['challenge']['scope_tradeoff']='Correction9/max12. A usable garment is only an internal prerequisite; face, crown and saddle stay blocking. No spending or partial Director handoff.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
art['STRATEGIZING']['method_choice']['chosen']=b['strategy']
art['STRATEGIZING']['resource_scope']='Appearance9/max12. Serial local solve and revealing images only, with retained history; no provider, installation, uploads or spending.'
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,'sikh339-c9-'+stage)
    dest=out/(stage.lower()+'-c9.json');assert not dest.exists();dest.write_text(json.dumps(response,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None)
(out/'challenge-input-c9.json').write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['planning_step'])
