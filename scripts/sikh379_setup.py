"""Explicit379 source reconciliation and one atomic original-task revision."""
import copy,json,subprocess
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep,planning_pipeline as pp,reference_readiness as rr
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh379';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==136 and s['max_corrections']==137
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(name,v):
 p=o/name
 text=json.dumps(v,indent=2)+'\n'
 if p.exists():
  if p.read_text()!=text:raise ValueError('PRESERVE379:'+name)
 else:p.write_text(text)
 return bind(str(p.relative_to(r)))

b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources'])
# Preserve the historical policy bytes instead of relabeling them as current.
old=subprocess.check_output(['git','show','6b5d5ac:docs/engineering-intelligence/STAGE_MODEL_ROUTING.md'],cwd=r)
arch=o/'historical-routing360.md';arch.write_bytes(old)
assert pk.file_hash(arch)==b['source_bindings']['historical:routing360']['sha256']
b['source_bindings']['historical:routing360']=bind(str(arch.relative_to(r)))
reviewed={'docs/engineering-intelligence/STAGE_MODEL_ROUTING.md','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/production_workflow.py','src/movie_factory/adapters/blender/nihang_cache376.py'}
for k,v in b['source_bindings'].items():
 if pk.file_hash(r/v['path'])!=v['sha256']:
  assert v['path'] in reviewed,('UNREVIEWED_DRIFT',k,v['path'])
  b['source_bindings'][k]=bind(v['path'])
for row in src:
 if row['id']=='routing360':row['binding']=bind(row['binding']['path']);row['lines']=[1,35]
 if row['id']=='strategy374':row['lines']=[1,7]
for ident,path,category,statement,lines in [
 ('director379','results/sikh379/REQUEST.md','direction','Explicit resume, ten available same-task cycles137..146; no Astra or spend.',None),
 ('reference378','docs/knowledge/REFERENCE_READINESS_378.md','references','Purpose-qualified coverage decisions govern this continuation.',[22,27]),
 ('target379','results/sikh379/REFERENCE_QUALIFICATION.md','references','Inspected frontal/oblique/rearing target features and role exclusions.',[10,20])]:
 row=dict(id=ident,category=category,binding=bind(path),status='adopted',required=True,statement=statement,scope='379 chest micro-appearance; accepted motion/style protected')
 if lines:row['lines']=lines
 src.append(row)
for row in src:b['source_bindings'][row['id']]=row['binding']

for ident,path,observation in [
 ('pectoral_front','.runtime/art-direction/sikh379-references/umn-front-pectorals.jpg','Paired supported pectoral masses, central groove, distinct roots into forelegs.'),
 ('pectoral_rear','.runtime/art-direction/sikh379-references/cavalo-rear.jpg','Rounded shoulder and supported continuous underside while forelimbs lift; no flat bib.'),
 ('pectoral_opposite','.runtime/art-direction/sikh379-references/friesian-rear.jpg','Folded limb roots and continuous chest on opposite-facing/partial-lift horse.')]:
 ref=dict(id=ident,role='directional_design',binding=bind(path),authority='Agent-owned379 physical-reference qualification within approved chest goal',scope='Gross physical chest/neck/proximal-limb form only',fidelity=observation,allowed_variation='Existing horse proportions and accepted primary motion; anatomical interpretation, not pixel matching',not_authority='Not identity/breed, film palette/materials, choreography, or permission to incorporate source pixels',aspects=[dict(id='physical_junction',instruction=observation,requirements=['form','interfaces','evidence','whole_look'])])
 b['references'].append(ref);b['reference_plan'][ident]=dict(reference_digest=pk.digest(ref),application=observation+' Internal study only; source pixels not copied.')

needs=[dict(id='junction',purpose='physical_form',question='What positive chest/neck/raised upper-leg contours replace the bib?',critical=True,coverage=['front','oblique_rear','opposite_partial']),dict(id='motion',purpose='motion_mechanics',question='Which accepted action and pose family must remain fixed?',critical=True,coverage=['prep_apex_landing']),dict(id='film',purpose='film_style',question='What established quality/style must this horse inhabit?',critical=True,coverage=['accepted_look']),dict(id='preservation',purpose='technical_validation',question='Can source invariants be checked deterministically?',critical=True,coverage=['hash_action_controls'])]
ready=dict(version=1,scope=dict(version=1,id='horse-chest379',kind='micro_appearance',needs=needs),decisions={})
byid={x['id']:x for x in b['references']}
def selected(ident,origin,coverage,provenance):
 ref=byid[ident]
 return dict(id=ident,origin=origin,observation=ref['fidelity'],governs=ref['scope'],excluded_authority=ref['not_authority'],provenance=provenance,rights_use='reference_only',coverage=coverage,evidence=[ref['binding'],bind('results/sikh379/REFERENCE_QUALIFICATION.md')])
for key,values in [
 ('junction',[selected('pectoral_front','image_search',{'front':'Rounded paired muscles and central groove; distinct forelimbs'},'UMN CVM Lab1 image10, public internal anatomy study'),selected('pectoral_rear','image_search',{'oblique_rear':'Supported chest underside and rounded limb roots during rear'},'Jonathan Wilkins own photo,22Nov2007,CC BY-SA3.0; source page in acquisition.json'),selected('pectoral_opposite','image_search',{'opposite_partial':'Opposite-facing partial lift and folded limb/chest continuity'},'KaRede own photo,17Aug2016,CC BY-SA4.0; source page in acquisition.json')]),
 ('motion',[selected('reference_rear','director',{'prep_apex_landing':'Original14..19 video and exact66/75/80 accepted motion source'},'Director-provided reference-b, protected accepted action')]),
 ('film',[selected('accepted_film','accepted_asset',{'accepted_look':'Illustrated rich coherent forms/materials, separate from anatomical truth'},'Director253 provisional production comparator; no permission to modify')])]:
 ready['decisions'][key]=dict(decision='reuse_existing' if key!='junction' else 'acquire',reason='Inspected qualified sources address gross scoped target; limits and exclusions documented.',reopen_when='A required hidden view or motion/form feature is unresolved or contradicted by actual proof.',status='sufficient',references=values)
ready['decisions']['preservation']=dict(decision='none_needed',reason='Exact native/action/source comparison is deterministic; no additional illustrative reference required.',reopen_when='Claim extends to physical or artistic correctness.',status='not_needed',references=[])
b['reference_readiness']=ready;b['reference_mapping']={'preservation':['motion','preservation'],'form':['junction'],'interfaces':['junction','motion'],'evidence':['junction','motion','film'],'whole_look':['junction','film'],'director_form_motion':['junction','motion']}
for rid,aspects in b['reference_mapping'].items():
 m=b['expert_plan']['realizations'][rid];m['reference_ids']=list(dict.fromkeys(m['reference_ids']+[q['id'] for k in aspects for q in ready['decisions'][k]['references']]))
b['expert_plan']['realizations']['form']['derivation']='New qualified real-photo contours establish rounded supported pectoral/shoulder/foreleg junction. Prior precise smoothing targets failed. Preserve local differential shape with ARAP and restrained partial restoration, then actual worst-pose proof; no anatomy PASS from the solver.'
b['work_unit']['cycle_window']=[137,146];b['work_unit']['edit_kinds']=['mounted_horse_chest379','mounted_horseform374_inspect','mounted_horseform374_contact']
new=['results/sikh379/REQUEST.md','results/sikh379/STRATEGY.md','results/sikh379/REFERENCE_QUALIFICATION.md','src/movie_factory/horse_shape379.py','src/movie_factory/adapters/blender/nihang_chest379.py','scripts/sikh379_targets.py','scripts/sikh379_plan.py','tests/test_horse_shape379.py','docs/knowledge/REFERENCE_READINESS_378.md','results/workflow378/CHEST_HYPOTHESIS.md','results/sikh376/REJECT136.md','.runtime/context-hygiene/runs/sikh379-handler-tests/stdout.log','.runtime/art-direction/sikh379-targets/c137.npz','.runtime/art-direction/sikh379-targets/c137.json','.runtime/art-direction/sikh379-references/acquisition.json']
new += [x['binding']['path'] for x in b['references']]
for p in new:b['source_bindings'][p]=bind(p)
t=pk.read_json(r,'results/sikh379/reference-task.json');t.update(id='sikh379-native137',phase='execution',inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()},execution_authority=dict(source='results/sikh379/REQUEST.md',scope='Resume same torso appearance task, up to10 available137..146, protected action, Sol, no new resources.'))
write('task137.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet137.json',packet)
b.update(knowledge_task='results/sikh379/task137.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind('results/sikh379/task137.json');row['lines']=[1,14]
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings']['results/sikh379/task137.json']=bind('results/sikh379/task137.json')
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
write('revised137-brief.json',b);write('sources137.json',src)
pp.source_context(r,dict(context_sources=src));rr.brief(r,b,required=True)
method='Reference-grounded local ARAP preserves rounded differential shape with fixed limb/body/neck interfaces and .28 partial recovery of flattened legacy rest form. Data-only183half-frame target, protected original source/actions, native source-match checks.'
proof='Actual339 then333/342 opposite/front/side plus283367 must show supported rounded chest without sheet/shelf/pinch/bulb. Source/cache metrics are technical only. Known bodyFAIL blocks coat/full integration.'
steps=[dict(id='repair',depends_on=[],recipe=dict(operation='nihang_patch',frame=367,width=432,height=768,samples=8,edits=[dict(kind='mounted_horse_chest379',target='horse',data=bind('.runtime/art-direction/sikh379-targets/c137.npz'))]))]
for ident,view in [('worst','horse_form_reverse374'),('front','horse_form_front374'),('side','horse_form_side374')]:
 steps.append(dict(id=ident,depends_on=['repair']+(['worst'] if ident!='worst' else []),recipe=dict(operation='nihang_frames',frame=339,frames=[339,333,342,283,367],view=view,width=640,height=640,samples=8)))
cfg=dict(parent='.runtime/factory-native/sikh375-appearance-c129-inspect/scene.blend',brief_path='results/sikh379/revised137-brief.json',method=method,proof=proof,scope='Same horse torso micro-appearance, first actual proof under379, primary motion fixed; no full leader/crowd claim.',reconciliation='Qualified gross reference coverage and explicit378 reference contract; existing failures, accepted action and limits retained. No runtime/model/new-spend authority.',alternatives='Prior shrink/gather/cache precision approaches failed actualform. ARAP is a changed construction hypothesis, not a guaranteed anatomy cure or universal rig replacement.',failure='Any source drift, bib/crease/shelf/globe/limb-root collapse or missing view remains internalFAIL. Reassess target versus method; no automatic Astra.',cause='Mixed insufficiently frozen positive target and construction failure, per378; qualified source board now permits discriminating native construction.',expected='Supported continuous powerful horse chest through existing motion, with unrelated surfaces/actions unchanged.',steps=steps,sources=new,retrospective_evidence=['results/sikh379/REQUEST.md','results/sikh379/STRATEGY.md','results/sikh379/REFERENCE_QUALIFICATION.md','results/workflow378/CHEST_HYPOTHESIS.md','results/sikh376/REJECT136.md'])
write('appearance-c137.json',cfg)
challenge=pk.read_json(r,'results/sikh376/appearance-c136-challenge.json')
observations={'grounding':'379 resumes same task with ten available slots;378 input gap reconciled through inspected new source photos, old faithful motion/style protected.','expert_coverage':'Anatomy/rigging separates connected positive form from method; contact/surface interfaces remain required, no new acting or sound.','film_alignment':'Photographic references govern gross anatomy only; accepted illustrated film quality remains separate.','preferences':'High quality and larger-than-life power retained; no early handoff for incremental failed form.','reference_roles':'UMN front, clear oblique rear and opposite partial lift support gross junction; missing high-rear frontal detail is an explicit reopening trigger.','method':'Changed from shrinking to ARAP with tested rigid-pose and fixed-interface controls; actualnative339 is the falsifier.','interfaces':'Skin/nap coupling and finalcontact remain required after early bodyproof; no hiding with coat. Protected motion/source outside target unchanged.','efficient_quality':'Existing source clock/cache reused, fixed source hashes and serial worker, fail worstview before broader render.','authority':'No Astra/provider/spend/install; originaltask and137..146 allowance only,319/313 quality and Director AV boundaries retained.'}
for facet in challenge['checks']:challenge['checks'][facet].update(observation=observations[facet],comparison='379 request, qualified reference features and strategy versus original accepted motion/quality; planning admission only.',source_ids=['director379','target379','reference378'])
challenge['strongest_counterexample']='Preserving a flattened rest form may still produce a wrong rounded/chest shape or retain the bib. Qualified gross references do not guarantee ARAP succeeds; actual worstpose and opposite/partial views veto it.'
challenge['reference_challenge']=dict(readiness_digest=pk.digest(ready),checks={k:dict(status='PASS',observation=d['reason'] if k!='preservation' else d['reason'],counterexample=d['reopen_when'],evidence=[e for q in d['references'] for e in q['evidence']]) for k,d in ready['decisions'].items()})
write('appearance-c137-challenge.json',challenge)
c.revise(task,b,bind('results/sikh379/REQUEST.md'),'379 explicit resume; qualified role-specific references and new supported construction proof, no automatic artist/model pass.','sikh379-reference-target137',grounding=dict(context_sources=src,reason='Explicit378 policy/source changes and new379 physical reference qualification. Historical policy snapshot retained; strategy374 bounded to its applicable original first7lines, full source read and remaining current obligations retained in existing sources/core/new reference contract. New source excerpts select the actual per-aspect requirement and observed physical features rather than duplicate the whole read guides.',evidence={p:bind(p) for p in ['results/sikh379/STRATEGY.md','results/sikh379/REFERENCE_QUALIFICATION.md','results/workflow378/CALIBRATION.md']}))
assert c.state(task)['cycle']==137
# Ten available attempts137..146 includes the already approved unused137.
decision=write('APPROVED_ALLOWANCE.json',dict(task=task,decision='approve_additional_corrections',prior_cycle=137,prior_max_corrections=137,additional_corrections=9,director_reply='ok resume. 10 cycles approved',question='379 authorizes ten available137..146; unused137 retained, nine added, no double-counted eleventh slot.'))
entry=dict(text='379 ten available torso corrections137..146',operations=['document'],rationale='Preserve already unused137 and addnine explicit same-task slots; no reset or model/spend change.',amendment_task=task,authority=decision)
write('allowance-entry.json',entry);c.route_request('sikh379-allowance',entry)
extend(c,task,'sikh379-allowance',decision,'sikh379-ten-available')
print('Original task137/max146; ready for staged planning')
