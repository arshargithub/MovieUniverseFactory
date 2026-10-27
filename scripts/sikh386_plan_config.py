"""Same-task staged transport only. Artistic reviews/challenges are supplied files."""
import copy,json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE

r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
s=c.state(task);cy=s['cycle'];tag=f'appearance-c{cy}';action=sys.argv[1]
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
    p=o/n;t=json.dumps(v,indent=2)+'\n'
    if p.exists():assert p.read_text()==t,n
    else:p.write_text(t)
    return bind(str(p.relative_to(r)))
cfg_path=sys.argv[2] if action=='plan' else f'results/sikh386/{tag}.json'
cfg=pk.read_json(r,cfg_path)
if action=='plan':
    b=copy.deepcopy(pk.read_json(r,cfg['brief_path']));direction=s['direction'];ids=[q['id'] for q in b['requirements']]
    b.update(strategy=cfg['method'],early_proof=cfg['proof'],scope=cfg['scope'],audience_result=b['intent'])
    for p in [f'results/sikh386/{tag}.json',cfg['parent'],'scripts/sikh386_plan.py','scripts/sikh386_plan_config.py',cfg_path]+cfg.get('sources',[]):b['source_bindings'][p]=bind(p)
    for src in direction['context_sources']:b['source_bindings'][src['binding']['path']]=src['binding']
    from movie_factory import work_units
    from movie_factory.adapters.blender import nihang_patch,nihang_control
    from movie_factory.native_admission import timeout_limit
    steps=[]
    for spec in cfg['steps']:
        recipe=spec['recipe'];assert spec.get('timeout',600)<=timeout_limit(recipe)
        work_units.native(dict(task=task,cycle=cy,max_corrections=s['max_corrections'],brief=b),recipe)
        (nihang_patch.validate if recipe['operation']=='nihang_patch' else nihang_control.validate)(recipe)
        rb=write(f'{tag}-{spec["id"]}-recipe.json',recipe);b['source_bindings'][rb['path']]=rb
        steps.append(dict(id=spec['id'],kind='proof',depends_on=spec['depends_on'],requirements=spec['requirements'],acceptance=spec.get('acceptance',cfg['proof']),native_recipe=rb))
    b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
    uses={};cm={}
    for row in direction['context_sources']:
        sid=row['id'];application=cfg['context_application'][sid]
        uses[sid]=dict(disposition=application['disposition'],reason=application['reason'],implication=application['implication'])
        cm[sid]=dict(requirements=application['requirements'],reason=application['reason'])
    g=dict(reference_readiness=b['reference_readiness'],uses=uses,knowledge_uses={k:v['reason'] for k,v in b['knowledge_mapping'].items()},reconciliation=cfg['reconciliation'],unresolved=[])
    d=dict(reference_readiness=b['reference_readiness'],reference_mapping=b['reference_mapping'],requirements=b['requirements'],beats=b['expert_plan']['beats'],
        derivations={k:{f:m[f] for f in pp.DERIVATION_FIELDS} for k,m in b['expert_plan']['realizations'].items()},context_mapping=cm,knowledge_mapping=b['knowledge_mapping'])
    strat=dict(brief=b,steps=steps,method_choice=dict(chosen=cfg['method'],alternatives=cfg['alternatives'],evidence_status=cfg['evidence_status'],discriminating_test=cfg['proof']),
        resource_scope=f'Original task{task},cycle{cy}/226 shared Director386ceiling, one native worker, no provider/spend/escalation.',replan_triggers=cfg['failure'])
    for stage,art in [('GROUNDING',g),('DERIVING',d),('STRATEGIZING',strat)]:
        if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
        p=c.packet(task);v=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=art)
        c.submit(task,p['actor'],p['ticket'],v,f'sikh386-{tag}-{stage}');write(tag+'-'+stage.lower()+'.json',v)
    print(c.state(task)['planning_step'])
elif action=='admit':
    v=pk.read_json(r,f'results/sikh386/{tag}-challenge.json');p=c.packet(task);v['input_digest']=p['planning_input_digest']
    c.submit(task,p['actor'],p['ticket'],v,'sikh386-'+tag+'-admit');print('Plan admitted; retrospective guards still apply')
elif action in {'review','auto-review'}:
    raise SystemExit('No automated artistic PASS. Supply an evidence-backed actual review through Bridge/Controller.')
else:
    step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==action)
    spec=next(x for x in cfg['steps'] if x['id']==action)
    parent=bind(spec.get('parent',cfg['parent'])) if not spec['depends_on'] else pk.read_json(r,f'results/sikh386/{tag}-{spec["depends_on"][0]}-run.json')['artifacts']['native']
    result=Bridge(c).dispatch(task,action,'sikh386-'+tag+'-'+action,parent=parent,blender_bin=BLENDER_BIN,timeout=spec.get('timeout',600),recipe=step['native_recipe'])
    write(f'{tag}-{action}-run.json',result);print(result['status'])
    if result['status']!='RETURNED':raise SystemExit(2)
