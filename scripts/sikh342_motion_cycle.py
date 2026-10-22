"""Final previously authorized motion correction, independent of appearance cap."""
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
 reason='Native5 descent slows over345-348 and root pitch eases before350 impact. Reference17.9-18.2 shows concentrated landing. Use remaining original motion10, not an appearance extension. Rebuild unchanged29 appearance after motion to avoid stale garment pose caches; appearance remains rejected.'
 if s['cycle']==9:
  d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,'sikh342-motion10-reground')
 assert c.state(task)['cycle']==10
 arts={stage:pk.read_json(r,f'results/sikh335/motion01/{stage.lower()}-c9.json')['artifact'] for stage in pp.STEPS[:3]}
 b=arts['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_') or ref['path'].startswith('tests/test_nihang');ref['sha256']=actual
 paths=['results/sikh335/MOTION_342.md','results/sikh335/look01/rejection-c29.json',
 'results/sikh335/preserved-comparisons/reference-3.jpg' if (r/'results/sikh335/preserved-comparisons/reference-3.jpg').exists() else 'results/sikh321/preserved-comparisons/reference-3.jpg',
 '.runtime/factory-native/sikh335-motion-c5-save/patch-evidence.json',
 '.runtime/factory-native/sikh342-look-c23-save/scene.blend',
 'src/movie_factory/adapters/blender/nihang_motion.py','src/movie_factory/adapters/blender/nihang_transfer.py',
 'src/movie_factory/adapters/blender/nihang_finish.py','src/movie_factory/adapters/blender/nihang_look.py',
 'tests/test_nihang335_motion.py','scripts/sikh342_motion_cycle.py']
 for path in paths:b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 arts['GROUNDING']['reconciliation']+=' '+reason
 arts['GROUNDING']['knowledge_uses']['current_state']=reason
 b['strategy']='Concentrate late descent by moving338 anchor to341 and345 to347, retaining350/351 contacts. Use finite pitch arrival and1.25-fold secant arrival. Re-bake supported actual motion, then replay unchanged29 garment transfer/finish after updated pose owners. No appearance correction or acceptance.'
 b['early_proof']='Actual all-frame support/contact/velocity metrics and16 densely sampled phase images versus saved5 and original reference. Reject pre-impact slowdown, reach failure, floating support, contactFX mismatch and adjacent garment regression. Full-speed AV remains pending; known appearance blocks integrated delivery.'
 b['exclusions']='No appearance algorithm changes or cast propagation, camera/setting/principal changes, new services/spend/egress. No artistic or AV pass from metrics or stills; no complete failed-passage queue.'
 methods={'preservation':'Retain23 input and29 appearance as immutable derivatives. New serial motion10 derivative; accepted Pashtun and320 source unchanged.',
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
 recipe['edits'] += [dict(kind='neutral_actor_transfer',target='mounted leader',phase='leader'),dict(kind='supporting_finish',target='mounted leader')]
 render=dict(operation='nihang_frames',frame=327,frames=[294,307,327,341,343,345,346,347,348,349,350,351,353,355,357,360],view='production',width=432,height=768,samples=8)
 steps=[]
 for name,value in [('save',recipe),('render',render)]:
  bind=write(f'{name}-c10-recipe.json',value);b['source_bindings'][bind['path']]=bind
  steps.append(dict(id=name,kind='proof',depends_on=[] if name=='save' else ['save'],requirements=['preservation','support','phases','rider','evidence'],acceptance=b['early_proof'],native_recipe=bind))
 strategy['steps']=steps;strategy['resource_scope']='Last original motion correction10/max10; appearance29/max29 exhausted and unchanged. One local native worker. No spend or provider.'
 strategy['replan_triggers']='Failed actual support/contact or final approach; appearance remains separately blocked. No further correction without Director authority.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[stage])
  c.submit(task,p['actor'],p['ticket'],v,'sikh342-motion10-'+stage);write(f'{stage.lower()}-c10.json',v)
 p=c.packet(task);p.pop('ticket',None);write('challenge-input-c10.json',p)
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,'results/sikh335/motion01/challenge-verdict-c10.json');v['input_digest']=p['planning_input_digest']
 c.submit(task,p['actor'],p['ticket'],v,'sikh342-motion10-admit');print(c.state(task)['stage'])
elif action=='technical':
 run=pk.read_json(r,'results/sikh335/motion01/save-run-c10.json');assert run['status']=='RETURNED'
 for a in run['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,run['artifacts']['patch']['path']);diagnostic=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert not diagnostic['blocked_drivers'] and not diagnostic['known_source_defects']
 motion=next(x['motion'] for x in patch['support'] if 'motion' in x);rows=motion['frames'];assert len(rows)==190
 old=pk.read_json(r,'.runtime/factory-native/sikh335-motion-c5-save/patch-evidence.json')
 before={a['frame']:a for a in next(x['motion']['frames'] for x in old['support'] if 'motion'in x)};after={a['frame']:a for a in rows}
 def speeds(records,side):
  return {f:(records[f]['hind_support'][side]['fore_visible_hoof'][2]-records[f-1]['hind_support'][side]['fore_visible_hoof'][2])*24 for f in range(343,352)}
 metrics={'before_L':speeds(before,0),'after_L':speeds(after,0),'before_R':speeds(before,1),'after_R':speeds(after,1),'landing_fx':motion['landing_fx'],'scope':'Measured trajectory only, not AV or appearance approval.'}
 write('impact-metrics-c10.json',metrics)
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Fresh native save/reopen, drivers and all190 recorded support states returned. Unchanged appearance construction replayed after motion owner update.',comparison='Technical prerequisite only. Actual trajectory and images still require review; appearance remains rejected and AV NOT_RUN.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write('save-technical-review-c10.json',v);print(json.dumps(metrics))
else:
 assert action in ('save','render');s=c.state(task);assert s['cycle']==10
 parent=pk.read_json(r,'results/sikh335/look01/save-run-c23.json' if action=='save' else 'results/sikh335/motion01/save-run-c10.json')['artifacts']['native']
 recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 run=Bridge(c).dispatch(task,action,'sikh342-motion-c10-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(action+'-run-c10.json',run);print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
 if run['status']!='RETURNED':raise SystemExit(2)
