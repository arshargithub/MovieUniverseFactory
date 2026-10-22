"""Apply the actual two-correction approval, retaining the same exhausted task."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import production_allowance as pa
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1]
c=wf.Controller(r,DATABASE); task='sikh335-supporting-appearance'
path='results/sikh335/look01/allowance-341.json'
decision={'path':path,'sha256':pk.file_hash(r/path)}
c.route_request('sikh341-appearance-extension',{
 'text':'Approved: two further corrections for actual native neutral garment then controlled bend.',
 'operations':['code','test','document'],'authority':decision,'amendment_task':task,
 'rationale':'Preserve the exhausted task and all failures; neutral native evidence is a hard prerequisite.'})
s=pa.extend(c,task,'sikh341-appearance-extension',decision,'sikh341-two-approved')
report={k:s[k] for k in ('task','stage','planning_step','cycle','max_corrections')}
p=r/'results/sikh335/look01/allowance-receipt341.json'
if p.exists(): assert json.loads(p.read_text())==report
else: p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
