"""One budgeted export-only recovery; no model download or generation."""
import argparse
import json
from pathlib import Path
import tarfile

import trellis298_cloud as previous
from movie_factory import production_knowledge as pk

c, t, ROOT = previous.c, previous.t, previous.ROOT
OUT = ROOT / 'results/trellis298/cloud-d'
DATA = ROOT / '.runtime/trellis298c/retrieved/evidence/head512'


def packet():
    task = json.loads((ROOT/'results/trellis298/task.json').read_text())
    task.update(id='trellis298-export-only-d', phase='execution',
        intent='Reconstruct preserved512 unsigned source with official remesh path; no generation/encoder/weights; cumulative14USD reservation within15')
    for p in (Path(__file__),ROOT/'scripts/trellis298_export_worker.py',ROOT/'scripts/trellis298_worker.py',
              ROOT/'results/trellis298/STRATEGY.md',DATA/'source.safetensors',DATA/'geometry.json',
              ROOT/'results/trellis298/cloud-c/teardown-verification.json'):
        task['inputs'][str(p.relative_to(ROOT))] = c.sha(p)
    result = pk.task_packet(ROOT, task)
    c.dump(OUT/'execution-task.json',task)
    c.dump(OUT/'packet.json',result)
    (OUT/'packet.md').write_text(pk.packet_markdown(result))
    assert result['dispatch_ready'], result['blockers']
    return result


def configure():
    previous.configure('d')
    c.packet = t.packet = packet


def prepare():
    previous.no_active()
    assert not any(json.loads((ROOT/'results/trellis298/cloud-c/teardown-verification.json').read_text())['remaining'].values())
    t.prepare(reservation_usd=4)
    original = c.LOCAL/'payload.tar.gz'
    original.rename(c.LOCAL/'synthetic-payload.tar.gz')
    repack()


def repack():
    assert not c.state().get('instance')
    packet()
    original = c.LOCAL/'payload.tar.gz'
    manifest = json.loads((ROOT/'results/trellis293/payload-a10-manifest.json').read_text())
    additions = {'scripts/'+n:ROOT/'scripts'/n for n in ('trellis298_export_worker.py','trellis298_worker.py','trellis294_runtime.py')}
    additions.update({'input/source.safetensors':DATA/'source.safetensors','input/geometry.json':DATA/'geometry.json'})
    with tarfile.open(c.LOCAL/'synthetic-payload.tar.gz') as src, tarfile.open(original,'w:gz',compresslevel=1) as dst:
        for member in src.getmembers():
            dst.addfile(member,src.extractfile(member))
        for name,path in additions.items():
            dst.add(path,arcname=name,recursive=False)
            manifest[name] = c.sha(path)
    assert all('.env' not in n and 'token' not in Path(n).name.lower() for n in manifest)
    c.dump(OUT/'payload-manifest.json',manifest)
    c.save('payload_sha256',c.sha(original))
    c.save('controller_sha256',c.sha(Path(__file__)))
    c.dump(OUT/'payload.json',{'sha256':c.sha(original),'bytes':original.stat().st_size,
        'source_sha256':c.sha(DATA/'source.safetensors'),'encoder_upload':False,'credential_upload':False,'new_generation':False})
    print('Export-only payload prepared; no cloud mutations')


def restage():
    assert c.state().get('guard_verified') and not c.state().get('instance')
    previous.no_active()
    verify_frozen()
    c.aws('s3api','put-object','--bucket',c.BUCKET,'--key','input/payload.tar.gz','--body',c.LOCAL/'payload.tar.gz')
    c.save('staged_payload_sha256',c.state()['payload_sha256'])
    print('Updated private staged payload; no instance launched')


def guards():
    verify_frozen()
    previous.no_active()
    previous.continuation_aggregate(4)
    c.guards(amount_usd=4,run_id='trellis298d')
    c.save('staged_payload_sha256',c.state()['payload_sha256'])
    c.dump(OUT/'aggregate-reserved.json',previous.continuation_aggregate())


def launch():
    verify_frozen()
    assert c.state()['staged_payload_sha256'] == c.state()['payload_sha256']
    previous.no_active()
    c.userdata = lambda: previous.ORIGINAL_USERDATA().replace('scripts/trellis293_worker.py','scripts/trellis298_export_worker.py')
    t.launch('us-east-1a',reserved_usd=4,client_token=c.JOB+'-one-worker')


def verify_frozen():
    assert c.sha(Path(__file__)) == c.state()['controller_sha256']
    assert c.sha(c.LOCAL/'payload.tar.gz') == c.state()['payload_sha256']
    manifest = json.loads((OUT/'payload-manifest.json').read_text())
    for name in ('trellis298_export_worker.py','trellis298_worker.py','trellis294_runtime.py'):
        assert c.sha(ROOT/'scripts'/name) == manifest['scripts/'+name]


if __name__ == '__main__':
    configure()
    p=argparse.ArgumentParser()
    p.add_argument('operation',choices=['packet','prepare','repack','restage','guards','launch','status','retrieve','cleanup'])
    a=p.parse_args()
    if a.operation in ('status','retrieve','cleanup'):
        getattr(c,a.operation)()
    elif a.operation=='packet':
        print(pk.packet_markdown(packet()))
    else:
        globals()[a.operation]()
