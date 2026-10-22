"""Apply the explicit five-cycle extension without resetting task history."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import production_allowance as pa
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1]
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
path='results/sikh335/look01/allowance-340.json'
decision={'path':path,'sha256':pk.file_hash(r/path)}
c.route_request('sikh340-appearance-extension',{
 'text':'Director approves five more appearance corrections,12 to17, no new spending.',
 'operations':['code','test','document'],'authority':decision,'amendment_task':task,
 'rationale':'Same exhausted task. Preserve failed evidence and require fresh staged planning.'})
s=pa.extend(c,task,'sikh340-appearance-extension',decision,'sikh340-appearance-five-approved')
report={k:s[k] for k in ('task','stage','planning_step','cycle','max_corrections')}
dest=r/'results/sikh335/look01/allowance-receipt340.json'
if dest.exists():assert json.loads(dest.read_text())==report
else:dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
