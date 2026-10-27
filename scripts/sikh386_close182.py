"""Actual spatial-reference qualification; never passes the production horse."""
from pathlib import Path
import json
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==182
bind=lambda f:dict(path=f,sha256=pk.file_hash(r/f));ev={}
for step in ['front','side','oblique']:
 run=pk.read_json(r,f'results/sikh386/appearance-c182-{step}-run.json')
 v=dict(verdict='PASS',run_digest=pk.digest(run),observation='Actual neutral3Dguide shows continuous chest/shoulder volume joining distinct proximal forelegs; no separate lower sphere, cape or skinweb in the claimed junction. Qualified as gross spatialguide only.',comparison='Front/side/oblique compared to UMNfront and Cavalorear/Friesian/studrear junction features. Reference is lowresolution and has different head/stance/proportions; not filmlook or exact breed/identity. Originalcurve overlays abovehead/atback are unclaimed reference-scene clutter, not guide surface.',open_defects=[],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Reference qualification only; no repaired originalhorse, motion or finalappearancePASS.'),requirement_outcomes={k:dict(status='NOT_TESTED',observation='Static reference available for grossshape guidance; originalhorse anatomy and moving/contact proof still unqualified.') for k in ['form','interfaces','whole_look']})
 Bridge(c).record_review(task,step,v);f=f'results/sikh386/appearance-c182-{step}-review.json';(r/f).write_text(json.dumps(v,indent=2)+'\n');ev[f]=bind(f)
close=dict(cycle=182,max=226,disposition='causal_control_only',art_candidates=0,source='CC0LyndonDaniels3697vertexbodyOBJ',qualified='Gross3Dspatial chest/root/neck anatomyguide only, actualthreeviews inspected',excluded=['headidentity/style/texture','thirdparty rig/action','finishedfilmhorse','registration/fitting/deformation','fullspeedAV'],limits=['Lowreference resolution','Different neutral head/stance/proportions','Unclaimed oldscene curveclutter'],next='183register guide to local anatomical landmarks; fit only previoushorse bounded chest/root region and carry correction with actualsourceone-ring deformation; native neutral/raisedproof before fullmatrix.')
f='results/sikh386/CYCLE182_CLOSEOUT.json';(r/f).write_text(json.dumps(close,indent=2)+'\n');ev[f]=bind(f)
pending=c.retrospective_packet(task)['pending_effects386'];keys=set(x['key'] for x in pending.values());oid='sikh386-c182-spatial-guide-qualified-only'
c.retrospective(task,'outcome',dict(attempt=oid,role='diagnostic',origin='actual_reference_goal_control',observations=[dict(requirement=k,status='UNKNOWN',observation='Reference guide is useful; actual oldhorse positiveform/fitting/deformation remains untested. Do not close artistic finding from reference success.') for k in keys],evidence=ev),oid)
for aid,x in pending.items():
 c.retrospective(task,'evaluate',dict(key=x['key'],evaluation=dict(admission_event=aid,result='inconclusive',outcome_event=oid,observation='Prerequisite reference established, originalhorse outcome still unresolved; no artPASS.',evidence=ev)),aid+'-actual-effect')
print('Spatial guide qualified only;44sharedcorrections remain')
