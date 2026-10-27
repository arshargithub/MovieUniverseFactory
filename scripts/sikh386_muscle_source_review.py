"""Actual primary-performance preservation only, not pectoral artistic approval."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=w.Controller(r,'.runtime/factory-entry.sqlite3');t='sikh335-supporting-appearance';cy=c.state(t)['cycle'];step=sys.argv[1]
run=p.read_json(r,f'results/sikh386/appearance-c{cy}-{step}-run.json');a=p.read_json(r,f'.runtime/factory-native/sikh386-appearance-c{cy}-{step}/anatomy386-muscle.json');m=a['metrics']
assert run['status']=='RETURNED' and a['old_geometry_keys_weights_rest_bones_primary_curves_exact']
assert m['primary_matrix_error']<=1e-7 and max(m[k] for k in ['outside_error','true_distal_error','neutral_error','boundary_error'])<=2e-5
assert m['upper_elbow_buffer_vertices']==8 and m['upper_elbow_buffer_error']<=.005 and m['max_posed_delta']<=.22
assert a['secondary_bones']==['DEF-breast.L','DEF-breast.R'] and (not a['new_channels'] if a['amount']==0 else len(a['new_channels'])==2 and all(v['index']==1 for v in a['new_channels']))
v=dict(verdict='PASS',run_digest=p.digest(run),observation='Actual primary-performance/source preservation passed across twelve frames. Only declared two secondary scale-Y channels may differ. Primarymatrix error='+str(m['primary_matrix_error'])+', true-distal/exterior/neutral/boundary error='+str({k:m[k] for k in ['true_distal_error','outside_error','neutral_error','boundary_error']})+'. Coupled eight-point upper-elbow skin delta='+str(m['upper_elbow_buffer_error'])+'. Contacts='+str(a['surface_diagnostics'])+'. This is not anatomical/contact/consumer/AV approval.',comparison='Actual same-source amount-zero versus bounded secondary tissue operation, exact original geometry/weights/keys/rest/old channels and strict primary-joint/boundary/distal checks.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Source/primary invariant control only; all physical failures still block adoption.'))
Bridge(c).record_review(t,step,v);(r/f'results/sikh386/appearance-c{cy}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n');print(step,'PASSprimary/source control only')
