"""Queue the explicitly approved amendment at a native-job-free boundary.

No heavy work, engine edits or production dispatch. Retain the same appearance
task and its audited reference repair. The active motion task is untouched.
"""
import json
import time
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import production_allowance as pa
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
c = wf.Controller(root, DATABASE)
task = 'sikh335-supporting-appearance'
path = 'results/sikh335/look01/allowance-337.json'
decision = {'path': path, 'sha256': pk.file_hash(root / path)}
c.route_request('sikh337-appearance-extension', {
    'text': 'Director approves four additional corrections for the existing appearance task.',
    'operations': ['code', 'test', 'document'], 'authority': decision,
    'amendment_task': task,
    'rationale': 'Administrative amendment at a native-job-free boundary. No task reset, engine edit or production launch; full planning follows.'})
while True:
    try:
        state = pa.extend(c, task, 'sikh337-appearance-extension', decision,
                          'sikh337-appearance-four-approved')
        break
    except wf.Blocked as error:
        if str(error) != 'JOB_STILL_ACTIVE':
            raise
        time.sleep(1)
report = {key: state[key] for key in ('task', 'stage', 'planning_step', 'cycle', 'max_corrections')}
report.update(native_dispatch=False, appearance_pass=False)
(root / 'results/sikh335/look01/allowance-receipt337.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
