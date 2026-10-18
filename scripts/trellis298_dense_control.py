"""Offline, fixed grid-cluster control of preserved dense source geometry.

This bypasses the cloud simplifier, never regenerates the character, and writes
an untextured diagnostic PLY. It is not retopology or a production-asset pass.
"""
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.runtime/trellis298c/retrieved/evidence/head512/source.safetensors'
OUT = ROOT / '.runtime/art-direction/series01-trellis298/dense-control'
RESOLUTION = 192


def read_arrays():
    with SOURCE.open('rb') as f:
        size = struct.unpack('<Q', f.read(8))[0]
        assert size < 65536
        header = json.loads(f.read(size))
    arrays = {}
    for name, dtype in (('vertices', 'F32'), ('faces', 'I32')):
        spec = header[name]
        assert spec['dtype'] == dtype and spec['shape'][1] == 3
        arrays[name] = np.memmap(SOURCE, dtype={'F32': '<f4', 'I32': '<i4'}[dtype],
            mode='r', offset=8+size+spec['data_offsets'][0], shape=tuple(spec['shape']))
    return arrays


def cluster(vertices, faces, resolution=RESOLUTION):
    assert resolution == RESOLUTION
    assert np.isfinite(vertices).all()
    q = np.floor((vertices + .5)*resolution).astype(np.int64)
    assert q.min() >= 0 and q.max() < resolution
    keys = q[:, 0] + resolution*(q[:, 1] + resolution*q[:, 2])
    del q
    unique, inverse = np.unique(keys, return_inverse=True)
    del keys
    count = np.bincount(inverse)
    points = np.column_stack([np.bincount(inverse, weights=vertices[:, k])/count for k in range(3)]).astype('<f4')
    remapped = inverse[faces].astype(np.uint64)
    del inverse
    keep = (remapped[:, 0] != remapped[:, 1]) & (remapped[:, 0] != remapped[:, 2]) & (remapped[:, 1] != remapped[:, 2])
    remapped = remapped[keep]
    ordered = np.sort(remapped, axis=1)
    n = len(points)
    assert n**3 < 2**64
    keys = ordered[:, 0] + n*(ordered[:, 1] + n*ordered[:, 2])
    del ordered
    _, first = np.unique(keys, return_index=True)
    result = remapped[first].astype('<i4')
    return points, result


def main(packet_only=False):
    from movie_factory import production_knowledge as pk
    task = json.loads((ROOT / 'results/trellis298/task.json').read_text())
    task.update(id='trellis298-dense-source-control', phase='execution')
    for path in (Path(__file__), SOURCE, ROOT / 'results/trellis298/STRATEGY.md'):
        task['inputs'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    packet = pk.task_packet(ROOT, task)
    (ROOT / 'results/trellis298/dense-source-packet.json').write_text(json.dumps(packet, indent=2))
    assert packet['dispatch_ready'], packet['blockers']
    if packet_only:
        print(pk.packet_markdown(packet))
        return
    arrays = read_arrays()
    points, faces = cluster(arrays['vertices'], arrays['faces'])
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'source-cluster.ply'
    with path.open('wb') as f:
        f.write(('ply\nformat binary_little_endian 1.0\nelement vertex %d\nproperty float x\nproperty float y\nproperty float z\nelement face %d\nproperty list uchar int vertex_indices\nend_header\n' % (len(points), len(faces))).encode())
        f.write(points.tobytes())
        packed = np.empty(len(faces), dtype=[('count', 'u1'), ('indices', '<i4', (3,))])
        packed['count'] = 3
        packed['indices'] = faces
        f.write(packed.tobytes())
    record = {'resolution': RESOLUTION, 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'vertices': len(points), 'faces': len(faces), 'ply_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'production_ready': False, 'limits': 'Untextured diagnostic grid cluster, no production topology or material claim'}
    (OUT / 'control.json').write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet-only', action='store_true')
    main(parser.parse_args().packet_only)
