"""301 export controls. Preparation is read-only AWS/local-only; root dispatch separate."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import zipfile

import trellis298_cloud as previous
import trellis301_prepare as local
from movie_factory import production_knowledge as pk
from movie_factory.budget import BudgetLedger

c, t, ROOT = previous.c, previous.t, previous.ROOT
OUT = ROOT / 'results/trellis301/cloud-export'
DATA = ROOT / '.runtime/trellis298c/retrieved/evidence/head512'
SHELL = ROOT / '.runtime/trellis298d/retrieved/evidence/remeshed-source.safetensors'
TEARDOWNS = ['results/trellis293/teardown-verification.json', 'results/trellis294/teardown-verification.json',
    'results/trellis295/cloud-a/teardown-verification.json', 'results/trellis298/teardown-verification.json',
    *[f'results/trellis298/cloud-{v}/teardown-verification.json' for v in 'bcd']]


def ledger():
    return BudgetLedger(ROOT / '.runtime/trellis301/export/budget.jsonl', campaign_limit=5,
        scope_limits={'qualification': 5}, stage_limits={'gpu_session': (4, 1)}, request_limit=1,
        request_ceiling_usd=4)


def aggregate(add=0):
    for name in TEARDOWNS:
        record = json.loads((ROOT / name).read_text())
        if any(record['remaining'].values()):
            raise RuntimeError('Historical resources remain')
    current = ledger().summary()
    total = 10 + current['committed_usd'] + add
    if total > 15 + 1e-9:
        raise RuntimeError('Original USD15 aggregate ceiling exceeded')
    return {'effective_ceiling_usd': 15, 'closed_liability_bound_usd': 10,
        'closed_actual_bill_usd': None, 'conditional_extra_usd_activated': 0,
        'admission_total_usd': total, 'new': current, 'basis': 'results/trellis301/STRATEGY.md',
        'historical_holds_preserved_not_invoice': True,
        'teardown_bindings': {p: local.sha(ROOT / p) for p in TEARDOWNS}}


def packet():
    task = json.loads((ROOT / 'results/trellis301/task.json').read_text())
    task.update(id='trellis301-fixed-source-export', phase='execution',
        execution_authority={'source': 'results/trellis301/STRATEGY.md',
            'scope': 'Director301 fixed-source controls; root-reviewed dispatch only; original aggregate15USD'})
    for p in [Path(__file__), ROOT / 'scripts/trellis301_export_worker.py',
              ROOT / 'src/movie_factory/trellis301_quality.py', ROOT / 'scripts/trellis298_worker.py',
              ROOT / 'scripts/trellis294_runtime.py', ROOT / 'results/trellis301/STRATEGY.md',
              DATA / 'source.safetensors', DATA / 'geometry.json', SHELL]:
        task['inputs'][str(p.relative_to(ROOT))] = local.sha(p)
    result = pk.task_packet(ROOT, task)
    c.dump(OUT / 'task.json', task)
    c.dump(OUT / 'packet.json', result)
    (OUT / 'packet.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']:
        raise RuntimeError(result['blockers'])
    return result


def configure():
    previous.configure('d')
    c.OUT, c.LOCAL = OUT, ROOT / '.runtime/trellis301/export'
    c.STATE = c.LOCAL / 'cloud-state.json'
    c.JOB = 'trellis301-export'
    c.BUCKET = 'mf-trellis301-export-281482331395'
    c.ROLE, c.GUARD = 'mf-trellis301-export-worker', 'mf-trellis301-export-guard'
    c.ledger = t.ledger = ledger
    t.aggregate = aggregate
    c.packet = t.packet = packet
    c.userdata = lambda: previous.ORIGINAL_USERDATA().replace('scripts/trellis293_worker.py', 'scripts/trellis301_export_worker.py')


def no_active():
    previous.no_active()
    rows = t.aws('ec2', 'describe-instances', '--filters', c.j([
        {'Name': 'tag:MovieFactoryJob', 'Values': ['trellis301-*']},
        {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped', 'shutting-down']}]))
    if any(r['Instances'] for r in rows['Reservations']):
        raise RuntimeError('301 worker already active')


def closed_resource_inventory():
    """Fresh read-only c/d inventory before replacing their reservations with bounds."""
    jobs = ['trellis298c-inference', 'trellis298d-inference']
    roles = {f'mf-trellis298{x}-{kind}' for x in 'cd' for kind in ('worker', 'guard')}
    worker_roles = {f'mf-trellis298{x}-worker' for x in 'cd'}
    guards = {f'mf-trellis298{x}-guard' for x in 'cd'}
    buckets = {f'mf-trellis298{x}-281482331395' for x in 'cd'}
    tags = c.j([{'Name': 'tag:MovieFactoryJob', 'Values': jobs}])
    instances = [i for r in t.aws('ec2', 'describe-instances', '--filters', tags)['Reservations'] for i in r['Instances']]
    remaining = {
        'instances': [i['InstanceId'] for i in instances if i['State']['Name'] != 'terminated'],
        'volumes': [v['VolumeId'] for v in t.aws('ec2', 'describe-volumes', '--filters', tags)['Volumes']],
        'buckets': [b['Name'] for b in t.aws('s3api', 'list-buckets')['Buckets'] if b['Name'] in buckets],
        'roles': [r['RoleName'] for r in t.aws('iam', 'list-roles')['Roles'] if r['RoleName'] in roles],
        'profiles': [p['InstanceProfileName'] for p in t.aws('iam', 'list-instance-profiles')['InstanceProfiles'] if p['InstanceProfileName'] in worker_roles],
        'functions': [f['FunctionName'] for f in t.aws('lambda', 'list-functions')['Functions'] if f['FunctionName'] in guards],
        'groups': [g['GroupId'] for g in t.aws('ec2', 'describe-security-groups', '--filters',
            c.j([{'Name': 'group-name', 'Values': jobs}, {'Name': 'vpc-id', 'Values': [c.VPC]}]))['SecurityGroups']],
        'rules': [r['Name'] for guard in sorted(guards) for r in t.aws('events', 'list-rules', '--name-prefix', guard)['Rules'] if r['Name'] == guard],
    }
    receipt = {'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Exact closed298c/d temporary resources; read-only, not billing reconciliation', 'remaining': remaining}
    c.dump(OUT / 'closed-resource-preflight.json', receipt)
    if any(remaining.values()):
        raise RuntimeError('Closed298c/d resources remain; cannot adopt reduced liability bounds')
    return receipt


def verify_frozen():
    state = c.state()
    if local.sha(Path(__file__)) != state['controller_sha256']:
        raise RuntimeError('Controller changed after payload freeze')
    if local.sha(c.LOCAL / 'payload.tar.gz') != state['payload_sha256']:
        raise RuntimeError('Payload changed after freeze')
    if local.sha(c.LOCAL / 'watchdog.zip') != state['watchdog_sha256']:
        raise RuntimeError('Watchdog changed after freeze')
    for path, digest in state['local_bindings'].items():
        if local.sha(ROOT / path) != digest:
            raise RuntimeError('Bound source changed: ' + path)


def prepare():
    offline()
    no_active()
    closed_resource_inventory()
    aggregate(4)
    identity = t.aws('sts', 'get-caller-identity')
    if identity['Account'] != c.ACCOUNT:
        raise RuntimeError('Wrong AWS account')
    quota = t.aws('service-quotas', 'get-service-quota', '--service-code', 'ec2', '--quota-code', 'L-DB2E81BA')['Quota']
    if quota['Value'] < 8:
        raise RuntimeError('Insufficient GPU vCPU quota')
    prices = t.aws('pricing', 'get-products', '--service-code', 'AmazonEC2', '--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6.2xlarge',
        'Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux', 'Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA', 'Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    products = [json.loads(x) for x in prices['PriceList']]
    rates = [float(d['pricePerUnit']['USD']) for p in products for term in p['terms']['OnDemand'].values()
             for d in term['priceDimensions'].values() if d['unit'] == 'Hrs']
    if len(rates) != 1 or rates[0] > 1:
        raise RuntimeError('Reassess export reservation against current rate')
    image = t.aws('ec2', 'describe-images', '--image-ids', c.AMI)['Images'][0]
    if image.get('ImageOwnerAlias') != 'amazon' and image['OwnerId'] != '898082745236':
        raise RuntimeError('AMI publisher drift')
    subnet = t.aws('ec2', 'describe-subnets', '--subnet-ids', c.SUBNET)['Subnets'][0]
    if subnet['VpcId'] != c.VPC:
        raise RuntimeError('Subnet drift')
    c.dump(OUT / 'preflight.json', {'account': identity['Account'], 'quota': quota, 'price': products,
        'image': image, 'subnet': subnet, 'aggregate': aggregate(4), 'capacity_test': 'NOT_RUN',
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
    c.save('rate', rates[0])
    # Refresh both relevant rates without launching/testing capacity.
    prices = t.aws('pricing', 'get-products', '--service-code', 'AmazonEC2', '--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6e.2xlarge',
        'Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux', 'Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA', 'Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    products = [json.loads(x) for x in prices['PriceList']]
    c.dump(OUT / 'contingent-1024-price.json', {'products': products, 'capacity_test': 'NOT_RUN',
        'generation_admitted': False, 'reason': 'Fixed-source review and separate root budget review first'})
    c.dump(OUT / 'preparation-status.json', {'prepared_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'cloud_mutations': False, 'paid_calls': False, 'root_dispatch_review': 'PENDING'})
    c.save('prepared', True)


def offline():
    if c.state().get('instance') or c.state().get('reservation'):
        raise RuntimeError('Cannot rewrite a reserved/dispatched worker')
    local.packet()
    c.LOCAL.mkdir(parents=True, exist_ok=True)
    if not (c.LOCAL / 'synthetic-payload.tar.gz').exists():
        shutil.copyfile(ROOT / '.runtime/trellis293/payload-a10.tar.gz', c.LOCAL / 'synthetic-payload.tar.gz')
    watchdog = (ROOT / 'scripts/trellis293_watchdog.py').read_text().replace('trellis293-synthetic', c.JOB).replace('ca-central-1', 'us-east-1')
    with zipfile.ZipFile(c.LOCAL / 'watchdog.zip', 'w') as archive:
        archive.writestr('watchdog.py', watchdog)
    repack()
    c.dump(OUT / 'offline-preparation.json', {'cloud_mutations': False, 'aws_queries': False,
        'watchdog_sha256': local.sha(c.LOCAL / 'watchdog.zip'), 'live_preflight': 'NOT_RUN'})


def repack():
    if c.state().get('instance'):
        raise RuntimeError('Cannot repack a dispatched worker')
    packet()
    base_manifest = json.loads((ROOT / 'results/trellis293/payload-a10-manifest.json').read_text())
    additions = {'scripts/' + n: ROOT / 'scripts' / n for n in
                 ('trellis301_export_worker.py', 'trellis298_worker.py', 'trellis294_runtime.py')}
    additions.update({'src/movie_factory/trellis301_quality.py': ROOT / 'src/movie_factory/trellis301_quality.py',
        'input/source.safetensors': DATA / 'source.safetensors', 'input/geometry.json': DATA / 'geometry.json',
        'input/remeshed-source.safetensors': SHELL})
    manifest = dict(base_manifest)
    with tarfile.open(c.LOCAL / 'synthetic-payload.tar.gz') as src, tarfile.open(c.LOCAL / 'payload.tar.gz', 'w:gz', compresslevel=1) as dst:
        if set(src.getnames()) != set(base_manifest):
            raise RuntimeError('Synthetic base inventory drift')
        for member in src.getmembers():
            if not member.isfile() or member.name.startswith('/') or '..' in Path(member.name).parts:
                raise RuntimeError('Unsafe payload member')
            content = src.extractfile(member).read()
            if hashlib.sha256(content).hexdigest() != base_manifest[member.name]:
                raise RuntimeError('Synthetic payload hash drift')
            import io
            dst.addfile(member, io.BytesIO(content))
        for name, path in additions.items():
            if name in manifest or path.is_symlink():
                raise RuntimeError('Duplicate/symlink payload member')
            dst.add(path, arcname=name, recursive=False)
            manifest[name] = local.sha(path)
    if any('.env' in n or any(x in Path(n).name.lower() for x in ('credential', 'token')) for n in manifest):
        raise RuntimeError('Credential-like payload path')
    c.dump(OUT / 'payload-manifest.json', manifest)
    c.save('payload_sha256', local.sha(c.LOCAL / 'payload.tar.gz'))
    c.save('controller_sha256', local.sha(Path(__file__)))
    controls = [ROOT / 'scripts' / n for n in ('trellis293_cloud.py', 'trellis294_cloud.py',
        'trellis295_cloud.py', 'trellis298_cloud.py', 'trellis293_watchdog.py', 'trellis301_prepare.py')]
    controls += [ROOT / 'results/trellis301/STRATEGY.md', ROOT / 'src/movie_factory/budget.py']
    c.save('local_bindings', {str(p.relative_to(ROOT)): local.sha(p) for p in [*additions.values(), *controls]})
    c.save('watchdog_sha256', local.sha(c.LOCAL / 'watchdog.zip'))
    c.dump(OUT / 'payload.json', {'sha256': c.state()['payload_sha256'],
        'bytes': (c.LOCAL / 'payload.tar.gz').stat().st_size, 'files': len(manifest),
        'new_generation': False, 'encoder_upload': False, 'credential_upload': False,
        'comparison': ['300k-2k', '1m-2k', '1m-4k'], 'new_unsigned_reconstruction': False})


def guards(root_reviewed=False):
    if not root_reviewed:
        raise RuntimeError('Root must review budget, preflight and exact payload before dispatch')
    verify_frozen()
    no_active()
    closed_resource_inventory()
    aggregate(4)
    c.guards(amount_usd=4, run_id='trellis301-export')
    c.save('staged_payload_sha256', c.state()['payload_sha256'])
    c.dump(OUT / 'aggregate-reserved.json', aggregate())


def launch(root_reviewed=False):
    if not root_reviewed:
        raise RuntimeError('Root dispatch review required')
    verify_frozen()
    if c.state()['staged_payload_sha256'] != c.state()['payload_sha256']:
        raise RuntimeError('Staged payload differs')
    no_active()
    t.launch('us-east-1a', reserved_usd=4, client_token=c.JOB + '-one-worker')


if __name__ == '__main__':
    configure()
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['offline', 'prepare', 'repack', 'packet', 'guards', 'launch', 'status', 'retrieve', 'cleanup'])
    parser.add_argument('--root-reviewed', action='store_true')
    args = parser.parse_args()
    if args.operation in ('guards', 'launch'):
        globals()[args.operation](args.root_reviewed)
    elif args.operation in ('status', 'retrieve', 'cleanup'):
        getattr(c, args.operation)()
    else:
        globals()[args.operation]()
