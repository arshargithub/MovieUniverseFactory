"""Source-bound existing task planning and admitted native proof."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh357';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=out/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
action=sys.argv[1];s=c.state(task);cycle=s['cycle'];assert 73<=cycle<=82
config=pk.read_json(r,f'results/sikh357/config-c{cycle}.json');parent=config['parent'];method=config['method'];proof=config['proof']
if action=='plan':
 arts={st:pk.read_json(r,f'results/sikh353/{st.lower()}-c67.json')['artifact'] for st in pp.STEPS[:3]}
 g,d,a=[arts[k] for k in pp.STEPS[:3]];b=a['brief'];direction=s['direction']
 for src in direction['context_sources']:
  g['uses'][src['id']]=dict(disposition='apply',reason=src['statement'],implication=method if src['id'] in {'strategy357','retro357','lessons354','controls'} else g['uses'].get(src['id'],{}).get('implication',src['statement']))
  d['context_mapping'][src['id']]=dict(requirements=['preservation','form','interfaces','evidence'],reason=src['statement'])
 packet=pk.read_json(r,'results/sikh357/appearance-knowledge-packet.json')
 for o in packet['obligations']:
  k=o['id'];v=g['knowledge_uses'][k]
  if k in {'current_state','strategy','construction_interfaces','au_contact','visual_gate'}:v=method+' '+proof
  if k=='crowd_support':v='Crowd deferred by353/357; unchanged contextual crowd not accepted or edited in this task.'
  g['knowledge_uses'][k]=v;d['knowledge_mapping'][k]['reason']=v
 g.update(reconciliation='357 ten total appearance73–82 on integrated motion16. Original reference/quality retained; causal retro audit distinguishes trigger from effectiveness.',unresolved=[])
 b.update(knowledge_task=direction['knowledge_task'],knowledge_digest=direction['knowledge_digest'],knowledge_mapping=d['knowledge_mapping'])
 b['source_bindings']={src['id']:src['binding'] for src in direction['context_sources']}
 for p in [parent,'results/sikh357/REQUEST.md','results/sikh357/STRATEGY.md','results/sikh354/RETRO_AUDIT.md',f'results/sikh357/config-c{cycle}.json','src/movie_factory/adapters/blender/nihang_beard357.py','src/movie_factory/adapters/blender/nihang_patch.py','tests/test_nihang357_beard.py','scripts/sikh357_plan.py']+config.get('extra_sources',[]):b['source_bindings'][p]=bind(p)
 for ref in direction['references']:b['source_bindings'][ref['id']]=ref['binding']
 b.update(strategy=method,early_proof=proof,scope='Leader/horse appearance on preserved motion16. Full form and motion acceptance separate.',exclusions='Crowd construction, full sequence render, spend/providers/cloud/egress, protected Pashtun edits, new motion corrections.')
 for row in b['expert_plan']['realizations'].values():row.update(method=method,early_proof=proof,failure_condition='Known visible form/interface failure or missing evidence blocks whole actor admission. Local improvement is not completion.')
 for beat in d['beats']:
  beat['framing']='Actual production plus face/front/reverse controls at resting, crest and landed poses.'
  beat['lenses']['anatomy_contact']['why']='Keep original body/rig and material hand contact; attachments inherit actual owner across preserved motion16.'
  beat['lenses']['camera_editorial']['why']='Intended phone-size and revealing close/reverse views separate visible defects from irrelevant magnification.'
 b['expert_plan']['beats']=d['beats']
 b['expert_plan']['challenge'].update(cross_discipline_conflicts='Form must survive inherited head/torso action; surface projection cannot substitute for coherent garment edges.',omission_probe='Whole face/eyes/turban/beard/garments/tack/horse remain required; beard-only success cannot pass whole actor.',scope_tradeoff='Only scoped actual leader proofs; no crowd/full sequence render on failed appearance.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 rec=write(f'save-recipe-c{cycle}.json',dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind=config['kind'],target='mounted leader')]))
 steps=[dict(id='save',kind='proof',depends_on=[],requirements=['preservation'],acceptance='Reopened reversible derivative, no known scripts/driver defects; technical only.',native_recipe=rec)];b['source_bindings'][rec['path']]=rec
 for name,frames in config['views'].items():
  assert 327 in frames
  rec=write(f'{name}-recipe-c{cycle}.json',dict(operation='nihang_frames',frame=327,frames=frames,view=name,width=640 if name!='production' else 432,height=640 if name!='production' else 768,samples=config.get('samples',12)));b['source_bindings'][rec['path']]=rec
  steps.append(dict(id=name,kind='proof',depends_on=['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=proof,native_recipe=rec))
 a.update(steps=steps,method_choice=dict(chosen=method,alternatives='Do not repeat surface finish or more fibers on straight curtain. Preserve current whole scene and change failed representation.',evidence_status='hypothesis',discriminating_test=proof),resource_scope=f'Appearance{cycle}/82, ten additional total; motion16 unchanged. One local worker, no spend.',replan_triggers='Whole-form or adjacent regression retains failure and triggers revised construction, not labels.')
 for st in pp.STEPS[:3]:
  if pp.STEPS.index(st)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[st]);c.submit(task,p['actor'],p['ticket'],v,f'sikh357-c{cycle}-{st}');write(f'{st.lower()}-c{cycle}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh357/challenge-c{cycle}.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh357-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
 result=pk.read_json(r,f'results/sikh357/save-run-c{cycle}.json');diag=pk.read_json(r,result['artifacts']['scripts']['path']);assert not diag['blocked_drivers'] and not diag['known_source_defects']
 for item in result['artifacts'].values():assert pk.file_hash(r/item['path'])==item['sha256']
 patch=pk.read_json(r,result['artifacts']['patch']['path']);report=patch['support'][0][config['kind'].removeprefix('mounted_')];assert report['changed'] and report['source_preserved']
 v=dict(verdict='PASS',run_digest=pk.digest(result),evidence=result['artifacts'],observation='Reversible derivative saved/reopened; artifacts verified and script diagnostics clean. Fixed form change only; no visual pass.',comparison='Original integrated16 source preserved; actual diagnostic report retained.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-c{cycle}.json',v)
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 source=bind(parent) if action=='save' else pk.read_json(r,f'results/sikh357/save-run-c{cycle}.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,f'sikh357-c{cycle}-{action}',parent=source,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write(f'{action}-run-c{cycle}.json',result);print({k:result.get(k) for k in ['id','status','error']})
 if result['status']!='RETURNED':raise SystemExit(2)
