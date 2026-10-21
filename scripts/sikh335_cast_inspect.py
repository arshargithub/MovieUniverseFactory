"""Independent read-only supporting-cast inventory; zero correction allowance.

Does not resume the failed motion task or enlarge its correction limit.
"""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
from movie_factory.native_admission import Bridge,BLENDER_BIN
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/sikh335/cast-inspect';TASK='sikh335-cast-inventory'
def bind(p):return {'path':p,'sha256':pk.file_hash(ROOT/p)}
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n')

def plan():
    OUT.mkdir(exist_ok=True);c=wf.Controller(ROOT,DATABASE)
    req=pk.read_json(ROOT,'results/sikh335/request.json')
    req['operations']=['native_inspect','asset','code','test','document']
    req['rationale']='Independent read-only supporting-cast inventory while motion remains failed and its retry extension is pending. No art authoring, native edits or correction reset.'
    c.route_request('sikh335-cast-inspect',req)
    old=c.state('sikh335-control-ownership');direction=json.loads(json.dumps(old['direction']))
    art=json.loads(json.dumps(old['planning_artifacts']));brief=art['STRATEGIZING']['brief']
    intent='Inspect actual leader and nearest crowd mesh, pose-cache and material ownership against observed same-film shortcomings before adapting their appearance.'
    direction.update(intent=intent,deliverable_id=TASK,beat_intents={'ownership':intent})
    specs={
        'preservation':'Read-only inventory leaves accepted Pashtun, source320 and blocked motion candidate2 untouched.',
        'ownership':'Report real leader/near crowd garment, turban, face/hair, saddle-accessory owners, local transforms, mesh counts and material nodes.',
        'support':'Identify shape-key and parent interfaces that appearance changes must preserve; do not introduce new cloth/limb gaps.',
        'no_false_pass':'Inventory is not same-film appearance approval or a motion retry; visible schematic costume and glossy horse remain rejected.'}
    for row in brief['requirements']:row['criterion']=specs[row['id']]
    brief.update(intent=intent,audience_result='Subsequent appearance work changes the actual material/mesh owners rather than adding unbound decorative layers.',
        strategy='Read-only compact component inventory on existing source320; inspect local material graphs and cached garment ownership before construction.',
        early_proof='Inventory before any topology/material modification.',scope='Independent read-only supporting-cast prerequisite',
        exclusions='No motion correction, appearance authoring or approval, provider, acquisition, cloud or upload.')
    brief['expert_plan']['beat_intents']={'ownership':intent}
    brief['expert_plan']['beats'][0]['audience_read']=brief['audience_result']
    brief['expert_plan']['beats'][0]['framing']='Current supporting-actor source, at283; same-film image comparison informs diagnosis, not production review.'
    for k,v in brief['expert_plan']['realizations'].items():
        v.update(derivation=specs[k],method=brief['strategy'],early_proof=brief['early_proof'],
                 interfaces=['actor parents → garment pose caches → surface/material ownership → later motion merge'],
                 failure_condition='Missing component owners or treating inventory as appearance quality.',reopen_when='Supporting asset geometry, material assignment or parent/cache ownership changes.')
    ref=direction['references'][0];ref['scope']='Preserve original rearing authority for later interface merge; this read-only stage cannot qualify action.'
    ref['aspects'][0]['instruction']='Discover supporting-actor attachments needed to survive the reference performance; no new motion work.'
    brief['references']=[ref]
    brief['reference_plan']={'reference_rear':{'reference_digest':pk.digest(ref),'application':ref['aspects'][0]['instruction']}}
    source='.runtime/art-direction/series01-sikh320/build-10/sequence.blend'
    recipe={'operation':'nihang_cast_inspect','frame':283,'width':64,'height':64,'samples':1};save('recipe.json',recipe)
    paths=[source,'results/sikh335/cast-inspect/recipe.json','src/movie_factory/adapters/blender/nihang_control.py',
           'src/movie_factory/native_admission.py','scripts/sikh335_cast_inspect.py',
           '.runtime/art-direction/series01-finish248/opening08/actual-450.png','results/sikh335/motion01/PHASE_REVIEW_C2.md']
    brief['source_bindings']={s['id']:s['binding'] for s in direction['context_sources']}|{p:bind(p) for p in paths}
    knowledge=pk.task_packet(ROOT,pk.read_json(ROOT,'results/sikh335/task.json'));assert knowledge['dispatch_ready']
    brief['knowledge_digest']=knowledge['packet_digest'];direction['knowledge_digest']=knowledge['packet_digest']
    brief['expert_plan']['challenge'].update(plan_digest=ep.plan_digest(brief),
        cross_discipline_conflicts='Appearance must preserve garment pose caches and future horse/rider contacts; current motion failure stays blocked.',
        omission_probe='Procedural texture may exist but be assigned to the wrong visible material; inspect ownership, not source function intent.',
        scope_tradeoff='Read-only supporting-cast inspection can proceed independently without consuming another motion attempt.')
    art['DERIVING']['requirements']=brief['requirements'];art['DERIVING']['beats']=brief['expert_plan']['beats']
    art['DERIVING']['derivations']={k:{f:v[f] for f in pp.DERIVATION_FIELDS} for k,v in brief['expert_plan']['realizations'].items()}
    art['STRATEGIZING'].update(brief=brief,method_choice={'chosen':brief['strategy'],
        'alternatives':'Do not add another cloth layer or blindly increase texture strength before checking real visible owners.',
        'evidence_status':'hypothesis','discriminating_test':'Inventory identifies actual mesh/material/cache owners needed for faithful appearance changes.'},
        steps=[{'id':'inspect','kind':'proof','depends_on':[],'requirements':list(specs),
                'acceptance':'Actual read-only cast report with no new native or image; no appearance or motion pass.',
                'native_recipe':bind('results/sikh335/cast-inspect/recipe.json')}],
        resource_scope='One local read-only job; zero corrections authorized in this inventory task. Motion task remains blocked pending its existing question.',
        replan_triggers='Missing ownership evidence requires diagnosis, not unbound writes or motion retry.')
    c.create(TASK,'production',bind('results/sikh335/REQUEST.md'),'sikh335-cast-create',max_corrections=0,
             direction=direction,mode='local_native',admission='sikh335-cast-inspect')
    for stage in pp.STEPS[:3]:
        p=c.packet(TASK);result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
        c.submit(TASK,p['actor'],p['ticket'],result,'sikh335-cast-'+stage);save(stage.lower()+'.json',result)
    p=c.packet(TASK);p.pop('ticket',None);save('challenge-input.json',p)
    print(c.state(TASK)['planning_step'])

def dispatch():
    c=wf.Controller(ROOT,DATABASE);p=c.packet(TASK)
    v=pk.read_json(ROOT,'results/sikh335/cast-inspect/challenge-verdict.json');v['input_digest']=p['planning_input_digest']
    c.submit(TASK,p['actor'],p['ticket'],v,'sikh335-cast-challenge')
    run=Bridge(c).dispatch(TASK,'inspect','sikh335-cast-inspection',parent=bind('.runtime/art-direction/series01-sikh320/build-10/sequence.blend'),
        blender_bin=BLENDER_BIN,timeout=300,recipe=bind('results/sikh335/cast-inspect/recipe.json'))
    save('inspect-run.json',run);print(json.dumps({'status':run['status'],'error':run.get('error'),'artifacts':run.get('artifacts')},indent=2))

if __name__=='__main__':
    {'plan':plan,'dispatch':dispatch}[sys.argv[1]]()
