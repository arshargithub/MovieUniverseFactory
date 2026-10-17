"""Explicit stages for ONE authorized synthetic session; no implicit launch/retry."""
import argparse,base64,datetime,hashlib,json,os,subprocess,tarfile,time,zipfile
from pathlib import Path
from movie_factory.budget import BudgetLedger
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/trellis293'
LOCAL=ROOT/'.runtime/trellis293'
STATE=LOCAL/'cloud-state.json'
REGION='ca-central-1';ACCOUNT='281482331395';JOB='trellis293-synthetic'
BUCKET='mf-trellis293-281482331395';ROLE='mf-trellis293-worker';GUARD='mf-trellis293-guard'
AMI='ami-086b9a2f2fe469726';SUBNET='subnet-059587ec4e59e0731';VPC='vpc-02afcbb776e222f2d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
def state():return json.loads(STATE.read_text()) if STATE.exists() else {}
def save(key,value):s=state();s[key]=value;dump(STATE,s);return value
def aws(service,op,*args,region=REGION,raw=False):
    cmd=['aws',service,op,*map(str,args),'--profile','adi-sso','--region',region,'--no-cli-pager']
    if not raw:cmd+=['--output','json']
    result=subprocess.run(cmd,capture_output=True,text=True)
    if result.returncode:raise RuntimeError(service+' '+op+': '+result.stderr[-3000:])
    return result.stdout if raw else (json.loads(result.stdout) if result.stdout.strip() else {})
def j(data):return json.dumps(data,separators=(',',':'))
def ledger():return BudgetLedger(ROOT/'.runtime/trellis288/budget.jsonl',campaign_limit=15,
    scope_limits={'qualification':15},stage_limits={'gpu_session':(15,1)},request_limit=1,request_ceiling_usd=15)
def packet():
    task=json.loads((ROOT/'results/sikh288/task.json').read_text())
    task.update(id='trellis293-cuda-qualification',phase='execution',open_decisions=[],
        intent='Synthetic CUDA exporter only under Director288 USD15 authorization; no protagonist/model inference. Cloud rights/safety manually reconciled.',
        execution_authority={'source':'results/trellis293/STRATEGY.md','scope':'Continue approved synthetic GPU qualification, one Canadian worker, USD15 aggregate cap'})
    paths=[OUT/'STRATEGY.md',ROOT/'scripts/trellis288_cuda_probe.py',ROOT/'scripts/trellis293_worker.py',
           ROOT/'scripts/trellis293_watchdog.py',Path(__file__),ROOT/'results/sikh288/STRATEGY.md']
    paths+=list((ROOT/'src/movie_factory/trellis_adapter').glob('*.py'))
    task['inputs'].update({str(p.relative_to(ROOT)):sha(p) for p in paths})
    p=pk.task_packet(ROOT,task);dump(OUT/'task.json',task);dump(OUT/'packet.json',p)
    (OUT/'packet.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise RuntimeError(p['blockers'])
    return p
def prepare():
    LOCAL.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
    if state():raise RuntimeError('Preserve existing state; inspect before continuation')
    packet()
    identity=aws('sts','get-caller-identity');assert identity['Account']==ACCOUNT
    quota=aws('service-quotas','get-service-quota','--service-code','ec2','--quota-code','L-DB2E81BA')['Quota']
    assert quota['Value']>=8
    prices=aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g6.2xlarge','Type=TERM_MATCH,Field=location,Value=Canada (Central)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used',region='us-east-1')
    product=json.loads(prices['PriceList'][0]);terms=product['terms']['OnDemand'];rates=[float(d['pricePerUnit']['USD']) for term in terms.values() for d in term['priceDimensions'].values() if d['unit']=='Hrs']
    assert len(rates)==1 and rates[0]<=1.10
    image=aws('ec2','describe-images','--image-ids',AMI)['Images'][0]
    assert image['OwnerId']=='898082745236' or image.get('ImageOwnerAlias')=='amazon'
    subnet=aws('ec2','describe-subnets','--subnet-ids',SUBNET)['Subnets'][0];assert subnet['VpcId']==VPC
    # Exact source revisions and nested source tree remain reviewable.
    pins={'CuMesh':'12289e1062f0603f2f0d0771b02e1395d247f26f','FlexGEMM':'6dd94a859c26ee8246888502eada3dd8ad85532e',
      'CuMesh/third_party/cubvh':'ce92267a24ef6ad7d2c8ccbc2ae2c021a6597e70','CuMesh/third_party/cubvh/third_party/eigen':'e63d9f6ccb7f6f29f31241b87c542f3f0ab3112b'}
    for name,pin in pins.items():
        found=subprocess.check_output(['git','-C',str(ROOT/'.runtime/trellis293-sources'/name),'rev-parse','HEAD'],text=True).strip();assert found==pin
    selected={}
    for p in (ROOT/'src/movie_factory/trellis_adapter').glob('*.py'):selected[str(p.relative_to(ROOT))]=p
    for name in ('trellis288_cuda_probe.py','trellis293_worker.py'):selected['scripts/'+name]=ROOT/'scripts'/name
    for p in (ROOT/'results/sikh288/upstream').glob('*.py'):selected[str(p.relative_to(ROOT))]=p
    selected['third_party/trellis288/NOTICE.md']=ROOT/'third_party/trellis288/NOTICE.md'
    for base in ('CuMesh','FlexGEMM'):
        for p in (ROOT/'.runtime/trellis293-sources'/base).rglob('*'):
            if p.is_file() and not p.is_symlink() and '.git' not in p.parts and p.name!='.git':
                selected['sources/'+str(p.relative_to(ROOT/'.runtime/trellis293-sources'))]=p
    assert all('.env' not in name and 'credentials' not in name for name in selected)
    with tarfile.open(LOCAL/'payload.tar.gz','w:gz') as archive:
        for name,p in sorted(selected.items()):archive.add(p,arcname=name,recursive=False)
    manifest={name:sha(p) for name,p in selected.items()};dump(OUT/'payload-manifest.json',manifest)
    with zipfile.ZipFile(LOCAL/'watchdog.zip','w') as archive:archive.write(ROOT/'scripts/trellis293_watchdog.py','watchdog.py')
    dump(OUT/'preflight.json',{'identity':identity,'quota':quota,'rate_usd_per_hour':rates[0],'image':image,'subnet':subnet,'pins':pins,
        'payload_bytes':(LOCAL/'payload.tar.gz').stat().st_size,'payload_sha256':sha(LOCAL/'payload.tar.gz'),'payload_files':len(selected),
        'exclusions':['credentials','.env','production images','weights','production scenes','Git history']})
    save('prepared',True);save('rate',rates[0]);save('payload_sha256',sha(LOCAL/'payload.tar.gz'))
    print('Prepared',len(selected),'files;', (LOCAL/'payload.tar.gz').stat().st_size,'bytes. No cloud mutations.')
def role(name,service,policy):
    arn=aws('iam','create-role','--role-name',name,'--assume-role-policy-document',j({'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'Service':service},'Action':'sts:AssumeRole'}]}),'--tags',j([{'Key':'MovieFactoryJob','Value':JOB}]))['Role']['Arn']
    save(name,arn)
    aws('iam','put-role-policy','--role-name',name,'--policy-name','bounded-test','--policy-document',j({'Version':'2012-10-17','Statement':policy}))
    return arn
def guards(amount_usd=10, run_id='trellis293'):
    s=state();assert s.get('prepared') and not s.get('reservation')
    packet();rid=ledger().reserve(amount_usd=amount_usd,stage='gpu_session',scope='qualification',run_id=run_id,purpose='synthetic_aws_session')
    save('reservation',rid);dump(OUT/'budget-reserved.json',ledger().summary())
    location=[] if REGION=='us-east-1' else ['--create-bucket-configuration',j({'LocationConstraint':REGION})]
    aws('s3api','create-bucket','--bucket',BUCKET,*location);save('bucket',BUCKET)
    aws('s3api','put-public-access-block','--bucket',BUCKET,'--public-access-block-configuration',j(dict(BlockPublicAcls=True,IgnorePublicAcls=True,BlockPublicPolicy=True,RestrictPublicBuckets=True)))
    aws('s3api','put-bucket-encryption','--bucket',BUCKET,'--server-side-encryption-configuration',j({'Rules':[{'ApplyServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]}))
    aws('s3api','put-bucket-lifecycle-configuration','--bucket',BUCKET,'--lifecycle-configuration',j({'Rules':[{'ID':'temporary-only','Status':'Enabled','Filter':{'Prefix':''},'Expiration':{'Days':1},'AbortIncompleteMultipartUpload':{'DaysAfterInitiation':1}}]}))
    aws('s3api','put-bucket-policy','--bucket',BUCKET,'--policy',j({'Version':'2012-10-17','Statement':[{'Effect':'Deny','Principal':'*','Action':'s3:*','Resource':['arn:aws:s3:::'+BUCKET,'arn:aws:s3:::'+BUCKET+'/*'],'Condition':{'Bool':{'aws:SecureTransport':'false'}}}]}))
    aws('s3api','put-object','--bucket',BUCKET,'--key','input/payload.tar.gz','--body',LOCAL/'payload.tar.gz')
    role(ROLE,'ec2.amazonaws.com',[{'Effect':'Allow','Action':'s3:GetObject','Resource':'arn:aws:s3:::'+BUCKET+'/input/*'},
        {'Effect':'Allow','Action':'s3:PutObject','Resource':'arn:aws:s3:::'+BUCKET+'/output/*'}])
    aws('iam','create-instance-profile','--instance-profile-name',ROLE);save('profile',ROLE)
    aws('iam','add-role-to-instance-profile','--instance-profile-name',ROLE,'--role-name',ROLE)
    arn=role(GUARD,'lambda.amazonaws.com',[{'Effect':'Allow','Action':'ec2:DescribeInstances','Resource':'*'},
        {'Effect':'Allow','Action':'ec2:TerminateInstances','Resource':f'arn:aws:ec2:{REGION}:{ACCOUNT}:instance/*','Condition':{'StringEquals':{'ec2:ResourceTag/MovieFactoryJob':JOB}}}])
    time.sleep(10)
    fn=aws('lambda','create-function','--function-name',GUARD,'--runtime','python3.12','--role',arn,'--handler','watchdog.handler','--timeout','30','--memory-size','128','--zip-file','fileb://'+str(LOCAL/'watchdog.zip'))
    save('function',fn['FunctionArn'])
    aws('lambda','wait','function-active-v2','--function-name',GUARD)
    rule=aws('events','put-rule','--name',GUARD,'--schedule-expression','rate(5 minutes)','--state','ENABLED');save('rule',rule['RuleArn'])
    aws('lambda','add-permission','--function-name',GUARD,'--statement-id','scheduled-guard','--action','lambda:InvokeFunction','--principal','events.amazonaws.com','--source-arn',rule['RuleArn'])
    targets=aws('events','put-targets','--rule',GUARD,'--targets',j([{'Id':'guard','Arn':fn['FunctionArn']}]))
    assert targets['FailedEntryCount']==0
    result=aws('lambda','invoke','--function-name',GUARD,LOCAL/'guard-test.json')
    assert 'FunctionError' not in result
    observed=json.loads((LOCAL/'guard-test.json').read_text());assert not observed['seen'] and not observed['terminated']
    dump(OUT/'guard-test.json',observed);save('guard_verified',True)
    sg=aws('ec2','create-security-group','--group-name',JOB,'--description','Synthetic qualification no inbound','--vpc-id',VPC)['GroupId'];save('security_group',sg)
    group=aws('ec2','describe-security-groups','--group-ids',sg)['SecurityGroups'][0];assert not group['IpPermissions']
    dump(OUT/'security-group.json',group);print('Budget reserved; private bucket and independent guard verified; NO INSTANCE launched.')
def userdata():
    # Filesystem writes are generated bootstrap content in isolated disposable VM.
    return '''#!/bin/bash
set -eu
export AWS_DEFAULT_REGION=ca-central-1
mkdir -p /opt/mf-trellis293/evidence
cd /opt/mf-trellis293
shutdown -h +115
AWS=$(command -v aws)
finish() {
  code=$?
  trap - EXIT
  printf '%s\\n' "$code" > evidence/exit-code.txt
  tar -czf /opt/mf-trellis293-results.tar.gz evidence
  "$AWS" s3 cp /opt/mf-trellis293-results.tar.gz s3://mf-trellis293-281482331395/output/results.tar.gz --only-show-errors || true
  shutdown -h now
}
trap finish EXIT
"$AWS" s3 cp s3://mf-trellis293-281482331395/input/payload.tar.gz payload.tar.gz --only-show-errors
echo "PAYLOAD_HASH  payload.tar.gz" | sha256sum --check
tar -xzf payload.tar.gz
export PYTHONPATH=/opt/mf-trellis293/src
nvidia-smi > evidence/nvidia-smi.txt
(while sleep 30; do "$AWS" s3 cp evidence/build.log s3://mf-trellis293-281482331395/output/build.log --only-show-errors || true; done) &
timeout 6500 /usr/bin/python3 scripts/trellis293_worker.py > evidence/build.log 2>&1
'''.replace('PAYLOAD_HASH',state()['payload_sha256'])
def launch(retry_capacity=False):
    s=state();assert s.get('guard_verified') and not s.get('instance')
    if retry_capacity:
        if retry_capacity=='a10b':
            assert s.get('a10_attempted') and not s.get('a10b_attempted')
            assert json.loads((OUT/'capacity-failure-a10.json').read_text())['error']=='InsufficientInstanceCapacity'
        elif retry_capacity=='a10':
            assert s.get('a10_prepared') and not s.get('a10_attempted')
        elif retry_capacity=='d':
            assert s.get('capacity_retry') and not s.get('capacity_retry_d')
            assert json.loads((OUT/'capacity-failure-b.json').read_text())['error']=='InsufficientInstanceCapacity'
        else:
            assert s.get('launch_attempted') and not s.get('capacity_retry')
            assert json.loads((OUT/'capacity-failure.json').read_text())['error']=='InsufficientInstanceCapacity'
    else:assert not s.get('launch_attempted')
    packet();assert ledger().summary()['reserved_unknown_usd']>=10
    quota=aws('service-quotas','get-service-quota','--service-code','ec2','--quota-code','L-DB2E81BA')['Quota'];assert quota['Value']>=8
    existing=aws('ec2','describe-instances','--filters',j([{'Name':'tag:MovieFactoryJob','Values':[JOB]},{'Name':'instance-state-name','Values':['pending','running','stopping','stopped']}]))
    assert not existing['Reservations']
    by_token=aws('ec2','describe-instances','--filters',j([{'Name':'client-token','Values':['trellis293-one-worker']}]))
    assert not by_token['Reservations'],'Resolve existing client-token result before retry'
    subnet=SUBNET
    if retry_capacity and retry_capacity not in {'a10','a10b'}:
        subnet='subnet-0ce1aa172ea810c66' if retry_capacity=='d' else 'subnet-0eed77a024ba7b913'
        row=aws('ec2','describe-subnets','--subnet-ids',subnet)['Subnets'][0]
        assert row['VpcId']==VPC and row['AvailabilityZone']==('ca-central-1d' if retry_capacity=='d' else 'ca-central-1b')
        save('capacity_retry_d' if retry_capacity=='d' else 'capacity_retry',True)
    if retry_capacity=='a10':save('a10_attempted',True)
    if retry_capacity=='a10b':
        subnet='subnet-0eed77a024ba7b913';save('a10b_attempted',True)
    assert aws('events','describe-rule','--name',GUARD)['State']=='ENABLED'
    assert aws('events','list-targets-by-rule','--rule',GUARD)['Targets'][0]['Arn']==s['function']
    deadline=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=7200)).isoformat()
    user=LOCAL/'user-data.sh';user.write_text(userdata())
    tags=[{'Key':'MovieFactoryJob','Value':JOB},{'Key':'Name','Value':JOB},{'Key':'ExpiresAt','Value':deadline}]
    save('launch_attempted',datetime.datetime.now(datetime.timezone.utc).isoformat())
    data=aws('ec2','run-instances','--image-id',AMI,'--instance-type','g5.2xlarge' if retry_capacity in {'a10','a10b'} else 'g6.2xlarge','--count','1','--client-token','trellis293-a10-worker' if retry_capacity in {'a10','a10b'} else 'trellis293-one-worker',
        '--subnet-id',subnet,'--security-group-ids',s['security_group'],'--iam-instance-profile',j({'Name':ROLE}),
        '--metadata-options',j({'HttpTokens':'required','HttpEndpoint':'enabled','HttpPutResponseHopLimit':1}),
        '--instance-initiated-shutdown-behavior','terminate','--block-device-mappings',j([{'DeviceName':'/dev/sda1','Ebs':{'VolumeSize':80,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}]),
        '--tag-specifications',j([{'ResourceType':'instance','Tags':tags},{'ResourceType':'volume','Tags':tags}]),'--user-data','file://'+str(user))
    instance=data['Instances'][0];save('instance',instance['InstanceId']);dump(OUT/'launch.json',instance)
    print('Launched',instance['InstanceId'],'deadline',deadline)
def retry_capacity():launch(retry_capacity=True)
def retry_capacity_d():launch(retry_capacity='d')
def prepare_a10():
    s=state();assert s.get('capacity_retry_d') and not s.get('instance') and not s.get('a10_prepared')
    existing=aws('ec2','describe-instances','--filters',j([{'Name':'tag:MovieFactoryJob','Values':[JOB]}]));assert not existing['Reservations']
    prices=aws('pricing','get-products','--service-code','AmazonEC2','--filters',
        'Type=TERM_MATCH,Field=instanceType,Value=g5.2xlarge','Type=TERM_MATCH,Field=location,Value=Canada (Central)',
        'Type=TERM_MATCH,Field=operatingSystem,Value=Linux','Type=TERM_MATCH,Field=tenancy,Value=Shared',
        'Type=TERM_MATCH,Field=preInstalledSw,Value=NA','Type=TERM_MATCH,Field=capacitystatus,Value=Used',region='us-east-1')
    data=json.loads(prices['PriceList'][0]);terms=data['terms']['OnDemand'];rates=[float(d['pricePerUnit']['USD']) for t in terms.values() for d in t['priceDimensions'].values() if d['unit']=='Hrs']
    assert len(rates)==1 and rates[0]<=1.35
    dump(OUT/'a10-price.json',{'product':data['product'],'on_demand':terms});save('rate',rates[0])
    old=json.loads((OUT/'payload-manifest.json').read_text());new={}
    payload=LOCAL/'payload-a10.tar.gz'
    with tarfile.open(payload,'w:gz') as archive:
        for name,digest in sorted(old.items()):
            p=ROOT/name if not name.startswith('sources/') else ROOT/'.runtime/trellis293-sources'/name.removeprefix('sources/')
            if name!='scripts/trellis293_worker.py':assert sha(p)==digest
            new[name]=sha(p);archive.add(p,arcname=name,recursive=False)
    dump(OUT/'payload-a10-manifest.json',new);save('payload_sha256',sha(payload))
    aws('s3api','put-object','--bucket',BUCKET,'--key','input/payload.tar.gz','--body',payload)
    save('a10_prepared',True);packet();print('A10G payload prepared; same synthetic scope, reservation and guards.')
def launch_a10():launch(retry_capacity='a10')
def launch_a10b():launch(retry_capacity='a10b')
def status():
    s=state();print(j({'instance':s.get('instance'),'reservation':s.get('reservation')}))
    if s.get('instance'):
        data=aws('ec2','describe-instances','--instance-ids',s['instance']);dump(OUT/'latest-instance.json',data)
        print(data['Reservations'][0]['Instances'][0]['State'])
    if s.get('bucket'):
        objects=aws('s3api','list-objects-v2','--bucket',BUCKET,'--prefix','output/');dump(OUT/'remote-outputs.json',objects)
        print([(o['Key'],o['Size']) for o in objects.get('Contents',[])])
        if any(o['Key']=='output/build.log' for o in objects.get('Contents',[])):
            aws('s3api','get-object','--bucket',BUCKET,'--key','output/build.log',LOCAL/'build.log')
            print((LOCAL/'build.log').read_text()[-2500:])
def retrieve():
    aws('s3api','get-object','--bucket',BUCKET,'--key','output/results.tar.gz',LOCAL/'results.tar.gz')
    target=LOCAL/'retrieved';target.mkdir(exist_ok=True)
    with tarfile.open(LOCAL/'results.tar.gz') as archive:
        for member in archive.getmembers():
            if member.name.startswith('/') or '..' in Path(member.name).parts or member.issym() or member.islnk():raise ValueError('Unsafe result member')
        archive.extractall(target,filter='data')
    dump(OUT/'retrieved-manifest.json',{str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()})
    save('retrieved',True);print((target/'evidence/exit-code.txt').read_text())
def cleanup():
    s=state()
    if s.get('instance'):
        data=aws('ec2','describe-instances','--instance-ids',s['instance'])['Reservations'][0]['Instances'][0]
        assert {t['Key']:t['Value'] for t in data['Tags']}['MovieFactoryJob']==JOB
        if data['State']['Name']!='terminated':aws('ec2','terminate-instances','--instance-ids',s['instance'])
        # Caller polls completion; do not block a long time and hide progress.
        data=aws('ec2','describe-instances','--instance-ids',s['instance'])['Reservations'][0]['Instances'][0]
        if data['State']['Name']!='terminated':print('Termination requested; rerun cleanup after termination');return
        dump(OUT/'terminated-instance.json',data)
    # Preserve outputs until recovered. Do not delete evidence on an error.
    if s.get('bucket'):
        rows=aws('s3api','list-objects-v2','--bucket',BUCKET).get('Contents',[])
        if any(o['Key'].startswith('output/') for o in rows) and not s.get('retrieved'):raise RuntimeError('Retrieve outputs before deleting temporary bucket')
        assert len(rows)<1000
        for obj in rows:aws('s3api','delete-object','--bucket',BUCKET,'--key',obj['Key'])
        aws('s3api','delete-bucket','--bucket',BUCKET);save('bucket',None)
    if s.get('rule'):
        aws('events','remove-targets','--rule',GUARD,'--ids','guard');aws('events','delete-rule','--name',GUARD);save('rule',None)
    if s.get('function'):aws('lambda','delete-function','--function-name',GUARD);save('function',None)
    if s.get('profile'):
        aws('iam','remove-role-from-instance-profile','--instance-profile-name',ROLE,'--role-name',ROLE)
        aws('iam','delete-instance-profile','--instance-profile-name',ROLE);save('profile',None)
    for name in (ROLE,GUARD):
        if s.get(name):
            aws('iam','delete-role-policy','--role-name',name,'--policy-name','bounded-test');aws('iam','delete-role','--role-name',name);save(name,None)
    if s.get('security_group'):aws('ec2','delete-security-group','--group-id',s['security_group']);save('security_group',None)
    volumes=aws('ec2','describe-volumes','--filters',j([{'Name':'tag:MovieFactoryJob','Values':[JOB]}]))
    assert not volumes['Volumes'],'Residual tagged EBS needs explicit inspection'
    dump(OUT/'cleanup.json',{'instance_terminated':bool(s.get('instance')),'tagged_volumes':volumes['Volumes'],'temporary_resources_removed':True,'billing_actual_usd':None})
    if s.get('reservation'):ledger().settle(s['reservation'],cost_usd=None,response_id=s.get('instance'),error='Actual AWS billing pending; retain reservation, do not equate estimate with invoice')
    dump(OUT/'budget-final.json',ledger().summary());print('Temporary resources removed; billed amount remains unknown/reserved.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','guards','launch','retry_capacity','retry_capacity_d','prepare_a10','launch_a10','launch_a10b','status','retrieve','cleanup']);a=p.parse_args()
    globals()[a.operation]()
