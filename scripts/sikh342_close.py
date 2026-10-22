"""Record failed qualification and exact controller state; never admit media."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk, production_workflow as wf
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
out = root / 'results/sikh335/closure342'
out.mkdir(exist_ok=True)

def write(name, value):
    path = out / name
    text = json.dumps(value, indent=2) + '\n'
    if path.exists():
        assert path.read_text() == text
    else:
        path.write_text(text)

controller = wf.Controller(root, DATABASE)
states = {}
for task in ('sikh335-supporting-appearance', 'sikh335-continuous-performance'):
    state = controller.state(task)
    states[task] = {k: state.get(k) for k in ('stage', 'cycle', 'max_corrections', 'planning_step')}
    assert state['stage'] == 'REPLAN_REQUIRED'
write('controller-state.json', states)

packet = pk.read_json(root, '.runtime/knowledge-pilot213/sikh342-current.json')
paths = ['results/sikh335/REASSESSMENT_342.md',
         'results/sikh335/look01/rejection-c29.json',
         'results/sikh335/motion01/challenge-verdict-c10.json']
evidence = [{'path': p, 'sha256': pk.file_hash(root / p)} for p in paths]
checks = []
for obligation in packet['obligations']:
    checks.append({
        'id': obligation['id'], 'kind': obligation['check_kind'],
        'status': 'FAIL' if obligation['id'] in {'construction_interfaces', 'visual_gate'} else 'NOT_RUN',
        'action_taken': 'Preserved scoped prerequisites and failures; withheld integrated production handoff at exhausted authority.',
        'observation': 'This closure does not establish complete obligation satisfaction. Appearance29 has known frame-visible failures; motion10 was rejected before native dispatch. See exact scoped evidence, not an inherited PASS.',
        'evidence': evidence,
    })
write('knowledge-review-v2.json', {
    'packet_digest': packet['packet_digest'],
    'scope': 'Blocked production closure, not media admission or global knowledge calibration.',
    'checks': checks,
    'hypotheses': [{'prediction': 'Local proxy-interface patches may expose adjacent failures rather than qualify a complete actor.',
                    'result': 'unresolved', 'observation': 'Repeated cuff/neck/waist and same-film failures persist in29.',
                    'response': 'Withhold propagation and propose coherent complete-actor proof under renewed authority.', 'evidence': evidence}],
    'adjacent_regressions': {'status': 'FAIL', 'observation': 'Standing cuff and whole-actor appearance remain rejected.', 'evidence': evidence},
    'stopping_reason': 'Both authorized correction limits exhausted; renewed authority and method reassessment required. No known-failure waiver.',
})
print(json.dumps(states))
