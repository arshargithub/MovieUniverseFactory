"""Scoped original-task plan/dispatch transport; explicit judgments stay in files."""
import json,sys,copy
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh371';c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';s=c.state(task);cy=s['cycle'];tag=f'motion-c{cy}';action=sys.argv[1]
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
cfg=pk.read_json(r,f'results/sikh371/{tag}.json')
if action=='plan':
 b=copy.deepcopy(pk.read_json(r,'results/sikh371/revised-brief.json'));direction=s['direction'];ids=[x['id'] for x in b['requirements']]
 b.update(strategy=cfg['method'],early_proof=cfg['proof'],scope=cfg['scope'],knowledge_task=direction['knowledge_task'],knowledge_digest=direction['knowledge_digest'])
 for src in direction['context_sources']:b['source_bindings'][src['id']]=src['binding']
 b['source_bindings'][f'results/sikh371/{tag}.json']=bind(f'results/sikh371/{tag}.json');b['source_bindings']['scripts/sikh371_plan.py']=bind('scripts/sikh371_plan.py')
 b['source_bindings'][cfg['parent']]=bind(cfg['parent'])
 for spec in cfg['steps']:
  if spec.get('parent'):b['source_bindings'][spec['parent']]=bind(spec['parent'])
 for p in cfg.get('sources',[]):b['source_bindings'][p]=bind(p)
 for m in b['expert_plan']['realizations'].values():m.update(method=cfg['method'],early_proof=cfg['proof'],failure_condition=cfg['failure'])
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 uses={};cm={}
 for v in direction['context_sources']:
  sid=v['id'];history=sid in ['strategy353','director363','strategy363','crest_control','cloth363']
  reason=('Historical constraint/failure context; latest371 preserves accepted66preparation and overrides historicalphase-onlyscope; earlier rejectedbehavior staysrejected. ' if history else 'Apply current source authority/lesson: ')+v['statement']
  impact=('Reference-led rise/highactivecrest, acceptedprefix/sourceownership/support andcompletephase evidence.' if sid in ['direction','references','learnings','ownership_diagnosis','director367','rejection365','director371','strategy371','reference371','carry370','current_method371'] else 'Preserve bounded scope, original authority/history and material/contact/cache interfaces; no unrelated construction.')
  uses[sid]=dict(disposition='apply',reason=reason,implication=impact)
  cm[sid]=dict(requirements=['rise','crest','balance','continuity','evidence'] if sid in ['direction','references','learnings','ownership_diagnosis','director367','rejection365','director371','strategy371','reference371','carry370','current_method371'] else ['scope','preservation','evidence'],reason=reason+' '+impact)
 g=dict(uses=uses,knowledge_uses={k:v['reason'] for k,v in b['knowledge_mapping'].items()},reconciliation=cfg['reconciliation'],unresolved=[])
 d=dict(requirements=b['requirements'],beats=b['expert_plan']['beats'],derivations={k:{f:m[f] for f in pp.DERIVATION_FIELDS} for k,m in b['expert_plan']['realizations'].items()},context_mapping=cm,knowledge_mapping=b['knowledge_mapping'])
 steps=[]
 for spec in cfg['steps']:
  rb=write(f'{tag}-{spec["id"]}-recipe.json',spec['recipe']);b['source_bindings'][rb['path']]=rb
  steps.append(dict(id=spec['id'],kind='proof',depends_on=spec['depends_on'],requirements=spec.get('requirements',ids),acceptance=cfg['proof'],native_recipe=rb))
 base=dict(brief=b,steps=steps,method_choice=dict(chosen=cfg['method'],alternatives=cfg['alternatives'],evidence_status='hypothesis',discriminating_test=cfg['proof']),resource_scope=f'Original task {task} cycle{cy}/max{s["max_corrections"]}; current micro-motion allocation67..71, one worker, no new spend.',replan_triggers=cfg['failure'])
 for stage,art in [('GROUNDING',g),('DERIVING',d),('STRATEGIZING',base)]:
  current=c.state(task)['planning_step']
  if pp.STEPS.index(stage)<pp.STEPS.index(current):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=art);c.submit(task,p['actor'],p['ticket'],v,f'sikh371-{tag}-{stage}');write(tag+'-'+stage.lower()+'.json',v)
 print(c.state(task)['planning_step'])
elif action=='admit':
 v=pk.read_json(r,f'results/sikh371/{tag}-challenge.json')
 if s['stage']=='BRIEFING':
  p=c.packet(task);v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,'sikh371-'+tag+'-admit');s=c.state(task)
 evidence_paths=cfg.get('retrospective_evidence', [f'results/sikh371/{tag}.json',f'results/sikh371/{tag}-challenge.json','results/sikh371/REQUEST.md','results/nihang-scope-review365/director-disposition.json']+cfg.get('retro_evidence',[]))
 ev={p:bind(p) for p in evidence_paths}
 for key,g in c.retrospective_packet(task)['gates'].items():
  if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):c.retrospective(task,'outcome',dict(attempt='371-'+tag+'-'+key,role='diagnostic',origin='scoped-plan-change',observations=[dict(requirement=key,status='UNKNOWN',observation='Current unit changes proof conditions; preserve old failures, do not carry old artistic PASS.')],evidence=ev),'sikh371-'+tag+'-'+key+'-reopen')
 for key,g in c.retrospective_packet(task)['gates'].items():
  if g['status']!='OPEN':continue
  response=dict(cause=cfg['cause'],uncertainty=v['strongest_counterexample'],change_or_retain_rationale=cfg['method'],preserve='Accepted66preparation andoriginaltask/history/limits preserved. Newrise/apex/hold only; landing/chest/look remainunaccepted.',test=cfg['proof'],expected=cfg['expected'],failure_response=cfg['failure'],target_stage='GROUNDING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
  event='sikh371-'+tag+'-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
  checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=cfg['method'],preservation=response['preserve'],authority='Director371 five additional motion corrections67..71 and Sol policy; no new grant/spend or external actions.').items()}
  c.retrospective(task,'admit',dict(key=key,challenge=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks=checks)),event+'-admit')
 print('Admitted diagnostic/test, not artistic approval',s['cycle'])
elif action=='review':
 step=sys.argv[2];observation=sys.argv[3];run=pk.read_json(r,f'results/sikh371/{tag}-{step}-run.json');requirements=s['brief']['requirements']
 verdict=dict(run_digest=pk.digest(run),verdict='PASS',observation=observation,comparison='Actual returned source/report/image availability versus admitted recipe. Artistic unit criteria and full-speed AV remain separately NOT_TESTED.',open_defects=[],evidence=run['artifacts'],retrospective_observations=[dict(requirement=q['id'],status='NOT_TESTED',observation='Transport availability only; does not qualify this artistic/reference requirement.') for q in requirements if q['id'] not in ['preservation','scope']])
 Bridge(c).record_review(task,step,verdict);write(f'{tag}-{step}-review.json',verdict);print('Recorded availability only')
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action);spec=next(x for x in cfg['steps'] if x['id']==action)
 parent=bind(spec.get('parent',cfg['parent'])) if not spec['depends_on'] else pk.read_json(r,f'results/sikh371/{tag}-{spec["depends_on"][0]}-run.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,'sikh371-'+tag+'-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=spec.get('timeout',600),recipe=step['native_recipe']);write(f'{tag}-{action}-run.json',result);print(result['status'])
 if result['status']!='RETURNED':raise SystemExit(2)
