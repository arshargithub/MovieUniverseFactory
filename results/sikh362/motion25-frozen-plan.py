"""Existing-task, source-bound361 planning/dispatch; no standalone native launch."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh362';c=wf.Controller(r,DATABASE)
label=sys.argv[1];action=sys.argv[2];task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=out/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
s=c.state(task);cy=s['cycle'];tag=f'{label}-c{cy}';cfg=pk.read_json(r,f'results/sikh362/{tag}.json')
if action=='plan':
 template=cfg.get('template','results/sikh353/strategizing-c67.json')
 base=pk.read_json(r,template)['artifact'];b=base['brief']
 g=pk.read_json(r,template.replace('strategizing','grounding'))['artifact']
 d=pk.read_json(r,template.replace('strategizing','deriving'))['artifact']
 # Current bounded continuation, not wholesale copying old correction prose.
 g['uses']={};g['knowledge_uses']={};d['context_mapping']={};d['knowledge_mapping']={}
 direction=s['direction'];ids=[x['id'] for x in d['requirements']]
 for src in direction['context_sources']:
  g['uses'][src['id']]=dict(disposition='apply',reason=src['statement'],implication=cfg['method']+' Original source intent/reference roles remain; historical failed candidates are controls, not current acceptance.')
  d['context_mapping'][src['id']]=dict(requirements=ids,reason=src['statement'])
 packet=pk.read_json(r,f'results/sikh361/{label}-knowledge-packet.json')
 for item in packet['obligations']:
  key=item['id'];v=item['action']+' Current application: '+cfg['method']+' '+cfg['proof']
  if key=='crowd_support':v='Crowd remains deferred;361 only leader/horse. No background acceptance.'
  g['knowledge_uses'][key]=v;d['knowledge_mapping'][key]=dict(requirements=ids,reason=v)
 g.update(reconciliation='362 ten additional appearance98..107 only; motion25..31 retained. Sol default, no Astra.361 actual layer audit supersedes coat-only proof;97 impossible query rejected. Repair supported skirt seam then whole leader/horse and isolated passage. Crowd deferred; no spending.',unresolved=[])
 b.update(knowledge_task=direction['knowledge_task'],knowledge_digest=direction['knowledge_digest'],knowledge_mapping=d['knowledge_mapping'],strategy=cfg['method'],early_proof=cfg['proof'],scope=cfg['scope'],exclusions='No crowd/principal/Pashtun changes, external calls, spend, new sound or complete-sequence render.')
 b['source_bindings']={x['id']:x['binding'] for x in direction['context_sources']}
 for p in [cfg['parent'],'results/sikh362/REQUEST.md','results/sikh362/STRATEGY.md',f'results/sikh362/{tag}.json','scripts/sikh362_motion.py']+cfg.get('sources',[]):b['source_bindings'][p]=bind(p)
 for ref in direction['references']:b['source_bindings'][ref['id']]=ref['binding']
 for key,row in b['expert_plan']['realizations'].items():
  row.update(method=cfg['methods'].get(key,cfg['method']),early_proof=cfg['proof'],failure_condition='Visible skirt through belt, pinched or floating waist, clay face/horse, attached beard, disconnected tack, changed performance, adjacent regression or missing evidence fails; no AV inference.')
 b['expert_plan']['challenge'].update(omission_probe='Transition interiors can expose sleeve, skirt, rein or hoof failures missed in static hero poses; inspect all125 frames and original faithful phases.',cross_discipline_conflicts='A revised appearance can change attachment/occlusion even when actions match; complete actor/horse/contact chain must remain visible and supported.',scope_tradeoff='One local worker, existing isolated scope with handles, no full sequence or new audio. Full-speed AV belongs to Director313; static/timed frames cannot pass it.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 steps=[]
 for spec in cfg['steps']:
  recipe=write(f'{tag}-{spec["id"]}-recipe.json',spec['recipe']);b['source_bindings'][recipe['path']]=recipe
  steps.append(dict(id=spec['id'],kind='proof',depends_on=spec['depends_on'],requirements=spec.get('requirements',ids),acceptance=spec.get('acceptance',cfg['proof']),native_recipe=recipe))
 base.update(brief=b,steps=steps,method_choice=dict(chosen=cfg['method'],alternatives='Retain supported86 headstall; reject old endpoint blending and sparse visibility. A conservative whole-segment test must pass actual horse use, then intended visual review.',evidence_status='hypothesis',discriminating_test=cfg['proof']),resource_scope=f'{label}{cy}/{s["max_corrections"]}; one local worker,no new spend. Original task/history retained.',replan_triggers='Failed anatomical surface support or adjacent regression requires source-backed reconstruction, not pose-specific patches.')
 arts=dict(GROUNDING=g,DERIVING=d,STRATEGIZING=base)
 for st in pp.STEPS[:3]:
  if pp.STEPS.index(st)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[st]);c.submit(task,p['actor'],p['ticket'],v,f'sikh362-{tag}-{st}');write(f'{tag}-{st.lower()}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'{tag}-challenge-input.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh362/{tag}-challenge.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh362-{tag}-admit');print(c.state(task)['stage'])
elif action=='technical':
 step=sys.argv[3];result=pk.read_json(r,f'results/sikh362/{tag}-{step}-run.json')
 for item in result['artifacts'].values():assert pk.file_hash(r/item['path'])==item['sha256']
 diag=pk.read_json(r,result['artifacts']['scripts']['path']);assert not diag['blocked_drivers'] and not diag['known_source_defects']
 v=dict(verdict='PASS',run_digest=pk.digest(result),evidence=result['artifacts'],observation='Source preserved; returned native artifacts hash-verified, diagnostics clean. Read-only report or derivative reopen only; no visual or motion approval.',comparison='Parent unchanged; source-bound worker. Subsequent actual inspection independently required.',open_defects=[])
 Bridge(c).record_review(task,step,v);write(f'{tag}-{step}-technical.json',v)
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 spec=next(x for x in cfg['steps'] if x['id']==action)
 parent=bind(cfg['parent']) if not spec['depends_on'] else pk.read_json(r,f'results/sikh362/{tag}-{spec["depends_on"][0]}-run.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,f'sikh362-{tag}-{action}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write(f'{tag}-{action}-run.json',result);print({k:result.get(k) for k in ('id','status','error')})
 if result['status']!='RETURNED':raise SystemExit(2)
