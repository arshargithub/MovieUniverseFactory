"""US configuration of reviewed293 controls; cumulative10+5 budget, one worker."""
import argparse,datetime,json,shutil,tarfile,zipfile
from pathlib import Path
import trellis293_cloud as c
from movie_factory.budget import BudgetLedger
from movie_factory import production_knowledge as pk

OLD_LEDGER=c.ledger
BASE_AWS=c.aws
REGION='us-east-1'
def ledger():
    return BudgetLedger(c.LOCAL/'budget.jsonl',campaign_limit=5,scope_limits={'qualification':5},
        stage_limits={'gpu_session':(5,1)},request_limit=1,request_ceiling_usd=5)
def aggregate(add=0):
    old=OLD_LEDGER().summary();new=ledger().summary()
    total=old['committed_usd']+new['committed_usd']+add
    if total>15+1e-9:raise RuntimeError('Cumulative USD15 ceiling exceeded')
    return {'ceiling_usd':15,'prior':old,'us':new,'committed_plus_proposed_usd':total}
def aws(service,op,*args,**kwargs):
    # All operations use explicitly selected region; no inherited CA default.
    kwargs.setdefault('region',REGION)
    return BASE_AWS(service,op,*args,**kwargs)
def configure():
    c.OUT=c.ROOT/'results/trellis294';c.LOCAL=c.ROOT/'.runtime/trellis294';c.STATE=c.LOCAL/'cloud-state.json'
    c.REGION=REGION;c.JOB='trellis294-synthetic';c.BUCKET='mf-trellis294-281482331395'
    c.ROLE='mf-trellis294-worker';c.GUARD='mf-trellis294-guard';c.AMI='ami-012ba162b9cd2729c'
    c.SUBNET='subnet-06b0dcf65205ee1a8';c.VPC='vpc-0b4a0b22ad2150a91'
    c.aws=aws;c.ledger=ledger;c.packet=packet
def packet():
    task=json.loads((c.ROOT/'results/trellis293/task.json').read_text())
    task.update(id='trellis294-us-synthetic',intent='Director294 US retry, cumulative USD15; synthetic exporter only.',
        execution_authority={'source':'results/trellis294/STRATEGY.md','scope':'One US synthetic worker, linked remaining USD5 allocation; no inference'})
    for p in (c.OUT/'STRATEGY.md',Path(__file__),c.ROOT/'scripts/trellis293_cloud.py',c.ROOT/'scripts/trellis293_worker.py'):
        task['inputs'][str(p.relative_to(c.ROOT))]=c.sha(p)
    p=pk.task_packet(c.ROOT,task);c.dump(c.OUT/'task.json',task);c.dump(c.OUT/'packet.json',p)
    (c.OUT/'packet.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise RuntimeError(p['blockers'])
    return p
def prepare(reservation_usd=5):
    assert not c.state();c.LOCAL.mkdir(parents=True,exist_ok=True)
    packet();aggregate(add=reservation_usd)
    identity=aws('sts','get-caller-identity');assert identity['Account']==c.ACCOUNT
    quota=aws('service-quotas','get-service-quota','--service-code','ec2','--quota-code','L-DB2E81BA')['Quota'];assert quota['Value']>=8
    prices=aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6.2xlarge','Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    product=json.loads(prices['PriceList'][0]);rates=[float(d['pricePerUnit']['USD']) for t in product['terms']['OnDemand'].values() for d in t['priceDimensions'].values() if d['unit']=='Hrs']
    assert len(rates)==1 and rates[0]<=1.0
    image=aws('ec2','describe-images','--image-ids',c.AMI)['Images'][0];assert image.get('ImageOwnerAlias')=='amazon' or image['OwnerId']=='898082745236'
    subnet=aws('ec2','describe-subnets','--subnet-ids',c.SUBNET)['Subnets'][0];assert subnet['VpcId']==c.VPC
    source=c.ROOT/'.runtime/trellis293/payload-a10.tar.gz'
    manifest=json.loads((c.ROOT/'results/trellis293/payload-a10-manifest.json').read_text())
    with tarfile.open(source) as archive:
        assert set(archive.getnames())==set(manifest)
        for m in archive.getmembers():
            assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
            import hashlib
            assert hashlib.sha256(archive.extractfile(m).read()).hexdigest()==manifest[m.name]
    shutil.copyfile(source,c.LOCAL/'payload.tar.gz');c.dump(c.OUT/'payload-manifest.json',manifest)
    watchdog=(c.ROOT/'scripts/trellis293_watchdog.py').read_text().replace('trellis293-synthetic',c.JOB).replace('ca-central-1',REGION)
    with zipfile.ZipFile(c.LOCAL/'watchdog.zip','w') as z:z.writestr('watchdog.py',watchdog)
    c.dump(c.OUT/'preflight.json',{'identity':identity,'quota':quota,'price':product['terms']['OnDemand'],'image':image,'subnet':subnet,
        'payload_sha256':c.sha(source),'payload_files':len(manifest),'watchdog_sha256':c.sha(c.LOCAL/'watchdog.zip'),'aggregate':aggregate(add=reservation_usd)})
    c.save('prepared',True);c.save('rate',rates[0]);c.save('payload_sha256',c.sha(source));print('Prepared, no cloud mutations')
def guards():
    aggregate(add=5);c.guards(amount_usd=5,run_id='trellis294');c.dump(c.OUT/'aggregate-reserved.json',aggregate())
def launch(zone='us-east-1a',reserved_usd=5,client_token='trellis294-one-worker'):
    s=c.state();assert s.get('guard_verified') and not s.get('instance') and not s.get('worker_created')
    assert ledger().summary()['reserved_unknown_usd']>=reserved_usd;aggregate();packet()
    rows=aws('ec2','describe-instances','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':[c.JOB]}]))['Reservations']
    assert not rows,'Any prior worker, including terminated, consumes this attempt'
    token=client_token
    assert not aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[token]}]))['Reservations']
    assert aws('events','describe-rule','--name',c.GUARD)['State']=='ENABLED'
    assert aws('events','list-targets-by-rule','--rule',c.GUARD)['Targets'][0]['Arn']==s['function']
    subnets=aws('ec2','describe-subnets','--filters',c.j([{'Name':'vpc-id','Values':[c.VPC]},{'Name':'availability-zone','Values':[zone]},{'Name':'default-for-az','Values':['true']}]))['Subnets']
    assert len(subnets)==1 and subnets[0]['AvailableIpAddressCount']>0
    bootstrap=c.userdata().replace('ca-central-1',REGION).replace('mf-trellis293-281482331395',c.BUCKET)
    # Preserve the worker's fixed isolated /opt path; only cloud destination changes.
    p=c.LOCAL/'user-data.sh';p.write_text(bootstrap)
    deadline=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=7200)).isoformat()
    tags=[{'Key':'MovieFactoryJob','Value':c.JOB},{'Key':'Name','Value':c.JOB},{'Key':'ExpiresAt','Value':deadline}]
    try:
        data=aws('ec2','run-instances','--image-id',c.AMI,'--instance-type','g6.2xlarge','--count','1','--client-token',token,
            '--subnet-id',subnets[0]['SubnetId'],'--security-group-ids',s['security_group'],'--iam-instance-profile',c.j({'Name':c.ROLE}),
            '--metadata-options',c.j({'HttpTokens':'required','HttpEndpoint':'enabled','HttpPutResponseHopLimit':1}),
            '--instance-initiated-shutdown-behavior','terminate','--block-device-mappings',c.j([{'DeviceName':'/dev/sda1','Ebs':{'VolumeSize':80,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}]),
            '--tag-specifications',c.j([{'ResourceType':'instance','Tags':tags},{'ResourceType':'volume','Tags':tags}]),'--user-data','file://'+str(p))
    except RuntimeError as e:
        c.dump(c.OUT/('launch-failure-'+zone+'.json'),{'error':str(e),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});raise
    i=data['Instances'][0];c.save('instance',i['InstanceId']);c.save('worker_created',True);c.dump(c.OUT/'launch.json',i);print('Launched',i['InstanceId'],deadline)
def main():
    configure();p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','guards','launch','status','retrieve','cleanup','packet']);p.add_argument('--zone',default='us-east-1a');a=p.parse_args()
    if a.operation=='launch':launch(a.zone)
    elif a.operation in {'status','retrieve','cleanup'}:getattr(c,a.operation)()
    else:globals()[a.operation]()
if __name__=='__main__':main()
