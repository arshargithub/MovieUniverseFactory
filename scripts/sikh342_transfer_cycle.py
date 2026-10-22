"""Admitted actual-actor transfer stage of the existing appearance task."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
cycle=s['cycle'];assert 24<=cycle<=29
out=r/'results/sikh335/look01';action=sys.argv[1]
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
if action=='plan':
 artifacts={stage:pk.read_json(r,f'results/sikh335/look01/{stage.lower()}-c23.json')['artifact'] for stage in pp.STEPS[:3]}
 b=artifacts['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_') or ref['path'].startswith('tests/test_nihang');ref['sha256']=actual
 paths=['results/sikh335/TRANSFER_342.md','results/sikh335/look01/prerequisite-c23.json',
 'results/sikh335/look01/allowance342-sikh335-supporting-appearance-23.json',
 'scripts/sikh342_transfer_cycle.py','src/movie_factory/adapters/blender/nihang_transfer.py','tests/test_nihang342_transfer.py',
 '.runtime/factory-native/sikh342-look-c23-save/scene.blend']
 for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 reason='Neutral23 and connected-arm bend passed all three views; source donor topology corrected the false thigh diagnosis. Advance inside existing task to actual leader garment, exact cached pose endpoints, preserved owners, supported sash and neckline. Four more shared cycles allocated24-27;2 remain reserved.'
 artifacts['GROUNDING']['reconciliation']+=' '+reason
 artifacts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['early_proof']='Actual mounted leader stance and reverse plus327 crest, including cuff, shoulder, collar and waist/sash support. No crowd propagation until the leader transfer qualifies.'
 b['exclusions']='No new head/crown/horse, production camera, provider, spend or upload in this dependency proof. Those original appearance obligations remain pending and prevent a whole-character pass.'
 b['strategy']='Transfer continuous physically settled neutral cloth through measured319 anatomical segment mapping into actual existing207 leader poses; preserve source rig/owners. Retarget outside sash support; inspect real pose and reverse before further costume work.'
 b['expert_plan']['realizations']['form']['method']=b['strategy']
 b['expert_plan']['realizations']['interfaces']['method']='Read poseNNNN cache coordinates directly, never stale hidden-object transforms. Copy actual shirt ownership/inverse. Connected forearm masks keep cuffs whole; measured cuff means must stay within7mm of targets. Sash binds to new shirt. All original transforms remain unchanged.'
 b['expert_plan']['realizations']['preservation']['method']='Use saved qualified neutral23 derivative; keep original production rig and accepted assets untouched. Retain old garment hidden and original cache in derivative.'
 b['expert_plan']['realizations']['evidence']['method']='Independent saved native reopen plus actual leader front/reverse/stance/crest renders. Cuff numeric guards allow inspection only; no character or motion pass.'
 for row in b['expert_plan']['realizations'].values():
  row['early_proof']=b['early_proof'];row['failure_condition']='Actual garment has disconnected sleeve, distorted shoulder/elbow/cuff, broken collar, skin penetration, floating sash or waist gap. Existing face/crown/tack defects remain whole-character vetoes.'
  row['reopen_when']='Donor, pose cache, parent ownership, garment or layer support changes.'
 b['expert_plan']['challenge']['scope_tradeoff']='Actual leader garment dependency only. Neutral progress does not pass supporting cast. Do not propagate a failed interface.'
 b['expert_plan']['challenge']['omission_probe']='Clothing success cannot excuse hollow eyes, static expression, weak crown or tack. Full original intent remains the final gate.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy=artifacts['STRATEGIZING'];strategy['method_choice']={'chosen':b['strategy'],'alternatives':'Do not reuse rejected posed rectangular shell or inflate old muscle-following surface. Do not infer garment fit from neutral alone.','evidence_status':'hypothesis','discriminating_test':b['early_proof']}
 steps=[]
 recipes={'save':dict(operation='nihang_patch',frame=283,width=540,height=960,samples=24,edits=[dict(kind='neutral_actor_transfer',target='mounted leader',phase='leader')]),
 'leader_front':dict(operation='nihang_frames',frame=283,frames=[283],view='leader_front',width=540,height=960,samples=24),
 'leader_reverse':dict(operation='nihang_frames',frame=283,frames=[283],view='leader_reverse',width=540,height=960,samples=24),
 'render':dict(operation='nihang_frames',frame=283,frames=[283,310,327,348],view='production',width=540,height=960,samples=24)}
 for name,recipe in recipes.items():
  binding=write(f'{name}-recipe-c{cycle}.json',recipe);b['source_bindings'][binding['path']]=binding
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=binding))
 strategy['steps']=steps;strategy['resource_scope']='Current appearance24-27 from shared10;2 unallocated. One native worker, no newspend/egress. No task completion from this narrower prerequisite.'
 strategy['replan_triggers']='Cache/coordinate assumptions fail; actual neckline, armhole, elbow, cuff or sash fails; missing native proof; known whole-character quality veto remains.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);response=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=artifacts[stage])
  c.submit(task,p['actor'],p['ticket'],response,f'sikh342-transfer-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',response)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p)
 write(f'source-manifest-c{cycle}.json',{str(p.relative_to(r)):pk.file_hash(p) for p in sorted((r/'src/movie_factory/adapters/blender').glob('*.py'))})
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,f'sikh342-transfer-c{cycle}-challenge');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert patch['before']['objects']==patch['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
 transfer=patch['support'][0]['transfer'];assert transfer['cached_poses']==206 and transfer['maximum_cuff_mean_error']<.007
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Original four production owners unchanged and driver-safe. Actual cached endpoints and finite native garment produced; cuff mean guard below7mm. Technical prerequisite only.',comparison='Actual visible contacts and clothing silhouette NOT_RUN.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-review-c{cycle}.json',v);print('Technical only')
else:
 step=action;assert step in {'save','leader_front','leader_reverse','render'}
 path='results/sikh335/look01/save-run-c23.json' if step=='save' else f'results/sikh335/look01/save-run-c{cycle}.json'
 parent=pk.read_json(r,path)['artifacts']['native'];recipe=next(v['native_recipe'] for v in s['planning_artifacts']['STRATEGIZING']['steps'] if v['id']==step)
 run=Bridge(c).dispatch(task,step,f'sikh342-look-c{cycle}-{step}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(f'{step}-run-c{cycle}.json',run);print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
 if run['status']!='RETURNED':raise SystemExit(2)
