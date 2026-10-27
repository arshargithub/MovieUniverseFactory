"""Scoped same-task head/tack proof; source roles and shared allowance retained."""
import copy,json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh384';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==167 and s['max_corrections']==176
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
b=copy.deepcopy(pk.read_json(r,'results/sikh383/revised166-brief.json'));src=copy.deepcopy(s['direction']['context_sources'])
for row in src:
 if row['id']=='learnings':row['lines']=[10,14]
 if row['id']=='audit363':row['lines']=[8,13]
changed=['src/movie_factory/adapters/blender/warhorse384.py','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/adapters/blender/nihang_control.py','tests/test_warhorse384.py','scripts/sikh384_plan.py','scripts/sikh384_setup.py']
new=['results/sikh384/REQUEST.md','results/sikh384/APPROVED_ALLOWANCE.json','results/sikh384/STRATEGY.md','results/sikh384/HANDLER_REVIEW.md','results/sikh384/REFERENCE_ACQUISITION.json','results/sikh384/REFERENCE_QUALIFICATION.md']+changed
for key,v in b['source_bindings'].items():
 if pk.file_hash(r/v['path'])!=v['sha256']:
  assert v['path'] in changed,('UNREVIEWED_DRIFT',v['path']);b['source_bindings'][key]=bind(v['path'])
for p in new:b['source_bindings'][p]=bind(p)
for sid,p,category,statement in [
 ('director384','results/sikh384/REQUEST.md','direction','Director384 accepts383 heavy build and authorizes ten167..176 head/tack adaptation proof slots, before leader fit.'),
 ('strategy384','results/sikh384/STRATEGY.md','constraints','Actual before/after close proof first; material adaptation cannot hide a helmet-shaped face.'),
 ('refs384','results/sikh384/REFERENCE_QUALIFICATION.md','learnings','Actual conformation/anatomy and coat/leather references cover structure/material separately, without breed/style adoption.')]:
 src.append(dict(id=sid,category=category,binding=bind(p),lines=[1,min(20,len((r/p).read_text().splitlines()))],status='adopted',required=True,statement=statement,scope='384 head/tack proof only, original motion/film/identity preserved'))
criteria=dict(preservation='Accepted masters and donor geometry/topology/weights/actions unchanged in first material proof; source maps unmodified.',form='Exposed horse forehead, eye, cheek, bridge and muzzle read as natural coherent anatomy, not recolored plate or rigid helmet.',interfaces='Real eyes/muzzle/coat preserved; adapted breastcollar reads as leather with supported strap routes, not chrome or skin plate.',evidence='Matched before/after close front/side/chest plus oblique standing/apex/descent; source remains available and head changes remain coherent through motion.',whole_look='Accepted heavy build and rich dark bay look retained, new surface belongs to film quality; no broad body/groom/rider redesign.',director_form_motion='Full-speed AV remains Director313-owned; source action unchanged does not automatically qualify transferred motion.')
b['intent']='Prove bare-head and rugged leather tack adaptation on Director-accepted heavier Warhorse build before any leader integration.'
for q in b['requirements']:q['criterion']=criteria[q['id']]
unit=b['work_unit'];unit.update(id='horse-head-tack384',primary_outcome=b['intent'],phase='head_tack_adaptation',cycle_window=[167,176],allowed_domains=['horse_head_surface','horse_tack_surface','neutral_evidence_camera'],frozen_domains=['donor_geometry','donor_weights','accepted_motion_masters','pashtun','production_scene','leader','crowd','groom','sound'],edit_kinds=['warhorse_surface384'])
unit['appearance_proof'].update(motion_source=bind('.runtime/factory-native/sikh383-appearance-c166-import/scene.blend'),poses=[283,333,339],views=['warhorse_head_front384','warhorse_head_side384','warhorse_head_oblique384'],interfaces=['eye/coat/head surface','bridle/cheek/muzzle','breastcollar/chest','fixed pose/shader'])
b['source_bindings'][unit['appearance_proof']['motion_source']['path']]=unit['appearance_proof']['motion_source']
for row in unit['positive_criteria']:row.update(reference_feature=criteria[row['id']],comparison='Matched same-source384 close views, real qualified head/material study and383 accepted heavier build.',failure='Any obvious armor-shaped forehead, hard material border, eye loss, malformed chest or unsupported strap fails.')
beat=b['expert_plan']['beats'][0];beat.update(audience_read=b['intent'],framing='Revealing close front/side/opposite head and breastcollar; final wholehorse size only after close proof.')
b['expert_plan']['beat_intents']['torso']=b['intent']
# Explicit new physical/material need supplements retained torso/motion/film roles.
ready=b['reference_readiness'];ready['scope']['id']='horse-head-tack384'
ready['scope']['needs'].append(dict(id='head_surface',purpose='physical_form',question='Which unarmored head planes and tactile coat/leather differences must survive adaptation?',critical=True,coverage=['profile_structure','lateral_anatomy','coat_leather']))
aq=pk.read_json(r,'results/sikh384/REFERENCE_ACQUISITION.json');chosen=[(2,'head_conformation384','profile_structure','Visible poll, eye socket, cheek, bridge and muzzle continuity; breed convexity excluded.'),(3,'head_anatomy384','lateral_anatomy','Skull/muscle relations corroborate physical planes, not exposed-muscle final look.'),(0,'head_material384','coat_leather','Short coat variation around eye and worn separate leather strap edges; macro crop not overall head form.')]
selected=[]
for i,rid,coverage,obs in chosen:
 a=aq[i];binding=bind(a['path']);b['source_bindings'][a['path']]=binding
 ref=dict(id=rid,binding=binding,role='directional_design',authority='Agent-qualified real physical study under378.',scope='384 head/tack physical study only.',fidelity=obs,allowed_variation='Preserve accepted heavy dark bay build and film style; do not copy breed convexity.',not_authority='Not breed/identity, film palette, source pixels or new choreography.',aspects=[dict(id=coverage,instruction=obs,requirements=['form','interfaces','evidence','whole_look'])])
 b['references'].append(ref)
 b['reference_plan'][rid]=dict(reference_digest=pk.digest(ref),application=obs+' Reference-only physical study; actual native view remains decisive.')
 selected.append(dict(id=rid,origin='image_search',observation=obs,coverage={coverage:obs},evidence=[binding,bind('results/sikh384/REFERENCE_QUALIFICATION.md')],governs='Scoped physical head or coat/leather study only',excluded_authority='No breed/identity/style/choreography adoption, no source-pixel incorporation',provenance=a['url']+'; '+a['rights_use'],rights_use='reference_only'))
ready['decisions']['head_surface']=dict(decision='acquire',reason='Inspected real conformation photo/anatomy plate and coat/leather macro resolve scoped target; blinker profile explicitly rejected for forehead coverage.',references=selected,status='sufficient',reopen_when='Actual exposed surface lacks structure beyond observed views or hidden anatomy must be reconstructed.')
for rid,m in b['expert_plan']['realizations'].items():
 if rid!='preservation':b['reference_mapping'][rid]=list(dict.fromkeys(b['reference_mapping'][rid]+['head_surface']))
 for need in b['reference_mapping'][rid]:
  for q in ready['decisions'][need]['references']:
   if q['id'] not in m['reference_ids']:m['reference_ids'].append(q['id'])
 m.update(derivation=criteria[rid],method='Fixed material/normal reinterpretation with original metallic pixels and named surface domains; no geometry removal.',early_proof='Actual matched close head front/side and breastcollar before broader poses; silhouette/baked armor read is a falsifier.',failure_condition='Recolored helmet, hard mask seam, coat mismatch, damaged eye/muzzle or changed geometry/action fails.',interfaces=['head surface/material','coat/bridle','leather/chest','source pose/surface'],reopening_trigger='Changed material, surface mask, camera, donor or action reopens affected proof.')
# Current controlled task bindings; stale historical code is refreshed only from reviewed list.
t=pk.read_json(r,s['direction']['knowledge_task']);t.update(id='sikh384-native168',intent=b['intent'],query='head anatomy coat leather tack surface mask silhouette reference efficient early proof',inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()},execution_authority=dict(source='results/sikh384/REQUEST.md',scope='Same task167..176, accepted donor adaptation proof only, no new resources.'));write('task168.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet168.json',packet);b.update(knowledge_task='results/sikh384/task168.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind('results/sikh384/task168.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings']['results/sikh384/task168.json']=bind('results/sikh384/task168.json');b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised168-brief.json',b)
method='Material-only source-metal pixel adaptation to natural dark bay coat and rugged leather; original actual outer surface and motion preserved.'
proof='Matched before/after head front, side and chest close views first; then front/side/oblique283333339 plus wholehorse to reject recolored helmet, seams and damaged eyes.'
cfg=dict(parent='.runtime/factory-native/sikh383-appearance-c166-import/scene.blend',brief_path='results/sikh384/revised168-brief.json',method=method,cause='Accepted heavy build carries fused metal face/breast plate; no intact underlying anatomy is known.',scope='384 bare-head/tack adaptation proof only; no production adoption or leader/groom work.',proof=proof,failure='Visible helmet identity, discontinuous coat, damaged anatomy/eyes, unsupported tack or source mutation rejects method before downstream work.',alternatives='Deleting plate triangles risks absent anatomy; material reinterpretation is smallest discriminating proof. Local geometry reconstruction only after actual failure.',expected='Natural exposed head and matte rugged leather without changing accepted heavier form or choreography.',reconciliation='Director384 accepts383 build and grants167..176 adaptation proof. Old torso-construction scopes are historical failed methods, original quality/motion/protection remain binding.',reference_reason='384 real bare profile/anatomy plus coat/leather macro address head target; original reference video/accepted film remain their separate authorities.',sources=new+[a['path'] for a in aq],retrospective_evidence=new[:6],steps=[])
def frames(ident,parent,view,fs,requirements):
 cfg['steps'].append(dict(id=ident,depends_on=[parent],recipe=dict(operation='nihang_frames',frame=283,frames=fs,view=view,width=640,height=640,samples=8),requirements=requirements))
cfg['steps'].append(dict(id='source',depends_on=[],recipe=dict(operation='nihang_save',frame=283,width=640,height=640,samples=8),requirements=['preservation']))
for label,view in [('front','warhorse_head_front384'),('side','warhorse_head_side384'),('chest','warhorse_chest384')]:frames('before_'+label,'source',view,[283],['preservation'])
cfg['steps'].append(dict(id='adapt',depends_on=['source','before_front','before_side','before_chest'],recipe=dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[dict(kind='warhorse_surface384',target='warhorse383')]),requirements=['preservation']))
for label,view in [('front','warhorse_head_front384'),('side','warhorse_head_side384'),('oblique','warhorse_head_oblique384')]:frames('after_'+label,'adapt',view,[283,333,339],['form','interfaces','evidence','whole_look'])
frames('after_chest','adapt','warhorse_chest384',[283,333,339],['interfaces','evidence'])
frames('whole','adapt','warhorse_reverse383',[283,333,339],['evidence','whole_look','director_form_motion'])
write('appearance-c168.json',cfg)
ch=pk.read_json(r,'results/sikh383/appearance-c166-challenge.json')
texts=dict(grounding='384 accepts heavier build, preserves original task and scope; true metal map is inspected, no hidden anatomy assumed.',expert_coverage='Anatomy/material craft demands natural exposed planes/eye/muzzle plus distinct matte leather; matched revealing evidence tests this.',film_alignment='Accepted dark bay heavy horse retained; reference anatomy does not dictate photoreal style, source armor not automatically adopted.',preferences='High quality with early visible proof; ten cycles are a ceiling, not mandatory variants.',reference_roles='New bare profile/anatomy corroborate form, macro coat/leather material; blinker image excluded; original motion and film roles retained.',method='Fixed closed shader and view handler tested at dispatch boundary; first bpy call remains actual integration test and may fail.',interfaces='Preserve geometry/weights/actions; eye/muzzle/coating and strap/chest interfaces checked before rider work.',efficient_quality='Matched head/chest close proof before whole or moving render; no full sequence rerender.',authority='Director384 ten167..176 Sol default; no spend, install, cloud, upload, native source mutation or Astra.')
for k,v in ch['checks'].items():v.update(status='PASS',observation=texts[k],comparison='Challenge exact384 intent, inspected source maps and reviewed closed handler against foreseeable recolored-helmet failure.',source_ids=['director384','strategy384','refs384'])
ch['strongest_counterexample']='A matte brown helmet may still have rigid borders and flattened forehead; material change can succeed technically and fail the actual close image.'
ch['reference_challenge']['readiness_digest']=pk.digest(ready)
ch['reference_challenge']['checks']['head_surface']=dict(status='PASS',observation='Actual bare conformation side, anatomical plate and short-coat/leather macro inspected with separate scopes.',counterexample='References cannot prove this armor outer surface contains convincing head structure; native close test must decide.',evidence=[x for q in selected for x in q['evidence']])
write('appearance-c168-challenge.json',ch)
pp.source_context(r,dict(context_sources=src))
c.revise(task,b,bind('results/sikh384/REQUEST.md'),'384 scoped material/head-tack proof;167 source/ref/handler reconciliation,168 first native comparison.', 'sikh384-prepare168',grounding=dict(context_sources=src,reason=cfg['reconciliation'],evidence={p:bind(p) for p in new[:6]}))
print('Prepared',c.state(task)['cycle'],c.state(task)['max_corrections'])
