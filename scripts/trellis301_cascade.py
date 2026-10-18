"""Single contingent48GB comparison; original aggregate15USD, no extra authority."""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

import trellis301_cloud as export
from movie_factory import production_knowledge as pk
from movie_factory.budget import BudgetLedger
from movie_factory.trellis_adapter.patch import adapted_sources

c, t, ROOT = export.c, export.t, export.ROOT
OUT = ROOT / 'results/trellis301/cloud-1024'
LOCAL = ROOT / '.runtime/trellis301/cascade'
ENCODER = ROOT / '.runtime/trellis298c/encoder.tar'
RESERVATION = 3.5


def ledger():
    return BudgetLedger(LOCAL / 'budget.jsonl', campaign_limit=RESERVATION,
        scope_limits={'qualification':RESERVATION}, stage_limits={'gpu_session':(RESERVATION,1)},
        request_limit=1, request_ceiling_usd=RESERVATION)


def aggregate(add=0):
    paths = export.TEARDOWNS + ['results/trellis301/cloud-export/teardown-verification.json']
    for p in paths:
        if any(json.loads((ROOT / p).read_text())['remaining'].values()):
            raise RuntimeError('Residual historical resources')
    receipt = json.loads((ROOT / paths[-1]).read_text())
    if receipt['compute_estimate_upper_usd'] > .367:
        raise RuntimeError('Export liability bound invalid')
    total = 11.5 + ledger().summary()['committed_usd'] + add
    if total > 15 + 1e-9:
        raise RuntimeError('Original USD15 ceiling exceeded')
    return {'admission_total_usd':total, 'closed_liability_bound_usd':11.5,
        'actual_billed_usd':None, 'effective_ceiling_usd':15, 'extra10_activated':False,
        'current':ledger().summary(), 'basis':'results/trellis301/EXPORT_REVIEW.md',
        'historical_raw_ledgers_preserved':True,
        'teardown_bindings':{p:c.sha(ROOT / p) for p in paths}}


def packet():
    task = json.loads((ROOT / 'results/trellis301/task.json').read_text())
    task.update(id='trellis301-single1024', phase='execution',
        intent='Previously authorized contingent1024 comparison; source quality not actor acceptance',
        execution_authority={'source':'results/trellis301/CASCADE_PLAN.md',
            'scope':'Single48GB worker after root payload/budget/guard admission; original15USD'})
    for p in [Path(__file__), ROOT/'scripts/trellis301_infer_worker.py',
              ROOT/'results/trellis301/CASCADE_PLAN.md', ROOT/'results/trellis301/EXPORT_REVIEW.md']:
        task['inputs'][str(p.relative_to(ROOT))] = c.sha(p)
    result = pk.task_packet(ROOT, task)
    c.dump(OUT/'task.json',task); c.dump(OUT/'packet.json',result)
    (OUT/'packet.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']:
        raise RuntimeError(result['blockers'])
    return result


def configure():
    export.configure()
    c.OUT, c.LOCAL, c.STATE = OUT, LOCAL, LOCAL/'cloud-state.json'
    c.JOB = 'trellis301-1024'
    c.BUCKET = 'mf-trellis301-1024-281482331395'
    c.ROLE, c.GUARD = 'mf-trellis301-1024-worker', 'mf-trellis301-1024-guard'
    c.ledger = t.ledger = ledger
    t.aggregate = aggregate
    c.packet = t.packet = packet
    c.userdata = userdata


def userdata():
    body = export.previous.ORIGINAL_USERDATA()
    body = body.replace('scripts/trellis293_worker.py','scripts/trellis301_infer_worker.py')
    body = body.replace('shutdown -h +115','shutdown -h +55').replace('timeout 6500','timeout 3000')
    fetch = '''"$AWS" s3 cp s3://mf-trellis293-281482331395/input/encoder.tar encoder.tar --only-show-errors
echo "ENCODER_HASH  encoder.tar" | sha256sum --check
tar -xf encoder.tar
'''.replace('ENCODER_HASH',c.state()['encoder_sha256'])
    return body.replace('nvidia-smi >',fetch+'nvidia-smi >').replace('ca-central-1','us-east-1').replace('mf-trellis293-281482331395',c.BUCKET)


def offline():
    if c.state().get('reservation') or c.state().get('instance'):
        raise RuntimeError('Frozen dispatched attempt')
    packet(); LOCAL.mkdir(parents=True,exist_ok=True)
    base = ROOT/'.runtime/trellis298c/payload.tar.gz'
    manifest = json.loads((ROOT/'results/trellis298/cloud-c/payload-manifest.json').read_text())
    replace = {'scripts/trellis301_infer_worker.py':(ROOT/'scripts/trellis301_infer_worker.py').read_bytes()}
    replace.update({'inference/'+n:s.encode() for n,s in adapted_sources(ROOT/'results/sikh288/upstream').items()})
    entries = {}
    with tarfile.open(base) as src, tarfile.open(LOCAL/'payload.tar.gz','w:gz',compresslevel=1) as dst:
        if set(src.getnames()) != set(manifest):
            raise RuntimeError('Prior payload inventory drift')
        for m in src.getmembers():
            if not m.isfile() or m.name.startswith('/') or '..' in Path(m.name).parts:
                raise RuntimeError('Unsafe prior member')
            data = src.extractfile(m).read()
            if hashlib.sha256(data).hexdigest() != manifest[m.name]:
                raise RuntimeError('Prior payload hash drift')
            if m.name in replace:
                data = replace.pop(m.name)
            info = tarfile.TarInfo(m.name); info.size = len(data)
            dst.addfile(info,io.BytesIO(data)); entries[m.name] = hashlib.sha256(data).hexdigest()
        for name,data in replace.items():
            info = tarfile.TarInfo(name); info.size = len(data)
            dst.addfile(info,io.BytesIO(data)); entries[name] = hashlib.sha256(data).hexdigest()
    encoder_record = json.loads((ROOT/'results/trellis298/cloud-c/encoder-manifest.json').read_text())
    with tarfile.open(ENCODER) as archive:
        expected = {'encoder/'+n: r['sha256'] for n,r in encoder_record['files'].items()}
        expected['encoder/manifest.json'] = c.sha(ROOT/'.runtime/trellis298-encoder/manifest.json')
        if set(archive.getnames()) != set(expected):
            raise RuntimeError('Encoder inventory drift')
        for member in archive.getmembers():
            if not member.isfile() or hashlib.sha256(archive.extractfile(member).read()).hexdigest()!=expected[member.name]:
                raise RuntimeError('Encoder content drift')
    watchdog = (ROOT/'scripts/trellis293_watchdog.py').read_text().replace('trellis293-synthetic',c.JOB).replace('ca-central-1','us-east-1').replace('seconds=7200','seconds=3600')
    with zipfile.ZipFile(LOCAL/'watchdog.zip','w') as archive:
        archive.writestr('watchdog.py',watchdog)
    c.save('encoder_sha256',c.sha(ENCODER)); c.save('payload_sha256',c.sha(LOCAL/'payload.tar.gz'))
    bindings = [Path(__file__), ROOT/'scripts/trellis301_infer_worker.py',
        ROOT/'scripts/trellis298_worker.py',ROOT/'scripts/trellis293_cloud.py',ROOT/'scripts/trellis293_watchdog.py',
        ROOT/'scripts/trellis294_cloud.py', ROOT/'scripts/trellis301_cloud.py',
        ROOT/'results/trellis301/CASCADE_PLAN.md',ROOT/'results/trellis301/EXPORT_REVIEW.md']
    c.save('bindings',{str(p.relative_to(ROOT)):c.sha(p) for p in bindings})
    c.save('watchdog_sha256',c.sha(LOCAL/'watchdog.zip'))
    c.dump(OUT/'payload-manifest.json',entries)
    c.dump(OUT/'payload.json',{'payload_bytes':(LOCAL/'payload.tar.gz').stat().st_size,
        'encoder_bytes':ENCODER.stat().st_size,'payload_sha256':c.state()['payload_sha256'],
        'encoder_sha256':c.state()['encoder_sha256'],'files':len(entries),
        'input_sha256':entries['input/head.png'],'credentials':False,'public':False,'destination':c.BUCKET})
    print('Offline payload verified; no cloud mutation')


def frozen():
    for p,digest in c.state()['bindings'].items():
        if c.sha(ROOT/p)!=digest: raise RuntimeError('Bound source changed: '+p)
    for path,key in [(ENCODER,'encoder_sha256'),(LOCAL/'payload.tar.gz','payload_sha256'),(LOCAL/'watchdog.zip','watchdog_sha256')]:
        if c.sha(path)!=c.state()[key]: raise RuntimeError('Payload/guard drift')


def prepare():
    offline(); export.no_active(); aggregate(RESERVATION)
    identity = t.aws('sts','get-caller-identity')
    if identity['Account'] != c.ACCOUNT: raise RuntimeError('Wrong account')
    quota = t.aws('service-quotas','get-service-quota','--service-code','ec2','--quota-code','L-DB2E81BA')['Quota']
    if quota['Value']<8: raise RuntimeError('GPU quota insufficient')
    price = t.aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6e.2xlarge','Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    products = [json.loads(x) for x in price['PriceList']]
    rates = [float(d['pricePerUnit']['USD']) for p in products for term in p['terms']['OnDemand'].values() for d in term['priceDimensions'].values() if d['unit']=='Hrs']
    if len(rates)!=1 or rates[0]>2.25: raise RuntimeError('Cost reassessment required')
    image = t.aws('ec2','describe-images','--image-ids',c.AMI)['Images'][0]
    if image.get('ImageOwnerAlias')!='amazon' and image['OwnerId']!='898082745236': raise RuntimeError('AMI drift')
    subnet = t.aws('ec2','describe-subnets','--subnet-ids',c.SUBNET)['Subnets'][0]
    if subnet['VpcId']!=c.VPC: raise RuntimeError('Subnet drift')
    c.dump(OUT/'preflight.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'price':products,'quota':quota,'image':image,'subnet':subnet,'aggregate':aggregate(RESERVATION),'capacity':'NOT_RUN'})
    c.save('rate',rates[0]); c.save('prepared',True)
    print('Fresh preflight PASS; no cloud mutation')


def guards(reviewed=False):
    if not reviewed: raise RuntimeError('Root admission required')
    frozen(); export.no_active(); aggregate(RESERVATION)
    c.guards(amount_usd=RESERVATION,run_id='trellis301-1024')
    t.aws('s3','cp',ENCODER,'s3://'+c.BUCKET+'/input/encoder.tar','--only-show-errors',raw=True)
    c.save('encoder_uploaded',True); c.dump(OUT/'aggregate-reserved.json',aggregate())


def launch(reviewed=False):
    if not reviewed: raise RuntimeError('Root admission required')
    frozen(); export.no_active(); aggregate(); packet()
    s=c.state()
    if not s.get('guard_verified') or not s.get('encoder_uploaded') or s.get('instance') or s.get('worker_created'):
        raise RuntimeError('Guard/staging/one-worker admission failed')
    if ledger().summary()['reserved_unknown_usd']<RESERVATION: raise RuntimeError('Missing reservation')
    token=c.JOB+'-one-worker'
    if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[token]}]))['Reservations']:
        raise RuntimeError('Worker already attempted')
    if t.aws('events','describe-rule','--name',c.GUARD)['State']!='ENABLED': raise RuntimeError('Guard disabled')
    if t.aws('events','list-targets-by-rule','--rule',c.GUARD)['Targets'][0]['Arn']!=s['function']: raise RuntimeError('Guard binding')
    p=LOCAL/'user-data.sh'; p.write_text(userdata())
    deadline=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=3600)).isoformat()
    tags=[{'Key':'MovieFactoryJob','Value':c.JOB},{'Key':'Name','Value':c.JOB},{'Key':'ExpiresAt','Value':deadline}]
    data=t.aws('ec2','run-instances','--image-id',c.AMI,'--instance-type','g6e.2xlarge','--count','1','--client-token',token,
        '--subnet-id',c.SUBNET,'--security-group-ids',s['security_group'],'--iam-instance-profile',c.j({'Name':c.ROLE}),
        '--metadata-options',c.j({'HttpTokens':'required','HttpEndpoint':'enabled','HttpPutResponseHopLimit':1}),
        '--instance-initiated-shutdown-behavior','terminate','--block-device-mappings',c.j([{'DeviceName':'/dev/sda1','Ebs':{'VolumeSize':80,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}]),
        '--tag-specifications',c.j([{'ResourceType':'instance','Tags':tags},{'ResourceType':'volume','Tags':tags}]),'--user-data','file://'+str(p))
    instance=data['Instances'][0]; c.save('instance',instance['InstanceId']); c.save('worker_created',True); c.dump(OUT/'launch.json',instance)
    print('Launched',instance['InstanceId'],deadline)


if __name__=='__main__':
    configure()
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['offline','prepare','packet','guards','launch','status','retrieve','cleanup'])
    parser.add_argument('--root-reviewed',action='store_true');args=parser.parse_args()
    if args.operation in ('guards','launch'): globals()[args.operation](args.root_reviewed)
    elif args.operation in ('status','retrieve','cleanup'): getattr(c,args.operation)()
    else: globals()[args.operation]()
