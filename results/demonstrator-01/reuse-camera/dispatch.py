"""Fixed local CLI; caller supplies a validated structured request, never code."""
import sys,json,hashlib
from movie_factory.experiment_ledger import Ledger
from pathlib import Path
from movie_factory.adapters.blender.runner import run_blender
from movie_factory.adapters.blender.demo_reuse import validate
job=json.loads(Path(sys.argv[1]).read_text());validate(job)
freeze=Path('results/demonstrator-01/reuse-camera/FREEZE.json')
if freeze.exists():
 for row in json.loads(freeze.read_text())['implementation_files']:
  assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'], 'Post-freeze implementation changed'
events=Ledger(Path('.runtime/experiment-ops.sqlite3')).events()
used=sum(e.get('duration_seconds',0) or 0 for e in events if e['experiment_id']=='DEMONSTRATOR-01' and e['episode_id'] in {'reuse-01','reuse-02','reuse-camera'} and e['event_type']=='job_completed' and e.get('job_kind')=='native')
# Runner receipts are an independent conservative native-process measure.
used=max(used,sum(json.loads(p.read_text()).get('elapsed',0) for p in Path('runs/demonstrator-01/reuse-01').glob('*/runner-status.json')))
remaining=5400-used
if remaining<30:raise RuntimeError('Native budget exhausted')
r=run_blender(job,blender_bin='/Applications/Blender.app/Contents/MacOS/Blender',timeout=min(1800,remaining-5))
print(json.dumps({'ok':r['ok'],'elapsed':r['elapsed'],'error':r.get('error')}))
raise SystemExit(0 if r['ok'] else 1)
