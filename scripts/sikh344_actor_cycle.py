"""Three-pose layer proof on existing actor; shared344 allowance only."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
s=c.state(task);cycle=s['cycle'];assert 34<=cycle<=37
out=r/'results/sikh335/look01';action=sys.argv[1]
def write(name,value):
 p=out/name;text=json.dumps(value,indent=2)+'\n'
 if p.exists():assert p.read_text()==text
 else:p.write_text(text)
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
if action=='plan':
 arts={st:pk.read_json(r,f'results/sikh335/look01/{st.lower()}-c33.json')['artifact'] for st in pp.STEPS[:3]}
 b=arts['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_') or ref['path']=='tests/test_nihang343_actor.py';ref['sha256']=actual
 for path in ['results/sikh335/allowance344.json','results/sikh335/STRATEGY_344.md','results/sikh335/REASSESSMENT_343.md',
 '.runtime/knowledge-pilot213/sikh344-current.json','src/movie_factory/adapters/blender/nihang_refit.py',
 'tests/test_nihang344_refit.py','scripts/sikh344_actor_cycle.py','results/sikh335/look01/rejection-c33.json',
 '.runtime/factory-native/sikh343-look-c33-save/scene.blend']:
  b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 reason='344 five shared additions; motion12 used one. Existing coherent33 native is structurally reusable but visually rejected. Bind outer layers to actual coat, inspect actual three poses before any new full bake or crowd propagation. No identity, skin or donor acceptance inferred.'
 arts['GROUNDING']['reconciliation']=reason
 arts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['strategy']='Retain36 actual-body coat, bound layers and removal of false pants hand islands. Keep coat hem1.005m but reduce skirt-root extension to35mm so the belt remains outside and visible. Oppose each actual thumb across the index grip with fixed anatomical lengths, rather than curling thumb around the four-finger axis. Retain all other rig action. Inspect three front/reverse poses and intended production framing; no crowd propagation.'
 b['early_proof']='Native bind and save/reopen; numerical layer signed distances and actual front/reverse stance283 crest327 landing350. Reject missing binding, intersections, cuff/hand distortion, seat failure, unqualified whole-face/form, or adjacent regressions. Real-time AV and whole actor remain separate from scoped layer proof.'
 b['exclusions']='No crowd, principal Sikh, terrain, camera, audio, new assets, installation, provider, spending, egress. No acceptance of rejected33 body look or source265 principal identity. Horse12 remains separate until both interfaces qualify.'
 methods={'preservation':'Retain all originals and33 native. Derive new scene; protect four production owners and accepted Pashtun.',
 'form':b['strategy'],'interfaces':'Actual evaluated coat owns outer layers through native surface binding. Cuffs retain forearm ownership; inspect bare anatomy visible at boundaries. Signed-distance metrics are diagnostic, not a visual pass.',
 'evidence':b['early_proof']}
 for key,row in b['expert_plan']['realizations'].items():
  row['method']=methods[key];row['early_proof']=b['early_proof'];row['failure_condition']='Missing binding, visible penetration, unsupported cuffs/hands/seat, same-film failure, or missing actual pose evidence.'
  row['reopen_when']='Any source, pose, topology, material, camera or integration changes.'
 b['expert_plan']['challenge']['scope_tradeoff']='Layer prerequisite can advance without passing generic face or whole actor; known failures remain internal and block ensemble.'
 b['expert_plan']['challenge']['omission_probe']='34 actual frames exposed severe body-through-template intersections. Binding success was irrelevant to invalid coat support. Inspect shoulder/chest coverage and cuff ownership before layers, then all posed interfaces and entire figure; body-derived shell may still read as tight anatomical skin rather than cloth.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy=arts['STRATEGIZING'];strategy['method_choice']=dict(chosen=b['strategy'],alternatives='Do not add larger offsets to independently weighted layers, hide anatomy, or rebake190 frames before stance proof.',evidence_status='hypothesis',discriminating_test=b['early_proof'])
 recipes={'save':dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,edits=[dict(kind='coherent_refit',target='mounted leader')])}
 for name,view in [('leader_front','leader_front'),('leader_reverse','leader_reverse'),('render','production')]:
  recipes[name]=dict(operation='nihang_frames',frame=283,frames=[283,327,350],view=view,width=540,height=960,samples=16)
 steps=[]
 for name,value in recipes.items():
  bind=write(f'{name}-recipe-c{cycle}.json',value);b['source_bindings'][bind['path']]=bind
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=bind))
 strategy['steps']=steps;strategy['resource_scope']='Five shared344 corrections; each existing-task allocation recorded. One local heavy worker, no new spend/egress.'
 strategy['replan_triggers']='Binding or actual posed interfaces fail; reassess only affected method, preserve shared limit and failure history.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[stage])
  c.submit(task,p['actor'],p['ticket'],v,f'sikh344-actor-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,f'sikh344-actor-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert patch['before']['objects']==patch['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
 refit=patch['support'][0]['refit'];assert all(x['bound'] for x in refit['layers'])
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Native surface bindings, saved poses and protected owners verified.',comparison='Technical prerequisite only, all visual and full-speed judgments separate.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-review-c{cycle}.json',v);print(json.dumps(refit))
else:
 assert action in ('save','leader_front','leader_reverse','render')
 parent=pk.read_json(r,'results/sikh335/look01/save-run-c33.json' if action=='save' else f'results/sikh335/look01/save-run-c{cycle}.json')['artifacts']['native']
 recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 run=Bridge(c).dispatch(task,action,f'sikh344-look-c{cycle}-{action}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(f'{action}-run-c{cycle}.json',run);print(json.dumps(dict(id=run['id'],status=run['status'],error=run.get('error'))))
 if run['status']!='RETURNED':raise SystemExit(2)
