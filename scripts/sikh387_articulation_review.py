"""Only actual source/endpoint/preservation controls, never an artistic verdict."""
import sys,json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];step=sys.argv[1];prefix=f'.runtime/factory-native/sikh387-appearance-c{cy}-{step}'
run=pk.read_json(r,f'results/sikh387/appearance-c{cy}-{step}-run.json');a=pk.read_json(r,prefix+'/articulation387.json');m=a['metrics'];assert a['old_geometry_keys_weights_bones_primary_actions_exact']
assert max(m[k] for k in ['outside_error','true_distal_error','neutral_error','boundary_error'])<=2e-5 and m['primary_matrix_error']<=1e-7 and m['upper_elbow_buffer_error']<=.15 and m['max_posed_delta']<=.4
if a['strength']:assert len(a['endpoint_audit'])==20 and max(x['error'] for x in a['endpoint_audit'])<=2e-5
else:assert m['max_posed_delta']==0 and not a['new_paths']
v=dict(verdict='PASS',run_digest=pk.digest(run),observation='Actual saved native compiledleaf-control/endpoint and primary/source invariants passed. Fulltissue movement remains subject to actualanatomical/contact/temporal judgment.',comparison='Actual metrics and authoredendpoint audit versus declared387source and guardrails; no inferred artistic quality.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Technical control only; natural chest/root/volume and AV remainunqualified.'),requirement_outcomes=dict(preservation=dict(status='PASS',observation='Measured originalsource/action/primary/world/true-distal and neutral preservation.'),evidence=dict(status='NOT_TESTED',observation='Technicalintegration doesnotpass anatomy/contact/AV.')))
Bridge(c).record_review(task,step,v);(r/f'results/sikh387/appearance-c{cy}-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n');print(step,'technicalcontrolPASS only',m)
