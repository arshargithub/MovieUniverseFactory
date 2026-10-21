"""Last appearance correction: fresh planning and challenge, history retained."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/look01'
c=wf.Controller(root,DATABASE);task='sikh335-supporting-appearance'
state=c.state(task)
if state['cycle']==3:
    d=state['direction']
    c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
      'Five real c3 images FAIL. Replace analytic anatomical envelope with isolated collision-supported cloth drape; repair explicit collar and crown seams and stale camera transform. Preserve original authority, candidate5 parent, all failures and counters.',
      'sikh337-look-drape-reground')
assert c.state(task)['cycle']==4
art={s:pk.read_json(root,f'results/sikh335/look01/{s.lower()}-c3.json')['artifact'] for s in pp.STEPS[:3]}
brief=art['STRATEGIZING']['brief']
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
def save(name,data):
    p=out/name
    if p.exists():assert json.loads(p.read_text())==data
    else:p.write_text(json.dumps(data,indent=2)+'\n')
for p in list(brief['source_bindings']):
    if p.startswith(('src/movie_factory/adapters/blender/nihang_','tests/test_nihang337')):
        brief['source_bindings'][p]=bind(p)
for p in ['src/movie_factory/adapters/blender/nihang_drape.py','tests/test_nihang337_drape.py',
          'results/sikh335/look01/STRATEGY_C4.md','results/sikh335/look01/render-review-c3.json',
          'results/sikh335/look01/leader_front-review-c3.json','results/sikh335/look01/leader_reverse-review-c3.json',
          'scripts/sikh337_look_drape_plan.py']:
    brief['source_bindings'][p]=bind(p)
art['GROUNDING']['reconciliation']+=' Correction3 five-image evidence rejected body-hugging analytic cloth, angular collar, crown seam and face integration. Use collision-supported cloth proof, not another untested analytic wrinkle patch; same authority and references.'
real=brief['expert_plan']['realizations']
real['form']['method']='Isolated temporary Blender scene settles posed shirt against contracted collision proxy, pins shoulder/cuff/waist, transfers bounded central torso displacement to all existing caches. Weld exact crown duplicates; lower collar; retain continuous shirt beneath removed planar panel. Static drape is not animated cloth qualification.'
real['form']['failure_condition']='Nonfinite/excessive displacement, topology mismatch, bodysuit or inflated cloth, broken crest/cache transfer, unsupported collar, crown helmet, mannequin face or floating pad rejects; numerical success cannot waive these.'
real['evidence']['method']='Same two shot frames and three diagnostic views, with evaluated camera matrix captured after dependency update. Static evidence only; all known appearance defects must close before propagation.'
real['evidence']['early_proof']='Actual saved derivative, stance/crest plus front/reverse and near-warrior comparison against accepted quality floor; failed evidence stays internal.'
for rid in ('form','evidence'):art['DERIVING']['derivations'][rid]={f:real[rid][f] for f in pp.DERIVATION_FIELDS}
brief['strategy']='Replace failed envelope method with physically settled static drape proof, repair independent crown/collar/evidence defects, and test all interfaces before any propagation or motion qualification.'
brief['expert_plan']['challenge'].update(
 omission_probe='Cloth convergence does not address weak eyes/beard or helmet silhouette; those remain explicit vetoes. A source-shirt collider is a prototype approximation, not a human body simulation.',
 cross_discipline_conflicts='Rest-pose displacement across207 cached poses may violate the crest; no full-speed or contact pass follows from static convergence.',
 scope_tradeoff='Two actors only, last appearance correction. No new spend, master edits or release claims; independent motion remains authorized.')
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],evidence_status='hypothesis',
 alternatives='Do not continue embossed musculature or add surface noise. Local solver proof uses existing topology with guarded deformation; failure means this method is not admitted.',
 discriminating_test=real['evidence']['early_proof'])
art['STRATEGIZING']['resource_scope']='Appearance correction4/max4, one isolated native save and five images serially; no additional spend or providers.'
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,'sikh337-look-c4-'+stage);save(stage.lower()+'-c4.json',response)
p=c.packet(task);p.pop('ticket',None);save('challenge-input-c4.json',p)
print(c.state(task)['planning_step'])
