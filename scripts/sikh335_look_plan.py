"""Initial independent appearance proof; does not reset the failed motion task."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results/sikh335/look01'; TASK='sikh335-supporting-appearance'
SOURCE='.runtime/art-direction/series01-sikh320/build-10/sequence.blend'
def bind(p):return {'path':p,'sha256':pk.file_hash(ROOT/p)}
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n')

def main():
    OUT.mkdir(exist_ok=True); c=wf.Controller(ROOT,DATABASE)
    request=pk.read_json(ROOT,'results/sikh335/request.json')
    request['rationale']='Initial independent supporting-appearance proof for two existing actors and saddle. No further motion correction or reset of its exhausted allowance.'
    c.route_request('sikh335-look',request)
    old=c.state('sikh335-cast-inventory'); direction=json.loads(json.dumps(old['direction']))
    intent='Test structural supporting-costume adaptation on the leader and nearest crowd member before propagation; preserve existing pose caches and original same-film quality floor.'
    direction.update(intent=intent,deliverable_id=TASK,beat_intents={'appearance':intent})
    direction['context_sources'].append({'id':'cast_findings','category':'learnings','binding':bind('results/sikh335/cast-inspect/FINDINGS.md'),
        'required':True,'status':'adopted','scope':'Actual cast ownership and limits of inventory',
        'statement':'High topology and assigned texture already exist. Address cylindrical turban, smooth costume silhouette and unsupported saddle form before extra surface noise; preserve207 garment pose keys.'})
    knowledge=pk.task_packet(ROOT,pk.read_json(ROOT,'results/sikh335/task.json'));assert knowledge['dispatch_ready']
    direction['knowledge_digest']=knowledge['packet_digest']
    ref=direction['references'][0]
    ref['scope']='Preserve faithful rearing performance authority; appearance must survive existing moving parents, but motion remains rejected in the separate task.'
    ref['aspects'][0]['instruction']='Check that costume and saddle remain attached through stance and crest; this does not qualify reference action.'
    quality=json.loads(json.dumps(ref));quality.update(id='accepted_film',scope='Accepted Pashtun quality comparator; no identity copying or modification.',fidelity='Comparable material, cloth construction and living-character readability at intended framing.')
    # Keep the established reference contract and replace its exact file binding.
    quality['binding']=bind('.runtime/art-direction/series01-finish248/opening08/actual-450.png')
    quality['aspects']=[{'id':'whole_pose','instruction':'Compare believable textile structure and integrated supporting character against accepted film image, not rejected320 alone.','requirements':['form','evidence']}]
    direction['references']=[ref,quality]
    specs={
        'preservation':('Original320, accepted Pashtun and failed motion2 remain untouched; all new assets stay local derivative.','production_reuse'),
        'form':('Wrapped crown reads as layered Sikh cloth rather than a cylinder; clothing has supported volume and waist-origin folds; saddle pad follows actual horse surface.','story_performance'),
        'interfaces':('Existing207 garment poses, head parents, sash, horse and rider interfaces remain intact; no hovering or clipping accepted as detail.','anatomy_contact'),
        'evidence':('Actual stance, crest and nearest-crowd images compared with accepted film floor; head/beard/horse surface and full-speed motion remain open, not passed by this limited proof.','camera_editorial')}
    ids=list(specs);ref['aspects'][0]['requirements']=ids
    reqs=[{'id':k,'criterion':v[0],'modes':['technical'] if k=='preservation' else ['technical','image'],'director_av':False} for k,v in specs.items()]
    applications=pk.read_json(ROOT,'results/sikh335/learning-application.json')
    mapping={k:{'requirements':ids,'reason':v} for k,v in applications.items()}
    lenses={n:[k for k,v in specs.items() if v[1]==n] for n in ep.LENSES}
    beats=[{'id':'appearance','audience_read':'A materially credible supporting warrior in the same film, not a dressed mannequin.',
        'framing':'Existing283 stance,327 crest and390 crowd cameras; diagnostic samples only, no entire sequence render.',
        'lenses':{n:{'applies':bool(lenses[n]),'requirements':lenses[n],'why':'Required for source-preserving costume construction and visual proof.' if lenses[n] else 'Existing motion, FX and audio remain unqualified and unchanged by this appearance-only construction.'} for n in ep.LENSES}}]
    strategy='Fixed trusted local handler adapts actual owned meshes: tapered layered crown, garment-volume changes applied to all cache poses, actual torso-fitted sash and horse-surface saddle pad. Test two actors before propagation.'
    real={k:{'beats':['appearance'],'lenses':[n for n in ep.LENSES if k in lenses[n]],'derivation':v[0],
        'method':strategy,'interfaces':['crown → head parent','garment basis → all207 cache poses → sash','saddle body surface → moving horse → rider legs'],
        'early_proof':'Save with retained cache/ownership evidence, then three actual diagnostic images.',
        'failure_condition':'Cone/hat appearance, decorative ridges instead of folds, new cache gap, floating saddle, weakened identity or false same-film pass.',
        'reopen_when':'Any form, material, camera or motion dependency changes.','priority':'quality_floor','origin':'craft_inference','reference_ids':['reference_rear','accepted_film']} for k,v in specs.items()}
    save('save-recipe.json',{'operation':'nihang_patch','frame':283,'width':540,'height':960,'samples':16,
        'edits':[{'kind':'repair_bbone_targets','target':'horse.rig'},{'kind':'supporting_look','target':'mounted leader'}]})
    save('render-recipe.json',{'operation':'nihang_frames','frame':283,'width':540,'height':960,'samples':16,'frames':[283,327,390]})
    paths=[SOURCE,'results/sikh335/cast-inspect/FINDINGS.md','results/sikh335/motion01/PHASE_REVIEW_C2.md',
        'results/sikh335/look01/save-recipe.json','results/sikh335/look01/render-recipe.json',
        'src/movie_factory/adapters/blender/nihang_look.py','src/movie_factory/adapters/blender/nihang_patch.py',
        'src/movie_factory/adapters/blender/nihang_control.py','src/movie_factory/native_admission.py','scripts/sikh335_look_plan.py',quality['binding']['path']]
    brief=json.loads(json.dumps(old['brief']))
    brief.update(intent=intent,scope='Initial supporting appearance proof only; no motion retry or production pass.',
        audience_result=beats[0]['audience_read'],strategy=strategy,early_proof=real['form']['early_proof'],
        exclusions='No replacement principal, provider, image generation, asset acquisition, cloud, upload, motion correction or acceptance.',
        requirements=reqs,references=direction['references'],knowledge_digest=knowledge['packet_digest'],knowledge_mapping=mapping,
        source_bindings={s['id']:s['binding'] for s in direction['context_sources']}|{p:bind(p) for p in paths})
    brief['expert_plan']={'version':1,'beat_intents':{'appearance':intent},'beats':beats,'realizations':real}
    brief['expert_plan']['challenge']={'plan_digest':ep.plan_digest(brief),'open_issues':[],
        'intent_coverage':{'appearance':{'reason':'Form, supporting interfaces, preservation and actual visual rejection criteria.','requirements':ids}},
        'cross_discipline_conflicts':'Decorative geometry can break caches and contact; modify all poses and inspect under existing motion before propagation.',
        'omission_probe':'Mathematical winding can still read as a cone; three images are an early rejection test, not proof of complete supporting-character quality.',
        'scope_tradeoff':'Two actors and a saddle expose method failure without spending on the whole crowd. Head/beard and horse surface remain open.'}
    brief['reference_plan']={r['id']:{'reference_digest':pk.digest(r),'application':r['aspects'][0]['instruction']} for r in direction['references']}
    art={'GROUNDING':{'uses':{s['id']:{'disposition':'apply','reason':s['statement'],'implication':s['statement']} for s in direction['context_sources']},
        'knowledge_uses':applications,'reconciliation':'Initial appearance work is independent of the failed two-correction motion task. No resets, spread, new correction allowance or claim of semantic qualification.','unresolved':[]},
        'DERIVING':{'requirements':reqs,'beats':beats,'derivations':{k:{f:v[f] for f in pp.DERIVATION_FIELDS} for k,v in real.items()},
            'context_mapping':{s['id']:{'requirements':ids,'reason':s['statement']} for s in direction['context_sources']},'knowledge_mapping':mapping},
        'STRATEGIZING':{'brief':brief,'method_choice':{'chosen':strategy,'alternatives':'Do not add more texture to existing smooth forms or propagate unreviewed changes to all actors.',
            'evidence_status':'hypothesis','discriminating_test':'Actual same-camera images distinguish supported cloth from mathematical ridges; pose/cache records catch interface loss.'},
            'steps':[{'id':'save','kind':'proof','depends_on':[],'requirements':['preservation','interfaces'],'acceptance':'Saved healthy derivative with retained garment caches and identified supported structures; visual judgment follows.','native_recipe':bind('results/sikh335/look01/save-recipe.json')},
                {'id':'render','kind':'proof','depends_on':['save'],'requirements':ids,'acceptance':'Inspect all three actual images against accepted film and construction criteria; known defects remain FAIL.','native_recipe':bind('results/sikh335/look01/render-recipe.json')}],
            'resource_scope':'One initial local appearance construction, three diagnostic renders, serial heavy jobs; zero additional corrections allocated while motion extension is pending.',
            'replan_triggers':'Visible unsuitable crown, cloth ridges, cache damage or unsupported pad fails this method; no reset to obtain another attempt.'}}
    c.create(TASK,'production',bind('results/sikh335/REQUEST.md'),'sikh335-look-create',max_corrections=0,direction=direction,mode='local_native',admission='sikh335-look')
    for stage in pp.STEPS[:3]:
        p=c.packet(TASK);result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
        c.submit(TASK,p['actor'],p['ticket'],result,'sikh335-look-'+stage);save(stage.lower()+'.json',result)
    p=c.packet(TASK);p.pop('ticket',None);save('challenge-input.json',p);print(c.state(TASK)['planning_step'])

if __name__=='__main__':main()
