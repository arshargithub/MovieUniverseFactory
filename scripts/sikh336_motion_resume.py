"""Apply exact Director extension and reground the same failed motion task."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,production_allowance as pa,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01';task='sikh335-continuous-performance'
c=wf.Controller(root,DATABASE)
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
decision=bind('results/sikh335/motion01/allowance-336.json')
request={'text':'Approve four additional corrections','operations':['code','test','document'],
    'authority':decision,'amendment_task':task,'rationale':'Administrative allowance amendment only, not production dispatch. Explicit Director reply extends this existing motion task by four; retained plan must be fully regrounded before native work. No new spend or counter reset.'}
c.route_request('sikh336-motion-extension',request)
old=c.state(task);art=json.loads(json.dumps(old['planning_artifacts']))
pa.extend(c,task,'sikh336-motion-extension',decision,'sikh336-four-approved')
brief=art['STRATEGIZING']['brief']
brief['strategy']+=' Separate finite-velocity flight arrival from grounded contact; body absorption follows impact.'
brief['expert_plan']['realizations']['phases']['method']+=' Incoming fold endpoint uses finite monotonic descent; ground-side slope stays zero. Measure actual DEF-hoof positions and compare the last descending frames.'
brief['expert_plan']['realizations']['phases']['failure_condition']+=' Reject any pronounced pre-contact braking in actual visible-hoof velocity, even when scalar endpoint tests pass.'
for p in ['results/sikh335/motion01/allowance-336.json','results/sikh335/motion01/PHASE_REVIEW_C2.md','src/movie_factory/production_allowance.py','scripts/sikh336_motion_resume.py']:
    brief['source_bindings'][p]=bind(p)
# Reviewed source changes: contact interpolation + prior cast-inspection handler.
# Actual original input/reference/authority bindings must remain exact.
for p in ['src/movie_factory/adapters/blender/nihang_motion.py','src/movie_factory/adapters/blender/nihang_control.py','src/movie_factory/adapters/blender/nihang_patch.py','src/movie_factory/native_admission.py']:
    brief['source_bindings'][p]=bind(p)
recipe=pk.read_json(root,'results/sikh335/motion01/render-c2-recipe.json')
recipe['frames']=[294,301,307,327,343,345,347,348,349,350,351,353,357]
(out/'render-c3-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
binding=bind('results/sikh335/motion01/render-c3-recipe.json');brief['source_bindings'][binding['path']]=binding
art['STRATEGIZING']['steps'][1]['native_recipe']=binding
art['STRATEGIZING']['steps'][1]['acceptance']='All13 actual phase frames and measured deformed-hoof landing trajectories; source-visible failures reject. Full-speed AV and supporting appearance remain separate.'
art['STRATEGIZING']['resource_scope']='First of four additional Director-approved corrections, same task cycle3/max6; serial local jobs only. No new appearance-task allowance, provider, cloud or spend.'
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],discriminating_test='Actual forehoof last-step downward speed must not collapse before contact; fixed support, reach limits and phase images must remain credible.')
brief['expert_plan']['challenge'].update(plan_digest=ep.plan_digest(brief),omission_probe='Interior continuity was insufficient: actual deformed-hoof speed at the flight/contact boundary is the discriminating control.')
art['GROUNDING']['reconciliation']+=' Director336 explicitly approves four more corrections on this task; retain cycle2 failures, startcycle3/max6. No other allowance extension.'
for stage in pp.STEPS[:3]:
    packet=c.packet(task);result={'input_digest':packet['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,packet['actor'],packet['ticket'],result,'sikh336-contact-'+stage)
    (out/(stage.lower()+'-c3.json')).write_text(json.dumps(result,indent=2)+'\n')
packet=c.packet(task);packet.pop('ticket',None)
(out/'contact-challenge-input-c3.json').write_text(json.dumps(packet,indent=2)+'\n')
print(json.dumps({k:c.state(task)[k] for k in ('task','stage','planning_step','cycle','max_corrections')}))
