"""Coordinated actual supporting-look correction under the same task ceiling."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
cycle=s['cycle'];assert 25<=cycle<=29
out=r/'results/sikh335/look01';action=sys.argv[1]
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
if action=='plan':
 artifacts={stage:pk.read_json(r,f'results/sikh335/look01/{stage.lower()}-c24.json')['artifact'] for stage in pp.STEPS[:3]}
 b=artifacts['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_') or ref['path'].startswith('tests/test_nihang');ref['sha256']=actual
 paths=['results/sikh335/TRANSFER_342.md','results/sikh335/look01/prerequisite-c23.json',
 'results/sikh335/look01/allowance342-sikh335-supporting-appearance-23.json',
 'scripts/sikh342_finish_cycle.py','src/movie_factory/adapters/blender/nihang_finish.py','tests/test_nihang342_transfer.py',
 'results/sikh335/look01/rejection-c24.json','results/sikh335/look01/rejection-c25.json','results/sikh335/look01/rejection-c26.json','results/sikh335/look01/rejection-c27.json','results/sikh335/look01/allowance342-sikh335-supporting-appearance-27.json','.runtime/factory-native/sikh342-look-c24-save/scene.blend']
 for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 reason='Actual27 isolated actor exposes hand/cuff overlap, crown-to-forehead clipping and overstated cloth mottling. Sash binds source topology but support was sampled before rendered shirt modifiers.28 must correct evaluated support, measured wrist setback, head-fitted cloth and restrained material range. All10 shared cycles allocated;28-29 remain, not a new allowance.'
 artifacts['GROUNDING']['reconciliation']+=' '+reason
 artifacts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['early_proof']='Actual leader and one nearest crowd front/reverse plus leader stance/spear plant/crest/landing. Judge whole figures, supported sash, crown/eyes/beard, coat/pad and standing waist/cuffs against accepted film floor. No ensemble propagation until representative proof.'
 b['exclusions']='No principal Sikh changes, crowd-wide propagation, production camera or timing changes, provider, spend or upload. Full-speed motion and Director acceptance remain separate.'
 b['strategy']='Use final evaluated shirt surface for sash fit and a bounded clearance modifier after ribbon subdivision. Preserve original pose binding. Set standing cuff18mm proximal to existing end target, leaving hand/wrist intact. Fit crown base and overlapping layers outside actual head in crown-local coordinates; do not alter identity. Reduce fabric colour contrast and include original trousers in shared treatment. Keep all diagnostics and actual rear/crowd frames.'
 b['expert_plan']['realizations']['form']['method']=b['strategy']
 b['expert_plan']['realizations']['interfaces']['method']='Rendered-surface sash clearance is applied after subdivision and before its own thickness. Head fit uses actual head-to-crown transform with35mm maximum correction guard. Only standing cuff shortens18mm along measured forearm. Same motion owners, head geometry and original production camera remain. Actual hand/cuff, forehead/crown, waist and pad poses must pass before ensemble reuse.'
 b['expert_plan']['realizations']['preservation']['method']='Use saved24 derivative; retain original body, all four motion owners and accepted assets unchanged. Replace only supporting costume/material derivatives and retain old hidden objects.'
 b['expert_plan']['realizations']['evidence']['method']='Actual matched front/reverse/stance/crest/landing frames against prior24 and accepted Pashtun floor. No scene lighting change to disguise artifacts. Whole-character veto remains if mannequin impression persists.'
 for row in b['expert_plan']['realizations'].values():
  row['early_proof']=b['early_proof'];row['failure_condition']='Actual garment has disconnected sleeve, distorted shoulder/elbow/cuff, broken collar, skin penetration, floating sash or waist gap. Existing face/crown/tack defects remain whole-character vetoes.'
  row['reopen_when']='Donor, pose cache, parent ownership, garment or layer support changes.'
 b['expert_plan']['challenge']['scope_tradeoff']='Leader plus one representative standing actor; all other crowd untouched until this proof. No automatic support-cast approval.'
 b['expert_plan']['challenge']['omission_probe']='Clothing success cannot excuse hollow eyes, static expression, weak crown or tack. Full original intent remains the final gate.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy=artifacts['STRATEGIZING'];strategy['method_choice']={'chosen':b['strategy'],'alternatives':'Reject low-resolution nearest-surface sash deformation that caused serrated clipping. Avoid more surface noise as substitute for coherent silhouette or physically supported layers.','evidence_status':'hypothesis','discriminating_test':b['early_proof']}
 steps=[]
 recipes={'save':dict(operation='nihang_patch',frame=283,width=540,height=960,samples=24,edits=[dict(kind='supporting_finish',target='mounted leader')]),
 'leader_front':dict(operation='nihang_frames',frame=283,frames=[283],view='leader_front',width=540,height=960,samples=24),
 'leader_reverse':dict(operation='nihang_frames',frame=283,frames=[283],view='leader_reverse',width=540,height=960,samples=24),
 'crowd_front':dict(operation='nihang_frames',frame=283,frames=[283],view='crowd_front',width=540,height=960,samples=24),
 'crowd_reverse':dict(operation='nihang_frames',frame=283,frames=[283],view='crowd_reverse',width=540,height=960,samples=24),
 'render':dict(operation='nihang_frames',frame=283,frames=[283,310,327,348,393,414],view='production',width=540,height=960,samples=24)}
 for name,recipe in recipes.items():
  binding=write(f'{name}-recipe-c{cycle}.json',recipe);b['source_bindings'][binding['path']]=binding
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=binding))
 strategy['steps']=steps;strategy['resource_scope']='Current appearance28-29 uses final2 of shared10;0 unallocated. One native worker, no new spend/egress. No task completion from narrower prerequisite.'
 strategy['replan_triggers']='Cache/coordinate assumptions fail; actual neckline, armhole, elbow, cuff or sash fails; missing native proof; known whole-character quality veto remains.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);response=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=artifacts[stage])
  c.submit(task,p['actor'],p['ticket'],response,f'sikh342-finish-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',response)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p)
 write(f'source-manifest-c{cycle}.json',{str(p.relative_to(r)):pk.file_hash(p) for p in sorted((r/'src/movie_factory/adapters/blender').glob('*.py'))})
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,f'sikh342-finish-c{cycle}-challenge');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert patch['before']['objects']==patch['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
 finish=patch['support'][0]['finish'];assert len(finish['actors'])==2
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Original four production owners unchanged and driver-safe. Coordinated leader candidate saved with source-bound sash, coat and fitted saddle. Technical prerequisite only.',comparison='Actual whole-character look, contacts and silhouette NOT_RUN.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-review-c{cycle}.json',v);print('Technical only')
else:
 step=action;assert step in {'save','leader_front','leader_reverse','crowd_front','crowd_reverse','render'}
 path='results/sikh335/look01/save-run-c24.json' if step=='save' else f'results/sikh335/look01/save-run-c{cycle}.json'
 parent=pk.read_json(r,path)['artifacts']['native'];recipe=next(v['native_recipe'] for v in s['planning_artifacts']['STRATEGIZING']['steps'] if v['id']==step)
 run=Bridge(c).dispatch(task,step,f'sikh342-look-c{cycle}-{step}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(f'{step}-run-c{cycle}.json',run);print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
 if run['status']!='RETURNED':raise SystemExit(2)
