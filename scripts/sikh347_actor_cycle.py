"""Three-pose layer proof on existing actor; shared346 allowance only."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
s=c.state(task);cycle=s['cycle'];assert 48<=cycle<=52
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
 for path in ['results/sikh335/allowance347.json','results/sikh335/STRATEGY_347.md','results/sikh335/REASSESSMENT_346.md',
 '.runtime/knowledge-pilot213/sikh347-current.json','src/movie_factory/adapters/blender/nihang_finish345.py',
 'tests/test_nihang345_finish.py','scripts/sikh347_actor_cycle.py','results/sikh335/look01/rejection-c37.json',
 '.runtime/factory-native/sikh346-look-c47-save/scene.blend',
 '.runtime/art-direction/series01-sikh265/candidate-04/character.blend',
 'src/movie_factory/adapters/blender/nihang_control.py','src/movie_factory/adapters/blender/nihang_whole347.py','tests/test_nihang347_whole.py',
 '.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-02/skin-authored.png']:
  b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 reason='347 extends existing task47 by five; complete mounted appearance is the proof, not another isolated contact solve. Actual47 front and reverse are failing controls. Preserve original intent, source roles, accepted co-star floor and motion12.'
 arts['GROUNDING']['reconciliation']=reason
 arts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['strategy']='Read STRATEGY_347: derive47; preserve hands/skeleton and torso anatomy. Freeze waist/cuffs, relax shoulder rest surface and all hidden supports together; linear skinning with corrective joint relaxation, waist-origin folds, fabric grain, crown compression and integrated beard. Whole actor three poses before any crowd.'
 b['early_proof']='Save/reopen derivative47, then actual front/reverse at283,327,350 plus contact and production. Reject ballooning, skin penetration, elbow pocket, disconnected beard/eyes, simplistic crown, saddle mismatch or whole-actor same-film failure. Motion/audio remain separately pending.'
 b['exclusions']='No crowd, principal Sikh, terrain, camera, audio, new assets, installations, provider, spending or egress. No principal acceptance of source265. Preserve motion12.'
 methods={'preservation':'Retain all originals and33 native. Derive new scene; protect four production owners and accepted Pashtun.',
 'form':b['strategy'],'interfaces':'Waist and shoulder have distinct geometric support and actual-bone ownership. Preflight full sampling before animation. Cuffs retain forearm ownership; inspect bare anatomy and wrist continuity. Metrics are not visual admission.',
 'evidence':b['early_proof']}
 for key,row in b['expert_plan']['realizations'].items():
  row['method']=methods[key];row['early_proof']=b['early_proof'];row['failure_condition']='Missing binding, visible penetration, unsupported cuffs/hands/seat, same-film failure, or missing actual pose evidence.'
  row['reopen_when']='Any source, pose, topology, material, camera or integration changes.'
 b['expert_plan']['challenge']['scope_tradeoff']='Whole actor appearance is the exit, not a layer-only pass. No full passage render while static defects remain; no lowering accepted co-star floor.'
 b['expert_plan']['challenge']['omission_probe']='An orthogonal hand frame and reachable thumb can still produce a bad visible fist; inspect all digits, sleeve, shaft penetration and silhouette. A root supported in rest can separate in the crest; inspect waist and thigh in all poses. Face/crown/saddle remain known open quality work, never inferred passed.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy=arts['STRATEGIZING'];strategy['method_choice']=dict(chosen=b['strategy'],alternatives='Do not add larger offsets to independently weighted layers, hide anatomy, or rebake190 frames before stance proof.',evidence_status='hypothesis',discriminating_test=b['early_proof'])
 recovered='.runtime/factory-native/sikh345-look-c39-save/scene.blend'
 for path in [recovered,'results/sikh335/look01/save-run-c39.json','results/sikh335/look01/rejection-c39.json']:
  b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 recipes={'save':dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,edits=[dict(kind=k,target='mounted leader') for k in ('mounted_whole347',)])}
 for name,view in [('leader_front','leader_front'),('leader_reverse','leader_reverse'),('leader_contact','leader_contact'),('leader_anatomy','leader_anatomy'),('render','production')]:
  recipes[name]=dict(operation='nihang_frames',frame=283,frames=[283,327,350],view=view,width=540,height=960,samples=16)
 steps=[]
 for name,value in recipes.items():
  bind=write(f'{name}-recipe-c{cycle}.json',value);b['source_bindings'][bind['path']]=bind
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=bind))
 strategy['steps']=steps;strategy['resource_scope']='Five approved347 corrections48 through52 on same task. One local worker, no spend/egress.'
 strategy['replan_triggers']='Binding or actual posed interfaces fail; reassess only affected method, preserve shared limit and failure history.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[stage])
  c.submit(task,p['actor'],p['ticket'],v,f'sikh347-actor-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,f'sikh347-actor-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert patch['before']['objects']==patch['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
 whole=patch['support'][0]['whole347']
 assert whole['changed'] and whole['objects']
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Protected owners and source diagnostics verified; complete actor mutation saved and reopened.',comparison='Technical prerequisite only, no image or performance pass.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-review-c{cycle}.json',v);print(json.dumps({'changed':whole['changed'],'max_change':whole['maximum_rest_change']}))

else:
 assert action in ('save','leader_front','leader_reverse','leader_contact','leader_anatomy','render')
 if action=='save':
  path='.runtime/factory-native/sikh346-look-c47-save/scene.blend';parent={'path':path,'sha256':pk.file_hash(r/path)}
 else:parent=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json')['artifacts']['native']
 recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 run=Bridge(c).dispatch(task,action,f'sikh347-look-c{cycle}-{action}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(f'{action}-run-c{cycle}.json',run);print(json.dumps(dict(id=run['id'],status=run['status'],error=run.get('error'))))
 if run['status']!='RETURNED':raise SystemExit(2)

