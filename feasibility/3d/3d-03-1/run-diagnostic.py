"""Run the fixed diagnostic from the project .venv; never calls a provider."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
if Path(sys.prefix).resolve()!=ROOT/'.venv':
    raise SystemExit('Use this project\'s .venv/bin/python')
from movie_factory.adapters.blender.runner import run_blender

p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
a=p.parse_args()
output=(ROOT/a.output).resolve()
if not output.is_relative_to(ROOT/'runs/3d031-diagnostic'):
    raise SystemExit('Diagnostic output must be below runs/3d031-diagnostic')
output.mkdir(parents=True,exist_ok=False)
base=ROOT/'runs/3d03/character-v1-20260910T201716Z-dd48f85a'
plan=json.loads((base/'initial/build/job.json').read_text())['plan']
source_files=['src/movie_factory/adapters/blender/worker.py','src/movie_factory/adapters/blender/character_diagnostic.py','src/movie_factory/adapters/blender/runner.py','feasibility/3d/3d-03-1/run-diagnostic.py']
binding={'status':'DIAGNOSTIC_SOURCE_FILES_SNAPSHOTTED_BEFORE_DISPATCH',
         'base_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip(),
         'files':[],'provider_calls':0}
for rel in source_files:
    data=(ROOT/rel).read_bytes()
    target=output/'execution-source'/rel
    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
    binding['files'].append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
(output/'execution-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
status=run_blender({'mode':'character_bake_diagnostic','output_dir':str(output),'parent_native':str(base/'initial/build/scene.blend'),'plan':plan,'profile':{},'seed':303},blender_bin='/Applications/Blender.app/Contents/MacOS/Blender',timeout=300)
print(json.dumps({'ok':status['ok'],'output':str(output),'error':status.get('error'),'provider_calls':0}))
raise SystemExit(0 if status['ok'] else 1)
