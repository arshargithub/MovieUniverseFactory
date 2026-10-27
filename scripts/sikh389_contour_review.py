"""Native static contour transport checks only, never anatomical approval."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];assert cy==251
run=pk.read_json(r,'results/sikh387/appearance-c251-source-run.json');a=pk.read_json(r,'.runtime/factory-native/sikh387-appearance-c251-source/anatomy389-contour.json')
assert a['frame']==339 and a['max_delta']<=.2 and a['actual_error']<=2e-6 and a['outside_exact'] and a['original_shapes_actions_othergeometry_preserved'] and a['diagnostic_render_profile']['diagnostic_use_motion_blur'] is False
v=dict(verdict='PASS',run_digest=pk.digest(run),observation='Actual339snapshot, existing200mmguard, outside points and original data checks passed. No anatomical verdict.',comparison='Declared fixed field, actual target playback and original shape/action/othergeometry source.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Static source transport only; anatomy remains unjudged.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Native target and original data checks passed.'),evidence=dict(status='NOT_TESTED',observation='Requires actual nativeviews.')))
Bridge(c).record_review(task,'source',v);(r/'results/sikh387/appearance-c251-source-review.json').write_text(json.dumps(v,indent=2)+'\n');print(a['max_delta'])
