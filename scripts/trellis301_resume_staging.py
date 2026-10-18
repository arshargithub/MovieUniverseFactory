"""Restore exact approved staging after pre-launch cleanup; reuse unlaunched hold."""
import json
import time
from pathlib import Path
import trellis301_cascade as m


def main():
    m.configure();c,t=m.c,m.t
    m.frozen();m.export.no_active();m.aggregate()
    s=c.state()
    if s.get('instance') or s.get('worker_created') or not s.get('reservation'):
        raise RuntimeError('Only never-launched reserved attempt may resume')
    summary=m.ledger().summary()
    if summary['calls']!=1 or summary['reserved_unknown_usd']!=3.5:
        raise RuntimeError('Original single reservation must remain intact')
    if not json.loads((m.OUT/'cleanup.json').read_text())['temporary_resources_removed']:
        raise RuntimeError('Prior staging cleanup required')
    payload=json.loads((m.OUT/'payload.json').read_text())
    if payload['payload_sha256']!='20a6d3d0d01d93f28840d6c572a33912eddfe72345c600010e7b04d69c8b1f46' or payload['encoder_sha256']!='e2608d00bb9a3db55f940f22314cf8e6288290ace107ee122f7757d8c3aa19eb':
        raise RuntimeError('Exact Director-approved payload changed')
    # Read-only absence checks before recreating the same exact resources.
    if any(b['Name']==c.BUCKET for b in t.aws('s3api','list-buckets')['Buckets']): raise RuntimeError('Bucket still exists')
    if any(r['RoleName'] in (c.ROLE,c.GUARD) for r in t.aws('iam','list-roles')['Roles']): raise RuntimeError('Roles still exist')
    if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[c.JOB+'-one-worker']}]))['Reservations']:
        raise RuntimeError('An earlier worker exists')
    c.save('guard_verified',False);c.save('encoder_uploaded',False)
    t.aws('s3api','create-bucket','--bucket',c.BUCKET);c.save('bucket',c.BUCKET)
    t.aws('s3api','put-public-access-block','--bucket',c.BUCKET,'--public-access-block-configuration',c.j(dict(BlockPublicAcls=True,IgnorePublicAcls=True,BlockPublicPolicy=True,RestrictPublicBuckets=True)))
    t.aws('s3api','put-bucket-encryption','--bucket',c.BUCKET,'--server-side-encryption-configuration',c.j({'Rules':[{'ApplyServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]}))
    t.aws('s3api','put-bucket-lifecycle-configuration','--bucket',c.BUCKET,'--lifecycle-configuration',c.j({'Rules':[{'ID':'temporary-only','Status':'Enabled','Filter':{'Prefix':''},'Expiration':{'Days':1},'AbortIncompleteMultipartUpload':{'DaysAfterInitiation':1}}]}))
    t.aws('s3api','put-bucket-policy','--bucket',c.BUCKET,'--policy',c.j({'Version':'2012-10-17','Statement':[{'Effect':'Deny','Principal':'*','Action':'s3:*','Resource':['arn:aws:s3:::'+c.BUCKET,'arn:aws:s3:::'+c.BUCKET+'/*'],'Condition':{'Bool':{'aws:SecureTransport':'false'}}}]}))
    t.aws('s3api','put-object','--bucket',c.BUCKET,'--key','input/payload.tar.gz','--body',m.LOCAL/'payload.tar.gz')
    t.aws('s3','cp',m.ENCODER,'s3://'+c.BUCKET+'/input/encoder.tar','--only-show-errors',raw=True);c.save('encoder_uploaded',True)
    c.role(c.ROLE,'ec2.amazonaws.com',[{'Effect':'Allow','Action':'s3:GetObject','Resource':'arn:aws:s3:::'+c.BUCKET+'/input/*'},
        {'Effect':'Allow','Action':'s3:PutObject','Resource':'arn:aws:s3:::'+c.BUCKET+'/output/*'}])
    t.aws('iam','create-instance-profile','--instance-profile-name',c.ROLE);c.save('profile',c.ROLE)
    t.aws('iam','add-role-to-instance-profile','--instance-profile-name',c.ROLE,'--role-name',c.ROLE)
    arn=c.role(c.GUARD,'lambda.amazonaws.com',[{'Effect':'Allow','Action':'ec2:DescribeInstances','Resource':'*'},
        {'Effect':'Allow','Action':'ec2:TerminateInstances','Resource':f'arn:aws:ec2:us-east-1:{c.ACCOUNT}:instance/*','Condition':{'StringEquals':{'ec2:ResourceTag/MovieFactoryJob':c.JOB}}}])
    time.sleep(10)
    fn=t.aws('lambda','create-function','--function-name',c.GUARD,'--runtime','python3.12','--role',arn,'--handler','watchdog.handler','--timeout','30','--memory-size','128','--zip-file','fileb://'+str(m.LOCAL/'watchdog.zip'))
    c.save('function',fn['FunctionArn']);t.aws('lambda','wait','function-active-v2','--function-name',c.GUARD)
    rule=t.aws('events','put-rule','--name',c.GUARD,'--schedule-expression','rate(5 minutes)','--state','ENABLED');c.save('rule',rule['RuleArn'])
    t.aws('lambda','add-permission','--function-name',c.GUARD,'--statement-id','scheduled-guard','--action','lambda:InvokeFunction','--principal','events.amazonaws.com','--source-arn',rule['RuleArn'])
    if t.aws('events','put-targets','--rule',c.GUARD,'--targets',c.j([{'Id':'guard','Arn':fn['FunctionArn']}]))['FailedEntryCount']:
        raise RuntimeError('Watchdog scheduling failed')
    result=t.aws('lambda','invoke','--function-name',c.GUARD,m.LOCAL/'guard-test.json')
    observed=json.loads((m.LOCAL/'guard-test.json').read_text())
    if 'FunctionError' in result or observed['seen'] or observed['terminated']: raise RuntimeError('Guard test failed')
    c.dump(m.OUT/'guard-restored-test.json',observed);c.save('guard_verified',True)
    sg=t.aws('ec2','create-security-group','--group-name',c.JOB,'--description','Approved private comparison no inbound','--vpc-id',c.VPC)['GroupId'];c.save('security_group',sg)
    group=t.aws('ec2','describe-security-groups','--group-ids',sg)['SecurityGroups'][0]
    if group['IpPermissions']: raise RuntimeError('Inbound access prohibited')
    c.dump(m.OUT/'security-group-restored.json',group)
    c.dump(m.OUT/'staging-restored.json',{'source_sha256':c.sha(Path(__file__)),
        'authority':'Director exact payload consent after launch safety rejection302',
        'reservation_id':s['reservation'],'budget':m.aggregate(),'gpu_launches':0,
        'original_payload_hashes_unchanged':True})
    print('Exact approved staging restored; same single reservation; no GPU launched')


if __name__=='__main__':main()
