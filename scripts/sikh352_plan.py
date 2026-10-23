"""Retained task352: coupled arm/contact, matched deformation proof."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh352';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(name,v):
 p=out/name;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,name
 else:p.write_text(t)
 return bind(str(p.relative_to(r)))
action=sys.argv[1];state=c.state(task);cycle=state['cycle'];assert 58<=cycle<=61
parent='.runtime/factory-native/sikh347-look-c52-save/scene.blend' if cycle<60 else '.runtime/factory-native/sikh352-c59-save/scene.blend'
if cycle==61:parent='.runtime/factory-native/sikh352-c60-save/scene.blend'
if action=='plan':
 arts={st:pk.read_json(r,f'results/sikh335/look01/{st.lower()}-c33.json')['artifact'] for st in pp.STEPS[:3]}
 ground,derive,strategy=[arts[x] for x in pp.STEPS[:3]];b=strategy['brief'];d=state['direction']
 reason='352 four additional appearance corrections58–61. Solve shoulder/elbow/wrist with grip height and azimuth on the unchanged spear; compare identical evaluated poses under volume preserving and linear skinning. Do not freeze an unaccepted hand constraint or conceal failed anatomy with cloth. Whole actor and AV remain unqualified.'
 for s in d['context_sources']:
  ground['uses'][s['id']]=dict(disposition='apply',reason=s['statement'],implication=reason if s['id'] in {'audit348','strategy352','controls','cast_findings','reconciliation351'} else ground['uses'].get(s['id'],{}).get('implication',s['statement']))
  derive['context_mapping'][s['id']]=dict(requirements=['preservation','form','interfaces','evidence'],reason=s['statement'])
 packet=pk.read_json(r,'results/sikh352/knowledge-packet.json')
 for o in packet['obligations']:
  k=o['id'];v=ground['knowledge_uses'][k]
  if k in {'current_state','anatomy','au_deformation','strategy','visual_gate','construction_interfaces','au_contact'}:v=reason
  if k=='secondary':v='Preserve horse/root/opposite arm and separate motion12. This is a coupled spear-arm diagnostic, not whole motion acceptance.'
  if k=='render_profile':v='Matched temporary studio CPU8 controls640 square; production contact frame supplements anatomy. No acceleration claim.'
  ground['knowledge_uses'][k]=v;derive['knowledge_mapping'][k]['reason']=v
 ground.update(reconciliation=reason,unresolved=[])
 b.update(knowledge_task=d['knowledge_task'],knowledge_digest=d['knowledge_digest'],knowledge_mapping=derive['knowledge_mapping'])
 b['source_bindings']={s['id']:s['binding'] for s in d['context_sources']}
 for path in ['results/sikh352/REQUEST.md','results/sikh352/STRATEGY.md','results/sikh351/CLOSEOUT.md','results/sikh351/DIAGNOSIS57.md','results/sikh348/CAUSAL_LEDGER.md',parent,
 '.runtime/factory-native/sikh342-look-c23-neutral_front/frame.png','.runtime/factory-native/sikh351-c57-anatomy_custom_front/frame.png',
 'src/movie_factory/adapters/blender/nihang_control.py','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/adapters/blender/nihang_arm352.py','tests/test_nihang352_arm.py','scripts/sikh352_plan.py']:
  b['source_bindings'][path]=bind(path)
 for ref in d['references']:b['source_bindings'][ref['id']]=ref['binding']
 b['strategy']='Use fixed coupled352 solver: choose a single shaft-relative grip drop/azimuth and elbow policy over all190frames; preserve shoulder origin and arm lengths, carry finger closure with wrist. Test same body with DQ versus linear skinning. No mesh smoothing or costume concealment.'
 b['early_proof']='Reopened pose derivative; front/back/side at283,290,327,350 under paired skinning plus actual hand/shaft closeup. Check shoulder shelf, hinge, wrist kink, interpenetration and opposite body regression. Numeric scores are not visual acceptance; extrema beyond these samples require evidence before any pass.'
 b['scope']='Diagnostic prerequisite to retained whole supporting-appearance deliverable, not an independent finished asset.'
 b['exclusions']='No horse/root/camera change, crowd propagation before actor qualifies, full sequence render, provider/install/cloud/publication/spend.'
 for row in b['expert_plan']['realizations'].values():
  row.update(method=b['strategy'],early_proof=b['early_proof'],failure_condition='Any malformed bare joint/contact, missing paired control or uninspected extremum blocks garment transfer; no acceptance by metrics.')
 for beat in derive['beats']:
  beat['framing']='Matched bare front/back/side preparation283, extrema290, crest327, landing350; close hand/shaft contact. Production camera unchanged.'
  beat['lenses']['anatomy_contact']['why']='Treat reach, elbow plane and wrist/shaft orientation as coupled; separate pose errors from linear-versus-volume-preserving deformation.'
  beat['lenses']['camera_editorial']['why']='Reverse and side reveal defects hidden frontally; intended framing follows qualified anatomy, never replaces diagnostic controls.'
 b['expert_plan']['beats']=derive['beats']
 b['expert_plan']['challenge'].update(cross_discipline_conflicts='Spear contact cannot force implausible wrist/shoulder; historical hand height is not accepted identity.',omission_probe='Inspect both arms and hips when changing body skinning; verify fist actually contacts shaft rather than only center proxy.',scope_tradeoff='No clothing/crowd before integrated bare anatomy; this does not clear full actor form gate.')
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
 strategy.update(method_choice=dict(chosen=b['strategy'],alternatives='351 fixed wrist pole changes failed. Do not repeat them or hide with sleeves.',evidence_status='hypothesis',discriminating_test=b['early_proof']),resource_scope=f'Existing appearance{cycle}/61; one local worker; no new spend.',replan_triggers='Failed anatomy or contact revises coupled strategy within retained count; no task reset.')
 rec=write(f'save-recipe-c{cycle}.json',dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_arm352' if cycle<60 else 'mounted_cloth352' if cycle==60 else 'mounted_cloth352_refine',target='mounted leader')]))
 b['source_bindings'][rec['path']]=rec
 steps=[dict(id='save',kind='proof',depends_on=[],requirements=['preservation'],acceptance='Technical save/reopen of original52 derivative with protected owners intact; not anatomy acceptance.',native_recipe=rec)]
 views=[f'anatomy_{p}_{v}' for p in ('custom','linear') for v in ('front','back','side')]+['leader_contact'] if cycle<60 else ['leader_front','leader_reverse','leader_contact','anatomy_custom_side']
 for name in views:
  rec=write(f'{name}-recipe-c{cycle}.json',dict(operation='nihang_frames',frame=327,frames=[283,290,327,350] if cycle<60 else [283,288,327,350],view=name,width=640,height=640,samples=8));b['source_bindings'][rec['path']]=rec
  steps.append(dict(id=name,kind='proof',depends_on=['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=rec))
 if cycle>=59:
  b['source_bindings']['diagnosis58']=bind('results/sikh352/DIAGNOSIS58.md')
  b['strategy']='59: torso-supported elbow down/out and forearm forward; preserve segment lengths. Solve shaft orientation and hand frame together around unchanged spear tip at every original frame. Preserve horse/root/opposite arm; compare DQ and linear skinning. Fixed grip on old shaft orientation failed58 and is replaced, not silently retained.'
  b['early_proof']='All190frames hard wrist/clearance/continuity and exact tip preservation; front/back/side283/290/327/350 plus actual shaft contact. Neither numeric bounds nor contact qualify skin. Whole actor and movement remain pending.'
  for row in b['expert_plan']['realizations'].values():row.update(method=b['strategy'],early_proof=b['early_proof'])
  b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
  strategy['method_choice'].update(chosen=b['strategy'],alternatives='Fixed-shaft paired control58 failed with torso penetration and393mm elbow jump.',discriminating_test=b['early_proof'])
  for step in steps[1:]:step['acceptance']=b['early_proof']
 if cycle>=60:
  for path in ['results/sikh352/CLOTH60_STRATEGY.md','src/movie_factory/adapters/blender/nihang_cloth352.py','tests/test_nihang352_cloth.py','.runtime/factory-native/sikh342-look-c23-save/neutral-proof.npz','results/sikh352/anatomy_custom_front-visual-c59.json','results/sikh352/anatomy_custom_side-visual-c59.json','results/sikh352/anatomy_custom_back-visual-c59.json','results/sikh352/leader_contact-visual-c59.json']:
   b['source_bindings'][path]=bind(path)
  b['strategy']='60 restore actual23 independent neutral cloth, map through anatomical landmarks and interpolate native weights. Push inside-rest vertices out only; no skin-following shrinkwrap or52 body-shell. Match hidden support and retain materials. Body/arm59 unchanged.'
  b['early_proof']='Exact288 wrist extremum in bare side plus leader front/reverse/contact283/288/327/350. Inspect neck, shoulders, armpits, cuffs, waist and sash; retain whole actor/tack/face obligations. No crowd copies before a viable actor.'
  for row in b['expert_plan']['realizations'].values():row.update(method=b['strategy'],early_proof=b['early_proof'])
  for beat in b['expert_plan']['beats']:beat['framing']='Leader front/reverse/contact283/288/327/350 and bare exact288 extremum. Production camera/horse unchanged.'
  b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
  strategy['method_choice'].update(chosen=b['strategy'],alternatives='Do not relax or shrinkwrap52 body shell again.',discriminating_test=b['early_proof'])
  for step in steps[1:]:step['acceptance']=b['early_proof']
 if cycle==61:
  b['source_bindings']['diagnosis60']=bind('results/sikh352/DIAGNOSIS60.md')
  b['strategy']='61 localized elbow ease on independent60 cloth, central coat hem shortened under new coherent waist band. Preserve59 body and tip action. Rebind hidden supports to new coat and inspect actual interfaces; no blanket smoothing or skin-following garment.'
  b['early_proof']='Leader front/reverse/contact283/288/327/350; elbow breakthrough, rear hem/band lips and sash/cuff clearance must close in actual images. Whole supporting actor remains distinct from a repaired shirt. Last approved correction61.'
  for row in b['expert_plan']['realizations'].values():row.update(method=b['strategy'],early_proof=b['early_proof'])
  b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
  strategy['method_choice'].update(chosen=b['strategy'],alternatives='60 independent cloth retained; do not return to52 body shell.',discriminating_test=b['early_proof'])
  for step in steps[1:]:step['acceptance']=b['early_proof']
 strategy['steps']=steps
 for st in pp.STEPS[:3]:
  if pp.STEPS.index(st)<pp.STEPS.index(c.state(task)['planning_step']):continue
  p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[st]);c.submit(task,p['actor'],p['ticket'],v,f'sikh352-c{cycle}-{st}');write(f'{st.lower()}-c{cycle}.json',v)
 p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
 p=c.packet(task);v=pk.read_json(r,f'results/sikh352/challenge-c{cycle}.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh352-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
 result=pk.read_json(r,f'results/sikh352/save-run-c{cycle}.json');diag=pk.read_json(r,result['artifacts']['scripts']['path'])
 assert not diag['blocked_drivers'] and not diag['known_source_defects']
 for a in result['artifacts'].values():assert pk.file_hash(r/a['path'])==a['sha256']
 patch=pk.read_json(r,result['artifacts']['patch']['path']);assert patch['before']['objects']==patch['after']['objects']
 report=patch['support'][0]['arm352' if cycle<60 else 'cloth352'];assert report['changed']
 if cycle<60:assert len(report['records'])==190
 else:assert report['source_preserved'] and 1000<report['vertices']<10000
 v=dict(verdict='PASS',run_digest=pk.digest(result),evidence=result['artifacts'],observation='Coupled pose saved/reopened, all190frames solved, protected owners retained. No visual anatomy/contact acceptance.',comparison='Original52 remains unqualified control.',open_defects=[])
 Bridge(c).record_review(task,'save',v);write(f'save-technical-c{cycle}.json',v)
else:
 step=next(s for s in state['planning_artifacts']['STRATEGIZING']['steps'] if s['id']==action)
 source=bind(parent) if action=='save' else pk.read_json(r,f'results/sikh352/save-run-c{cycle}.json')['artifacts']['native']
 result=Bridge(c).dispatch(task,action,f'sikh352-c{cycle}-{action}',parent=source,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe']);write(f'{action}-run-c{cycle}.json',result)
 print(json.dumps({k:result.get(k) for k in ['id','status','error']}))
 if result['status']!='RETURNED':raise SystemExit(2)
