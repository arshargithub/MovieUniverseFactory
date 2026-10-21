"""Affected-stage repair4: reference poll action and actual-contact earth FX."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance'
assert c.state(task)['cycle']==4 and c.state(task)['planning_step']=='DERIVING'
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
art=pk.read_json(root,'results/sikh335/motion01/replan-source-c4.json')
brief=art['STRATEGIZING']['brief']
recipe=pk.read_json(root,'results/sikh335/motion01/save-recipe.json')
angles={294:(.28,.25),300:(.35,.50),307:(.15,.08),317:(-.12,-.25),
        327:(-.20,-.28),331:(-.20,-.20),338:(-.08,-.08),345:(.10,.08),
        350:(.20,.20),353:(.32,.35),360:(.05,.05)}
for a in recipe['edits'][1]['anchors']:
    if a['frame'] in angles:a['neck_pitch'],a['poll_pitch']=angles[a['frame']]
(out/'save-c4-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
render=pk.read_json(root,'results/sikh335/motion01/render-c3-recipe.json')
render['frames']=[294,301,307,317,327,338,345,349,350,351,353,355,357]
(out/'render-c4-recipe.json').write_text(json.dumps(render,indent=2)+'\n')
brief['strategy']+=' Reference-driven head load/lift/recovery and existing landing debris retimed to independent hoof contacts; never generic periodic neck noise.'
real=brief['expert_plan']['realizations']['phases']
real['method']+=' Poll lowers during load, lifts with rise/crest and dips during grounded absorption. Existing fixed landing dust/clod groups reanchor on measured contact and retain settled solids.'
real['interfaces']+=['Actual forehoof contact → existing world-space earth-response birth; poll/bit movement → rebuilt rein contact']
real['failure_condition']+=' Reject neck kinks/overextension, disconnected reins, FX before contact, missing terrain support or disappearing settled clods.'
real['early_proof']='Actual preparation/rise/crest/landing/recovery phase renders, unchanged anti-braking audit and explicit FX birth records. No static motion qualification.'
for path in ['src/movie_factory/adapters/blender/nihang_motion.py','results/sikh335/motion01/render-review-c3.json',
             'results/sikh335/motion01/landing-audit-c3.json','scripts/sikh336_head_contact_plan.py',
             'results/sikh335/motion01/save-c4-recipe.json','results/sikh335/motion01/render-c4-recipe.json']:
    brief['source_bindings'][path]=bind(path)
for step in art['STRATEGIZING']['steps']:
    step['native_recipe']=bind(f'results/sikh335/motion01/{step["id"]}-c4-recipe.json')
art['DERIVING']['derivations']['phases']={f:real[f] for f in pp.DERIVATION_FIELDS}
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],discriminating_test=real['early_proof'])
art['STRATEGIZING']['resource_scope']='Correction4/max6, second of four newly approved corrections. Existing fixed FX assets only; one serial local worker; no new spend or appearance allowance.'
brief['expert_plan']['challenge'].update(plan_digest=ep.plan_digest(brief),omission_probe='A powerful impact without anticipatory head/body performance remains mechanical; dust must originate at actual contact, not old timing.')
for stage in ('DERIVING','STRATEGIZING'):
    p=c.packet(task);result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],result,'sikh336-head-contact-'+stage)
    (out/(stage.lower()+'-c4.json')).write_text(json.dumps(result,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None)
(out/'head-contact-challenge-input-c4.json').write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['planning_step'])
