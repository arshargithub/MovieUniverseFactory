"""Read-only asset checks; writes a new, bounded verification record."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01/cleanup-portable-01'


def main():
    result = json.loads((PACKAGE / 'result.json').read_text())
    assert result['source_preserved']
    assert result['geometry_before'] == result['geometry_after']
    comparisons = []
    for first, second in [('procedural', 'baked'), ('baked', 'roundtrip')]:
        for view in ['front', 'left', 'right']:
            a = np.asarray(Image.open(PACKAGE / f'{first}-{view}.png').convert('RGB'), dtype=float)
            b = np.asarray(Image.open(PACKAGE / f'{second}-{view}.png').convert('RGB'), dtype=float)
            assert a.shape == b.shape == (640, 512, 3)
            difference = np.abs(a-b)
            comparisons.append({'first': first, 'second': second, 'view': view,
                                'rgb_mae_0_255': float(difference.mean()),
                                'max_channel_difference': float(difference.max())})
    artifacts = []
    for path in sorted(PACKAGE.iterdir()):
        if path.name == 'verification.json':
            continue
        assert path.is_file() and not path.is_symlink()
        artifacts.append({'path': path.name, 'bytes': path.stat().st_size,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    output = {'status': 'YELLOW', 'scope': 'Cleaned static head portability; not character completion',
              'comparisons': comparisons, 'artifacts': artifacts,
              'geometry_preserved': True, 'source_preserved': True,
              'acceptance': 'Original v02 provisional likeness approved; cleaned derivative not separately Director-approved',
              'limits': ['Three static views only', 'GLB plus material-sidecar, not bare GLB parity',
                         'Projected hair/scarf and painted shadows remain', 'No blink, rig or motion qualification',
                         'Local SSD package, not off-machine backup']}
    with (PACKAGE / 'verification.json').open('x') as stream:
        json.dump(output, stream, indent=2)
    print(json.dumps({'artifacts': len(artifacts), 'bytes': sum(a['bytes'] for a in artifacts),
                      'comparisons': comparisons}, indent=2))


if __name__ == '__main__':
    main()
