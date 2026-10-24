"""Original-task source/phase proof transport; no standalone Blender launch."""
import json,sys
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh363';c=wf.Controller(r,DATABASE)
label,action=sys.argv[1:3];task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance');s=c.state(task);cy=s['cycle'];tag=f'{label}-c{cy}'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
cfg=pk.read_json(r,f'results/sikh363/{tag}.json')
if action=='plan':
 old=pk.read_json(r,cfg['template'])['artifact'];b=deepcopy(old['brief']);direction=s['direction'];packet=pk.task_packet(r,pk.read_json(r,direction['knowledge_task']))
 d=deepcopy(pk.read_json(r,cfg['derived_template'])['artifact'])
 ids=[x['id'] for x in d['requirements']]
 for req in d['requirements']:
  if req['id'] in cfg.get('criteria',{}):req['criterion']=cfg['criteria'][req['id']]
 g=dict(uses={x['id']:dict(disposition='apply',reason=x['statement'],implication=cfg['applications'].get(x['id'],cfg['method'])) for x in direction['context_sources']},knowledge_uses={x['id']:('Crowd remains deferred and unqualified context; current proof leader/horse only.' if x['id']=='crowd_support' else cfg['method']+' '+cfg['proof']) for x in packet['obligations']},reconciliation=cfg['reconciliation'],unresolved=[])
 d['context_mapping']={x['id']:dict(requirements=ids,reason=x['statement']+' '+g['uses'][x['id']]['implication']) for x in direction['context_sources']}
 d['knowledge_mapping']={k:dict(requirements=ids,reason=v) for k,v in g['knowledge_uses'].items()}
 for beat in d['beats']:beat['framing']=cfg['framing']
 b.update(intent=direction['intent'],references=direction['references'],protected=direction['protected'],knowledge_task=direction['knowledge_task'],knowledge_digest=direction['knowledge_digest'],knowledge_mapping=d['knowledge_mapping'],requirements=d['requirements'],strategy=cfg['method'],early_proof=cfg['proof'],scope=cfg['scope'],exclusions='No crowd/principal/Pashtun authoring, sound, spend/providers/cloud/model escalation. No general asset or AV acceptance.')
 b['expert_plan']['beat_intents']=direction['beat_intents'];b['expert_plan']['beats']=d['beats']
 for rid,row in d['derivations'].items():
  real=b['expert_plan']['realizations'][rid];real.update(row,method=cfg['method'],early_proof=cfg['proof'],failure_condition=cfg['failure'])
 b['source_bindings']={x['id']:x['binding'] for x in direction['context_sources']}
 for p in [cfg['parent'],'results/sikh363/REQUEST.md','results/sikh363/STRATEGY.md',f'results/sikh363/{tag}.json','scripts/sikh363_plan.py']+cfg.get('sources',[]):b['source_bindings'][p]=bind(p)
 for ref in direction['references']:b['source_bindings'][ref['id']]=ref['binding']
 b['reference_plan']={x['id']:dict(reference_digest=pk.digest(x),application='Preserve exact original reference role.363 diagnosis/repair requires the faithful spear/rear phases and same-film quality, not literal identity or source readiness.') for x in direction['references']}
 b['expert_plan']['challenge'].update(omission_probe=cfg['failure'],cross_discipline_conflicts='Right hand, spear/flag/face and horse chest/performance are coupled. Evidence of one cannot pass another; old362 review rejected.',scope_tradeoff=cfg['scope'])
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 steps=[]
 for spec in cfg['steps']:
  rb=write(f'{tag}-{spec["id"]}-recipe.json',spec['recipe']);b['source_bindings'][rb['path']]=rb
  steps.append(dict(id=spec['id'],kind='proof',depends_on=spec['depends_on'],requirements=spec.get('requirements',ids),acceptance=cfg['proof'],native_recipe=rb))
 base=dict(brief=b,steps=steps,method_choice=dict(chosen=cfg['method'],alternatives=cfg['alternatives'],evidence_status='hypothesis',discriminating_test=cfg['proof']),resource_scope=f'Original{task} cycle{cy}/max{s["max_corrections"]}; one worker, no new spend; reversible exact source derivative.',replan_triggers=cfg['failure'])
 for stage,art in [('GROUNDING',g),('DERIVING',d),('STRATEGIZING',base)]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=art);c.submit(task,p['actor'],p['ticket'],v,f'sikh363-{tag}-{stage}');write(tag+'-'+stage.lower()+'.json',v)
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh363/{tag}-challenge.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh363-{tag}-admit');print(c.state(task)['stage'])
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action);spec=next(x for x in cfg['steps'] if x['id']==action)
 parent=bind(spec.get('parent',cfg['parent'])) if not spec['depends_on'] else pk.read_json(r,f'results/sikh363/{tag}-{spec["depends_on"][0]}-run.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,'sikh363-'+tag+'-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write(tag+'-'+action+'-run.json',result);print(result['status'])
 if result['status']!='RETURNED':raise SystemExit(2)
