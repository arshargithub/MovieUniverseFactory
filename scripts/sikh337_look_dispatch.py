"""Admit the appearance proof separately from its serial native execution."""
import json
import sys
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge, BLENDER_BIN
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
out = root / 'results/sikh335/look01'
task = 'sikh335-supporting-appearance'
c = wf.Controller(root, DATABASE)
step = sys.argv[1]
assert step in {'admit', 'save', 'render', 'leader_front', 'leader_reverse', 'crowd_front'}
state = c.state(task)
cycle = state['cycle']
assert cycle in {1, 2, 3, 4} and state['max_corrections'] == 4
if step == 'admit':
    packet = c.packet(task)
    verdict = pk.read_json(root, f'results/sikh335/look01/challenge-verdict-c{cycle}.json')
    verdict['input_digest'] = packet['planning_input_digest']
    c.submit(task, packet['actor'], packet['ticket'], verdict, f'sikh337-look-challenge-c{cycle}')
    print(json.dumps({k: c.state(task)[k] for k in ('stage', 'cycle', 'max_corrections')}))
else:
    parent_path = ('results/sikh335/motion01/save-run-c5.json' if step == 'save'
                   else f'results/sikh335/look01/save-run-c{cycle}.json')
    parent = pk.read_json(root, parent_path)['artifacts']['native']
    recipe = next(s['native_recipe'] for s in state['planning_artifacts']['STRATEGIZING']['steps'] if s['id'] == step)
    destination = out / (step + f'-run-c{cycle}.json')
    if destination.exists():
        raise RuntimeError('Preserve existing run; do not overwrite/retry blindly')
    run = Bridge(c).dispatch(task, step, f'sikh337-look-c{cycle}-' + step, parent=parent,
                             blender_bin=BLENDER_BIN, timeout=600, recipe=recipe)
    destination.write_text(json.dumps(run, indent=2) + '\n')
    print(json.dumps({'id':run['id'], 'status':run['status'], 'error':run.get('error')}))
    if run['status'] != 'RETURNED':
        raise SystemExit(2)
