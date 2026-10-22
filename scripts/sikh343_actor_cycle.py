"""Coherent supporting actor proof on existing task30–33, never a new budget."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
s=c.state(task);cycle=s['cycle'];assert 30<=cycle<=33 and s['max_corrections']==33
out=r/'results/sikh335/look01';action=sys.argv[1]
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
if action=='plan':
 arts={st:pk.read_json(r,f'results/sikh335/look01/{st.lower()}-c29.json')['artifact'] for st in pp.STEPS[:3]}
 b=arts['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith(('src/movie_factory/adapters/blender/nihang_','tests/test_nihang'));ref['sha256']=actual
 paths=['results/sikh335/allowance343.json','results/sikh335/REASSESSMENT_342.md','results/sikh335/task343.json',
 '.runtime/knowledge-pilot213/sikh343-current.json','scripts/sikh343_actor_cycle.py',
 'src/movie_factory/adapters/blender/nihang_actor.py','src/movie_factory/adapters/blender/nihang_patch.py',
 'tests/test_nihang343_actor.py','.runtime/art-direction/series01-sikh265/candidate-04/character.blend',
 '.runtime/art-direction/series01-sikh265/candidate-04/build.json','.runtime/art-direction/series01-sikh264/proof-01/reopen.json',
 'docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md','results/sikh335/look01/rejection-c29.json',
 '.runtime/factory-native/sikh342-look-c23-save/scene.blend']
 for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 reason='343 shared five corrections: motion11 rejected actual landing slowdown; four allocated to appearance30–33. Coherent MPFB candidate04 is rejected principal art but verified163-bone structural donor with existing local CC0 beard/moustache. Its old Harsh turban is excluded. No new identity acceptance or rig qualification inferred.'
 arts['GROUNDING']['reconciliation']=reason+' Preserve original335 intent and reference roles; prior29 mixed-anatomy assembly is the negative control. Fresh343 packet and manual AU06/09/10/13,319/320 interfaces govern this representative proof.'
 arts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['strategy']='Replace separate head/neck/hands/torso/waist skin with one complete existing weighted MPFB anatomical donor. Preserve its163-bone skeleton and source rest relationships. Construct coat/pants/boots from its evaluated rest surface with inherited deformation weights, split chola skirt, supported waist and shoulder wrap; attach crown/eyes/brows to same head control. Retarget existing palm/boot targets with fixed-length two-link chains. No ensemble copies before full representative figure succeeds.'
 if cycle>=31:
  b['strategy']+=' Correction31 retains the coherent body but replaces the failed global-cut coat with fitted qualified23 continuous garment topology and shared rig weights. Explicit holder-world crown transform replaces stale unevaluated child matrix; finger curl follows the anatomical across-palm axis and natural rest bend, not assumed localX.30 front/reverse failures remain preserved.'
  for path in ['results/sikh335/look01/rejection-c30.json','results/sikh335/look01/source-c30/nihang_actor.py']:
   b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 if cycle>=32:
  b['strategy']+='31 stopped before a candidate at an unsupported sash ray.32 derives waistband from actual garment radial intersections and bridges the shoulder over actual vertical surface hits. Sash edge adjustment is bounded to60mm with hard missing-support guards; no visual success inferred.'
  for path in ['results/sikh335/look01/rejection-c31.json','results/sikh335/look01/source-c31/nihang_actor.py']:
   b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 if cycle>=33:
  b['strategy']+='32 stopped at the waistband support guard.33 measures the actual fitted torso hem boundary and places the complete belt25mm above its highest point; sash starts above that. Preserve actual intermediate garment coordinates before support tracing. This is the final allocated appearance correction.'
  for path in ['results/sikh335/look01/rejection-c32.json','results/sikh335/look01/source-c32/nihang_actor.py']:
   b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 b['early_proof']='Save/reopen actual283 leader front/reverse then production283/310/327/350. Inspect whole person and neck/shoulder/cuff/finger/waist/seat/pad/crown interfaces at actual shot scale, against accepted Pashtun floor and rejected29. Inspect actual163-bone ownership, body/garment weights and190 sampled frames. Reject failed reach, doubled skin, holes, unrecognizable anatomy, generic doll silhouette or unstable costume. Static proofs do not qualify full-speed motion.'
 b['exclusions']='No principal Sikh change, crowd propagation, terrain, camera/timing, music, new assets/install/provider/spend/egress. Horse motion5 remains source; motion11 failed landing is not incorporated. No automatic acceptance of old MPFB principal face or old turban.'
 methods={'preservation':'Use original23 derivative; keep protected four production owners and accepted masters unchanged. Render-hide old leader geometry, preserve it for comparison. New donor objects and rigid/weighted ownership are separately named.',
 'form':b['strategy'],
 'interfaces':'One anatomical surface plus shared native armature for body and garments. Source morphs flattened only for cloth derivation; body stays editable. Same head transform drives accessories; actual wrist/ankle targets and fixed-length links, with strict reach failures. Complete clothed side/reverse/crest proof before any replication.',
 'evidence':b['early_proof']}
 for key,row in b['expert_plan']['realizations'].items():
  row['method']=methods[key];row['early_proof']=b['early_proof'];row['failure_condition']='Unreachable limbs, wrong source weights/masks/coordinates, visible joins or mannequin form, coat/sash/crown penetration, changed protected owners, or missing claimed evidence.'
  row['reopen_when']='Donor, skeleton, rest shape, garment topology, target pose, camera or integration changes.'
 b['expert_plan']['challenge']['scope_tradeoff']='Prove the complete mounted actor before near-crowd copies. Costume detail cannot excuse anatomical failures. Donor face remains unapproved and must be judged in the actual film.'
 b['expert_plan']['challenge']['omission_probe']='Inspect wrists and fingers, eyes/eyelids, head-to-neck and waist/hip continuity, reverse garment support, and seat against the horse—not just the front garment.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 # Replace inherited cache-specific requirement, preserving expert mappings.
 for req in arts['DERIVING']['requirements']:
  if req['id']=='interfaces':req['criterion']='One anatomical body/skeleton and weighted garment assembly; real sleeve/hand, neck, waist, seat and crown interfaces remain coherent across stance/crest/landing.'
 for req in b.get('requirements',[]):
  if req['id']=='interfaces':req['criterion']='One anatomical body/skeleton and weighted garment assembly; real sleeve/hand, neck, waist, seat and crown interfaces remain coherent across stance/crest/landing.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy=arts['STRATEGIZING'];strategy['method_choice']={'chosen':b['strategy'],'alternatives':'Reject another local patch of separate proxy skin or cosmetic beard/crown detail over broken joins. MPFB264/265 native rig is available; Blender Studio neutral mesh is not a verified rig. No specialist/new acquisition needed for this bounded structural proof.','evidence_status':'hypothesis','discriminating_test':b['early_proof']}
 recipes={'save':dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,edits=[dict(kind='coherent_actor',target='mounted leader')]),
 'leader_front':dict(operation='nihang_frames',frame=283,frames=[283],view='leader_front',width=540,height=960,samples=16),
 'leader_reverse':dict(operation='nihang_frames',frame=283,frames=[283],view='leader_reverse',width=540,height=960,samples=16),
 'render':dict(operation='nihang_frames',frame=327,frames=[283,310,327,350],view='production',width=540,height=960,samples=16)}
 steps=[]
 for name,recipe in recipes.items():
  bind=write(f'{name}-recipe-c{cycle}.json',recipe);b['source_bindings'][bind['path']]=bind
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=bind))
 strategy['steps']=steps;strategy['resource_scope']='Appearance30–33: four remaining shared343 corrections. One heavy local worker at a time, no new spend/egress. Failed plan/implementation still consumes correction; no reset.'
 strategy['replan_triggers']='Native donor/mask/weight precondition fails, protected owner changes, actual body/garment/contact failure, or same-film whole-character veto.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[stage])
  c.submit(task,p['actor'],p['ticket'],v,f'sikh343-actor-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p)
 write(f'source-manifest-c{cycle}.json',{str(p.relative_to(r)):pk.file_hash(p) for p in sorted((r/'src/movie_factory/adapters/blender').glob('*.py'))})
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,f'sikh343-actor-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert patch['before']['objects']==patch['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
 actor=patch['support'][0]['actor'];assert actor['bones']==163 and actor['frames']==190
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Protected production transforms unchanged. Coherent source163-bone body, weighted clothing and190 sampled pose states saved/reopened with safe drivers.',comparison='Technical prerequisite only; whole character, contacts, same-film look and AV remain unqualified.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-review-c{cycle}.json',v);print(json.dumps(actor))
else:
 assert action in ('save','leader_front','leader_reverse','render')
 parent=pk.read_json(r,'results/sikh335/look01/save-run-c23.json' if action=='save' else f'results/sikh335/look01/save-run-c{cycle}.json')['artifacts']['native']
 recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 run=Bridge(c).dispatch(task,action,f'sikh343-look-c{cycle}-{action}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(f'{action}-run-c{cycle}.json',run);print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
 if run['status']!='RETURNED':raise SystemExit(2)
