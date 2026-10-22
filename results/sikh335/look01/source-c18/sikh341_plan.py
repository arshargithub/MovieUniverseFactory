"""Staged neutral prerequisite on the existing appearance task and allowance."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE
from movie_factory.adapters.blender.nihang_neutral import DONOR
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==18 and s['max_corrections']==19 and s['planning_step'] in pp.STEPS[:3]
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
steps=[]
save=dict(operation='nihang_patch',frame=283,width=640,height=640,samples=16,
          edits=[dict(kind='neutral_garment_proof',target='mounted leader',phase='neutral')])
for name in ('save','neutral_front','neutral_back','neutral_side'):
 recipe=save if name=='save' else dict(operation='nihang_frames',frame=283,frames=[283],width=640,height=640,samples=16,view=name)
 ref=write(name+'-recipe-c18.json',recipe)
 steps.append({'id':name,'kind':'proof','depends_on':[] if name=='save' else ['save'],
   'requirements':['preservation','form','interfaces','evidence'],
   'acceptance':'Actual neutral native fit prerequisite only. Save safety first; revealed shoulder, armpit, neckline, waist and cuff forms must pass images before bending. No entire appearance admission.',
   'native_recipe':ref})
art={x:pk.read_json(r,f'results/sikh335/look01/{x.lower()}-c17.json')['artifact'] for x in pp.STEPS[:3]}
b=art['STRATEGIZING']['brief']
for ref in b['source_bindings'].values():
 actual=pk.file_hash(r/ref['path'])
 if actual!=ref['sha256']:
  assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_')
  ref['sha256']=actual
paths=['results/sikh335/look01/STRATEGY_C18.md','results/sikh335/look01/allowance-341.json',
 'results/sikh335/REASSESSMENT_340.md','scripts/sikh341_plan.py','scripts/sikh341_dispatch.py',
 'src/movie_factory/adapters/blender/nihang_neutral.py','tests/test_nihang341_neutral.py',DONOR]
for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
for step in steps:b['source_bindings'][step['native_recipe']['path']]=step['native_recipe']
art['GROUNDING']['reconciliation']+=' Director341 explicitly approves actual neutral garment then bend, corrections18–19.340 failed to perform that prerequisite. The body is now loaded in actual rest from the existing local donor; no posed shirt Basis or mathematical stand-in. Original complete appearance requirements remain pending; this strategy proves their upstream garment representation only.'
for key in ('construction_interfaces','strategy','visual_gate','anatomy','au_deformation'):
 art['GROUNDING']['knowledge_uses'][key]='Apply original obligation through actual neutral donor, continuous shoulder topology, bounded outside fit, physical settling and saved front/back/side evidence. Bend and production propagation are blocked until this native neutral prerequisite passes.'
art['GROUNDING']['knowledge_uses']['current_state']='Director341 two-correction approval; same task18/max19. Protected Pashtun and separate motion9/max10 unchanged. No final character or AV pass.'
art['GROUNDING']['knowledge_uses']['render_profile']='Serial640x640 CPU16 plain studio proof to reveal garment shape, not the production look or an acceleration claim.'
b['scope']='Actual neutral garment prerequisite, then separately authorized controlled bend; whole-character appearance remains pending.'
b['early_proof']='Actual neutral-body cloth saved, independently reopened and rendered front, back and side BEFORE any bending.'
b['strategy']='Stop posed-shell tuning. Use continuous neutral donor topology with supported physical drape; native images precede any controlled bend.'
b['exclusions']='No new face/crown/saddle/crowd edits, performance integration, provider, spend, upload or final production approval.'
methods={
 'preservation':'Source remains unchanged. New proof scene and derivative retain original production data but render only real neutral donor and cloth. Bind donor and source hashes.',
 'form':'Continuous neutral shoulder/arm topology,18mm initial ease and bounded outside clearance, then actual40-frame cloth settle. Reject bodysuit/anatomical embossing, slab chest, malformed armhole or unsupported collar from rendered views.',
 'interfaces':'Inspect actual neutral shoulder, armpit, collar, waist and cuff before any bend. No old207-pose transfer yet. Use same rest-joint field for body and garment only in the subsequent admitted bend proof.',
 'evidence':'Fresh-process front/back/side640-square images of actual saved geometry. Numerical settle and open success permit inspection only. All crown/face/tack/crowd and moving performance gates remain pending.'}
for name,method in methods.items():
 real=b['expert_plan']['realizations'][name];real['method']=method
 real['early_proof']=b['early_proof']
 real['failure_condition']='Neutral garment clips, reads as painted anatomy or has malformed shoulder/armpit/collar/waist/cuff. Missing native neutral renders blocks bending. No production appearance claim from this prerequisite.'
 real['reopen_when']='Any neutral geometry, supports, bend field or required production pose changes.'
art['STRATEGIZING']['steps']=steps
art['STRATEGIZING']['method_choice']={'chosen':b['strategy'],
 'alternatives':'Reject the prior rectangular armhole/posed shell. Continuous neutral donor topology is an in-scope construction choice, not a flat sewing-pattern claim. Reject numerical-only rest tests.',
 'evidence_status':'hypothesis','discriminating_test':b['early_proof']}
art['STRATEGIZING']['resource_scope']='Two approved corrections18–19, one heavy worker serial, existing local assets only. No new spending. Native neutral proof before bending is mandatory.'
art['STRATEGIZING']['replan_triggers']='Neutral visible form fails; initial fit or settle guard fails; bend loses support or silhouette; missing actual native neutral evidence.'
b['expert_plan']['challenge']['scope_tradeoff']='Native garment prerequisite only; retain complete original appearance requirements as pending. Neutral proof cannot be skipped for an attractive posed picture.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
for stage in pp.STEPS[:3]:
 if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
 p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
 c.submit(task,p['actor'],p['ticket'],response,'sikh341-c18-'+stage)
 write(stage.lower()+'-c18.json',response)
p=c.packet(task);p.pop('ticket',None);write('challenge-input-c18.json',p)
# Bind actual changed bytes with the existing Git parent instead of copying all
#97 handlers again. No snapshot-only source is omitted from the manifest.
manifest={str(p.relative_to(r)):pk.file_hash(p) for p in sorted((r/'src/movie_factory/adapters/blender').glob('*.py'))}
write('source-manifest-c18.json',manifest)
print(c.state(task)['planning_step'])
