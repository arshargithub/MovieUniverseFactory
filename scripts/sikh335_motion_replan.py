"""Explicitly retain failed continuous solve and re-admit reach-aware flight path."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance'
art=json.loads(json.dumps(c.state(task)['planning_artifacts']));brief=art['STRATEGIZING']['brief']
reason='Continuous candidate0 failed fixed-length foreleg reach before save. World wrist interpolation can leave the reachable sphere during rising shoulder arc. Keep grounded constraints; allow bounded reach-aware airborne retraction only, record every adjustment and reject excessive correction. No segment stretching. Preserve failed run and same shared correction counter.'
phase=len(sys.argv)>1 and sys.argv[1]=='placement'
if phase:
    reason='Actual candidate1 phase images and construction audit expose missing foot placement in gather and perfectly bilateral foreleg release/contact. Keep healthy supported trajectory; add low supported sequential placement and one-frame foreleg delay, not arbitrary sway. Native review was not recorded before handler changed, so no retroactive digest override: bound image audit retains FAIL, no native qualification claimed. Same temporal cycle2 of2.'
    brief['strategy']+=' Small supported placement steps precede lift; forelegs have one-frame release/contact separation.'
    brief['expert_plan']['realizations']['phases']['method']+=' Two low forefoot placement steps with held stance targets; independent one-frame foreleg release/contact.'
    path='results/sikh335/motion01/PHASE_REVIEW_C1.md'
    brief['source_bindings'][path]={'path':path,'sha256':pk.file_hash(root/path)}
    recipe=json.loads((out/'render-recipe.json').read_text());recipe['frames']=[294,301,307,327,345,349,350,351,353]
    (out/'render-c2-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
    path='results/sikh335/motion01/render-c2-recipe.json';binding={'path':path,'sha256':pk.file_hash(root/path)}
    brief['source_bindings'][path]=binding
    art['STRATEGIZING']['steps'][1]['native_recipe']=binding
else:
    brief['strategy']+=' Flight wrist paths are projected inside the flexed reach sphere only while airborne; grounded reach remains strict.'
    brief['expert_plan']['realizations']['support']['method']+=' During flight only, record bounded wrist retraction within fixed limb reach; fail if correction exceeds0.12 native units.'
for b in brief['source_bindings'].values():b['sha256']=pk.file_hash(root/b['path'])
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
art['STRATEGIZING']['method_choice']['chosen']=brief['strategy']
art['DERIVING']['derivations']['support']={f:brief['expert_plan']['realizations']['support'][f] for f in pp.DERIVATION_FIELDS}
art['DERIVING']['derivations']['phases']={f:brief['expert_plan']['realizations']['phases'][f] for f in pp.DERIVATION_FIELDS}
event='sikh335-motion-placement' if phase else 'sikh335-motion-flight-reach'
c.revise(task,brief,{'path':'results/sikh335/REQUEST.md','sha256':pk.file_hash(root/'results/sikh335/REQUEST.md')},reason,event)
for step in pp.STEPS[:3]:
    p=c.packet(task);result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[step]}
    c.submit(task,p['actor'],p['ticket'],result,event+'-'+step)
p=c.packet(task);p.pop('ticket',None)
(out/('placement-repair-challenge-input.json' if phase else 'flight-repair-challenge-input.json')).write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['cycle'])
