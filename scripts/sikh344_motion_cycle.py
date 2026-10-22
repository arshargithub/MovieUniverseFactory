"""Director344 motion12: explicit owning scene and late-descent proof only."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/motion01'
c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';action=sys.argv[1]
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
if action=='plan':
 s=c.state(task)
 reason='Director344 approves five shared corrections. One allocated to motion12, four remain.11 native scene ownership worked but actual endpoint slowed before impact. Specify actual world-space arrival with matched incoming speed and downward acceleration; preserve all failed evidence and unqualified appearance.'
 assert c.state(task)['cycle']==12
 arts={stage:pk.read_json(r,f'results/sikh335/motion01/{stage.lower()}-c11.json')['artifact'] for stage in pp.STEPS[:3]}
 b=arts['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_') or ref['path'].startswith('tests/test_nihang') or ref['path']=='results/sikh335/MOTION_342.md';ref['sha256']=actual
 paths=['results/sikh335/motion01/rejection-c11.json','tests/test_nihang344_arrival.py','src/movie_factory/adapters/blender/nihang_motion.py','.runtime/knowledge-pilot213/sikh344-current.json','results/sikh335/allowance344.json','results/sikh335/REASSESSMENT_343.md','src/movie_factory/adapters/blender/nihang_support.py','tests/test_nihang343_scene.py','results/sikh335/MOTION_342.md','results/sikh335/look01/rejection-c29.json',
 'results/sikh335/preserved-comparisons/reference-3.jpg' if (r/'results/sikh335/preserved-comparisons/reference-3.jpg').exists() else 'results/sikh321/preserved-comparisons/reference-3.jpg',
 '.runtime/factory-native/sikh335-motion-c5-save/patch-evidence.json',
 '.runtime/factory-native/sikh342-look-c23-save/scene.blend',
 'src/movie_factory/adapters/blender/nihang_motion.py','src/movie_factory/adapters/blender/nihang_transfer.py',
 'src/movie_factory/adapters/blender/nihang_finish.py','src/movie_factory/adapters/blender/nihang_look.py',
 'tests/test_nihang335_motion.py','scripts/sikh344_motion_cycle.py']
 for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 arts['GROUNDING']['reconciliation']+=' '+reason
 arts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['strategy']='Keep all original reference phases and existing scene ownership. For the final seven frames of each forehoof descent, use a world-space endpoint path matched to the measured incoming vertical speed and the original ground contact point, with constant downward acceleration. Recover wrist target from the foot and hoof offsets; solve fixed-length limb without target clamping. Preserve contact350/351 and existing body absorption after impact.'
 b['early_proof']='Actual all-frame support/contact/velocity metrics and16 densely sampled phase images versus saved5 and original reference. Reject pre-impact slowdown, reach failure, floating support, contactFX mismatch and adjacent garment regression. Full-speed AV remains pending; known appearance blocks integrated delivery.'
 b['exclusions']='No appearance algorithm changes or cast propagation, camera/setting/principal changes, new services/spend/egress. No artistic or AV pass from metrics or stills; no complete failed-passage queue.'
 methods={'preservation':'Retain23 input and29 appearance as immutable derivatives. New serial motion12 derivative; accepted Pashtun and320 source unchanged.',
 'phases':b['strategy'],
 'support':'Existing fixed-length hind/fore support and actual hoof targets retained. Inspect all190 recorded frames, final airborne speed and impact350/351; reject failed reach or grounded drift.',
 'rider':'Re-bake existing rider response and original shoulder/hand owners before replaying unchanged garment transfer. Never retain garment keys from the old movement after motion changes.',
 'evidence':b['early_proof']}
 for key,row in b['expert_plan']['realizations'].items():
  row['method']=methods[key];row['early_proof']=b['early_proof'];row['failure_condition']='Reach/support/contactFX failure, new garment distortion or final approach slowing before impact. Missing continuous judgment remains NOT_RUN, not PASS.'
 b['expert_plan']['challenge']['scope_tradeoff']='Narrow final motion proof is useful independent work but cannot resolve rejected appearance or deliver whole passage.'
 b['expert_plan']['challenge']['omission_probe']='Check all original reference phases, rider and interfaces rather than just the final speed number.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy=arts['STRATEGIZING'];strategy['method_choice']={'chosen':b['strategy'],'alternatives':'Do not increase noise, globally speed the clip, ease body to rest in air, or replay stale sleeve caches. No evidence that another shader pass would fix mechanics.','evidence_status':'hypothesis','discriminating_test':b['early_proof']}
 recipe=pk.read_json(r,'results/sikh335/motion01/save-c5-recipe.json')
 for a in recipe['edits'][1]['anchors']:
  if a['frame']==338:a['frame']=341
  elif a['frame']==345:a['frame']=347
 recipe.update(width=432,height=768,samples=8)
 # No failed appearance replay in a motion prerequisite.
 render=dict(operation='nihang_frames',frame=327,frames=[294,307,327,341,344,345,346,347,348,349,350,351,353,355,357,360],view='production',width=432,height=768,samples=8)
 steps=[]
 for name,value in [('save',recipe),('render',render)]:
  bind=write(f'{name}-c12-recipe.json',value);b['source_bindings'][bind['path']]=bind
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','support','phases','rider','evidence'],acceptance=b['early_proof'],native_recipe=bind))
 strategy['steps']=steps;strategy['resource_scope']='Motion12/max12 uses one of five shared344 corrections; four remain unallocated. Appearance29 remains rejected. One local native worker. No spend or provider.'
 strategy['replan_triggers']='Failed actual support/contact or final approach; appearance remains separately blocked. No further correction without Director authority.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[stage])
  c.submit(task,p['actor'],p['ticket'],v,'sikh344-motion12-'+stage);write(f'{stage.lower()}-c12.json',v)
 p=c.packet(task);p.pop('ticket',None);write('challenge-input-c12.json',p)
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,'results/sikh335/motion01/challenge-verdict-c12.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,'sikh344-motion12-admit');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,'results/sikh335/motion01/save-run-c12.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);diagnostic=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert not diagnostic['blocked_drivers'] and not diagnostic['known_source_defects']
 motion=next(x['motion'] for x in patch['support'] if 'motion' in x);rows=motion['frames'];assert len(rows)==190
 old=pk.read_json(r,'.runtime/factory-native/sikh335-motion-c5-save/patch-evidence.json')
 before={a['frame']:a for a in next(x['motion']['frames'] for x in old['support'] if 'motion'in x)};after={a['frame']:a for a in rows}
 def speeds(records,side):
  return {f:(records[f]['hind_support'][side]['fore_visible_hoof'][2]-records[f-1]['hind_support'][side]['fore_visible_hoof'][2])*24 for f in range(344,352)}
 metrics={'before_L':speeds(before,0),'after_L':speeds(after,0),'before_R':speeds(before,1),'after_R':speeds(after,1),'landing_fx':motion['landing_fx'],'scope':'Measured trajectory only, not AV or appearance approval.'}
 write('impact-metrics-c12.json',metrics)
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Fresh native save/reopen, drivers and all190 recorded support states returned. Production scene selected before baseline; no appearance replay or acceptance.',comparison='Technical prerequisite only. Actual trajectory and images still require review; appearance remains rejected and AV NOT_RUN.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write('save-technical-review-c12.json',v);print(json.dumps(metrics))
else:
 assert action in ('save','render');s=c.state(task);assert s['cycle']==12
 parent=pk.read_json(r,'results/sikh335/look01/save-run-c23.json' if action=='save' else 'results/sikh335/motion01/save-run-c12.json')['artifacts']['native']
 recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 run=Bridge(c).dispatch(task,action,'sikh344-motion-c12-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(action+'-run-c12.json',run);print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
 if run['status']!='RETURNED':raise SystemExit(2)
