"""Technical actual upper-arm discriminator only; never artistic approval."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];step=sys.argv[1];run=pk.read_json(r,f'results/sikh387/appearance-c{cy}-{step}-run.json');a=pk.read_json(r,f'.runtime/factory-native/sikh387-appearance-c{cy}-{step}/anatomy387-upperarm.json')
m=a['metrics'];assert a['geometry_weights_actions_rest_exact'] and m['primary_matrix_error']<=1e-7 and max(m['outside_error'],m['distal_error'])<=2e-5 and m['max_delta']<=.4
assert a['mode']==(0 if step=='zero' else 1) and (a['mode'] or m['max_delta']<=2e-5)
assert a['diagnostic_render_profile']['diagnostic_use_motion_blur'] is False
v=dict(verdict='PASS',run_digest=pk.digest(run),observation='Actual fixed upper-arm segmentation and source/matrix/outside/distal controls pass. Max changed skin distance '+str(m['max_delta'])+'m. This is a causal-control transport pass, no artistic/anatomical acceptance.',comparison='Actual source reports and declared four-bone control; original pose, weights, shape keys, meshes and actions retained.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Natural form, interface and full-speed performance remain unpassed.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Actual source/matrix/declared-edit controls passed.'),evidence=dict(status='NOT_TESTED',observation='No art/AV judgment from source checks.')))
Bridge(c).record_review(task,step,v);(r/f'results/sikh387/appearance-c{cy}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n');print(step,m)
