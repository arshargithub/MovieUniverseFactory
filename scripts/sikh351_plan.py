"""Source-grounded bare-deformation control, within existing appearance53."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, planning_pipeline as pp, expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';out=r/'results/sikh351'
def bind(path):return dict(path=path,sha256=pk.file_hash(r/path))
def write(name,data):
    p=out/name;value=json.dumps(data,indent=2)+'\n'
    if p.exists():assert p.read_text()==value, name
    else:p.write_text(value)
    return bind(str(p.relative_to(r)))
action=sys.argv[1];state=c.state(task);cycle=state['cycle'];assert 53<=cycle<=57
parent='.runtime/factory-native/sikh347-look-c52-save/scene.blend'
if action=='plan':
    arts={st:pk.read_json(r,f'results/sikh335/look01/{st.lower()}-c33.json')['artifact'] for st in pp.STEPS[:3]}
    ground,derive,strategy=[arts[x] for x in pp.STEPS[:3]];b=strategy['brief'];d=state['direction']
    reason='351 five additional appearance corrections53–57. First isolate bare deformation on unchanged52 using matched rest, native bend and custom mounted controls. Preserve23 neutral cloth and motion12; no costume patches until causal evidence. No whole-actor or AV acceptance.'
    for source in d['context_sources']:
        ground['uses'][source['id']]=dict(disposition='apply',reason=source['statement'],implication=reason if source['id'] in {'audit348','reconciliation351','controls','cast_findings'} else ground['uses'].get(source['id'],{}).get('implication',source['statement']))
        derive['context_mapping'][source['id']]=dict(requirements=['preservation','form','interfaces','evidence'],reason=source['statement'])
    packet=pk.read_json(r,'results/sikh351/knowledge-packet.json')
    for obligation in packet['obligations']:
        key=obligation['id'];existing=ground['knowledge_uses'][key]
        if key in {'current_state','anatomy','au_deformation','strategy','visual_gate','construction_interfaces'}:existing=reason
        if key=='secondary':existing='Preserve current motion52/motion12; no new hair/cloth/horse behavior claimed by static anatomy diagnosis.'
        if key=='render_profile':existing='Matched temporary body-only CPU8 studio controls at640 square, same rig-relative camera/light. No production look or render acceleration claim.'
        ground['knowledge_uses'][key]=existing;derive['knowledge_mapping'][key]['reason']=existing
    ground.update(reconciliation=reason,unresolved=[])
    b.update(knowledge_task=d['knowledge_task'],knowledge_digest=d['knowledge_digest'],knowledge_mapping=derive['knowledge_mapping'])
    b['source_bindings']={s['id']:s['binding'] for s in d['context_sources']}
    for path in ['results/sikh351/REQUEST.md','results/sikh351/GROUNDING_RECONCILIATION.md',
        'results/sikh348/CAUSAL_LEDGER.md','results/sikh335/REASSESSMENT_347.md',parent,
        '.runtime/factory-native/sikh342-look-c23-neutral_front/frame.png',
        '.runtime/factory-native/sikh347-look-c52-leader_anatomy/frame-0327.png',
        'src/movie_factory/adapters/blender/nihang_control.py','tests/test_nihang351_anatomy.py',
        'scripts/sikh351_plan.py']:
        b['source_bindings'][path]=bind(path)
    for ref in d['references']:b['source_bindings'][ref['id']]=ref['binding']
    b['strategy']='56 plane transport reduced slit but preserved implausible spear elbow behind shoulder.57 retains plane transport and tests a down/out/anterior elbow pole on the exact reachable circle. Preserve original shoulder origins, segment lengths and wrist/digit matrices. Body weights/material/shape unchanged. Bare283/327/350 must pass before any garment transfer; final authorized correction57.'
    b['early_proof']='Body-only rest/bend/custom front/back at327, actual custom283/327/350, joint-frame and weight inventory. A hard wedge or displaced joint blocks sleeve construction. Rest defects require donor/form reassessment; native-bend-only faults require joint/weight review; custom-only faults require transported frames/chain ownership diagnosis.'
    b['scope']='Diagnostic precursor within retained full supporting-appearance task. Unchanged52 parent; no appearance acceptance from this precursor.'
    b['exclusions']='No production motion change, full-passage render, crowd propagation, cosmetic finishing, paid calls, installation, upload or new identity decision.'
    for row in b['expert_plan']['realizations'].values():
        row['method']=b['strategy'];row['early_proof']=b['early_proof'];row['failure_condition']='Unmatched controls, missing actual anatomy, wrong native owner, or unchanged malformed bare arm. Failures remain blockers, not accepted diagnostic compromises.'
    for beat in derive['beats']:
        beat['framing']='Matched bare front/back controls, temporary studio lighting, at rest/90-degree native bend/custom327. Then custom stance283/landing350. Production camera unchanged.'
        beat['lenses']['anatomy_contact']['why']='Separate donor anatomy from weight/pivot/frame errors; fingertip or shaft contact never proves a believable elbow.'
        beat['lenses']['camera_editorial']['why']='Identical rig-relative framing and lighting isolate deformation; production read must follow later, not replace the revealing bare control.'
    b['expert_plan']['beats']=derive['beats'];b['expert_plan']['challenge'].update(
        cross_discipline_conflicts='Contact preservation cannot justify distorted anatomy. No costume masking; original mounted performance remains separate.',
        omission_probe='Check both arms, not just the exposed spear elbow; inspect parent scales, split deform bones, masked body regions and unrelated wrist twist.',
        scope_tradeoff='Diagnostic controls are internal, not a completed appearance review. No material polishing or crowd work before bare and cloth interfaces qualify.')
    b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
    strategy.update(method_choice=dict(chosen=b['strategy'],alternatives='Roll-only repair already failed46; body-shell relaxation failed48–52. Neither is repeated without discriminating evidence.',evidence_status='hypothesis',discriminating_test=b['early_proof']),
        resource_scope='Appearance53 of57, one local worker, no provider or additional spend.',replan_triggers='Any failed causal assumption routes strategy repair within remaining shared count; appearance cannot pass while foundational form fails.')
    for path in ['src/movie_factory/adapters/blender/nihang_anatomy351.py','src/movie_factory/adapters/blender/nihang_patch.py','results/sikh351/DIAGNOSIS.md']:
        b['source_bindings'][path]=bind(path)
    if cycle==57:b['source_bindings']['diagnosis57']=bind('results/sikh351/DIAGNOSIS57.md')
    recipe=write(f'save-recipe-c{cycle}.json',dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_anatomy351',target='mounted leader')]))
    b['source_bindings'][recipe['path']]=recipe
    steps=[dict(id='save',kind='proof',depends_on=[],requirements=['preservation'],acceptance='Reopen unchanged52 derivative with no unsafe drivers or missing dependencies; technical only.',native_recipe=recipe)]
    for pose in ('rest','bend','custom'):
        for view in ('front','back'):
            name=f'anatomy_{pose}_{view}';recipe=dict(operation='nihang_frames',frame=327,frames=[283,327,350] if pose=='custom' else [327],view=name,width=640,height=640,samples=8)
            binding=write(f'{name}-recipe-c{cycle}.json',recipe);b['source_bindings'][binding['path']]=binding
            steps.append(dict(id=name,kind='proof',depends_on=['save'],requirements=['preservation','form','interfaces','evidence'],acceptance=b['early_proof'],native_recipe=binding))
    strategy['steps']=steps
    for stage in pp.STEPS[:3]:
        if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
        p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=arts[stage]);c.submit(task,p['actor'],p['ticket'],v,f'sikh351-c{cycle}-{stage}');write(f'{stage.lower()}-c{cycle}.json',v)
    p=c.packet(task);p.pop('ticket',None);write(f'challenge-input-c{cycle}.json',p);print(c.state(task)['planning_step'])
elif action=='admit':
    p=c.packet(task);v=pk.read_json(r,f'results/sikh351/challenge-c{cycle}.json');v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh351-c{cycle}-admit');print(c.state(task)['stage'])
elif action=='technical':
    result=pk.read_json(r,f'results/sikh351/save-run-c{cycle}.json')
    diagnostics=pk.read_json(r,result['artifacts']['scripts']['path'])
    assert not diagnostics['blocked_drivers'] and not diagnostics['known_source_defects']
    for artifact in result['artifacts'].values():assert pk.file_hash(r/artifact['path'])==artifact['sha256']
    patch=pk.read_json(r,result['artifacts']['patch']['path']);assert patch['before']['objects']==patch['after']['objects']
    report=patch['support'][0]['anatomy351'];assert report['changed'] and max(x['contact_error'] for x in report['records'])<.0001
    value=dict(verdict='PASS',run_digest=pk.digest(result),evidence=result['artifacts'],observation='Pose-only candidate saved/reopened; protected owner snapshots and wrist/digit contact positions retained. Anatomy is not passed.',comparison='Source52 remains an unqualified negative control.',open_defects=[])
    Bridge(c).record_review(task,'save',value);write(f'save-technical-c{cycle}.json',value)
else:
    step=next(s for s in state['planning_artifacts']['STRATEGIZING']['steps'] if s['id']==action)
    source=bind(parent) if action=='save' else pk.read_json(r,f'results/sikh351/save-run-c{cycle}.json')['artifacts']['native']
    result=Bridge(c).dispatch(task,action,f'sikh351-c{cycle}-{action}',parent=source,blender_bin=BLENDER_BIN,timeout=600,recipe=step['native_recipe'])
    write(f'{action}-run-c{cycle}.json',result)
    print(json.dumps({k:result.get(k) for k in ['id','status','error']}))
    if result['status']!='RETURNED':raise SystemExit(2)
