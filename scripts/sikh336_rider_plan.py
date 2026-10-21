"""Repair5: load-related rider counterbalance and explicit poll ownership."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance'
assert c.state(task)['cycle']==5 and c.state(task)['planning_step']=='DERIVING'
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
art=pk.read_json(root,'results/sikh335/motion01/replan-source-c5.json');brief=art['STRATEGIZING']['brief']
recipe=pk.read_json(root,'results/sikh335/motion01/save-c4-recipe.json')
(out/'save-c5-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
render=pk.read_json(root,'results/sikh335/motion01/render-c4-recipe.json')
render['frames']=[294,301,307,317,327,331,338,345,350,351,353,355,357]
(out/'render-c5-recipe.json').write_text(json.dumps(render,indent=2)+'\n')
brief['strategy']+=' Rider torso counterbalances the root instead of compounding backward lean, with critically damped response and post-contact absorption. Poll position belongs explicitly to neck endpoint; deformation lengths are measured.'
real=brief['expert_plan']['realizations']['rider']
real['method']='Keep seat/root and existing connected garment/limb ownership; use positive pelvis-relative pitch during rear to oppose root backward inclination, damp velocity response and apply18mm post-contact body absorption. Rebuild reins and spear after torso updates.'
real['early_proof']='Matched preparation/crest/landing phases must show coordinated rider balance without seat lift, neck gaps or disconnected hands; actual support and neck-length ratios must pass separately.'
real['failure_condition']='Compounded backward lean, disconnected seat/garment/neck/hand interfaces, excessive limb deformation or falsely claiming static poses qualify motion.'
support=brief['expert_plan']['realizations']['support']
support['method']+=' Head translation is explicit neck-endpoint ownership; report four DEF-neck segment length ratios at every authored frame, fail outside0.85–1.15 of rest length. This bounds stretching, not anatomical aesthetics.'
for key in ('rider','support'):
    art['DERIVING']['derivations'][key]={f:brief['expert_plan']['realizations'][key][f] for f in pp.DERIVATION_FIELDS}
for path in ['src/movie_factory/adapters/blender/nihang_motion.py','src/movie_factory/adapters/blender/nihang_support.py',
             'results/sikh335/motion01/render-review-c4.json','scripts/sikh336_rider_plan.py',
             'results/sikh335/motion01/save-c5-recipe.json','results/sikh335/motion01/render-c5-recipe.json']:
    brief['source_bindings'][path]=bind(path)
for step in art['STRATEGIZING']['steps']:step['native_recipe']=bind(f'results/sikh335/motion01/{step["id"]}-c5-recipe.json')
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],discriminating_test=real['early_proof'])
art['STRATEGIZING']['resource_scope']='Correction5/max6, third of four approved motion corrections. No separate appearance allowance; local serial worker, no spend.'
brief['expert_plan']['challenge'].update(plan_digest=ep.plan_digest(brief),omission_probe='A rider with movable joints can still compound horse rotation and appear fixed; evaluate world-space balance and post-contact response, not existence of keys.')
for stage in ('DERIVING','STRATEGIZING'):
    p=c.packet(task);r={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],r,'sikh336-rider-'+stage)
    (out/(stage.lower()+'-c5.json')).write_text(json.dumps(r,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None)
(out/'rider-challenge-input-c5.json').write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['planning_step'])
