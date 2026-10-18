"""One private actor inference session, reusing295 cumulative budget and guard."""
import argparse
import io
import json
from pathlib import Path
import subprocess
import tarfile

import trellis295_cloud as prior
from movie_factory import production_knowledge as pk
from movie_factory.trellis_adapter.patch import adapted_sources
from movie_factory.budget import BudgetLedger

c = prior.c
t = prior.t
ROOT = c.ROOT
OUT = ROOT / 'results/trellis298'
BASE_RECORD = OUT
ATTEMPT = 'a'
ORIGINAL_USERDATA = c.userdata


def continuation_ledger():
    return BudgetLedger(ROOT / '.runtime/trellis298-continuation/budget.jsonl',
        campaign_limit=9, scope_limits={'qualification': 9},
        stage_limits={'gpu_session': (4, 1)}, request_limit=2, request_ceiling_usd=4)


def continuation_aggregate(add=0):
    paths = ['results/trellis293/teardown-verification.json',
             'results/trellis294/teardown-verification.json',
             'results/trellis295/cloud-a/teardown-verification.json',
             'results/trellis298/teardown-verification.json',
             'results/trellis298/cloud-b/teardown-verification.json']
    for path in paths:
        record = json.loads((ROOT / path).read_text())
        if any(record['remaining'].values()):
            raise RuntimeError('Closed-resource liability cannot be reconciled while resources remain')
    new = continuation_ledger().summary()
    total = 6 + new['committed_usd'] + add
    if total > 15 + 1e-9:
        raise RuntimeError('Original USD15 ceiling exceeded')
    return {'effective_ceiling_usd': 15, 'conditional_extra_usd_activated': 0,
            'closed_liability_bound_usd': 6, 'actual_total_billed_usd': None,
            'raw_prior_holds_preserved_not_invoice': True, 'new': new,
            'admission_total_usd': total, 'basis': 'results/trellis298/STRATEGY.md',
            'teardown_bindings': {p: c.sha(ROOT / p) for p in paths}}


def packet():
    task = json.loads((BASE_RECORD / 'task.json').read_text())
    task.update(id='trellis298-inference-' + ATTEMPT, phase='execution')
    for p in (Path(__file__), ROOT / 'scripts/trellis298_worker.py', BASE_RECORD / 'STRATEGY.md',
              ROOT / '.runtime/trellis298-encoder/manifest.json'):
        task['inputs'][str(p.relative_to(ROOT))] = c.sha(p)
    result = pk.task_packet(ROOT, task)
    c.dump(OUT / 'execution-task.json', task)
    c.dump(OUT / 'packet.json', result)
    (OUT / 'packet.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']:
        raise RuntimeError(result['blockers'])
    return result


def configure(attempt='a'):
    global OUT, ATTEMPT
    assert attempt in ('a', 'b', 'c', 'd')
    ATTEMPT = attempt
    suffix = '' if attempt == 'a' else attempt
    OUT = BASE_RECORD if attempt == 'a' else BASE_RECORD / ('cloud-' + attempt)
    prior.configure('b')
    c.OUT = OUT
    c.LOCAL = ROOT / ('.runtime/trellis298' + suffix)
    c.STATE = c.LOCAL / 'cloud-state.json'
    c.JOB = 'trellis298' + suffix + '-inference'
    c.BUCKET = 'mf-trellis298' + suffix + '-281482331395'
    c.ROLE = 'mf-trellis298' + suffix + '-worker'
    c.GUARD = 'mf-trellis298' + suffix + '-guard'
    c.packet = packet
    t.packet = packet
    if attempt in ('c', 'd'):
        c.ledger = t.ledger = continuation_ledger
        t.aggregate = continuation_aggregate


def no_active():
    prior.no_prior_active()
    rows = t.aws('ec2', 'describe-instances', '--filters', c.j([
        {'Name': 'tag:MovieFactoryJob', 'Values': ['trellis298-inference', 'trellis298b-inference', 'trellis298c-inference', 'trellis298d-inference']},
        {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped', 'shutting-down']}]))
    assert not rows['Reservations']


def prepare():
    no_active()
    t.prepare(reservation_usd=4)
    source = ROOT / '.runtime/trellis298-source'
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == '75fbf0183001ed9876c8dbb35de6b68552ee08bd'
    assert subprocess.check_output(['git', '-C', str(source / 'o-voxel/third_party/eigen'), 'rev-parse', 'HEAD'], text=True).strip() == '21e4582d1739107337a03460c81412981130373e'
    additions = {}
    for name in ('trellis298_worker.py', 'trellis294_runtime.py'):
        additions['scripts/' + name] = ROOT / 'scripts' / name
    for folder in ('trellis2', 'o-voxel'):
        for p in (source / folder).rglob('*'):
            if p.is_file() and not p.is_symlink() and '.git' not in p.parts and p.name != '.git':
                additions['inference/' + str(p.relative_to(source))] = p
    additions['inference/LICENSE'] = source / 'LICENSE'
    additions['input/head.png'] = ROOT / '.runtime/art-direction/series01-sikh295/head-input-v01.png'
    patches = {'inference/' + n: text.encode() for n, text in adapted_sources(ROOT / 'results/sikh288/upstream').items()}
    # The admitted path exports GLB/tensors and never reads PLY. Avoid eagerly
    # importing unused PLY I/O and introducing its GPL dependency into this route.
    init = source / 'o-voxel/o_voxel/__init__.py'
    assert c.sha(init) == 'ca30e1545d11f3e862b7d11b31af6200427c91482f11d8b543982d692cd8588b'
    assert init.read_text().count('    io,\n') == 1
    patches['inference/o-voxel/o_voxel/__init__.py'] = init.read_text().replace('    io,\n', '').encode()
    original = c.LOCAL / 'payload.tar.gz'
    original.rename(c.LOCAL / 'synthetic-payload.tar.gz')
    manifest = json.loads((OUT / 'payload-manifest.json').read_text())
    with tarfile.open(c.LOCAL / 'synthetic-payload.tar.gz') as src, tarfile.open(original, 'w:gz') as dst:
        for member in src.getmembers():
            dst.addfile(member, src.extractfile(member))
        for name, p in sorted(additions.items()):
            if name in patches:
                continue
            dst.add(p, arcname=name, recursive=False)
            manifest[name] = c.sha(p)
        import hashlib
        for name, data in patches.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            dst.addfile(info, io.BytesIO(data))
            manifest[name] = hashlib.sha256(data).hexdigest()
    c.dump(OUT / 'payload-manifest.json', manifest)
    assert all('.env' not in name and 'token' not in Path(name).name.lower() for name in manifest)
    c.save('payload_sha256', c.sha(original))
    # Separate data-only archive: credentials are not included, even indirectly.
    encoder = ROOT / '.runtime/trellis298-encoder'
    record = json.loads((encoder / 'manifest.json').read_text())
    with tarfile.open(c.LOCAL / 'encoder.tar', 'w') as dst:
        for name, info in record['files'].items():
            assert c.sha(encoder / name) == info['sha256']
            dst.add(encoder / name, arcname='encoder/' + name, recursive=False)
        dst.add(encoder / 'manifest.json', arcname='encoder/manifest.json', recursive=False)
    c.save('encoder_sha256', c.sha(c.LOCAL / 'encoder.tar'))
    c.dump(OUT / 'encoder-manifest.json', record)
    c.dump(OUT / 'payload.json', {'sha256': c.sha(original), 'files': len(manifest),
        'bytes': original.stat().st_size, 'encoder_archive_bytes': (c.LOCAL / 'encoder.tar').stat().st_size,
        'credential_upload': False, 'source_input': 'head-input-v01.png'})
    print('Private actor payload prepared; no cloud mutations')


def guards():
    no_active()
    aggregate = continuation_aggregate if ATTEMPT == 'c' else prior.aggregate
    aggregate(4)
    c.guards(amount_usd=4, run_id='trellis298' + ('' if ATTEMPT == 'a' else ATTEMPT))
    c.dump(OUT / 'aggregate-reserved.json', aggregate())
    # Authorized private model material staging, not public redistribution.
    t.aws('s3', 'cp', c.LOCAL / 'encoder.tar', 's3://' + c.BUCKET + '/input/encoder.tar', '--only-show-errors', raw=True)
    c.save('encoder_uploaded', True)


def userdata():
    body = ORIGINAL_USERDATA().replace('scripts/trellis293_worker.py', 'scripts/trellis298_worker.py')
    fetch = '''"$AWS" s3 cp s3://mf-trellis293-281482331395/input/encoder.tar encoder.tar --only-show-errors
echo "ENCODER_HASH  encoder.tar" | sha256sum --check
tar -xf encoder.tar
'''.replace('ENCODER_HASH', c.state()['encoder_sha256'])
    return body.replace('nvidia-smi >', fetch + 'nvidia-smi >')


def launch():
    no_active()
    assert c.state().get('encoder_uploaded')
    c.userdata = userdata
    t.launch('us-east-1a', reserved_usd=4, client_token=c.JOB + '-one-worker')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['prepare', 'guards', 'launch', 'status', 'retrieve', 'cleanup', 'packet'])
    parser.add_argument('--attempt', choices=['a', 'b', 'c'], default='a')
    args = parser.parse_args()
    configure(args.attempt)
    if args.operation in ('status', 'retrieve', 'cleanup'):
        getattr(c, args.operation)()
    else:
        globals()[args.operation]()


if __name__ == '__main__':
    main()
