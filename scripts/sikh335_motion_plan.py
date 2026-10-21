"""Prospective continuous-performance stage after the closed static control.

Uses source-bound four-stage planning; no provider or direct native launch.
Historical counters and rejected evidence are inherited, not reclassified.
"""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sikh335/motion01'
TASK='sikh335-continuous-performance'
SOURCE='.runtime/art-direction/series01-sikh320/build-10/sequence.blend'

def bind(path):return {'path':path,'sha256':pk.file_hash(ROOT/path)}
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n')

def main():
    OUT.mkdir(exist_ok=True)
    c=wf.Controller(ROOT,DATABASE)
    request=pk.read_json(ROOT,'results/sikh335/request.json')
    request['rationale']='New temporal/integrated interface stage of335 after completed static crest control. Static support cycles2/2 remain closed; this does not reopen331 or grant appearance/AV acceptance.'
    c.route_request('sikh335-motion',request)
    from movie_factory.adapters.blender.nihang_motion import FIELDS
    anchors=[dict(zip(('frame',*FIELDS),row)) for row in [
        (252,0,0,.03,0,0,0),(285,0,0,.03,0,0,0),
        (294,.035,.02,.07,.20,.13,0),(300,.02,.04,.10,.24,.14,0),
        (307,-.12,.06,.12,.10,.12,.18),(317,-.52,.10,.16,-.08,.10,.72),
        (327,-.80,.12,.18,-.18,.10,1),(331,-.79,.12,.18,-.16,.13,1),
        (338,-.65,.10,.14,-.08,.17,.88),(345,-.35,.05,.08,.03,.15,.45),
        (350,0,0,.03,.08,.10,0),(353,.035,-.01,.095,.20,.10,0),
        (360,0,0,.035,.04,.02,0),(370,0,0,.03,0,0,0),(441,0,0,.03,0,0,0)]]
    recipe={'operation':'nihang_patch','frame':327,'width':432,'height':768,'samples':8,
            'edits':[{'kind':'repair_bbone_targets','target':'horse.rig'},
                     {'kind':'supported_motion','target':'horse.rig','anchors':anchors}]}
    save('save-recipe.json',recipe)
    save('render-recipe.json',{'operation':'nihang_frames','frame':327,'width':432,'height':768,'samples':8,
                              'frames':[294,307,317,327,338,345,350,353]})
    previous=c.state('sikh335-supported-representation')
    direction=json.loads(json.dumps(previous['direction']))
    brief=json.loads(json.dumps(previous['brief']))
    knowledge=pk.task_packet(ROOT,pk.read_json(ROOT,'results/sikh335/task.json'))
    assert knowledge['dispatch_ready']
    intent='Construct continuous supported reference-phase rear with coupled rider and rebaked contacts; inspect gather, rise, crest, accelerating descent, impact and absorption before appearance finish and integrated clip.'
    direction.update(intent=intent,deliverable_id=TASK,beat_intents={'rear':intent})
    sources=direction['context_sources']
    sources.append({'id':'crest_control','category':'learnings','binding':bind('results/sikh335/support02/IMAGE_REVIEW.md'),
        'required':True,'status':'adopted','scope':'Static control only; no temporal or rider qualification',
        'statement':'Two static corrections are retained and closed. Crest supports anatomy but reins/spear disconnected and appearance rejected; capture immutable stance before continuous keys.'})
    specs={
        'preservation':('Original320/Pashtun unchanged; new serial derivative and fresh reopen.','production_reuse',['technical']),
        'support':('Visible hind endpoints stay grounded, segment lengths fixed; forelegs return to stance without outward twist or inverted hooves.','anatomy_contact',['technical','image']),
        'phases':('Coordinated gather drives rise; active short crest; forelegs reach and descend without stopping above ground; absorption follows contact.','animation_physics',['technical','image']),
        'rider':('Seat follows horse support while torso counterbalances; no rigid statue or floating/disconnected reins and spear. Limb/garment defects remain blockers, not hidden by contact metrics.','story_performance',['technical','image']),
        'evidence':('All phase images and contact evidence available; static samples never certify full-speed motion, audio or appearance.','camera_editorial',['technical','image'])}
    ids=list(specs);reqs=[{'id':k,'criterion':v[0],'modes':v[2],'director_av':False} for k,v in specs.items()]
    ref=direction['references'][0]
    ref.update(scope='Reference14–19s governs complete preparation to landing, not only crest; actual speed requires later clip.',
               fidelity='Faithful coupled loading, lift, brief crest, accelerating reach/contact and absorption; adapted existing horse proportions.')
    ref['aspects']=[{'id':'whole_pose','instruction':'Compare all visible action phases and body contacts; a smooth trajectory or fixed hoof target does not certify animation.','requirements':ids}]
    applications=pk.read_json(ROOT,'results/sikh335/learning-application.json')
    mapping={k:{'requirements':ids,'reason':v} for k,v in applications.items()}
    app={n:[k for k,v in specs.items() if v[1]==n] for n in ep.LENSES}
    beats=[{'id':'rear','audience_read':'One powerful living animal and mounted rider executing a deliberate salute, not pose interpolation.',
        'framing':'Existing shot camera with8 phase samples; later continuous clip plus revealing side checks.',
        'lenses':{n:{'applies':bool(app[n]),'requirements':app[n],
                    'why':'Needed for support, whole-body coordination, contacts or evidence validity.' if app[n] else
                    'Appearance, dust, audio and crowd remain inherited blockers for next integrated stages; not passed by this motion construction.'} for n in ep.LENSES}}]
    methods={
        'preservation':'Read-only master → numeric trusted choreography → new native → independent reopen.',
        'support':'Capture283 stance once. Fixed-length hind stifle/hock solve and grounded/airborne fore carpus targets with explicit FK authority.',
        'phases':'Reference phase anchors with shape-preserving cubic velocity continuity; dense frame sampling, no hidden Bezier overshoot.',
        'rider':'Pelvis follows new seat frame; torso responds to horse pitch velocity/load. Rebuild reins in curve-local coordinates and spear in world hand line.',
        'evidence':'Render8 actual phase frames from the saved scene; retain target/visible endpoint records and compare whole silhouettes.'}
    real={k:{'beats':['rear'],'lenses':applicable,'derivation':v[0],'method':methods[k],
        'interfaces':['stance → horse support → seat/pelvis/torso','bit/palms → reins/spear','pose → garments/tack/FX caches'],
        'early_proof':'Save technical support measurements before8 phase renders; inspect contact and body silhouette, not target coordinates alone.',
        'failure_condition':'Unreachable chain, angular discontinuity, twisted/float support, visible rider/contact gap, pre-impact slowdown or false static motion approval.',
        'reopen_when':'Any trajectory, rider parent, constraint, camera or cache dependency changes.',
        'priority':'quality_floor','origin':'craft_inference','reference_ids':['reference_rear']}
        for k,v in specs.items() for applicable in [[n for n in ep.LENSES if k in app[n]]]}
    # Keep inherited authority text; replace only scope-specific execution bindings.
    brief.update(intent=intent,scope='335 continuous supported choreography and interface proof; integrated production remains open',
        audience_result=beats[0]['audience_read'],strategy='Whole support representation over reference phases, followed by contact reconstruction and phase review.',
        early_proof='Eight actual phases and support records before high-resolution/whole-clip cost.',
        exclusions='No appearance approval, full-speed AV pass, external action, new asset or new Director direction.',
        requirements=reqs,references=[ref],knowledge_digest=knowledge['packet_digest'],knowledge_mapping=mapping)
    paths=[SOURCE,'results/sikh335/motion01/save-recipe.json','results/sikh335/motion01/render-recipe.json',
           'results/sikh335/support01/IMAGE_REVIEW.md','results/sikh335/support02/IMAGE_REVIEW.md',
           'src/movie_factory/adapters/blender/nihang_support.py','src/movie_factory/adapters/blender/nihang_motion.py',
           'src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/adapters/blender/nihang_control.py',
           'src/movie_factory/native_admission.py','scripts/sikh335_motion_plan.py']
    brief['source_bindings']={s['id']:s['binding'] for s in sources}|{p:bind(p) for p in paths}
    brief['expert_plan']={'version':1,'beat_intents':{'rear':intent},'beats':beats,'realizations':real}
    brief['expert_plan']['challenge']={'plan_digest':ep.plan_digest(brief),'open_issues':[],
        'intent_coverage':{'rear':{'reason':'Support, temporal phases, rider contacts and evidence boundaries derived explicitly.','requirements':ids}},
        'cross_discipline_conflicts':'New support trajectory invalidates existing rider limbs, garment/tack and impactFX; record rather than pass untouched interfaces.',
        'omission_probe':'Even mathematically grounded legs can form bad knees or grotesque silhouette; see every phase and actual contact.',
        'scope_tradeoff':'Eight phase images cheaply reject structural defects, but never stand in for full-speed Director AV review.'}
    brief['reference_plan']={'reference_rear':{'reference_digest':pk.digest(ref),'application':'Compare whole action phases, supported anatomy and rapid impact; no exact identity or still-based timing approval.'}}
    c.create(TASK,'production',bind('results/sikh335/REQUEST.md'),'sikh335-motion-create',max_corrections=2,
             direction=direction,mode='local_native',admission='sikh335-motion')
    art={
        'GROUNDING':{'uses':{s['id']:{'disposition':'apply','reason':s['statement'],'implication':s['statement']} for s in sources},
            'knowledge_uses':applications,'reconciliation':'Inherit original335 scope and closed331/static335 evidence. Distinct temporal/contact stage; no reset or reinterpretation of failed crest trials. No325 runtime calls.','unresolved':[]},
        'DERIVING':{'requirements':reqs,'beats':beats,'derivations':{k:{f:v[f] for f in pp.DERIVATION_FIELDS} for k,v in real.items()},
            'context_mapping':{s['id']:{'requirements':ids,'reason':s['statement']} for s in sources},'knowledge_mapping':mapping},
        'STRATEGIZING':{'brief':brief,'method_choice':{'chosen':brief['strategy'],
            'alternatives':'Do not retime root-rotation curves again, restore unknown drivers, recapture modified baseline or use independent easing phases stopping at impact.',
            'evidence_status':'hypothesis','discriminating_test':'Fixed-support whole action with correctly rebaked contacts survives all phase silhouettes; metrics cannot waive visible failures.'},
            'steps':[{'id':'save','kind':'proof','depends_on':[],'requirements':['preservation','support','phases','rider'],
                      'acceptance':'Healthy native dependency state and190 authored frames with actual support evidence; visual/contact quality deferred to phase images.',
                      'native_recipe':bind('results/sikh335/motion01/save-recipe.json')},
                     {'id':'render','kind':'proof','depends_on':['save'],'requirements':ids,
                      'acceptance':'Actual8 frame comparison; no known contact or silhouette error passed. AV/appearance explicitly NOT_RUN.',
                      'native_recipe':bind('results/sikh335/motion01/render-recipe.json')}],
            'resource_scope':'One local heavy job at a time; existing assets only, bounded190frames,8diagnosticimages. Two corrections for this temporal proof, retained prior static2/2 history.',
            'replan_triggers':'Unreachable baseline/limb chain, rider-fit failure or bad phase silhouette returns to affected method; never wardrobe camouflage or silent widening.'}}
    for stage in pp.STEPS[:3]:
        p=c.packet(TASK);result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
        c.submit(TASK,p['actor'],p['ticket'],result,'sikh335-motion-'+stage);save(stage.lower()+'.json',result)
    p=c.packet(TASK);p.pop('ticket',None);save('challenge-input.json',p)
    print(c.state(TASK)['planning_step'])

if __name__=='__main__':main()
