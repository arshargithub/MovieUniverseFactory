"""One guarded checkpoint-recovery worker; exact payload approval required."""
import argparse
import datetime
import hashlib
import io
import json
import sys
from pathlib import Path
import tarfile
import zipfile

import trellis301_cascade as prior
from movie_factory import production_knowledge as pk
from movie_factory.budget import BudgetLedger

c, t, ROOT = prior.c, prior.t, prior.ROOT
OUT = ROOT/'results/trellis303'
LOCAL = ROOT/'.runtime/trellis303'
CHECKPOINT = ROOT/'.runtime/trellis301/cascade/retrieved/evidence/predecode'
RESERVATION = 3.5


def ledger():
    return BudgetLedger(LOCAL/'budget.jsonl', campaign_limit=RESERVATION,
        scope_limits={'qualification':RESERVATION}, stage_limits={'gpu_session':(RESERVATION,1)},
        request_limit=1, request_ceiling_usd=RESERVATION)


def aggregate(add=0):
    receipt = ROOT/'results/trellis301/cloud-1024/teardown-verification.json'
    if any(json.loads(receipt.read_text())['remaining'].values()):
        raise RuntimeError('Historical cleanup incomplete')
    total = 15 + ledger().summary()['committed_usd'] + add
    if total > 18.5 + 1e-9: raise RuntimeError('Recovery ceiling exceeded')
    return {'admission_total_usd':total, 'prior_liability_held_usd':15,
        'actual_billed_usd':None, 'effective_ceiling_usd':18.5,
        'conditional_extra_authority_used_usd':max(0,total-15), 'current':ledger().summary(),
        'basis':'results/trellis303/STRATEGY.md', 'prior_receipt_sha256':c.sha(receipt)}


def packet():
    task = json.loads((ROOT/'results/trellis301/cloud-1024/task.json').read_text())
    task.update(id='trellis303-checkpoint-recovery', intent='Recover saved1024; no sampling; source quality not actor admission',
        execution_authority={'source':'results/trellis303/STRATEGY.md','scope':'One recovery worker; exact payload approval and3.50USD reservation'})
    for p in [Path(__file__),ROOT/'scripts/trellis303_worker.py',OUT/'STRATEGY.md',
              ROOT/'results/trellis301/CASCADE_REVIEW.md',CHECKPOINT/'latents.safetensors',CHECKPOINT/'latents.json']:
        task['inputs'][str(p.relative_to(ROOT))] = c.sha(p)
    result = pk.task_packet(ROOT,task)
    c.dump(OUT/'task.json',task); c.dump(OUT/'packet.json',result)
    (OUT/'packet.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']: raise RuntimeError(result['blockers'])
    return result


def configure():
    prior.export.configure()
    c.OUT,c.LOCAL,c.STATE = OUT,LOCAL,LOCAL/'cloud-state.json'
    c.JOB='trellis303-recovery'; c.BUCKET='mf-trellis303-recovery-281482331395'
    c.ROLE='mf-trellis303-recovery-worker'; c.GUARD='mf-trellis303-recovery-guard'
    c.ledger=t.ledger=ledger; t.aggregate=aggregate; c.packet=t.packet=packet; c.userdata=userdata


def userdata():
    return prior.export.previous.ORIGINAL_USERDATA().replace('scripts/trellis293_worker.py','scripts/trellis303_worker.py').replace(
        'shutdown -h +115','shutdown -h +55').replace('timeout 6500','timeout 3000').replace(
        'ca-central-1','us-east-1').replace('mf-trellis293-281482331395',c.BUCKET)


def offline():
    if c.state().get('reservation'): raise RuntimeError('Dispatched payload frozen')
    packet(); LOCAL.mkdir(exist_ok=True)
    base=ROOT/'.runtime/trellis301/cascade/payload.tar.gz'
    manifest=json.loads((ROOT/'results/trellis301/cloud-1024/payload-manifest.json').read_text())
    additions={'scripts/trellis303_worker.py':ROOT/'scripts/trellis303_worker.py',
        'checkpoint/latents.safetensors':CHECKPOINT/'latents.safetensors',
        'checkpoint/latents.json':CHECKPOINT/'latents.json',
        'checkpoint/weight-manifest.json':CHECKPOINT.parent/'weight-manifest.json'}
    entries={}
    with tarfile.open(base) as src, tarfile.open(LOCAL/'payload.tar.gz','w:gz',compresslevel=1) as dst:
        if set(src.getnames())!=set(manifest): raise RuntimeError('Prior inventory drift')
        def add(name,data):
            parts=Path(name).parts
            if name.startswith('/') or '..' in parts or any(x in parts for x in ('.env','.aws','.git','encoder')):
                raise ValueError('Forbidden payload member')
            info=tarfile.TarInfo(name); info.size=len(data)
            dst.addfile(info,io.BytesIO(data)); entries[name]=hashlib.sha256(data).hexdigest()
        for member in src.getmembers():
            if not member.isfile(): raise RuntimeError('Non-file payload member')
            data=src.extractfile(member).read()
            if hashlib.sha256(data).hexdigest()!=manifest[member.name]: raise RuntimeError('Prior payload drift')
            if member.name.startswith('input/'): continue
            add(member.name,data)
        for name,path in additions.items(): add(name,path.read_bytes())
    watchdog=(ROOT/'scripts/trellis293_watchdog.py').read_text().replace('trellis293-synthetic',c.JOB).replace('ca-central-1','us-east-1').replace('seconds=7200','seconds=3600')
    with zipfile.ZipFile(LOCAL/'watchdog.zip','w') as z: z.writestr('watchdog.py',watchdog)
    bindings=[Path(__file__),ROOT/'scripts/trellis303_worker.py',OUT/'STRATEGY.md',
        *[ROOT/'scripts'/n for n in ('trellis293_cloud.py','trellis293_watchdog.py','trellis294_cloud.py','trellis295_cloud.py',
          'trellis298_cloud.py','trellis301_cloud.py','trellis301_cascade.py')]]
    c.save('bindings',{str(p.relative_to(ROOT)):c.sha(p) for p in bindings})
    for name in ('payload.tar.gz','watchdog.zip'): c.save(name+'_sha256',c.sha(LOCAL/name))
    c.save('payload_sha256',c.sha(LOCAL/'payload.tar.gz'))
    c.dump(OUT/'payload-manifest.json',entries)
    c.dump(OUT/'payload.json',{'bytes':(LOCAL/'payload.tar.gz').stat().st_size,'sha256':c.sha(LOCAL/'payload.tar.gz'),
        'members':len(entries),'destination':c.BUCKET,'credentials':False,'encoder':False,'input_images':False,'public':False,
        'checkpoint_sha256':entries['checkpoint/latents.safetensors']})
    print(json.dumps(json.loads((OUT/'payload.json').read_text()),indent=2))


def frozen():
    for p,digest in c.state()['bindings'].items():
        if c.sha(ROOT/p)!=digest: raise RuntimeError('Bound source drift: '+p)
    for name in ('payload.tar.gz','watchdog.zip'):
        if c.sha(LOCAL/name)!=c.state()[name+'_sha256']: raise RuntimeError('Payload/guard drift')


def no_active():
    prior.export.no_active()
    rows=t.aws('ec2','describe-instances','--filters',c.j([
        {'Name':'tag:MovieFactoryJob','Values':[c.JOB]},
        {'Name':'instance-state-name','Values':['pending','running','stopping','stopped','shutting-down']}]))
    if rows['Reservations']: raise RuntimeError('Recovery worker already active')


def prepare():
    frozen(); no_active(); aggregate(RESERVATION)
    identity=t.aws('sts','get-caller-identity')
    if identity['Account']!=c.ACCOUNT: raise RuntimeError('Wrong account')
    hardware=t.aws('ec2','describe-instance-types','--instance-types','g6e.xlarge')['InstanceTypes'][0]
    if hardware['GpuInfo']['TotalGpuMemoryInMiB']<44*1024: raise RuntimeError('GPU too small')
    quota=t.aws('service-quotas','get-service-quota','--service-code','ec2','--quota-code','L-DB2E81BA')['Quota']
    if quota['Value']<4: raise RuntimeError('Quota too small')
    prices=t.aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6e.xlarge','Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    products=[json.loads(x) for x in prices['PriceList']]
    rates=[float(d['pricePerUnit']['USD']) for p in products for term in p['terms']['OnDemand'].values() for d in term['priceDimensions'].values() if d['unit']=='Hrs']
    if len(rates)!=1 or rates[0]>1.87: raise RuntimeError('Cost bound invalid')
    image=t.aws('ec2','describe-images','--image-ids',c.AMI)['Images'][0]
    if image['OwnerId']!='898082745236': raise RuntimeError('AMI owner mismatch')
    subnet=t.aws('ec2','describe-subnets','--filters',c.j([{'Name':'vpc-id','Values':[c.VPC]},
        {'Name':'availability-zone','Values':['us-east-1a']},{'Name':'default-for-az','Values':['true']}]))['Subnets']
    if len(subnet)!=1: raise RuntimeError('Subnet ambiguous')
    c.save('subnet',subnet[0]['SubnetId']); c.save('rate',rates[0]); c.save('prepared',True)
    c.dump(OUT/'preflight.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hardware':hardware,
        'quota':quota,'prices':products,'image':image,'subnet':subnet[0],'aggregate':aggregate(RESERVATION)})
    print('Read-only preflight PASS; no resources created')


def guards(reviewed):
    if not reviewed: raise RuntimeError('Exact payload approval required')
    frozen(); no_active(); aggregate(RESERVATION)
    approval=json.loads((OUT/'authority.json').read_text())
    if approval['payload_sha256']!=c.state()['payload_sha256'] or approval['approved'] is not True:
        raise RuntimeError('Missing exact payload authority')
    c.guards(amount_usd=RESERVATION,run_id=c.JOB)
    c.dump(OUT/'aggregate-reserved.json',aggregate())


def launch(reviewed):
    if not reviewed: raise RuntimeError('Root admission required')
    frozen(); no_active(); aggregate(); packet(); s=c.state()
    if s.get('instance') or not s.get('guard_verified') or ledger().summary()['reserved_unknown_usd']!=RESERVATION:
        raise RuntimeError('One-worker admission failed')
    token=c.JOB+'-one-worker'
    if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[token]}]))['Reservations']:
        raise RuntimeError('Attempt already used')
    if t.aws('events','describe-rule','--name',c.GUARD)['State']!='ENABLED': raise RuntimeError('Guard disabled')
    if t.aws('events','list-targets-by-rule','--rule',c.GUARD)['Targets'][0]['Arn']!=s['function']: raise RuntimeError('Guard target mismatch')
    p=LOCAL/'user-data.sh'; p.write_text(userdata())
    deadline=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=3600)).isoformat()
    tags=[{'Key':'MovieFactoryJob','Value':c.JOB},{'Key':'Name','Value':c.JOB},{'Key':'ExpiresAt','Value':deadline}]
    result=t.aws('ec2','run-instances','--image-id',c.AMI,'--instance-type','g6e.xlarge','--count','1','--client-token',token,
        '--subnet-id',s['subnet'],'--security-group-ids',s['security_group'],'--iam-instance-profile',c.j({'Name':c.ROLE}),
        '--metadata-options',c.j({'HttpTokens':'required','HttpEndpoint':'enabled','HttpPutResponseHopLimit':1}),
        '--instance-initiated-shutdown-behavior','terminate','--block-device-mappings',c.j([{'DeviceName':'/dev/sda1','Ebs':{
        'VolumeSize':80,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}]),
        '--tag-specifications',c.j([{'ResourceType':'instance','Tags':tags},{'ResourceType':'volume','Tags':tags}]),'--user-data','file://'+str(p))
    instance=result['Instances'][0]; c.save('instance',instance['InstanceId']); c.dump(OUT/'launch.json',instance)
    print('Launched',instance['InstanceId'],deadline)


if __name__=='__main__':
    configure(); p=argparse.ArgumentParser(); p.add_argument('operation',choices=['offline','prepare','packet','guards','launch','status','retrieve','cleanup','verify'])
    p.add_argument('--root-reviewed',action='store_true'); a=p.parse_args()
    if a.operation in ('guards','launch'): globals()[a.operation](a.root_reviewed)
    elif a.operation in ('status','retrieve','cleanup'): getattr(c,a.operation)()
    elif a.operation=='verify':
        import trellis301_verify_cleanup as verification
        verification.m=sys.modules[__name__]; verification.main()
    else: globals()[a.operation]()
