"""Existing appearance task: source-bound leader garment proof, no task reset."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh353';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=out/n;text=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==text,n
 else:p.write_text(text)
 return bind(str(p.relative_to(r)))
action=sys.argv[1];s=c.state(task);cycle=s['cycle'];assert 62<=cycle<=67
parent='.runtime/factory-native/sikh352-c61-save/scene.blend'
if cycle>=64:parent='.runtime/factory-native/sikh353-c63-save/scene.blend'
if cycle>=65:parent='.runtime/factory-native/sikh353-c64-save/scene.blend'
if action=='plan':
 arts={st:pk.read_json(r,f'results/sikh352/{st.lower()}-c61.json')['artifact'] for st in pp.STEPS[:3]}
 g,d,a=[arts[k] for k in pp.STEPS[:3]];b=a['brief'];direction=s['direction']
 method='Replace61 waist support query with explicitly central lower-trunk polygon set: spine/pelvis/root/upperleg support weight >.85 and arm/hand/clavicle weight <.10. Lower waist may inherit hip weights; do not mistake them for sleeves. Compare old unrestricted rays to new query; bound radial envelope and angular jumps before mutation. Preserve61 elbow ease,59 anatomy and all existing motion. Entire leader and horse remain open, crowd deferred.'
 proof='Save/reopen, compare unrestricted versus trunk-only support measurements, then leader front/reverse/contact283/288/327/350. Reject projecting strips, lobed waist, skin breakthrough, malformed cuffs and adjacent layer intersections. This narrow proof does not qualify face/turban/tack or rearing.'
 if cycle>=64:
  method='Retain63 semantic torso support. Bind band to nearby owned coat vertex weights instead of single spine05, preserve unsmoothed support radius and22mm clearance. Test actual four-pose front/reverse/contact for coat breakthrough and adjacent failures. Whole leader/horse and crowd deferral unchanged.'
  proof='Reopened63 derivative: verify band weights normalize and exclude arms; inspect front/reverse/contact283/288/327/350. No promotion from numerical attachment alone. Face/turban/tack and faithful motion still open.'
 if cycle>=65:
  method='Retain64 waist/body. Review whole actor: narrow existing layered crown ten percent, restore owned indigo cloth, moderate dense beard ends without replacing roots, preserve pigment texture and improve skin response, fit sash against actual coat and reduce horse metallic reading. Inspect actual eye inventory and close face before any form approval.'
  proof='Actual close face283/327/350, front/reverse283/288/327/350 and production283/307/327/350. Reject toy face/eye alignment, cap-like crown, rigid beard, layer penetration, shiny/blocky horse or slab tack. No full actor pass from a fixed waistband.'
 if cycle>=66:
  method+=' Correct65 omitted crown core: uniformly scale/material all eight assembly parts, assert core membership. Reduce regular thick eyebrow strokes using finer tapered varied strand lengths while preserving actual brow roots and expression. Use64 again, not cumulative65 edits.'
 if cycle>=67:
  method+='66 production still shows stiff skirt panels and uniform horse surface. Add modest rest folds and reduce thigh carry of hanging hem, preserving waist pins; actual reverse/crest checks must reject horse or leg penetration. Preserve woven saddle border; stable UV short-nap bump/roughness on horse, restrained cloth dye contrast and fine weave, retain skin pigment with bounded variation, reorient brow strokes. Authored drape is not cloth simulation.'
 for src in direction['context_sources']:
  g['uses'][src['id']]=dict(disposition='apply',reason=src['statement'],implication=method if src['id'] in {'strategy353','lessons352','controls'} else g['uses'].get(src['id'],{}).get('implication',src['statement']))
  d['context_mapping'][src['id']]=dict(requirements=['preservation','form','interfaces','evidence'],reason=src['statement'])
 packet=pk.read_json(r,'results/sikh353/appearance-knowledge-packet.json')
 for o in packet['obligations']:
  k=o['id'];v=g['knowledge_uses'][k]
  if k in {'current_state','strategy','construction_interfaces','au_contact','visual_gate'}:v=method+' '+proof
  g['knowledge_uses'][k]=v;d['knowledge_mapping'][k]['reason']=v
 g.update(reconciliation='353 ten total cycles: six appearance and four motion. Original reference/quality preserved;352 observed waist failure triggers semantic owner test. Crowd deferred.',unresolved=[])
 b.update(knowledge_task=direction['knowledge_task'],knowledge_digest=direction['knowledge_digest'],knowledge_mapping=d['knowledge_mapping'])
 b['source_bindings']={src['id']:src['binding'] for src in direction['context_sources']}
 for p in [parent,'results/sikh353/REQUEST.md','results/sikh353/STRATEGY.md','results/sikh352/CLOSEOUT.md','results/sikh352/EVIDENCE_SCOPE_NOTES.md','src/movie_factory/adapters/blender/nihang_waist353.py','src/movie_factory/adapters/blender/nihang_patch.py','tests/test_nihang353_waist.py','scripts/sikh353_plan.py']:
  b['source_bindings'][p]=bind(p)
 for ref in direction['references']:b['source_bindings'][ref['id']]=ref['binding']
 if cycle>=65:
  for p in ['results/sikh353/LOOK65_STRATEGY.md','src/movie_factory/adapters/blender/nihang_finish353.py','src/movie_factory/adapters/blender/nihang_control.py','tests/test_nihang353_finish.py']:
   b['source_bindings'][p]=bind(p)
 b.update(strategy=method,early_proof=proof,scope='Leader and horse integrated appearance/motion; first prerequisite waist semantic ownership. Not a completed actor.',exclusions='Crowd construction, full sequence render, new spending/installations/providers/cloud/egress, protected Pashtun edits.')
 for row in b['expert_plan']['realizations'].values():row.update(method=method,early_proof=proof,failure_condition='Any known visible body/cloth/contact defect or missing evidence blocks promotion. Whole actor remains distinct from waist proof.')
 for beat in d['beats']:
  beat['framing']='Leader front/reverse/contact283/288/327/350; existing production camera unchanged.'
  beat['lenses']['anatomy_contact']['why']='Support belongs to anatomical torso, never an incidental sleeve intersection; preserve valid59 pose.'
  beat['lenses']['camera_editorial']['why']='Inspect reverse waist and interfaces hidden by horse in front; then whole intended shot.'
 b['expert_plan']['beats']=d['beats']
 b['expert_plan']['challenge'].update(cross_discipline_conflicts='Belt needs independent load-bearing continuity without copying every cloth ripple; skin and sleeves may not support waist fitting.',omission_probe='Whole appearance includes face/eyes/turban/beard/skirt/boots/tack and horse; a fixed waist is not completion.',scope_tradeoff='Cheap interface proof precedes full actor motion, crowd deferred.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 steps=[]
 kind='mounted_finish353' if cycle>=65 else 'mounted_waist353_attach' if cycle>=64 else 'mounted_waist353'
 rec=write(f'save-recipe-c{cycle}.json',dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind=kind,target='mounted leader')]))
 steps.append(dict(id='save',kind='proof',depends_on=[],requirements=['preservation'],acceptance='Source preserved and semantic waist guard passes; technical save only.',native_recipe=rec));b['source_bindings'][rec['path']]=rec
 for name in (['leader_face','leader_front','leader_reverse','production'] if cycle>=65 else ['leader_front','leader_reverse','leader_contact']):
  frames=[283,327,350] if name=='leader_face' else [283,307,327,350] if name=='production' else [283,288,327,350]
  rec=write(f'{name}-recipe-c{cycle}.json',dict(operation='nihang_frames',frame=327,frames=frames,view=name,width=640,height=640,samples=12 if name=='leader_face' else 8));b['source_bindings'][rec['path']]=rec
  steps.append(dict(id=name,kind='proof',depends_on=['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=proof,native_recipe=rec))
 a.update(steps=steps,method_choice=dict(chosen=method,alternatives='Do not smooth or shrink the malformed61 band; correct query ownership while keeping source garment.',evidence_status='hypothesis',discriminating_test=proof),resource_scope=f'Appearance{cycle}/67, motion13/16; ten total. One local worker, no new spend.',replan_triggers='Wrong support or adjacent defects invalidate strategy; retain original counters/history.')
 for st in pp.STEPS[:3]:
  if pp.STEPS.index(st)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[st]);c.submit(task,p['actor'],p['ticket'],v,f'sikh353-c{cycle}-{st}');write(f'{st.lower()}-c{cycle}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh353/challenge-c{cycle}.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh353-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
 result=pk.read_json(r,f'results/sikh353/save-run-c{cycle}.json');diag=pk.read_json(r,result['artifacts']['scripts']['path']);assert not diag['blocked_drivers'] and not diag['known_source_defects']
 for item in result['artifacts'].values():assert pk.file_hash(r/item['path'])==item['sha256']
 patch=pk.read_json(r,result['artifacts']['patch']['path']);assert patch['before']['objects']==patch['after']['objects'];report=patch['support'][0]['finish353' if cycle>=65 else 'waist353'];assert report['changed'] and report['source_preserved']
 if cycle<65:assert report['excluded_faces']>0
 v=dict(verdict='PASS',run_digest=pk.digest(result),evidence=result['artifacts'],observation='Saved/reopened derivative, protected objects retained; torso-only face set and radial limits verified. Not a visual pass.',comparison='61 unrestricted support is preserved negative control; actual diagnostics retained.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-c{cycle}.json',v)
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 source=bind(parent) if action=='save' else pk.read_json(r,f'results/sikh353/save-run-c{cycle}.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,f'sikh353-c{cycle}-{action}',parent=source,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write(f'{action}-run-c{cycle}.json',result);print({k:result.get(k) for k in ['id','status','error']})
 if result['status']!='RETURNED':raise SystemExit(2)
