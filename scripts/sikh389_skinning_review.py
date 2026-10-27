"""Actual source/transport review only; never grants artistic approval."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];step=sys.argv[1];run=pk.read_json(r,f'results/sikh387/appearance-c{cy}-{step}-run.json');a=pk.read_json(r,f'.runtime/factory-native/sikh387-appearance-c{cy}-{step}/anatomy389-skinning.json')
assert a['source_preserved'] and a['primary_matrix_error']<=1e-7 and a['outside_error']<=2e-5 and a['max_surface_delta']<=.2
assert a['mode']==0 if step=='zero' else a['mode'] in (1,2)
assert a['diagnostic_render_profile']['diagnostic_use_motion_blur'] is False
if step=='zero':assert a['max_surface_delta']==0
elif a['mode']==1:
 assert a['cache']['samples']==183 and a['cache']['original_raw_shapes_actions_unchanged'] and a['cache']['other_geometry_unchanged']
 assert max(x['error'] for x in a['cache']['sample_playback_audit'])<2e-6
if a['mode']==2:
 assert a['static_probe']['frame']==339 and a['static_probe']['error']<2e-6 and a['static_probe']['outside_error']<2e-5 and a['static_probe']['original_shapes_preserved'] and a['static_probe']['primary_actions_preserved']
v=dict(verdict='PASS',run_digest=pk.digest(run),observation='Actual native source/matrix/exterior controls passed for fixed local skinning representation; anatomy unjudged.',comparison='Actual source control, declared interpolation edit and protected original action. No art PASS from volume or cache.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Anatomical form and full-speed remain unpassed.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Actual native source and matrix/exterior tests passed.'),evidence=dict(status='NOT_TESTED',observation='No artistic judgment from source controls.')))
Bridge(c).record_review(task,step,v);(r/f'results/sikh387/appearance-c{cy}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n');print(step,a['max_surface_delta'])
