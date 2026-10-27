"""Actual source controls: usable transport, known rejected anatomy."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as rt
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==178
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
for step in ['front','side']:
 run=pk.read_json(r,f'results/sikh386/appearance-c178-{step}-run.json')
 v=dict(verdict='FAIL',run_digest=pk.digest(run),observation='Original80source chest has a broad oval/shelf ending abruptly above the forelegs; in339side the underside projects forward with no believable pectoral-to-root continuation. Controls are usable, anatomy is rejected.',comparison='Actual283/333/339front and side inspected against physical frontpectorals/studrear: real chest mass attaches and narrows into limbs; this source has a continuous artificial bib. No new candidate is being accepted.',open_defects=['Inherited chest shelf/bib and unsupported lower mass'],evidence=run['artifacts'],cycle_disposition=dict(category='causal_control_only',observation='Read-only control establishes actual negative form and framing; no anatomyPASS.'))
 Bridge(c).record_review(task,step,v);(r/f'results/sikh386/appearance-c178-{step}-review.json').write_text(json.dumps(v,indent=2)+'\n')
ev={p:bind(p) for p in ['results/sikh386/appearance-c178-source-review.json','results/sikh386/appearance-c178-front-review.json','results/sikh386/appearance-c178-side-review.json','results/sikh386/RECOVERY178.md']}
packet=c.retrospective_packet(task);pending=packet['pending_effects386'];keys=set(x['key'] for x in pending.values())
oid='sikh386-c178-source-control-complete'
c.retrospective(task,'outcome',dict(attempt=oid,role='diagnostic',origin='actual_source_control',observations=[dict(requirement=k,status='PASS' if k=='__worker__' else 'UNKNOWN',observation='Actual source183sample native export/invariants succeeded. Source front/side controls expose inherited chest failure; no positive target, full image matrix or temporal qualification yet.') for k in keys],evidence=ev),oid)
for aid,v in pending.items():
 c.retrospective(task,'evaluate',dict(key=v['key'],evaluation=dict(admission_event=aid,result='effective' if v['key']=='__worker__' else 'inconclusive',outcome_event=oid,observation='Source integration qualified only; other creative findings await constructed target. Do not close those with diagnostic transport success.',evidence=ev)),aid+'-actual-effect')
close=dict(cycle=178,max=226,disposition='causal_control_only',art_candidates=0,source='actual original80 finite183sample cage/bone export',known_failure='Source shelf/bib retained as negative control.',not_run=['oblique source','whole source','positive target','moving-form proof'],early_stop='Known source anatomy failed first revealing controls; additional source renders cannot repair or reverse failure. Proceed to new positive target, not polish of this source.',next='179connected supported thorax/pectoral volume plus moving proximal-limb envelope; worst views first.')
(r/'results/sikh386/CYCLE178_CLOSEOUT.json').write_text(json.dumps(close,indent=2)+'\n');print(close)
