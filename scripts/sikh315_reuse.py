"""Narrow, evidence-bound reuse of movie10 opening in derivative11 only."""
import json
import shutil
import numpy as np
from PIL import Image
from sikh315_run import BASE, sha


def seed_opening(out):
    assert out == BASE / 'movie-11'
    old = BASE / 'movie-10'
    native = BASE / 'finish-11'
    binding = json.loads((old / 'bindings.json').read_text())
    key = '.runtime/art-direction/series01-sikh315/finish-10/sequence.blend'
    assert sha(BASE / 'finish-10/sequence.blend') == binding[key]
    correction = json.loads((native / 'settling-dilution.json').read_text())
    assert correction['gain_keys'][:2] == [[1, 1], [173, 1]]
    controls = []
    for f in (80, 126, 150):
        a = old / 'frames' / f'frame-{f:04d}.png'
        b = native / a.name
        with Image.open(a) as ia, Image.open(b) as ib:
            assert ia.size == ib.size == (720, 1280)
            delta = int(np.max(abs(np.asarray(ia).astype(np.int16) - np.asarray(ib).astype(np.int16))))
        controls.append({'frame': f, 'maximum_channel_difference': delta,
                         'source_sha256': sha(a), 'new_control_sha256': sha(b)})
    assert all(r['maximum_channel_difference'] <= 1 for r in controls)
    frames = out / 'frames'; frames.mkdir(exist_ok=False)
    copied = []
    for f in range(1, 169):
        p = old / 'frames' / f'frame-{f:04d}.png'
        with Image.open(p) as im:
            im.load(); assert im.size == (720, 1280)
        digest = sha(p); shutil.copy2(p, frames / p.name)
        assert sha(frames / p.name) == digest
        copied.append({'frame': f, 'sha256': digest})
    (out / 'opening-reuse.json').write_text(json.dumps({
        'source_movie': str(old), 'source_native_sha256': binding[key],
        'target_native_sha256': sha(native / 'sequence.blend'),
        'basis': 'Reviewed derivative11 changes only stop-cloud material density; linear gain is exactly1 through173. No geometry/motion/camera change.',
        'controls': controls, 'threshold': 1, 'frames': copied,
        'limits': 'These168 frames are reused, not newly rendered. Three matched controls support scoped compatibility, not universal renderer determinism.'
    }, indent=2))
    return 169
