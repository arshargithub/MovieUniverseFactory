"""Actual secondary-support precision control only; never anatomy/contact PASS."""
import json,sys
from pathlib import Path
import numpy as np
from movie_factory import production_workflow as w,production_knowledge as p
from movie_factory.native_admission import Bridge
from movie_factory.adapters.blender.anatomy_support386 import qualify_roundtrip
r=Path(__file__).resolve().parents[1];c=w.Controller(r,'.runtime/factory-entry.sqlite3');t='sikh335-supporting-appearance';cy=c.state(t)['cycle'];step=sys.argv[1]
run=p.read_json(r,f'results/sikh386/appearance-c{cy}-{step}-run.json');base=f'.runtime/factory-native/sikh386-appearance-c{cy}-{step}/';a=p.read_json(r,base+'anatomy386-support.json');n=np.load(r/(base+'anatomy386-support.npz'),allow_pickle=False)
assert run['status']=='RETURNED' and a['neutral_error']<=.0001 and a['source_geometry_keys_actions_exact']
assert a['original_pose_preservation']['outside_surface_max_error']<=.0001 and a['original_pose_preservation']['skeleton_and_world_max_error']<=.0001 and a['original_rest_error']<=.0001
assert a['new_bones']==(['MF386 pectoral rigid.L','MF386 pectoral rigid.R'] if a['strength'] else [])
if step=='source':
 q=np.load(r/'.runtime/factory-native/sikh386-appearance-c222-bind/anatomy386-support-preflight.npz',allow_pickle=False);error=qualify_roundtrip(n['rig_before'],n['rig_after'],q['rig_before'],q['rig_after']);detail=f'Zero no-added-bone roundtrip explains222originalmatrixdrift with maxvector error{error:.9f}.'
else:
 q=np.load(r/f'.runtime/factory-native/sikh386-appearance-c{cy}-source/anatomy386-support.npz',allow_pickle=False);matrix_error=float(abs(n['rig_after']-q['rig_before']).max());outside_error=float(abs(n['pose_after'][:,~n['selected']]-q['pose_before'][:,~n['selected']]).max());assert max(matrix_error,outside_error)<=.0001
 detail=f'Cumulativeoriginal-source matrixerror{matrix_error:.9f},outsideerror{outside_error:.9f}; bounded100microunits/metres policy, not bit-exact.'
v=dict(verdict='PASS',run_digest=p.digest(run),observation=f'Actual source/neutral/original-motion numeric preservation only: neutralerror{a["neutral_error"]:.9f}m. '+detail+' Sourcegeometry/keys/actions exact. Contacts='+str(a['surface_diagnostics'])+'. No anatomy/contact/consumer/AV qualification; allknownphysical failuresblockadoption.',comparison='Actual no-added-bone editroundtrip versus222failure and cumulative same-original-source pose matrices/surfaces; predeclared100microunit/metre visibility cap. Legacy guards unchanged.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Explicit numeric control only. Actual artistic/contact verdict separate; no known-defect waiver.'))
Bridge(c).record_review(t,step,v);(r/f'results/sikh386/appearance-c{cy}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n');print(step,'PASSnumeric control only; art/contact unqualified')
