"""Existing motion13 task: reference compactness and landing invariance."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh353';c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=out/n;text=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==text,n
 else:p.write_text(text)
 return bind(str(p.relative_to(r)))
action=sys.argv[1];s=c.state(task);cy=s['cycle'];assert 13<=cy<=16
parent='.runtime/factory-native/sikh353-c65-save/scene.blend'
if cy>=14:parent='.runtime/factory-native/sikh353-c67-save/scene.blend'
if cy>=15:parent='.runtime/factory-native/sikh353-motion-c14-save/scene.blend'
if action=='plan':
 arts={st:pk.read_json(r,f'results/sikh335/motion01/{st.lower()}-c12.json')['artifact'] for st in pp.STEPS[:3]}
 g,d,a=[arts[st] for st in pp.STEPS[:3]];b=a['brief'];direction=s['direction']
 method='On current leader/horse derivative capture all190 original poses. Rotate forefoot/toe/hoof together about unchanged carpus in sagittal plane; peak43degree extra curl follows existing fold. Smooth release to exactly zero by341. Preserve root/hind/neck/rider and every341–441 arrival transform; no global retime or wholesale action replay.'
 proof='Allframe transform preservation plus intended production samples294/307/317/327/331/337/341/347/350/353 against reference17.2–18.4s and original12. Reject outward toes, malformed foreleg folds, changed final arrival or any new contact/body defect. Full-speed judgment remains Director313; no known appearance waiver.'
 if cy>=14:
  method='Reapply exact12 phase/support anchors to current67 grounded stance, including accelerating actual visible-hoof arrival. Synchronize coherent spine response, preserve local head acting and rebind all17 visible head attachments. Re-solve supported spear arm preserving world tip, and bind reins to actual coherent right-hand grip. Then apply13 crest curl with exact341+ invariant of this corrected base.'
  proof='Verify both final visible-hoof speeds accelerate downward, all190 head attachments/real reins/spear supported, no invalid drivers; inspect production294/307/317/327/331/337/341/347/350/353 against original reference. Known appearance failure remains separate; static evidence cannot pass fluidity or rigid gesture.'
 if cy>=15:
  method='Preserve14 actual accelerating horse motion and coherent rider. Replace wrong permanently planted spear with cue/strike/carry states and constant material grip station. Capture190 source poses first; bounded two-link left arm using original lengths/elbow preference, highest feasible12–18cm lift, wrist<=45degrees, continuous elbow. Strike300 before drive, spear carried off ground during rear as original reference2/3.'
  proof='Actual source14 trajectory unchanged; constant grip material station and no ground penetration; inspect cue293/downstroke297/strike300/drive307/crest327/descent341/347/impact350/absorption353 plus revealing leader front293/300/327/350. Reject arm twist, disconnected cuffs, sliding fingers or wrong cue/contact timing. Appearance remains failed separately; no AV pass from numeric checks.'
 if cy==16:
  method+=' Replace15 symmetric easing downstroke with accelerating strike; actual tip velocity296–300 must accelerate into contact. Retain prior15 as negative timing control; geometry/horse and held material grip unchanged.'
  proof+=' Compare actual final tip velocities against15 slowdown, not endpoints alone; inspect the same ten phases and four front controls. Still no whole-motion or appearance qualification.'
 for src in direction['context_sources']:
  g['uses'][src['id']]=dict(disposition='apply',reason=src['statement'],implication=method if src['id'] in {'strategy353','lessons352','controls'} else g['uses'].get(src['id'],{}).get('implication',src['statement']))
  d['context_mapping'][src['id']]=dict(requirements=['preservation','support','phases','rider','evidence'],reason=src['statement'])
 packet=pk.read_json(r,'results/sikh353/motion-knowledge-packet.json')
 for o in packet['obligations']:
  k=o['id'];v=g['knowledge_uses'].get(k,'Apply source-bound obligation to current leader/horse scope; crowd deferred.')
  if k in {'current_state','strategy','animal_coordination','anatomy','au_performance','motion'}:v=method+' '+proof
  g['knowledge_uses'][k]=v;d['knowledge_mapping'].setdefault(k,dict(requirements=['preservation','support','phases','rider','evidence']))['reason']=v
 g.update(reconciliation='353 ten total cycles, four motion13–16.13 exposed missing12 arrival on actual consuming appearance branch; correct explicit interfaces rather than infer integration from similar crest. Appearance remains a candidate, not accepted actor.',unresolved=[])
 b.update(knowledge_task=direction['knowledge_task'],knowledge_digest=direction['knowledge_digest'],knowledge_mapping=d['knowledge_mapping'])
 b['source_bindings']={x['id']:x['binding'] for x in direction['context_sources']}
 for p in [parent,'results/sikh353/MOTION_STRATEGY.md','results/sikh335/motion01/save-c12-recipe.json','results/sikh335/motion01/landing-review-c12.md','results/sikh321/preserved-comparisons/reference-3.jpg','src/movie_factory/adapters/blender/nihang_motion353.py','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/adapters/blender/nihang_control.py','tests/test_nihang353_motion.py','scripts/sikh353_motion_plan.py']:
  b['source_bindings'][p]=bind(p)
 for ref in direction['references']:b['source_bindings'][ref['id']]=ref['binding']
 if cy>=14:
  for p in ['results/sikh353/INTEGRATION14_STRATEGY.md','results/sikh353/MOTION_INTEGRATION_FINDING.md','src/movie_factory/adapters/blender/nihang_integrate353.py','src/movie_factory/adapters/blender/nihang_arm352.py','src/movie_factory/adapters/blender/nihang_motion.py','src/movie_factory/adapters/blender/nihang_support.py','tests/test_nihang353_integration.py']:
   b['source_bindings'][p]=bind(p)
 if cy>=15:
  for p in ['results/sikh353/GESTURE15_STRATEGY.md','results/sikh321/preserved-comparisons/reference-2.jpg','src/movie_factory/adapters/blender/nihang_gesture353.py','tests/test_nihang353_gesture.py']:
   b['source_bindings'][p]=bind(p)
 if cy==16:
  b['source_bindings']['gesture16diagnosis']=bind('results/sikh353/GESTURE16_DIAGNOSIS.md')
 b.update(strategy=method,early_proof=proof,scope='Leader and horse integrated performance with original whole-reference and appearance gates.',exclusions='No crowd construction, accepted Pashtun/principal/camera edits, providers/spend/upload or full trailer render.')
 for row in b['expert_plan']['realizations'].values():row.update(method=method,early_proof=proof,failure_condition='Any displaced planted support, malformed fold, changed arrival or known visible actor/contact defect; no AV claim from frames.')
 b['expert_plan']['beats']=d['beats'];b['expert_plan']['challenge'].update(omission_probe='Correct arrival alone cannot qualify whole horse/rider motion, surface, face, spear/rein contacts or transition weight.',scope_tradeoff='Correct actual consuming branch before polishing secondary motion. Crowd deferred.',cross_discipline_conflicts='New base motion must carry coherent spine/head attachments, arm/real reins and leg/seat interfaces; preserved controls alone are insufficient.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 steps=[]
 frames=[283,293,297,300,307,327,341,347,350,353] if cy>=15 else [294,307,317,327,331,337,341,347,350,353]
 recipes=[('save',dict(operation='nihang_patch',frame=327,width=432,height=768,samples=8,edits=[dict(kind='mounted_gesture353' if cy>=15 else 'mounted_integrate353' if cy>=14 else 'mounted_motion353',target='mounted leader')])),('render',dict(operation='nihang_frames',frame=327,frames=frames,view='production',width=432,height=768,samples=8))]
 if cy>=15:recipes.append(('gesture_front',dict(operation='nihang_frames',frame=327,frames=[293,300,327,350],view='leader_front',width=640,height=640,samples=8)))
 for name,recipe in recipes:
  ref=write(f'motion-{name}-recipe-c{cy}.json',recipe);b['source_bindings'][ref['path']]=ref
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','support','phases','rider','evidence'],acceptance=proof,native_recipe=ref))
 a.update(steps=steps,method_choice=dict(chosen=method,alternatives='Do not globally speed clip or copy old costume action wholesale; integrate support method and actual current actor interfaces.',evidence_status='hypothesis',discriminating_test=proof),resource_scope=f'Motion{cy}/16 within353 ten total, one local worker, no spend.',replan_triggers='Any support/arrival regression or wrong fold shape requires same-task targeted repair; retain all history.')
 for st in pp.STEPS[:3]:
  if pp.STEPS.index(st)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[st]);c.submit(task,p['actor'],p['ticket'],v,f'sikh353-motion{cy}-{st}');write(f'motion-{st.lower()}-c{cy}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'motion-challenge-input-c{cy}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh353/motion-challenge-c{cy}.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh353-motion{cy}-admit');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,f'results/sikh353/motion-save-run-c{cy}.json');assert run['status']=='RETURNED'
 for item in run['artifacts'].values():assert pk.file_hash(r/item['path'])==item['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);report=patch['support'][0]['gesture353' if cy>=15 else 'integrate353' if cy>=14 else 'motion353']
 if cy>=15:
  assert report['maximum_material_grip_error']<1e-4 and report['maximum_horse_root_error']<1e-5 and report['maximum_wrist_bend']<=45 and len(report['frames'])==190
  if cy==16:assert all(b<a<0 for a,b in zip(report['strike_velocity'],report['strike_velocity'][1:]))
 else:
  curl=report['curl'] if cy>=14 else report;assert curl['maximum_preserved_error']<1e-4 and curl['maximum_arrival_error']<1e-4 and len(curl['frames'])==190
 if cy==14:
  assert report['maximum_attachment_error']<1e-4
  for v in report['landing_velocity'].values():assert all(b<a<0 for a,b in zip(v,v[1:]))
 diag=pk.read_json(r,run['artifacts']['scripts']['path']);assert not diag['blocked_drivers'] and not diag['known_source_defects']
 observation='Saved/reopened,190 frame guards passed.14 actual consuming-branch arrival integrated;15+ fixed material grip/horse-root preservation and bounded wrist passed. Technical prerequisite only.'
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation=observation,comparison='Reference shape/whole performance and actor appearance still require actual images and eventual Director AV.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'motion-save-technical-c{cy}.json',v)
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 source=bind(parent) if action=='save' else pk.read_json(r,f'results/sikh353/motion-save-run-c{cy}.json')['artifacts']['native']
 run=Bridge(c).dispatch(task,action,f'sikh353-motion-c{cy}-{action}',parent=source,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write(f'motion-{action}-run-c{cy}.json',run);print({k:run.get(k) for k in ['id','status','error']})
 if run['status']!='RETURNED':raise SystemExit(2)
