"""Actual shot-handle repair and explicit Director motion review ownership."""
import json,sys
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep,retrospective as retro
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';o=r/'results/sikh362';action=sys.argv[1]
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
s=c.state(task)
if action=='repair':
 assert s['cycle']==26
 bridge=Bridge(c);runs=bridge.runs(s)
 assert len(runs)==17
 for run in runs.values():bridge.qualified(run)
 write('source26-qualified.json',dict(source=bind('.runtime/factory-native/sikh362-appearance-c99-save/scene.blend'),runs={k:dict(id=v['id'],artifacts=v['artifacts']) for k,v in runs.items()},scope='All26 native steps reviewed; exact99 source, no artistic reuse beyond tested conditions or AV acceptance.'))
 p='results/sikh362/BOUNDARY_REPAIR.md'
 c.retrospective(task,'outcome',dict(attempt='362-boundary-derivation',role='diagnostic',origin='actual-camera-cut',observations=[dict(requirement='__planning__',status='FAIL',observation='Actual leader shot ends356, not template core352; extend unchanged-source context to380 for a full second. Make existing Director313 full-speed ownership explicit rather than leave it only in prose.',foundation=False)],evidence={'boundary':bind(p)}),'sikh362-motion-boundary-gap')
 s=c.replan(task,'DERIVING','Use actual shot276..356 with handles252..380. Preserve125 completed26 frames, exact99 master and all performance/camera. Add only four tail frames plus canonical readback; separately declare human full-speed requirement.','sikh362-motion27-derivation')
 print(s['cycle'],s['planning_step'])
elif action=='plan':
 assert s['cycle']==27
 d=pk.read_json(r,'results/sikh362/motion-c25-deriving.json')['artifact'];base=pk.read_json(r,'results/sikh362/motion-c26-strategizing.json')['artifact'];b=base['brief']
 method='Retain exact99 master and all125 completed source26 frames, actions and camera. Actual shot ends356; render only377..380 at the same432x768/16 profile plus canonical283 after a fresh no-edit save. Bind all source26 evidence and extend the clip to129 frames252..380. No retime, new pose/cloth/groom, crowd construction, sound or full sequence render.'
 proof='All129 exact source frames, actual one-second handles, same master/profile and canonical readback; known source/frame failures closed by actual observations. Human full-speed weight, fluidity, pacing and secondary response remain NOT_RUN under director_motion and cannot be self-passed.'
 new=dict(id='director_motion',criterion='Director313 must judge full-speed weight, fluidity, active crest, landing, rider/horse/secondary response and overall action effect in the exact assembled clip. Agent source/timed images/decoding cannot pass this.',director_av=True,modes=['direct_motion']);d['requirements'].append(new)
 lenses=['story_performance','camera_editorial','animation_physics']
 d['derivations']['director_motion']=dict(beats=['rear'],lenses=lenses,derivation='313 assigns audiovisual judgment to Director; preserve source/image duties separately and require explicit full-speed judgment after integrated clip availability.',origin='director',priority='quality_floor',reference_ids=['reference_rear'])
 d['beats'][0]['framing']='Actual leader shot276..356 and one-second handles252..380,432x768/16,24fps; crowd/principal context deferred.'
 for name in lenses:d['beats'][0]['lenses'][name]['requirements'].append('director_motion')
 ids=[x['id'] for x in d['requirements']]
 for mapping in [d['context_mapping'],d['knowledge_mapping']]:
  for row in mapping.values():row['requirements']=ids;row['reason']+=' Exact scoped source/image review remains agent-owned; direct_motion belongs only to Director313.'
 b.update(requirements=d['requirements'],knowledge_mapping=d['knowledge_mapping'],strategy=method,early_proof=proof,scope='Exact isolated leader/horse shot with one-second context each side; full-speed Director AV pending. Principal/crowd context remains deferred, no new sound.')
 b['expert_plan']['beats']=d['beats']
 for rid,row in d['derivations'].items():
  if rid not in b['expert_plan']['realizations']:b['expert_plan']['realizations'][rid]=deepcopy(b['expert_plan']['realizations']['evidence'])
  b['expert_plan']['realizations'][rid].update(row,method=method,early_proof=proof,failure_condition='Wrong actual cut/handle, changed master/profile, source/frame-visible failure or fabricated direct-motion pass blocks.')
 b['expert_plan']['realizations']['director_motion']['interfaces']=['Exact encoded media → source26/27 frames','Agent source/image checks → separate Director full-speed verdict']
 b['expert_plan']['challenge'].update(omission_probe='Actual camera cut is357; pose352 is not editorial boundary. Human AV must not disappear into technical/image PASS.',cross_discipline_conflicts='Native output availability is not human motion approval; all source/frame failures still belong to agent.',scope_tradeoff='Reuse125 exact frames and render only four new context frames plus readback; no repeated whole proof.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 for p in ['results/sikh362/BOUNDARY_REPAIR.md','results/sikh362/source26-qualified.json','scripts/sikh362_plan27.py']:b['source_bindings'][p]=bind(p)
 steps=[]
 for name,recipe,requires,depends in [('save',dict(operation='nihang_save',frame=283,width=432,height=768,samples=16),['preservation'],[]),('tail_context',dict(operation='nihang_frames',frame=283,frames=[283,377,378,379,380],view='production',width=432,height=768,samples=16),ids,['save'])]:
  rb=write(f'motion-c27-{name}-recipe.json',recipe);b['source_bindings'][rb['path']]=rb
  steps.append(dict(id=name,kind='proof',depends_on=depends,requirements=requires,acceptance=proof,native_recipe=rb))
 base.update(brief=b,steps=steps,method_choice=dict(chosen=method,alternatives='Do not shorten the requested handle or rerender unchanged125 frames; do not infer human AV from source/render success.',evidence_status='observed',discriminating_test=proof),resource_scope='Original motion27/max31, no new allowance/spend; one worker after100 readback.',replan_triggers='Changed source/profile/cut or any visible failure invalidates use; preserve history and original limits.')
 for stage,artifact in [('DERIVING',d),('STRATEGIZING',base)]:
  if c.state(task)['planning_step']!=stage:continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=artifact);c.submit(task,p['actor'],p['ticket'],v,'sikh362-motion27-'+stage);write('motion-c27-'+stage.lower()+'.json',v)
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,'results/sikh362/motion-c27-challenge.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,'sikh362-motion27-admit');print(c.state(task)['stage'])
else:
 assert s['cycle']==27
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 parent=bind('.runtime/factory-native/sikh362-appearance-c99-save/scene.blend') if action=='save' else pk.read_json(r,'results/sikh362/motion-c27-save-run.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,'sikh362-motion-c27-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write('motion-c27-'+action+'-run.json',result);print(result['status'])
 if result['status']!='RETURNED':raise SystemExit(2)
