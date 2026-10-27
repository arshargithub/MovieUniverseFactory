"""Deterministic target transport checks only; never reviews anatomy or motion."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];prefix=f'.runtime/factory-native/sikh387-appearance-c{cy}-source'
run=pk.read_json(r,f'results/sikh387/appearance-c{cy}-source-run.json');v=pk.read_json(r,prefix+'/anatomy386-target.json')
assert v['samples']==183 and v['original_raw_shapes_actions_unchanged'] and v['other_geometry_unchanged']
error=max(x['error'] for x in v['sample_playback_audit']);assert error<2e-5
verdict=dict(verdict='PASS',run_digest=pk.digest(run),observation=f'Actual bound target applied, saved/reopened;183source samples; original raw/shapes/actions/othergeometry retained. Sampled maximum replay error{error}.',comparison='Actual handler source/rest/replay invariants versus admitted data; exact transfer cannot establish correct anatomy.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Deterministic transfer verification only; art and temporal proof remain unqualified.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Source geometry/action and outside-mask sampledpoints preserved.'),evidence=dict(status='NOT_TESTED',observation='No anatomical or temporal evidence in this technical check.')))
Bridge(c).record_review(task,'source',verdict);(r/f'results/sikh387/appearance-c{cy}-source-review.json').write_text(json.dumps(verdict,indent=2)+'\n');print('Transport qualified only:',cy)
