"""Independent, read-only inventory of exact301 temporary resources after cleanup."""
import datetime
import json

import trellis301_cloud as m


def main():
    m.configure()
    c, aws = m.c, m.t.aws
    tags = c.j([{'Name': 'tag:MovieFactoryJob', 'Values': [c.JOB]}])
    instances = [i for r in aws('ec2', 'describe-instances', '--filters', tags)['Reservations'] for i in r['Instances']]
    remaining = {
        'instances': [i['InstanceId'] for i in instances if i['State']['Name'] != 'terminated'],
        'buckets': [x['Name'] for x in aws('s3api', 'list-buckets')['Buckets'] if x['Name'] == c.BUCKET],
        'roles': [x['RoleName'] for x in aws('iam', 'list-roles')['Roles'] if x['RoleName'] in (c.ROLE, c.GUARD)],
        'profiles': [x['InstanceProfileName'] for x in aws('iam', 'list-instance-profiles')['InstanceProfiles'] if x['InstanceProfileName'] == c.ROLE],
        'functions': [x['FunctionName'] for x in aws('lambda', 'list-functions')['Functions'] if x['FunctionName'] == c.GUARD],
        'rules': [x['Name'] for x in aws('events', 'list-rules', '--name-prefix', c.GUARD)['Rules'] if x['Name'] == c.GUARD],
        'groups': [x['GroupId'] for x in aws('ec2', 'describe-security-groups', '--filters', c.j([
            {'Name': 'group-name', 'Values': [c.JOB]}, {'Name': 'vpc-id', 'Values': [c.VPC]}]))['SecurityGroups']],
        'volumes': [x['VolumeId'] for x in aws('ec2', 'describe-volumes', '--filters', tags)['Volumes']],
    }
    now = datetime.datetime.now(datetime.timezone.utc)
    launch = c.OUT / 'launch.json'
    start = datetime.datetime.fromisoformat(json.loads(launch.read_text())['LaunchTime']) if launch.exists() else None
    seconds = (now - start).total_seconds() if start else None
    record = {'remaining': remaining, 'verified_utc': now.isoformat(),
        'terminated_instances': [i['InstanceId'] for i in instances if i['State']['Name'] == 'terminated'],
        'lifetime_upper_bound_seconds': seconds,
        'compute_estimate_upper_usd': seconds / 3600 * c.state()['rate'] if start else None,
        'actual_total_billed_usd': None, 'aggregate': m.aggregate()}
    c.dump(c.OUT / 'teardown-verification.json', record)
    if any(remaining.values()):
        raise RuntimeError('Residual owned301 resources; closure not verified')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
