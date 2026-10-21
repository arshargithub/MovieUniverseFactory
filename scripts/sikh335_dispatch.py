"""Canonical dispatch for the already-authored335 ownership proof."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge, BLENDER_BIN
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
out = root / 'results/sikh335'
c = wf.Controller(root, DATABASE)
task = 'sikh335-control-ownership'
p = c.packet(task)
verdict = json.loads((out / 'challenge-verdict.json').read_text())
verdict['input_digest'] = p['planning_input_digest']
c.submit(task, p['actor'], p['ticket'], verdict, 'sikh335-challenge-admit')
def bind(path): return {'path': path, 'sha256': pk.file_hash(root / path)}
run = Bridge(c).dispatch(task, 'inspect', 'sikh335-ownership',
    parent=bind('.runtime/art-direction/series01-sikh320/build-10/sequence.blend'),
    blender_bin=BLENDER_BIN, timeout=300, recipe=bind('results/sikh335/inspect-recipe.json'))
(out / 'inspect-run.json').write_text(json.dumps(run, indent=2) + '\n')
print(json.dumps(run, indent=2))
