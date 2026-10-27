"""Technical study transport control only; no anatomy or reference qualification."""
import json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=w.Controller(r,'.runtime/factory-entry.sqlite3');t='sikh335-supporting-appearance';cy=c.state(t)['cycle'];prefix=f'.runtime/factory-native/sikh387-appearance-c{cy}-source';a=p.read_json(r,prefix+'/anatomy386-reference.json');z=p.read_json(r,prefix+'/anatomy387-static-control.json');run=p.read_json(r,f'results/sikh387/appearance-c{cy}-source-run.json')
assert a['original_geometry_actions_unchanged'] and a['vertices']<=10000 and a['triangles']<=20000 and z['geometry_actions_unchanged'] and z['profile']['diagnostic_use_motion_blur'] is False
v=dict(verdict='PASS',run_digest=p.digest(run),observation='Actual bounded modelingstudy mesh imported on local derivative, sourcegeometry/actions retained and staticprofile confirmed. This qualifies transport only, not a positivevolume/anatomy or referenceauthority.',comparison='Actualcompiled source reports versus admitted inertmesh binding and explicitstudio scope.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Modelinggoal and skinfit unqualified.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Originalsourcegeometry/actions unchanged.'),evidence=dict(status='NOT_TESTED',observation='No anatomy/AV judgment from import.')))
Bridge(c).record_review(t,'source',v);(r/f'results/sikh387/appearance-c{cy}-source-review.json').write_text(json.dumps(v,indent=2)+'\n');print('Modelingstudy transport only')
