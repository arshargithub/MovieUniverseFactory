"""Same48GB recovery with larger host; fixed3.50USD admission, still one worker."""
import datetime
import json
from pathlib import Path
import trellis303_cloud as m


def main():
    m.configure();m.frozen();m.no_active();m.aggregate()
    c,t=m.c,m.t;s=c.state()
    if s.get('instance') or not s.get('guard_verified') or m.ledger().summary()['reserved_unknown_usd']!=3.5:
        raise RuntimeError('Single-worker guard/reservation admission failed')
    hardware=t.aws('ec2','describe-instance-types','--instance-types','g6e.2xlarge')['InstanceTypes'][0]
    admitted=json.loads((m.OUT/'preflight.json').read_text())['hardware']['GpuInfo']
    if hardware['GpuInfo']!=admitted or hardware['GpuInfo']['Gpus'][0]['Count']!=1:
        raise RuntimeError('Not the same single48GB GPU')
    quota=t.aws('service-quotas','get-service-quota','--service-code','ec2','--quota-code','L-DB2E81BA')['Quota']
    if quota['Value']<8:raise RuntimeError('Insufficient quota')
    price=t.aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6e.2xlarge','Type=TERM_MATCH,Field=location,Value=US East (N. Virginia)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used')
    products=[json.loads(x) for x in price['PriceList']]
    rates=[float(d['pricePerUnit']['USD']) for p in products for term in p['terms']['OnDemand'].values() for d in term['priceDimensions'].values() if d['unit']=='Hrs']
    if len(rates)!=1 or rates[0]>2.25:raise RuntimeError('Price above same-reservation bound')
    #70min includes guard polling and shutdown margin; remaining0.875USD covers
    #80GB short-lived disk, IP, staged data/egress and contingency, not an invoice.
    if rates[0]*70/60+.875>3.5:raise RuntimeError('Reservation insufficient')
    c.dump(m.OUT/'larger-capacity-plan.json',{'hardware':hardware,'quota':quota,'products':products,
        'compute70min_bound_usd':rates[0]*70/60,'ancillary_contingency_usd':.875,
        'source_sha256':c.sha(Path(__file__)),'payload_unchanged':True,'aggregate':m.aggregate(),
        'reason':'No xlarge capacity; same L40S48GB, more host CPUs/RAM, same worker count and deadline'})
    token=c.JOB+'-larger-one-worker'
    for zone in ('us-east-1a','us-east-1b','us-east-1c','us-east-1d'):
        m.no_active()
        if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':[c.JOB]}]))['Reservations']:
            raise RuntimeError('Any created worker consumes attempt')
        if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[token]}]))['Reservations']:
            raise RuntimeError('Ambiguous prior launch')
        if t.aws('events','describe-rule','--name',c.GUARD)['State']!='ENABLED':raise RuntimeError('Guard disabled')
        if t.aws('events','list-targets-by-rule','--rule',c.GUARD)['Targets'][0]['Arn']!=s['function']:raise RuntimeError('Guard target mismatch')
        subnets=t.aws('ec2','describe-subnets','--filters',c.j([{'Name':'vpc-id','Values':[c.VPC]},
            {'Name':'availability-zone','Values':[zone]},{'Name':'default-for-az','Values':['true']}]))['Subnets']
        if len(subnets)!=1:raise RuntimeError('Ambiguous subnet')
        p=m.LOCAL/'user-data.sh';p.write_text(m.userdata())
        deadline=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=3600)).isoformat()
        tags=[{'Key':'MovieFactoryJob','Value':c.JOB},{'Key':'Name','Value':c.JOB},{'Key':'ExpiresAt','Value':deadline}]
        try:
            result=t.aws('ec2','run-instances','--image-id',c.AMI,'--instance-type','g6e.2xlarge','--count','1','--client-token',token,
                '--subnet-id',subnets[0]['SubnetId'],'--security-group-ids',s['security_group'],'--iam-instance-profile',c.j({'Name':c.ROLE}),
                '--metadata-options',c.j({'HttpTokens':'required','HttpEndpoint':'enabled','HttpPutResponseHopLimit':1}),
                '--instance-initiated-shutdown-behavior','terminate','--block-device-mappings',c.j([{'DeviceName':'/dev/sda1','Ebs':{
                    'VolumeSize':80,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}]),
                '--tag-specifications',c.j([{'ResourceType':'instance','Tags':tags},{'ResourceType':'volume','Tags':tags}]),'--user-data','file://'+str(p))
        except RuntimeError as exc:
            c.dump(m.OUT/('larger-capacity-failure-'+zone+'.json'),{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':str(exc)})
            if 'InsufficientInstanceCapacity' not in str(exc):raise
            continue
        instance=result['Instances'][0];c.save('instance',instance['InstanceId']);c.save('rate',rates[0]);c.dump(m.OUT/'launch.json',instance)
        print('Launched',instance['InstanceId'],zone,deadline,flush=True);return
    raise RuntimeError('No same-GPU capacity; no GPU created')


if __name__=='__main__':main()
