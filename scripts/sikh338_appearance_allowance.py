"""Apply the exact Director-approved appearance extension; no native dispatch."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import production_allowance as pa
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
c = wf.Controller(root, DATABASE)
task = 'sikh335-supporting-appearance'
path = 'results/sikh335/look01/allowance-338.json'
decision = {'path': path, 'sha256': pk.file_hash(root / path)}
route = c.route_request('sikh338-appearance-extension', {
    'text': 'Approved: four further appearance corrections, starting with the collision-supported cloth test, then costume, headwear, face and saddle checks together.',
    'operations': ['code', 'test', 'document'], 'authority': decision,
    'amendment_task': task,
    'rationale': 'Exact administrative extension; retain the task, history and original production scope. Fresh staged planning required before native work.'})
print(json.dumps(route), flush=True)
state = pa.extend(c, task, 'sikh338-appearance-extension', decision,
                  'sikh338-appearance-four-approved')
report = {k: state[k] for k in ('task', 'stage', 'planning_step', 'cycle', 'max_corrections')}
report.update(native_dispatch=False, appearance_pass=False)
out = root / 'results/sikh335/look01/allowance-receipt338.json'
if out.exists():
    assert json.loads(out.read_text()) == report
else:
    out.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
