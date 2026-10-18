"""Same48GB L40S, fewer host CPUs; no extra worker, spend ceiling or payload."""
import datetime
import json
from pathlib import Path
import trellis301_cascade as m


def main():
    m.configure();m.frozen();m.export.no_active();m.aggregate();m.packet()
    c,t=m.c,m.t;s=c.state()
    if s.get('instance') or s.get('worker_created') or not s.get('guard_verified') or not s.get('encoder_uploaded'):
        raise RuntimeError('Single-worker/staging admission failed')
    if m.ledger().summary()['reserved_unknown_usd']!=3.5:
        raise RuntimeError('Existing single reservation required')
    hardware=t.aws('ec2','describe-instance-types','--instance-types','g6e.xlarge')['InstanceTypes'][0]
    if hardware['GpuInfo']['TotalGpuMemoryInMiB']<44*1024 or hardware['MemoryInfo']['SizeInMiB']<32768 or hardware['VCpuInfo']['DefaultVCpus']<4:
        raise RuntimeError('Hardware below admitted minimum')
    prices=t.aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6e.xlarge','Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    products=[json.loads(p) for p in prices['PriceList']]
    rates=[float(d['pricePerUnit']['USD']) for p in products for term in p['terms']['OnDemand'].values() for d in term['priceDimensions'].values() if d['unit']=='Hrs']
    if len(rates)!=1 or rates[0]>2.25:raise RuntimeError('Cost bound invalid')
    c.dump(m.OUT/'smaller-capacity-plan.json',{'hardware':hardware,'prices':products,
        'reason':'Same48GB L40S;32GiB host RAM matches prior successful sampling host;2-job builds retained; slower setup possible within same guard',
        'source_sha256':c.sha(Path(__file__)),'payload_unchanged':True,'aggregate':m.aggregate()})
    token=c.JOB+'-small-one-worker'
    for zone in ('us-east-1a','us-east-1b','us-east-1c','us-east-1d'):
        m.export.no_active()
        if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':[c.JOB]}]))['Reservations']:
            raise RuntimeError('Any worker consumes attempt')
        if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[token]}]))['Reservations']:
            raise RuntimeError('Client token already used')
        if t.aws('events','describe-rule','--name',c.GUARD)['State']!='ENABLED':raise RuntimeError('Guard disabled')
        if t.aws('events','list-targets-by-rule','--rule',c.GUARD)['Targets'][0]['Arn']!=s['function']:raise RuntimeError('Guard target mismatch')
        subnet=t.aws('ec2','describe-subnets','--filters',c.j([{'Name':'vpc-id','Values':[c.VPC]},{'Name':'availability-zone','Values':[zone]},{'Name':'default-for-az','Values':['true']}]))['Subnets']
        if len(subnet)!=1 or subnet[0]['AvailableIpAddressCount']<1:raise RuntimeError('Subnet unavailable')
        p=m.LOCAL/'user-data.sh';p.write_text(m.userdata())
        deadline=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=3600)).isoformat()
        tags=[{'Key':'MovieFactoryJob','Value':c.JOB},{'Key':'Name','Value':c.JOB},{'Key':'ExpiresAt','Value':deadline}]
        try:
            result=t.aws('ec2','run-instances','--image-id',c.AMI,'--instance-type','g6e.xlarge','--count','1','--client-token',token,
                '--subnet-id',subnet[0]['SubnetId'],'--security-group-ids',s['security_group'],'--iam-instance-profile',c.j({'Name':c.ROLE}),
                '--metadata-options',c.j({'HttpTokens':'required','HttpEndpoint':'enabled','HttpPutResponseHopLimit':1}),
                '--instance-initiated-shutdown-behavior','terminate','--block-device-mappings',c.j([{'DeviceName':'/dev/sda1','Ebs':{'VolumeSize':80,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}]),
                '--tag-specifications',c.j([{'ResourceType':'instance','Tags':tags},{'ResourceType':'volume','Tags':tags}]),'--user-data','file://'+str(p))
        except RuntimeError as exc:
            c.dump(m.OUT/f'smaller-launch-failure-{zone}.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':str(exc)})
            if 'InsufficientInstanceCapacity' not in str(exc):raise
            print('No capacity',zone,flush=True)
            continue
        instance=result['Instances'][0];c.save('rate',rates[0]);c.save('instance',instance['InstanceId']);c.save('worker_created',True)
        c.dump(m.OUT/'launch.json',instance);print('Launched',instance['InstanceId'],zone,deadline)
        return
    raise RuntimeError('48GB capacity unavailable across all four offered zones; no GPU launched')


if __name__=='__main__':main()
