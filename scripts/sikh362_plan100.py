"""Explicit whole-look derivation repair; all geometry/performance unchanged."""
import json,sys
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep
from movie_factory.task_router import DATABASE
from movie_factory.native_admission import Bridge,BLENDER_BIN
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==100
o=r/'results/sikh362';action=sys.argv[1]
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
if action=='plan':
 d=pk.read_json(r,'results/sikh362/appearance-c99-deriving.json')['artifact'];base=pk.read_json(r,'results/sikh362/appearance-c99-strategizing.json')['artifact'];b=base['brief']
 method='Preserve exact99 native and every action, mesh, material, pose/cache and camera. This is a qualification-scope repair only. Fresh admitted save/reopen and canonical283 repeat must retain selected state and image; review source-bound99 controls and complete26 passage against full supporting-film requirements, not just the garment proof. No duplicate full render or art edit; direct full-speed AV remains pending.'
 proof='Actual13 controls, all125 source frames and faithful-reference/accepted-film comparison must cover full head/eyes/beard/turban, skin/textiles/accessories and dark horse/head/mane/tail/tack. Require no known frame/source-visible failure, exact parent/source/camera and canonical repeat comparison. Do not infer playback, portability, general cloth dynamics or release approval.'
 for row in d['requirements']:
  if row['id']=='evidence':row['criterion']='Actual source-bound stance, sides, crest, landing and complete leader/horse passage compared with accepted film floor. Head/beard/horse surface are explicitly covered by whole_look; crowd is deferred and full-speed AV remains pending, not self-passed.'
 whole=dict(id='whole_look',criterion='Entire supporting leader and horse share accepted film richness and believable form: integrated head/eyes/skin/beard/crown, cloth/accessories/seat and horse head/coat/mane/tail/tack at actual shot size. A smooth mannequin, shell crown, clay horse, visible layer/contact failure or adjacent regression fails. No new principal identity or Director AV acceptance.',modes=['technical','image'],director_av=False)
 d['requirements'].append(whole);lenses=['story_performance','camera_editorial','anatomy_contact','effects_environment','production_reuse']
 d['derivations']['whole_look']=dict(beats=['appearance'],lenses=lenses,derivation='Original supporting-shot direction requires near-principal visible realism, not distant silhouettes or wardrobe-only correctness. Current362 integrated scope requires named whole-actor/horse checks; this omission is repaired before handoff.',origin='director',priority='quality_floor',reference_ids=['accepted_film','reference_rear'])
 beat=d['beats'][0];beat['framing']='Exact99 face/oblique/front/reverse controls and current26 production frames252..376. Leader/horse only, one-second context handles; principal/crowd in context explicitly unqualified.'
 for name in lenses:
  row=beat['lenses'][name];row['applies']=True;row['requirements'].append('whole_look');row['why']='Whole supporting actor/horse must read as one believable film element under actual camera/light; current crowd deferred, not forgotten. '+row['why']
 ids=[x['id'] for x in d['requirements']]
 for mapping in [d['context_mapping'],d['knowledge_mapping']]:
  for row in mapping.values():row['requirements']=ids;row['reason']+=' Whole-look coverage is now explicit; original source status, deferred crowd and Director AV boundaries remain.'
 b.update(requirements=d['requirements'],knowledge_mapping=d['knowledge_mapping'],strategy=method,early_proof=proof)
 b['expert_plan']['beats']=d['beats']
 for rid,row in d['derivations'].items():
  if rid not in b['expert_plan']['realizations']:b['expert_plan']['realizations'][rid]=deepcopy(b['expert_plan']['realizations']['form'])
  b['expert_plan']['realizations'][rid].update(row,method=method,early_proof=proof,failure_condition='Any known source/frame-visible whole-actor or horse failure blocks; old garment-only acceptance cannot close head/skin/groom/coat. Missing direct AV is pending human judgment, never PASS.')
 b['expert_plan']['realizations']['whole_look']['interfaces']=['head/eyes/skin/beard/crown under same light','horse head/coat/mane/tail/tack and rider seat','cloth/sash/band/skirt and hands','source/camera/frame-size/review-use identity']
 b['expert_plan']['challenge'].update(omission_probe='Compare original intent to full claimed actor/horse, not the inherited garment checklist; context placeholders remain excluded explicitly.',cross_discipline_conflicts='Unchanged good geometry can still be inadequately reviewed. Reuse exact source-bound views, not images from a different source/pose/camera; no schema-only look pass.',scope_tradeoff='Qualification repair with one canonical repeat, not unnecessary full rerender or portrait refinement.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 sources=['results/sikh362/SCOPE100.md','results/sikh362/STATIC_REVIEW99.md','results/sikh362/LEARNINGS.md','results/sikh362/appearance-c99-save-run.json','results/sikh362/appearance-c99-production-run.json','scripts/sikh362_plan100.py']
 for p in sources:b['source_bindings'][p]=bind(p)
 parent='.runtime/factory-native/sikh362-appearance-c99-save/scene.blend';b['source_bindings'][parent]=bind(parent)
 steps=[]
 for name,recipe,requires,depends in [
  ('save',dict(operation='nihang_save',frame=283,width=432,height=768,samples=16),['preservation'],[]),
  ('repeat',dict(operation='nihang_frames',frame=283,frames=[283],view='production',width=432,height=768,samples=16),ids,['save'])]:
  rb=write(f'appearance-c100-{name}-recipe.json',recipe);b['source_bindings'][rb['path']]=rb
  steps.append(dict(id=name,kind='proof',depends_on=depends,requirements=requires,acceptance=proof,native_recipe=rb))
 base.update(brief=b,steps=steps,method_choice=dict(chosen=method,alternatives='Do not rebuild or rerender the identical full asset merely to fix an omitted review requirement. Do not rubber-stamp the old narrow evidence row.',evidence_status='observed',discriminating_test=proof),resource_scope='Appearance100/max107, same task/history, one worker after26 finishes; no new spend.',replan_triggers='Any actual frame/source failure requires affected-stage correction, not relabeling it passed.')
 for stage,artifact in [('DERIVING',d),('STRATEGIZING',base)]:
  if c.state(task)['planning_step']!=stage:continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=artifact);c.submit(task,p['actor'],p['ticket'],v,'sikh362-appearance100-'+stage);write('appearance-c100-'+stage.lower()+'.json',v)
 print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,'results/sikh362/appearance-c100-challenge.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,'sikh362-appearance100-admit');print(c.state(task)['stage'])
else:
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
 parent=bind('.runtime/factory-native/sikh362-appearance-c99-save/scene.blend') if action=='save' else pk.read_json(r,'results/sikh362/appearance-c100-save-run.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,'sikh362-appearance-c100-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write('appearance-c100-'+action+'-run.json',result);print(result['status'])
 if result['status']!='RETURNED':raise SystemExit(2)
