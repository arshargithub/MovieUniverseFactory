"""Actual static-control/import qualification only; no artist verdict."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];step=sys.argv[1];prefix=f'.runtime/factory-native/sikh387-appearance-c{cy}-{step}';run=pk.read_json(r,f'results/sikh387/appearance-c{cy}-{step}-run.json')
if step=='zero':
 a=pk.read_json(r,prefix+'/anatomy387-static-control.json');assert a['geometry_actions_unchanged'];profile=a['profile']
else:
 a=pk.read_json(r,prefix+'/anatomy386-target.json');assert a['samples']==183 and a['original_raw_shapes_actions_unchanged'] and a['other_geometry_unchanged'];assert max(x['error'] for x in a['sample_playback_audit'])<=2e-5;profile=a['diagnostic_render_profile']
assert type(profile['source_use_motion_blur']) is bool and profile['diagnostic_use_motion_blur'] is False
v=dict(verdict='PASS',run_digest=pk.digest(run),observation='Actual source/static profile and source/import preservation qualified; source blur setting '+str(profile['source_use_motion_blur'])+'. Diagnostic blur disabled; no natural anatomy, embedding or AV pass.',comparison='Actual compiledreport and declaredsource/profile invariants, not assumeddefaults.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Static diagnostic/technical control only; actorform and moving/contact qualificationremainopen.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Actualsource/target and staticprofile checks passed.'),evidence=dict(status='NOT_TESTED',observation='No anatomical or audiovisual approval from profile/transport.')))
Bridge(c).record_review(task,step,v);(r/f'results/sikh387/appearance-c{cy}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n');print(step,'technicalonly; sourceblur',profile['source_use_motion_blur'])
