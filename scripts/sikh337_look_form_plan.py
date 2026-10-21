"""Correction3 changes failed forms and adds explicit revealing evidence views."""
import copy,json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/look01'
c=wf.Controller(root,DATABASE);task='sikh335-supporting-appearance'
state=c.state(task)
if state['cycle']==2:
    d=state['direction']
    c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
        'Actual c2 images fail regular cone crown and bodysuit form;390 occludes the test actor. Reviewed cloth-course/envelope/beard/coat changes and fixed diagnostic camera evidence replace those methods, retaining original references, parent and correction history.',
        'sikh337-look-form-reground')
assert c.state(task)['cycle']==3
art={s:pk.read_json(root,f'results/sikh335/look01/{s.lower()}-c2.json')['artifact'] for s in pp.STEPS[:3]}
brief=art['STRATEGIZING']['brief']
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
def save(name,data):
    p=out/name
    if p.exists():
        assert json.loads(p.read_text())==data
    else:p.write_text(json.dumps(data,indent=2)+'\n')
paths=['src/movie_factory/adapters/blender/nihang_look.py','src/movie_factory/adapters/blender/nihang_control.py',
       'src/movie_factory/native_admission.py','tests/test_nihang337_garment.py',
       'results/sikh335/look01/STRATEGY_C3.md','results/sikh335/look01/render-review-c2.json',
       'scripts/sikh337_look_form_plan.py']
for p in paths:brief['source_bindings'][p]=bind(p)
art['GROUNDING']['reconciliation']+=' Actual correction2 images rejected ring-cone crown and smooth bodysuit. The crowd image was not a useful proof. Correction3 changes whole cloth form, preserves dark horse identity and adds explicitly labeled diagnostic views without changing shot cameras.'
real=brief['expert_plan']['realizations']
real['form']['method']='Overlapping broad oblique cloth courses on a rounded asymmetric crown; torso cloth cross-section bridging anatomy with restrained waist/shoulder folds; broaden lower beard across its existing inertial shape keys; preserve dark authored horse UV coat with less polished specular response. Retain actual-surface saddle pad.'
real['form']['failure_condition']='Cone/helmet/rings, inflated spherical torso or repeated grooves, beard detached from skin, slick molded horse, hovering pad or weak same-film coherence reject the candidate.'
real['evidence']['method']='Inspect production283/327 plus temporary leader front/reverse and nearby warrior views. View enum and camera matrix are bound in manifest; production camera and native source remain unchanged. Extra views are diagnostics, not edited shots.'
real['evidence']['early_proof']='Two actual shot frames and three explicit revealing views; inspect all known form failures and interfaces before propagation.'
for rid in ('form','evidence'):
    art['DERIVING']['derivations'][rid]={f:real[rid][f] for f in pp.DERIVATION_FIELDS}
brief['expert_plan']['beats'][0]['framing']='Actual283 stance and327 crest plus labeled temporary leader front/reverse and near-crowd diagnostic views; no production camera edit.'
art['DERIVING']['beats']=brief['expert_plan']['beats']
brief['strategy']='Change failed cloth representation and visible material hierarchy, not surface noise on the rejected forms. Prove two actors and dark horse coat at actual shot framing and revealing temporary views; preserve primary motion and original assets.'
brief['expert_plan']['challenge'].update(
    omission_probe='A temporary view is not production framing; both are required. Beard has animated shape keys, so all must carry the same form repair. Tests of view enums do not prove the camera reveals the actor.',
    cross_discipline_conflicts='Looser cloth must preserve sash/cuff fit in rearing; broader beard must retain skin attachment and cached motion; matte coat must not erase dark horse form.',
    scope_tradeoff='Leader and one near actor only until actual proof passes; no principal, lighting, crowd trajectory, audio or full-speed acceptance.')
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
render={'operation':'nihang_frames','frame':283,'width':540,'height':960,'samples':16,'frames':[283,327]}
save('render-c3-recipe.json',render)
steps=copy.deepcopy(art['STRATEGIZING']['steps'])
steps[1]['native_recipe']=bind('results/sikh335/look01/render-c3-recipe.json')
steps[1]['acceptance']='Production stance/crest comparison; known form failures reject. Temporary revealing views follow independently, never hidden by shot framing.'
for view in ('leader_front','leader_reverse','crowd_front'):
    recipe=render|{'frames':[283],'view':view}
    name=view+'-c3-recipe.json';save(name,recipe);binding=bind('results/sikh335/look01/'+name)
    brief['source_bindings'][binding['path']]=binding
    steps.append({'id':view,'kind':'proof','depends_on':['save'],
                  'requirements':['form','interfaces','evidence'],
                  'acceptance':'Correctly labeled unchanged-scene diagnostic view must reveal the actor; inspect complete cloth/head/tack interfaces. It is not a production-camera or full-speed pass.',
                  'native_recipe':binding})
brief['source_bindings'][steps[1]['native_recipe']['path']]=steps[1]['native_recipe']
art['STRATEGIZING']['steps']=steps
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],evidence_status='hypothesis',
    alternatives='Do not keep refining the regular helical cone or inflate the original muscle surface. Retain native source, pose caches and supported pad; change failed whole-form construction.',
    discriminating_test=real['evidence']['early_proof'])
art['STRATEGIZING']['resource_scope']='Appearance correction3/max4; five local diagnostic images and one derivative, serial. No new spending, providers, accepted-master edits or release approval.'
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,'sikh337-look-c3-'+stage)
    save(stage.lower()+'-c3.json',response)
p=c.packet(task);p.pop('ticket',None);save('challenge-input-c3.json',p)
print(c.state(task)['planning_step'])
