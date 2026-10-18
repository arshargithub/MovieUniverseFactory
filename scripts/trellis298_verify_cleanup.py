"""Independent read-only inventory for exact298 attempt resources."""
import argparse
import datetime
import json
import trellis298_cloud as m


def main(attempt):
    m.configure(attempt)
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
        'groups': [x['GroupId'] for x in aws('ec2', 'describe-security-groups', '--filters', c.j([{'Name': 'group-name', 'Values': [c.JOB]}, {'Name': 'vpc-id', 'Values': [c.VPC]}]))['SecurityGroups']],
        'volumes': [x['VolumeId'] for x in aws('ec2', 'describe-volumes', '--filters', tags)['Volumes']],
    }
    now = datetime.datetime.now(datetime.timezone.utc)
    start = datetime.datetime.fromisoformat(json.loads((c.OUT / 'launch.json').read_text())['LaunchTime'])
    seconds = (now - start).total_seconds()
    record = {'remaining': remaining, 'verified_utc': now.isoformat(),
              'terminated_instances': [i['InstanceId'] for i in instances if i['State']['Name'] == 'terminated'],
              'lifetime_upper_bound_seconds': seconds,
              'compute_estimate_upper_usd': seconds / 3600 * c.state()['rate'],
              'actual_total_billed_usd': None, 'aggregate': (m.continuation_aggregate() if attempt in ('c', 'd') else m.prior.aggregate())}
    c.dump(c.OUT / 'teardown-verification.json', record)
    assert not any(remaining.values()), 'Residual owned resources'
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', choices=['a', 'b', 'c', 'd'], required=True)
    main(parser.parse_args().attempt)
