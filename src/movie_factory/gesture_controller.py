"""Bounded provider-free 3D-06A fixture screen; scoring is a separate stage."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import uuid
from pathlib import Path

from .adapters.blender.runner import run_blender
from .experiment_ledger import Ledger
from .packages import atomic_json, file_digest
from .telemetry import utc_now


def screen(repo: Path, plan_path: Path):
    campaign = json.loads((repo/'feasibility/3d/3d-04/campaign.json').read_text())
    parent = repo/campaign['baseline']['relative_path']
    if file_digest(parent) != campaign['baseline']['sha256']:
        raise ValueError('Accepted native fixture changed')
    plan = json.loads(plan_path.read_text())
    identity = 'screen-'+time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())+'-'+uuid.uuid4().hex[:8]
    output = repo/'runs/3d06a'/identity; output.mkdir(parents=True, exist_ok=False)
    source = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    package = {'experiment_id': '3D-06A', 'stage': 'FIXTURE_SCREEN', 'scored': False,
               'run_id': identity, 'source_commit': source, 'reference_plan_sha256': file_digest(plan_path),
               'baseline_native_sha256': file_digest(parent), 'provider_calls': 0, 'known_api_cost_usd': 0,
               'worktree_clean': not subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout.strip()}
    atomic_json(output/'work-package.json', package)
    ledger = Ledger(repo/'.runtime/experiment-ops.sqlite3')
    context = {'experiment_id': '3D-06A', 'episode_id': 'first', 'phase': 'fixture_screen',
               'job_id': identity, 'job_kind': 'native', 'clock_id': identity, 'run_id': identity,
               'evidence_ref': str(output.relative_to(repo)/'work-package.json')}
    ledger.append({**context, 'event_id': identity+'-start', 'event_type': 'job_started',
                   'utc': utc_now(), 'monotonic_seconds': time.monotonic()})
    try:
        status = run_blender({'mode': 'gesture_screen', 'output_dir': str(output), 'parent_native': str(parent),
            'baseline_sha256': package['baseline_native_sha256'], 'plan': plan,
            'profile': {'name': 'gesture_fixture', 'width': 480, 'height': 360, 'samples': 4, 'device': 'CPU', 'shots': ['shot_A', 'shot_B']}},
            blender_bin='/Applications/Blender.app/Contents/MacOS/Blender', timeout=180)
    except Exception:
        ledger.append({**context, 'event_id': identity+'-end', 'event_type': 'job_completed',
                       'utc': utc_now(), 'monotonic_seconds': time.monotonic(), 'outcome': 'FAILED'})
        raise
    ledger.append({**context, 'event_id': identity+'-end', 'event_type': 'job_completed',
                   'utc': utc_now(), 'monotonic_seconds': time.monotonic(), 'outcome': 'PASSED' if status['ok'] else 'FAILED'})
    print(json.dumps({'run': str(output), 'worker_ok': status['ok'], 'elapsed': status['elapsed'], 'error': status.get('error')}))
    return output, status


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, default=Path('feasibility/3d/3d-06a/reference-plan.json'))
    args = parser.parse_args()
    _, status = screen(Path.cwd(), args.plan)
    raise SystemExit(0 if status['ok'] else 1)
