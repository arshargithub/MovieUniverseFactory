"""Reviewed same-task scope reconciliation and exact fifty-correction grant.

No Blender/provider dispatch. Required source roles/history are retained.
"""
import copy
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import planning_pipeline as pp, expert_planning as ep, production_allowance as pa
from movie_factory.task_router import DATABASE

r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
    path=o/n;text=json.dumps(v,indent=2)+'\n'
    if path.exists():assert path.read_text()==text, n
    else:path.write_text(text)

s=c.state(task);assert s['cycle']==176 and s['max_corrections']==176
b=copy.deepcopy(pk.read_json(r,'results/sikh381/revised156-brief.json'))
sources=copy.deepcopy(s['direction']['context_sources'])
# Preserve every required original source's classification and statement.
# Current386 sources explicitly supersede old donor/expired model assignments.
for row in sources:
    if row['id']!='controls':row['binding']=bind(row['binding']['path'])
# Explicit current-purpose selections; full sources/statements/status/scope stay.
# Old donor method/costume is superseded, and old contact/garment detail is not
# this chest-mass proof. No mandatory source is silently omitted or repinned.
selections={'strategy383':[1,6],'strategy384':[1,6],'refs384':[1,6],
    'director_preferences':[1,14],'carry375':[7,10],'carry373':[19,20],
    'references':[11,26],'audit348':[24,36],'routing360':[1,14]}
for row in sources:
    if row['id'] in selections:row['lines']=selections[row['id']]
new_context=[
 ('director386','results/sikh386/REQUEST.md','direction',[1,2],
  'Director386 adopts385plan and one shared50additional corrections on previous horse; no armored donor or new resources.'),
 ('scope386','docs/knowledge/MICRO_APPEARANCE_WORKFLOW_386.md','constraints',[9,42],
  'New coherent units require scope/causal/dependency contracts and fresh separate challenge; semantics remain judgment.'),
 ('effects386','docs/knowledge/MICRO_APPEARANCE_WORKFLOW_386.md','learnings',[65,111],
  'A remedy needs outcome-linked effect disposition; superseded donor scope is explicit history, never an art PASS.'),
 ('audit385','results/sikh385/AUDIT.md','learnings',[76,102],
  'Wrong target, broad scope, ineffective interventions and weak proof retention caused failure; precision is not anatomy.'),
 ('strategy386','results/sikh386/STRATEGY.md','constraints',[3,36],
  'Source ownership then positive chest mass first; volumetric envelope is a falsifiable shape hypothesis, not anatomy truth.')]
for ident,p,category,lines,statement in new_context:
    sources.append(dict(id=ident,category=category,binding=bind(p),lines=lines,status='adopted',required=True,
        statement=statement,scope='386 chest micro-unitA and approved process; history/quality/action/authority retained'))

bindings={}
def gather(x):
    if isinstance(x,dict):
        if set(x)=={'path','sha256'}:
            assert pk.file_hash(r/x['path'])==x['sha256'],('REFERENCE_DRIFT',x['path']);bindings[x['path']]=x
        else:
            for v in x.values():gather(v)
    elif isinstance(x,list):
        for v in x:gather(v)
for obj in [b['references'],b['reference_readiness'],b['work_unit']['negative_controls']]:gather(obj)
for row in sources:
    if row['id']!='controls':bindings[row['binding']['path']]=row['binding']
required=[
 'results/sikh386/REQUEST.md','results/sikh386/APPROVAL.json','results/sikh386/APPROVED_ALLOWANCE.json',
 'results/sikh386/HANDLER_REVIEW.md','results/sikh386/STRATEGY.md','results/sikh386/WORKFLOW_QUALIFICATION.md',
 'results/sikh386/SOURCE_RECONCILIATION.md','results/sikh385/PROPOSAL.md','results/sikh385/AUDIT.md',
 'results/sikh385/CASES.md','docs/knowledge/WORK_UNITS_367.md','docs/knowledge/WORK_UNIT_GRANULARITY_369.md',
 'docs/knowledge/RETROSPECTIVE_WORKFLOW_350.md','docs/knowledge/MICRO_APPEARANCE_WORKFLOW_386.md',
 'docs/knowledge/PLANNING_PIPELINE_330.md','docs/knowledge/EXPERT_LENS_PLANNING_328.md',
 'docs/knowledge/pilot/catalog.json','docs/knowledge/pilot/source-pins.json',
 'src/movie_factory/production_workflow.py','src/movie_factory/work_units.py','src/movie_factory/retrospective.py',
 'src/movie_factory/production_allowance.py','src/movie_factory/planning_pipeline.py','src/movie_factory/expert_planning.py',
 'src/movie_factory/native_admission.py','src/movie_factory/adapters/blender/nihang_patch.py',
 'src/movie_factory/adapters/blender/nihang_control.py','src/movie_factory/adapters/blender/nihang_anatomy386.py',
 'scripts/sikh386_setup.py','scripts/sikh386_plan.py','tests/test_micro_appearance386.py','tests/test_anatomy386.py',
 'results/sikh374/SOURCE_FORM124_REVIEW.json','results/sikh374/INTERNAL_REJECTION128.json',
 'results/sikh381/RETROSPECTIVE381.md','results/sikh379/REFERENCE_QUALIFICATION.md',
 '.runtime/factory-native/sikh373-motion-c80-contact/scene.blend']
for p in required:bindings[p]=bind(p)
for row in b['references']:
    row['unit_required']=row['id']=='horse_form'
    b['reference_plan'][row['id']]['reference_digest']=pk.digest(row)
b['intent']='Establish a supported connected chest mass on the previous horse under accepted80action; no bulb, flat bib or pendant pectorals. UnitA only, before shoulder/lower-neck and integrated moving-form finish.'
criteria=dict(
 preservation='Accepted66/75/80primary action and protected masters remain unchanged; all skin/form changes reversible on the previous horse.',
 form='UnitA: modest paired pectoral relief remains supported by the thorax, with natural lower contour between distinct forelegs in stance and worst descent; no bulb, flat panel or pendant bib.',
 interfaces='Keep shoulders, upperforeleg roots, lower neck and barrel visible; no new detached patch, seam or loss of support. Existing outside-unit issues remain named for B/C rather than falsely passed.',
 evidence='Actual source and target in matched close front/side/opposite283333339 plus whole-horse scale; later complete moving/contact proof required before production adoption.',
 whole_look='Chest-mass proof retains the same horse/film and surrounding proportions; no costume/lighting concealment or whole-horse readiness claim from this unit.',
 director_form_motion='Director313fullspeed judgment is pending until integrated moving-form proof; this source/shape unit does not self-pass fluidity or final film.')
for q in b['requirements']:q['criterion']=criteria[q['id']]
unit=b['work_unit'];unit.update(version=2,id='horse-chest-mass386-A',task=task,phase='appearance_chest_mass',
    primary_outcome=b['intent'],cycle_window=[177,226],discipline='appearance',
    allowed_domains=['chest_surface','chest_skin_mapping','diagnostic_camera','source_export'],
    frozen_domains=['accepted_primary_action','head_identity','lower_legs','hindquarters','source_masters','leader','crowd','wardrobe','sound','terrain'],
    edit_kinds=['mounted_anatomy386_export','mounted_anatomy386_target'])
unit['appearance_proof'].update(motion_source=bind('.runtime/factory-native/sikh373-motion-c80-contact/scene.blend'),poses=[283,333,339],
    views=['anatomy_chest_front386','anatomy_chest_side386','anatomy_chest_oblique386'],interfaces=['chest/neck','chest/shoulder_upperleg','chest/barrel','skin/nap','body/saddle'])
unit['scope_decision']=dict(decision='split',rationale='385/386 separates a connected chest-mass outcome from root/neck finish; surrounding anatomy stays visible and coupled failures reopen scope.',
    independent_judgment='A normal viewer can reject the current low pectoral masses or flat bib in stance/descent without judging costume, tail or whole rear timing.',
    coupled_context='Lower neck, both shoulders and upperforelegs, barrel and whole-horse scale remain in evidence; no chest-only geometry box.',
    worst_proof='339opposite/front and stance283 before expensive detail;333 tests high rear.',integration_proof='UnitD whole accepted rear and consumer boundary/contact proof after A/B/C.',
    parent_task=task,allowance_binding=bind('results/sikh386/APPROVED_ALLOWANCE.json'),considered_outcomes=[
      dict(id='A',disposition='current',criterion=criteria['form'],reason='Supported mass is the first independent missing positive shape.'),
      dict(id='B',disposition='coupled',criterion='Natural shoulder/upperleg origins',reason='Context retained, detailed articulation next; if A cannot be judged separately merge necessary coupling.'),
      dict(id='C',disposition='deferred',criterion='Natural lowerneck blend',reason='Keep visible but avoid simultaneous new throat sculpt.'),
      dict(id='D',disposition='deferred',criterion='Whole moving-form and interfaces',reason='Requires actual usable A/B/C, cannot be inferred from static proof.')])
unit['causal_experiment']=dict(unknown='Positive target construction versus inherited chest ownership/skin deformation',
    hypothesis='An explicitly supported volumetric chest envelope can establish connected form where smoothing/fitting to source failed.',
    method_family='anatomically_anchored_volumetric_envelope',discriminator='Actual current80source cage/bone ownership, then reference-governed three-dimensional target in stance and worst descent.',
    success_prediction='Supported modest chest relief without a pendant edge, flat bib or detached paired bulbs; source action/outside region unchanged.',
    failure_prediction='Another sphere/shelf/web or disconnected limb root falsifies the envelope or unit boundary; numerical target fit is insufficient.',
    failure_response='Reject native proof, evaluate intervention, reassess target/representation/scope before another remedy.',
    failed_alternatives=['Uniform smoothing and Gaussian gain fields','Raw-rest restoration/whole-muscle rigid ownership','Biharmonic front cap','Accurate dense playback of wrong target'],
    evidence=[bind('results/sikh385/AUDIT.md'),bind('results/sikh381/RETROSPECTIVE381.md'),bind('results/sikh379/REFERENCE_QUALIFICATION.md')])
unit['scope_challenge']=dict(status='PASS',observation='One supported chest mass is judgeable in multiple poses with complete root/neck context; necessary coupling remains and can trigger merge.',
    counterexample='A neat isolated mass can still look like a hanging globe when roots are lifted; actual wholehorse/oblique333339 must veto it.',
    evidence=[bind('results/sikh385/PROPOSAL.md'),bind('results/sikh374/INTERNAL_REJECTION128.json')])
unit['dependencies']=[dict(id='accepted_action80',binding=unit['appearance_proof']['motion_source'],interfaces=['primary action','rig scalar tracks','limb endpoints'],
    disposition='preserve',reason='Director accepted primary rear only; no new motion to accommodate anatomy.')]
for q in unit['positive_criteria']:q.update(reference_feature=criteria[q['id']],comparison='Matched real physical references, actual source80 and negative128/156; new source control is not a positive target.',failure='Bulb/panel/bib, missing actual proof or new unsupported interface remains FAIL.')
b['expert_plan']['beat_intents']['torso']=b['intent'];b['expert_plan']['beats'][0].update(audience_read=b['intent'],framing='Close anatomical front/side/opposite and wholehorse controls across standing, crest and descent; no full sequence render.')
for rid,m in b['expert_plan']['realizations'].items():m.update(derivation=criteria[rid],method='Current source ownership followed by a positive volumetric target, not smoothing a rejected surface.',
    early_proof='339/283revealing controls before coat/contact/full motion',failure_condition='Any visible unsupported mass/panel/web or untested interface remains internal',interfaces=['chest/neck','chest/upperlegs','body/tack'],reopening_trigger='Changed shape, pose use, camera or boundary reopens relevant proof.')
b['source_bindings']=bindings
# Fresh knowledge task does not hash itself; its final binding joins the brief.
t=dict(id='sikh386-native177',operation='modeling',entities=['nihang_horse','nihang_leader','renderer'],
    query='previous horse supported chest mass positive anatomy micro appearance scope causal effect reference fixed rearing action source export',
    intent=b['intent'],phase='execution',inputs={p:v['sha256'] for p,v in bindings.items()},open_decisions=[],
    execution_prerequisites=['386source/handler/workflow qualification completed before native execution','Same task and50shared ceiling; no new resources'],
    execution_authority=dict(source='results/sikh386/REQUEST.md',scope='Previous-horse anatomy A/B/C/D within one50extra ceiling; first177 source/positive-method proof preparation'))
write('task177.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet177.json',packet)
b.update(knowledge_task='results/sikh386/task177.json',knowledge_digest=packet['packet_digest'])
for row in sources:
    if row['id']=='controls':row['binding']=bind('results/sikh386/task177.json')
    b['source_bindings'][row['binding']['path']]=row['binding']
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised177-brief.json',b)
pp.source_context(r,dict(context_sources=sources))
wf.validate_brief(r,b,'production',s.get('mode','offline'))

# Policy migration changes no art allowance; original events remain immutable.
from movie_factory import retrospective as rt
con=c.connect();projection=rt.snapshot(con,task);con.close()
if projection['engine']!=rt.engine():
    reconciliation=dict(state_digest=pk.digest(c.state(task)),coverage='Preserve335allhistory/176max176; new scope/effect dispositions apply prospectively; no retroactive artistic PASS.',
        unknowns='Actual anatomy construction remains unqualified; historical AV/global307 failures retained.',
        evidence={p:bind(p) for p in ['results/sikh386/REQUEST.md','results/sikh386/WORKFLOW_QUALIFICATION.md','results/sikh385/AUDIT.md']})
    write('POLICY_MIGRATION.json',reconciliation);c.migrate_retrospective(task,bind('results/sikh386/REQUEST.md'),reconciliation,'sikh386-policy')
c.revise(task,b,bind('results/sikh386/REQUEST.md'),'386 returns to original horse and approved micro-unitA; reconcile tested workflow/current-source drift, preserving exhausted176 and all historical failures.',
    'sikh386-scope-at176',grounding=dict(context_sources=sources,reason='Approved385/386return from donor to chest; all original required source roles/status/statements retained, historical scopes contextualized by latest explicit direction.',
        evidence={p:bind(p) for p in ['results/sikh386/REQUEST.md','results/sikh386/SOURCE_RECONCILIATION.md','results/sikh386/WORKFLOW_QUALIFICATION.md','results/sikh385/PROPOSAL.md']}))
pa.extend(c,task,'sikh386-allowance',bind('results/sikh386/APPROVED_ALLOWANCE.json'),'sikh386-fifty')
after=c.state(task);assert after['cycle']==177 and after['max_corrections']==226
write('START_STATE.json',{k:after[k] for k in ['task','cycle','max_corrections','stage','planning_step']})
print(json.dumps(dict(cycle=after['cycle'],max=after['max_corrections'],source_bindings=len(bindings),context_sources=len(sources))))
