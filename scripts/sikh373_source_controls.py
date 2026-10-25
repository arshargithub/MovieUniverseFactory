"""Bind actual native reports/masters and hoof arrival metrics, no artistic verdict."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh373'
def bind(path):return dict(path=path,sha256=pk.file_hash(r/path))
v=json.loads((r/'.runtime/factory-native/sikh373-motion-c80-prepare/landing373.json').read_text())
assert v['geometry_unchanged'] and v['accepted_prefix_action_error']==0 and max(v['accepted_prefix_errors'].values())==0
rows=v['frames'];assert [x['frame'] for x in rows]==list(range(334,368))
metrics={}
for side,contact in [('L',342),('R',343)]:
 trajectory={x['frame']:next(y for y in x['support'] if y['side']==side)['fore_visible_hoof'] for x in rows}
 final=[trajectory[f] for f in range(contact,368)]
 grounded_error=max(max(abs(a-b) for a,b in zip(q,final[0])) for q in final)
 steps=[(trajectory[f][2]-trajectory[f-1][2])*24 for f in range(336,contact+1)]
 assert all(b<a<0 for a,b in zip(steps,steps[1:])) and grounded_error<1e-4
 metrics[side]=dict(contact_frame=contact,world_hoof=trajectory[contact],last_airborne_downward_speed_m_s=steps[-1],previous_speed_m_s=steps[-2],postcontact_anchor_error_m=grounded_error)
contact_path='.runtime/factory-native/sikh373-motion-c80-contact/padsolve370.json'
cache=json.loads((r/contact_path).read_text());assert cache['phase']=='landing' and cache['interval']==[334,367] and len(cache['rows'])==34
assert cache['original_motion_actions_unchanged'] and cache['original_geometry_unchanged'] and min(x['min_gap'] for x in cache['rows'])>=.002
masters={}
for path,sha in [('.runtime/factory-native/sikh370-motion-c66-audit/scene.blend','4b31c8428034de3635c23992d4e3068d43fa83fa49eae1fa6dac7103a9b3e748'),('.runtime/factory-native/sikh372-motion-c75-source/scene.blend','9633bf00d5cabdedde370c2195729b9f1e5190e681130d75c2c9a6187b8701ca')]:
 b=bind(path);assert b['sha256']==sha;masters[path]=b
(o/'PROTECTED_MASTERS.json').write_text(json.dumps(masters,indent=2)+'\n')
record=dict(primary=bind('.runtime/factory-native/sikh373-motion-c80-prepare/scene.blend'),landing_native=bind('.runtime/factory-native/sikh373-motion-c80-contact/scene.blend'),pose_report=bind('.runtime/factory-native/sikh373-motion-c80-prepare/landing373.json'),contact_report=bind(contact_path),accepted_prefix=[276,333],prefix_pose_error=0,prefix_scalar_error=0,original_geometry_unchanged=True,hoof_metrics=metrics,cache_minimum_gap_m=min(x['min_gap'] for x in cache['rows']),cache_interval=cache['interval'],scope='Integer-frame worldpose/scalar/mesh support; finalsurfacevertex/trianglecentre clothclearance, notsubframephysics/directAV. Original padvisibilityexcludedfromactionhashbutall58acceptedvalues explicitlychecked bycachebuilder; actualprefixpixels separatelyrequired.')
(o/'SOURCE_CONTROLS80.json').write_text(json.dumps(record,indent=2)+'\n')
(o/'REUSE_HANDOFF80.json').write_text(json.dumps(dict(source=record['landing_native'],accepted_prefix_source=masters['.runtime/factory-native/sikh372-motion-c75-source/scene.blend'],new_phase=[334,367],last_two_coupled_states=rows[-2:],cache_interval=[334,367],future='368+action/cloth/flag/unrenderedmotion unqualified; tail/look/leaderflaggesture separate. Actualnative367pose/velocity/contact is entry for next unit, notan abstractanchor replay.'),indent=2)+'\n')
print('Verified34frame source/contact,58accepted pose/scalarstates,protectedmasters andfiniteacceleratinghoofarrivals')
