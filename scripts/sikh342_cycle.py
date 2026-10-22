"""Plan/dispatch existing task corrections from the shared342 allowance."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory import planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cycle=s['cycle'];action=sys.argv[1]
assert 20<=cycle<=29 and s['max_corrections']<=29
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
if action=='plan':
 art={x:pk.read_json(r,f'results/sikh335/look01/{x.lower()}-c19.json')['artifact'] for x in pp.STEPS[:3]}
 b=art['STRATEGIZING']['brief']
 for ref in b['source_bindings'].values():
  actual=pk.file_hash(r/ref['path'])
  if actual!=ref['sha256']:
   assert ref['path'].startswith('src/movie_factory/adapters/blender/nihang_') or ref['path']=='tests/test_nihang341_neutral.py';ref['sha256']=actual
 for path in ['results/sikh335/allowance342.json','results/sikh335/STRATEGY_342.md','scripts/sikh342_cycle.py','tests/test_nihang341_neutral.py']:
  b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
 steps=[]
 for old in art['STRATEGIZING']['steps']:
  step=dict(old);recipe=pk.read_json(r,old['native_recipe']['path'])
  step['native_recipe']=write(f"{step['id']}-recipe-c{cycle}.json",recipe)
  b['source_bindings'][step['native_recipe']['path']]=step['native_recipe'];steps.append(step)
 art['STRATEGIZING']['steps']=steps
 reason='342 shared ten-cycle authority, initially four appearance corrections.19 neckline FAIL retained. Face-intersecting planar cut replaces vertex-stair boundary; post-modifier clearance is measured and real images gate bending. All body and original production state protected.'
 art['GROUNDING']['reconciliation']+=' '+reason
 art['GROUNDING']['knowledge_uses']['current_state']=reason
 b['strategy']='Coherent planar opening on continuous neutral donor garment, actual settle and post-modifier clearance; save/reopen/front/back/side gate before bend and production integration.'
 b['expert_plan']['realizations']['form']['method']=b['strategy']
 b['expert_plan']['realizations']['interfaces']['method']='Closed continuous opening boundary must survive subdivision and clear actual evaluated skin. Both sides and reverse must pass before existing75-degree elbow proof. No collar concealment.'
 b['expert_plan']['challenge']['scope_tradeoff']='Neutral/bend dependency proof, not completed supporting costume. Original full leader/crowd intent and quality floor remain pending.'
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 art['STRATEGIZING']['resource_scope']='Ten shared additional cycles across existing tasks; first4 appearance,6 reserved; no new spending or uploads. Serial native jobs.'
 for stage in pp.STEPS[:3]:
  if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);response=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=art[stage])
  c.submit(task,p['actor'],p['ticket'],response,f'sikh342-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',response)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p)
 write(f'source-manifest-c{cycle}.json',{str(p.relative_to(r)):pk.file_hash(p) for p in sorted((r/'src/movie_factory/adapters/blender').glob('*.py'))})
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json')
 v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh342-c{cycle}-challenge');print(c.state(task)['stage'])
elif action=='technical':
 step=sys.argv[2];run=pk.read_json(r,f'results/sikh335/look01/{step}-run-c{cycle}.json');assert run['status']=='RETURNED'
 for b in run['artifacts'].values():assert pk.file_hash(r/b['path'])==b['sha256']
 p=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
 assert p['before']['objects']==p['after']['objects'] and not d['blocked_drivers'] and not d['known_source_defects']
 n=p['support'][0]['neutral'];assert n['phase'] in ('neutral','bend')
 if n['phase']=='neutral':assert n['maximum_displacement']<.09 and n['maximum_initial_fit']<.045
 else:assert all(x['unchanged_shoulder'] for x in n['objects'].values())
 v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Saved actual neutral/bend proof preserves original scene objects and driver safety. Bounded geometric guards pass.',comparison='Technical prerequisite only; visible form and contact still require image inspection.',open_defects=[])
 Bridge(c).record_review(task,step,v);write(f'{step}-technical-review-c{cycle}.json',v);print('technical prerequisite only')
else:
 step=action;assert step in {'save','neutral_front','neutral_back','neutral_side','bend','bend_front','bend_back','bend_side'}
 path='results/sikh335/motion01/save-run-c5.json' if step=='save' else f"results/sikh335/look01/{'bend' if step.startswith('bend_') else 'save'}-run-c{cycle}.json"
 parent=pk.read_json(r,path)['artifacts']['native']
 recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==step)
 assert not (out/f'{step}-run-c{cycle}.json').exists()
 run=Bridge(c).dispatch(task,step,f'sikh342-look-c{cycle}-{step}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
 write(f'{step}-run-c{cycle}.json',run);print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
 if run['status']!='RETURNED':raise SystemExit(2)
