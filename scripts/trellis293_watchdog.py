"""Cloud-side guard: only this exact job tag, never arbitrary IDs from input."""
import datetime
import boto3

TAG = 'trellis293-synthetic'
def handler(event, context):
    client=boto3.client('ec2',region_name='ca-central-1')
    rows=client.describe_instances(Filters=[{'Name':'tag:MovieFactoryJob','Values':[TAG]},
        {'Name':'instance-state-name','Values':['pending','running','stopping','stopped']}])
    now=datetime.datetime.now(datetime.timezone.utc)
    expired=[];seen=[]
    for reservation in rows['Reservations']:
        for instance in reservation['Instances']:
            tags={t['Key']:t['Value'] for t in instance.get('Tags',[])}
            # Missing/malformed expiration fails closed for this exact job only.
            try: deadline=datetime.datetime.fromisoformat(tags['ExpiresAt'])
            except (KeyError,ValueError): deadline=now
            hard=instance['LaunchTime']+datetime.timedelta(seconds=7200)
            seen.append(instance['InstanceId'])
            if now>=min(deadline,hard):expired.append(instance['InstanceId'])
    if expired:client.terminate_instances(InstanceIds=expired)
    return {'job':TAG,'seen':seen,'terminated':expired,'utc':now.isoformat()}
