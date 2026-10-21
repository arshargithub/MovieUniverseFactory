"""Re-admit the same form proof after a tested numerical endpoint repair."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import planning_pipeline as pp, expert_planning as ep
from movie_factory.task_router import DATABASE

root=Path(__file__).resolve().parents[1]
out=root/'results/sikh335/look01'
c=wf.Controller(root,DATABASE)
task='sikh335-supporting-appearance'
state=c.state(task)
assert state['cycle']==2 and state['max_corrections']==4 and state['planning_step'] in pp.STEPS[:3]
art={stage:pk.read_json(root,f'results/sikh335/look01/{stage.lower()}-c1.json')['artifact'] for stage in pp.STEPS[:3]}
brief=art['STRATEGIZING']['brief']
for path in ('src/movie_factory/adapters/blender/nihang_look.py',
             'tests/test_nihang337_garment.py','results/sikh335/REASSESSMENT_337.md',
             'results/sikh335/look01/save-run-c1.json',
             '.runtime/factory-native/sikh337-look-c1-save/worker-status.json',
             'scripts/sikh337_look_repair_plan.py'):
    brief['source_bindings'][path]={'path':path,'sha256':pk.file_hash(root/path)}
art['GROUNDING']['reconciliation']+=' First native appearance attempt rejected nonfinite float32 envelope before save. Correction2 repairs only that numerical boundary; all original visual counterexamples and scope remain. Source/reference authority is unchanged.'
art['STRATEGIZING']['resource_scope']='Appearance correction2/max4 after failed first native attempt; same two-actor source-preserving proof and three images, one local Blender worker, no new spending or acceptance.'
art['STRATEGIZING']['method_choice']['evidence_status']='hypothesis'
brief['expert_plan']['challenge']['omission_probe']+=' Numeric boundary tests must precede another native attempt; finiteness is not a cloth-form or same-film pass.'
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    packet=c.packet(task)
    response={'input_digest':packet['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,packet['actor'],packet['ticket'],response,'sikh337-look-c2-'+stage)
    target=out/(stage.lower()+'-c2.json')
    assert not target.exists()
    target.write_text(json.dumps(response,indent=2)+'\n')
packet=c.packet(task);packet.pop('ticket',None)
(out/'challenge-input-c2.json').write_text(json.dumps(packet,indent=2)+'\n')
print(c.state(task)['planning_step'])
