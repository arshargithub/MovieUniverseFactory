"""Read-only asset verification and exact fresh-open pixel parity receipts."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from entrance189_integrity import BASE, digest

PROTECTED = {
    'natural152-seal-16/natural-hair.blend': '9a204ec2e3951274aeff52aeb554de6b8bc7fa169933e27bfea7073bb62f323f',
    'body168-hip66/adult-body-fit.blend': '1ed613b16dc5b618ae601b9645f6042927e036f60f74314a31fc07e3c5e5c327',
    'wardrobe186-delivery06/riding-corrected.blend': '2dffaf976e1e2e9848f832c149c4578a4a65bbdbaefca67ba1c7e8703db8340e',
    'wardrobe185-seal02/neutral-look-master.blend': '8efd1cfee9684d2b479bc6b24e1e993d0f1a1147ad62f72c72cf82a611f313aa',
}


def compare(a, b):
    if a.shape != b.shape:
        raise ValueError('Image dimensions differ')
    d = abs(a.astype(np.int16) - b.astype(np.int16))
    return {'maximum_channel_difference': int(d.max()), 'mean_channel_difference': float(d.mean()),
            'status': 'PASS' if d.max() <= 1 else 'FAIL'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['reopen', 'render', 'delivery'])
    args = parser.parse_args()
    folder = BASE/'entrance190-perspective29'
    result = json.loads((folder/'result.json').read_text())
    sha = digest(folder/'scene.blend')
    if sha != result['native_sha256']:
        raise ValueError('Selected native changed')
    for name, expected in PROTECTED.items():
        if digest(BASE/name) != expected:
            raise ValueError('Protected original changed: '+name)
    for row in result['cache_checks']:
        path = (BASE/row['path']).resolve()
        if not path.is_relative_to(BASE.resolve()) or digest(path) != row['sha256']:
            raise ValueError('Cache changed')
    receipt = {'native_sha256': sha, 'protected_files': PROTECTED,
               'cache_checks': result['cache_checks'], 'status': 'PASS',
               'limits': 'File and pixel checks do not qualify visual motion, general dynamics or final film.'}
    if args.operation == 'reopen':
        reopened = BASE/'entrance190-reopen31'
        r = json.loads((reopened/'result.json').read_text())
        if r['source_sha256'] != sha or r['cache_checks'] != result['cache_checks']:
            raise ValueError('Reopen source binding differs')
        rows = []
        for f in (361, 457, 552):
            a, b = folder/f'frame-{f:04d}.png', reopened/f'frame-{f:04d}.png'
            row = compare(np.asarray(Image.open(a)), np.asarray(Image.open(b)))
            rows.append({'frame': f, 'original_sha256': digest(a), 'reopen_sha256': digest(b), **row})
        receipt['frames'] = rows
        receipt['status'] = 'PASS' if all(r['status'] == 'PASS' for r in rows) else 'FAIL'
        target = reopened/'pixel-comparison.json'
    elif args.operation == 'render':
        controlled = BASE/'entrance190-render32'
        r = json.loads((controlled/'result.json').read_text())
        if r['source_sha256'] != sha:
            raise ValueError('Render control source differs')
        rows = []
        for f in (362,457,552):
            original = BASE/'entrance190-motion30' if f == 362 else folder
            a,b = original/f'frame-{f:04d}.png', controlled/f'frame-{f:04d}.png'
            rows.append({'frame':f,'original_sha256':digest(a),'control_sha256':digest(b),
                         **compare(np.asarray(Image.open(a)),np.asarray(Image.open(b)))})
        receipt['frames'] = rows
        receipt['status'] = 'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL'
        retained = []
        for p in sorted((BASE/'entrance190-motion30').glob('frame-*.png')):
            with Image.open(p) as im: im.verify()
            retained.append({'name':p.name,'sha256':digest(p)})
        if [p['name'] for p in retained] != [f'frame-{f:04d}.png' for f in range(361,361+len(retained))]:
            raise ValueError('Stopped render is not a complete contiguous prefix')
        receipt['retained_original_frames'] = retained
        receipt['retained_original_source_sha256'] = sha
        receipt['retained_original_handler_sha256'] = digest(BASE/'entrance190-motion30/handler.py')
        target = controlled/'pixel-comparison.json'
    else:
        target = BASE/'entrance190-operating-progress/delivery-integrity.json'
    if target.exists():
        raise ValueError('Preserve prior verification')
    target.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'native_sha256': sha,
                      'protected_files': len(PROTECTED), 'cache_count': len(result['cache_checks'])}))
    if receipt['status'] != 'PASS':
        raise ValueError('Fresh-open pixels differ beyond the declared one-level tolerance')


if __name__ == '__main__':
    main()
