"""Second internal335 stage: supported crest discriminating proof.

The completed read-only diagnostic is not an artistic attempt. This retains
its evidence and starts the first representation candidate, max two corrections.
"""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk, production_workflow as wf, planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE

root=Path(__file__).resolve().parents[1]; out=root/'results/sikh335/support01'; out.mkdir(exist_ok=True)
def save(name,v): (out/name).write_text(json.dumps(v,indent=2)+'\n')
def bind(p): return {'path':p,'sha256':pk.file_hash(root/p)}
c=wf.Controller(root,DATABASE); task='sikh335-supported-representation'
request=pk.read_json(root,'results/sikh335/request.json')
request['rationale']='Internal335 supported-pose proof after completed read-only ownership diagnosis; first artistic representation candidate, not a331 retry or a new Director request.'
c.route_request('sikh335-support',request)
recipe={'operation':'nihang_patch','frame':327,'width':540,'height':960,'samples':8,
    'edits':[{'kind':'repair_bbone_targets','target':'horse.rig'},
        {'kind':'supported_pose','target':'horse.rig','frame':327,'pitch':-.8,'hip_back':.12,
         'hip_drop':.18,'neck_pitch':-.05,'poll_pitch':.60}]}
save('save-recipe.json',recipe)
save('render-recipe.json',{k:('nihang_render' if k=='operation' else v) for k,v in recipe.items() if k!='edits'})
old=c.state('sikh335-control-ownership')
direction=json.loads(json.dumps(old['direction']))
knowledge=pk.task_packet(root,pk.read_json(root,'results/sikh335/task.json')); assert knowledge['dispatch_ready']
intent='Prove explicit fixed-length supported crest representation and healthy driver targets before continuous animation or supporting-character finish.'
direction.update(intent=intent,deliverable_id=task,beat_intents={'crest':intent})
specs={
 'preservation':('No original or accepted media changes; derivative only.','production_reuse',['technical']),
 'driver_health':('All64 same-rig BBone properties resolve; no invalid used drivers remain. No generic restoration of removed controls.','animation_physics',['technical']),
 'support':('Fixed-length stifle/hock solution preserves planted visible hind hooves and non-stretched limbs with one explicit owner.','anatomy_contact',['technical','image']),
 'whole_pose':('Crest visibly coordinates bent hindquarters, lifted chest, flexed neck/poll and folded forelegs; reject rigid column, outward hooves and unsupported silhouette.','animation_physics',['image']),
 'persistence':('Fresh-open image uses the saved derivative; selected native state/dependencies unchanged.','production_reuse',['technical'])}
ids=list(specs)
ref=direction['references'][0]
ref['scope']='Crest phase within14–19s, diagnostic source camera327. Continuous motion and appearance remain separate blockers.'
ref['aspects'][0]['requirements']=ids
ref['aspects'][0]['instruction']='Compare complete supported crest, not independent joint angles; static proof does not certify dynamics.'
sources=direction['context_sources']
sources.append({'id':'ownership_diagnosis','category':'learnings','binding':bind('results/sikh335/CONTROL_FINDINGS.md'),
    'status':'adopted','required':True,'statement':'64 missing targets are BBone ease; missing object drivers leave IK/FK properties ineffective. Select actual constraints and solve bone lengths explicitly.',
    'scope':'335 explicit ownership and support representation'})
brief=json.loads(json.dumps(old['brief']))
brief.update(intent=intent,scope='335 first supported crest proof; not full-motion or appearance acceptance',
    audience_result='Horse reads as a supported coordinated animal rather than an upright rigid pivot.',
    strategy='Resolve only proven BBone paths; explicitly choose FK and use fixed-length whole-leg endpoint solving around a lowered pelvis.',
    early_proof='One supported crest at327, saved and independently reopened before animation expansion.',
    exclusions='Full clip, rider-contact/cache qualification, leader/crowd finish, AV pass, paid calls, cloud and publication.',
    knowledge_digest=knowledge['packet_digest'], references=direction['references'])
reqs=[{'id':k,'criterion':v[0],'modes':v[2],'director_av':False} for k,v in specs.items()]
brief['requirements']=reqs
brief['source_bindings']={s['id']:s['binding'] for s in sources}
for p in ['.runtime/art-direction/series01-sikh320/build-10/sequence.blend',
          'results/sikh335/support01/save-recipe.json','results/sikh335/support01/render-recipe.json',
          'src/movie_factory/adapters/blender/nihang_support.py','src/movie_factory/adapters/blender/nihang_patch.py',
          'src/movie_factory/adapters/blender/nihang_control.py','scripts/sikh335_support_plan.py']:
    brief['source_bindings'][p]=bind(p)
applications=pk.read_json(root,'results/sikh335/learning-application.json')
mapping={k:{'requirements':ids,'reason':v} for k,v in applications.items()}
brief['knowledge_mapping']=mapping
app={n:[k for k,v in specs.items() if v[1]==n] for n in ep.LENSES}
app['camera_editorial']=['whole_pose']
beats=[{'id':'crest','audience_read':'Powerful supported rear, not a rigid rotated statue.',
    'framing':'Existing source-camera crest327; single-frame discriminating proof, not whole sequence.',
    'lenses':{n:{'applies':bool(app[n]),'why':('Required for actual silhouette, support, ownership or persistence proof.' if app[n] else
        'Not mutated in this crest test; rider performance, costume, effects and sound remain unqualified downstream.'),'requirements':app[n]} for n in ep.LENSES}}]
real={k:{'beats':['crest'],'lenses':[n for n,rs in app.items() if k in rs], 'derivation':v[0],
    'method':'Explicit typed rig ownership and fixed-length endpoint solver; inspect diagnostic image and actual joint positions.',
    'interfaces':['pelvis → stifle/hock → world-planted hoof','neck/poll → head silhouette','source → save → fresh render'],
    'early_proof':'Crest327 plus visible hoof endpoint and bone-length measurements before temporal expansion.',
    'failure_condition':'Invalid dependency, stretching, lost ground contact, grotesque or rigid full silhouette, source drift.',
    'reopen_when':'Pose parameters, framing, control ownership, source or handler changes.', 'priority':'quality_floor',
    'origin':'craft_inference','reference_ids':['reference_rear']} for k,v in specs.items()}
brief['expert_plan']={'version':1,'beat_intents':{'crest':intent},'beats':beats,'realizations':real}
brief['expert_plan']['challenge']={'plan_digest':ep.plan_digest(brief),'open_issues':[],
    'intent_coverage':{'crest':{'reason':'Fixed support and whole silhouette explicitly tested before motion expansion.','requirements':ids}},
    'cross_discipline_conflicts':'Horse pose changes reopen rider, tack, reins and clothing; these are not hidden or passed in this pose-only proof.',
    'omission_probe':'Correct target coordinates can still yield a bad silhouette or crease; inspect actual rendered form.',
    'scope_tradeoff':'One diagnostic frame minimizes render waste; no claim of final look or dynamic quality.'}
brief['reference_plan']={'reference_rear':{'reference_digest':pk.digest(ref),'application':'Whole supported crest comparison; not a frame-perfect identity or pose match.'}}
c.create(task,'production',bind('results/sikh335/REQUEST.md'),'sikh335-support-create',max_corrections=2,
    direction=direction,mode='local_native',admission='sikh335-support')
artifacts={
 'GROUNDING':{'uses':{s['id']:{'disposition':'apply','reason':s['statement'],'implication':s['statement']} for s in sources},
    'knowledge_uses':applications,'reconciliation':'Actual335 inspection narrows334 assumptions; former331 trials remain closed. This is first supported representation candidate, not renewed offset corrections.','unresolved':[]},
 'DERIVING':{'requirements':reqs,'beats':beats,'derivations':{k:{f:v[f] for f in pp.DERIVATION_FIELDS} for k,v in real.items()},
    'context_mapping':{s['id']:{'requirements':ids,'reason':s['statement']} for s in sources},'knowledge_mapping':mapping},
 'STRATEGIZING':{'brief':brief,'method_choice':{'chosen':brief['strategy'],
    'alternatives':'Do not restore all Rigify drivers blindly, stretch legs to ground or repeat root-pivot angle offsets; do not replace weighted horse without a failed discriminating test.',
    'evidence_status':'hypothesis','discriminating_test':'Healthy BBone dependencies plus fixed-length supported crest must visibly differ from rigid column while preserving grounded hooves.'},
    'steps':[{'id':'save','kind':'proof','depends_on':[],'requirements':['preservation','driver_health','support'],
        'acceptance':'Actual saved scene, no invalid used driver, measured fixed-length support; appearance is judged only on dependent image.',
        'native_recipe':bind('results/sikh335/support01/save-recipe.json')},
       {'id':'render','kind':'proof','depends_on':['save'],'requirements':['whole_pose','support','persistence'],
        'acceptance':'Fresh-open state consistency and actual image compared with reference; bad silhouette fails regardless of numeric support.',
        'native_recipe':bind('results/sikh335/support01/render-recipe.json')}],
    'resource_scope':'Serial local Blender, existing asset, bounded typed operations; no provider/cloud calls. First representation proof,2 correction ceiling unchanged.',
    'replan_triggers':'Unreachable fixed-length chain, bad ownership or failed whole silhouette triggers method review, not clothing camouflage or more root offsets.'}}
for stage in pp.STEPS[:3]:
    p=c.packet(task); result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':artifacts[stage]}
    c.submit(task,p['actor'],p['ticket'],result,'sikh335-support-'+stage); save(stage.lower()+'.json',result)
p=c.packet(task);p.pop('ticket',None);save('challenge-input.json',p)
print(c.state(task)['planning_step'])
