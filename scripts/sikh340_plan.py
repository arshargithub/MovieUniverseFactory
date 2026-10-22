"""Reconcile the new rest-pattern proof into the same staged appearance task."""
import json,shutil
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory import planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==13 and s['max_corrections']==17
art={x:pk.read_json(r,f'results/sikh335/look01/{x.lower()}-c12.json')['artifact'] for x in pp.STEPS[:3]}
b=art['STRATEGIZING']['brief']
for ref in b['source_bindings'].values():
    actual=pk.file_hash(r/ref['path'])
    if actual!=ref['sha256']:
        assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_')
        ref['sha256']=actual
paths=['results/sikh335/look01/STRATEGY_C13.md','results/sikh335/look01/allowance-340.json',
       'scripts/sikh340_plan.py','scripts/sikh340_dispatch.py','tests/test_nihang340_garment.py',
       'results/sikh335/REASSESSMENT_339.md']
for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
art['GROUNDING']['reconciliation']+=' Director340 authorizes five further corrections13–17. Fresh340 packet manually reconciled to wardrobe interfaces and AU06/09/10/13. C12 geometry failed before images; neutral rest arc and posed elbow fit are separated in STRATEGY_C13. No full neutral drape or artistic success claimed.'
real=b['expert_plan']['realizations']
real['form']['method']='Complete sewn shell with a straight-rest arc-distance sleeve, two measured arm segments and an inside-corner fillet, avoiding the previous overshooting elbow curve. Preserve actual pre/post-solve geometry and collision donor. Retain90mm displacement guard. Native fit precedes whole-character face/crown/saddle continuation.'
real['interfaces']['method']='Preserve original cuff/elbow raw cache ownership and207 donor poses. Test straight rest distance, posed chain bounds and actual settled geometry. Barycentric pose transfer retains its100mm distance gate. Inspect shoulder/neck/cuff/waist/sash and revealing reverse; static solve is not dynamic qualification.'
for name in ('form','interfaces'):art['DERIVING']['derivations'][name]={f:real[name][f] for f in pp.DERIVATION_FIELDS}
b['strategy']='Separate rest sleeve parameterization, posed fit and gravity settle; preserve actual failure geometry before integrated supporting appearance review.'
b['expert_plan']['challenge']['scope_tradeoff']='Same task13/max17. No spending, no motion allowance change, no weaker same-film floor.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
art['STRATEGIZING']['method_choice']['chosen']=b['strategy']
art['STRATEGIZING']['method_choice']['alternatives']='Reject another unrestricted quadratic elbow bulge or relaxed displacement guard. Neutral rest mathematical control does not replace actual body-fit evidence.'
art['STRATEGIZING']['resource_scope']='Correction13/max17, serial local native solve and revealing images. No new tools, providers or spending.'
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,'sikh340-c13-'+stage)
    (out/(stage.lower()+'-c13.json')).write_text(json.dumps(response,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None);(out/'challenge-input-c13.json').write_text(json.dumps(p,indent=2)+'\n')
freeze=out/'source-c13';freeze.mkdir(exist_ok=False)
manifest={}
for path in sorted((r/'src/movie_factory/adapters/blender').glob('*.py')):
    shutil.copy2(path,freeze/path.name);manifest[path.name]=pk.file_hash(path)
(freeze/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(c.state(task)['planning_step'])
