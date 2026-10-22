"""Close inspected failure evidence and apply the separately confirmed extension."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import production_allowance as pa
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
observations={
 'leader_front':'Slab-like vertical channels and a hard chest ledge replace cloth folds. Crown is helmet-like, eye registration reads as inserts, beard is pointed and skin plastic.',
 'leader_reverse':'Anatomical smooth back, projecting collar point and rear crown seam remain. Saddle contact is not established.',
 'render':'Both actual-shot frames retain schematic clothing and mannequin face/headwear. Improved crown seam does not establish same-film coherence.',
 'crowd_front':'Target is partially occluded by a foreground warrior/shield. Visible hard chest transition and abrupt cheek/beard boundary fail; full garment coverage is NOT_RUN.'}
s=c.state(task)
if s['stage']=='EXECUTING' and s['cycle']==8:
    for step,observation in observations.items():
        dest=out/f'{step}-visual-review-c8.json'
        if dest.exists():continue
        run=pk.read_json(r,f'results/sikh335/look01/{step}-run-c8.json')
        v={'verdict':'FAIL','run_digest':pk.digest(run),'evidence':run['artifacts'],
           'observation':observation,
           'comparison':'Actual returned images inspected against accepted Pashtun quality and whole-character requirements. Numeric stability is not cloth construction or artistic acceptance.',
           'open_defects':['garment-form','same-film-appearance','face-headwear','incomplete-interface-proof']}
        Bridge(c).record_review(task,step,v)
        dest.write_text(json.dumps(v,indent=2)+'\n')
    d=s['direction']
    c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
               'C8 actual images reject panel-depth transfer, headwear and face. Four corrections exhausted; replace garment construction, retain all failure evidence.',
               'sikh339-look-c8-exhausted')
path='results/sikh335/look01/allowance-339.json';decision={'path':path,'sha256':pk.file_hash(r/path)}
c.route_request('sikh339-appearance-extension',{
 'text':'Director separately confirms four additional appearance corrections from eight to twelve, no new spending.',
 'operations':['code','test','document'],'authority':decision,'amendment_task':task,
 'rationale':'Exact administrative amendment; same task and original scope. Fresh staged planning required.'})
s=pa.extend(c,task,'sikh339-appearance-extension',decision,'sikh339-appearance-four-approved')
report={k:s[k] for k in ('task','stage','planning_step','cycle','max_corrections')}
dest=out/'allowance-receipt339.json'
if dest.exists():assert json.loads(dest.read_text())==report
else:dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
