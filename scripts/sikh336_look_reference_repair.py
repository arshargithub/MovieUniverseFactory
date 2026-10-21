"""Correct the rejected reference metadata without resetting its exhausted task.

No native dispatch and no allowance amendment. Existing revise preserves counters;
the later explicit four-correction extension starts the first new correction.
"""
import copy
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import expert_planning as ep, review_control as rc
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
out = root / 'results/sikh335/look01'
c = wf.Controller(root, DATABASE)
task = 'sikh335-supporting-appearance'

def bind(path):
    return {'path': path, 'sha256': pk.file_hash(root / path)}

decision = bind('results/sikh335/additional-allowance-336.json')
c.route_request('sikh336-look-reference-repair', {
    'text': 'Correct the already-rejected appearance reference contract within the approved continuation.',
    'operations': ['code', 'test', 'document'], 'authority': decision,
    'amendment_task': task,
    'rationale': 'Administrative source-role repair, no native work, new creative direction, allowance reset or old-plan admission.'})
before = c.state(task)
assert before['stage'] == 'REPLAN_REQUIRED' and before['cycle'] == before['max_corrections'] == 0
brief = copy.deepcopy(before['brief'] if before.get('brief') else
                      before['planning_artifacts']['STRATEGIZING']['brief'])
# Every existing byte binding was inspected and remains unchanged. No rehash.
for binding in brief['source_bindings'].values():
    rc.binding(root, binding)
replacement = pk.read_json(root, 'results/sikh335/look01/reference-contract-draft336.json')['reference']
old = next(r for r in brief['references'] if r['id'] == 'accepted_film')
assert old['binding'] == replacement['binding']
assert old['role'] == 'faithful_motion' and replacement['role'] == 'accepted_quality'
brief['references'] = [replacement if r['id'] == 'accepted_film' else r for r in brief['references']]
brief['reference_plan']['accepted_film'] = {
    'reference_digest': pk.digest(replacement),
    'application': replacement['aspects'][0]['instruction']}
brief['expert_plan']['challenge']['plan_digest'] = ep.plan_digest(brief)
wf.validate_brief(root, brief, 'production', 'local_native')
reason = ('Repair the documented clerical role error using original same-film Director authority: '
          'the accepted PNG is an appearance-quality comparator, not a14–19s motion source. '
          'Original motion reference, assets, intent, task, failure history and exhausted counters stay unchanged. '
          'This records a corrected input contract only; full regrounding/challenge follows the approved extension.')
after = c.revise(task, brief, decision, reason, 'sikh336-look-reference-reconciled')
assert after['stage'] == 'REPLAN_REQUIRED' and after['cycle'] == after['max_corrections'] == 0
report = {'task': task, 'before_reference': old, 'after_reference': replacement,
          'cycle': 0, 'max_corrections': 0, 'stage': after['stage'],
          'native_dispatch': False, 'appearance_pass': False,
          'scope': reason}
(out / 'reference-repair-receipt336.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('task', 'cycle', 'max_corrections', 'stage', 'native_dispatch')}))
