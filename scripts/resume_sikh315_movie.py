"""Recover the interrupted, hash-bound movie09 without overwriting evidence."""
import json
import os
import subprocess
import time
from pathlib import Path
from PIL import Image
from sikh315_run import ROOT, BASE, sha, validate_job


def main():
    out = BASE / 'movie-09'
    bindings = json.loads((out / 'bindings.json').read_text())
    def check_bindings():
        changed = [name for name, digest in bindings.items() if sha(ROOT / name) != digest]
        if changed:
            raise ValueError(f'Changed original inputs: {changed}')
    check_bindings()
    existing = sorted((out / 'frames').glob('frame-*.png'))
    preserved = {}
    for path in existing:
        with Image.open(path) as im:
            im.load()
            if im.size != (720, 1280):
                raise ValueError(f'Invalid completed frame: {path}')
        preserved[path.name] = sha(path)
    recovery = out / ('recovery-' + time.strftime('%Y%m%dT%H%M%S'))
    recovery.mkdir(exist_ok=False)
    (recovery / 'start.json').write_text(json.dumps({
        'reason': 'Original supervisor exited138; no worker remains; original receipt absent',
        'preserved_frames': preserved, 'bindings': bindings,
        'recovery_handler_sha': sha(Path(__file__)),
    }, indent=2))
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL') if k in os.environ}
    for key, folder in (('BLENDER_USER_CONFIG', 'config'), ('BLENDER_USER_SCRIPTS', 'scripts'), ('BLENDER_USER_DATAFILES', 'data')):
        env[key] = str(out / 'sandbox' / folder)
    receipts = []
    started = time.monotonic()
    for start in range(1, 697, 24):
        end = min(696, start + 23)
        paths = [out / 'frames' / f'frame-{f:04d}.png' for f in range(start, end + 1)]
        if all(p.exists() for p in paths):
            continue
        if any(p.exists() for p in paths):
            raise ValueError('Partial chunk requires separately reviewed recovery, never overwrite')
        check_bindings()
        job = out / 'chunks' / f'{start:04d}' / 'job.json'
        validate_job(json.loads(job.read_text()))
        tick = time.monotonic()
        with (recovery / f'chunk-{start:04d}.log').open('x') as log:
            result = subprocess.run([
                '/Applications/Blender.app/Contents/MacOS/Blender', '-b', '--factory-startup',
                '--disable-autoexec', '--offline-mode', '--python-exit-code', '7', '--python',
                str(ROOT / 'scripts/sikh315_native.py'), '--', str(job),
            ], env=env, stdout=log, stderr=subprocess.STDOUT)
        receipts.append({'start': start, 'end': end, 'returncode': result.returncode,
                         'seconds': time.monotonic() - tick})
        (recovery / 'processes.json').write_text(json.dumps(receipts, indent=2))
        print(json.dumps(receipts[-1]), flush=True)
        if result.returncode:
            raise RuntimeError(f'Chunk failed: {start}')
    check_bindings()
    assert all(sha(out / 'frames' / name) == digest for name, digest in preserved.items())
    frames = sorted((out / 'frames').glob('frame-*.png'))
    assert len(frames) == 696
    receipt = {'returncode': 0, 'recovery_seconds': time.monotonic() - started,
               'recovery': str(recovery.relative_to(ROOT)), 'frames': 696,
               'original_interrupted': True, 'preserved_frames_unchanged': True}
    target = ROOT / 'results/sikh315/movie-9/receipt.json'
    with target.open('x') as f:
        json.dump(receipt, f, indent=2)


if __name__ == '__main__':
    main()
