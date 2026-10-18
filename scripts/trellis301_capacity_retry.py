"""Same-region capacity retry after proved absence; never a second GPU worker."""
import datetime
import argparse
from pathlib import Path
import trellis301_cascade as m


def main(zone='us-east-1b'):
    if zone not in ('us-east-1b','us-east-1c','us-east-1d'):
        raise ValueError('Unadmitted zone')
    m.configure();m.frozen();m.export.no_active()
    c,t=m.c,m.t
    token=c.JOB+'-one-worker'
    prior=t.aws('ec2','describe-instances','--filters',c.j([{'Name':'client-token','Values':[token]}]))
    if prior['Reservations'] or c.state().get('instance') or c.state().get('worker_created'):
        raise RuntimeError('A worker already exists; retry prohibited')
    subnets=t.aws('ec2','describe-subnets','--filters',c.j([
        {'Name':'vpc-id','Values':[c.VPC]}, {'Name':'availability-zone','Values':[zone]},
        {'Name':'default-for-az','Values':['true']}]))['Subnets']
    if len(subnets)!=1 or subnets[0]['AvailableIpAddressCount']<1:
        raise RuntimeError('No admitted default subnet')
    c.dump(m.OUT/f'capacity-retry-{zone}.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'prior_outcome':'Prior capacity failure; zero matching workers independently confirmed',
        'subnet':subnets[0],'client_token':token,'reservation_unchanged':c.state()['reservation'],
        'source_sha256':c.sha(Path(__file__)),'aggregate':m.aggregate()})
    c.SUBNET=subnets[0]['SubnetId']
    try:
        m.launch(reviewed=True)
    except RuntimeError as exc:
        c.dump(m.OUT/f'launch-failure-{zone}.json',{'error':str(exc),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--zone',choices=['us-east-1b','us-east-1c','us-east-1d'],default='us-east-1b')
    main(parser.parse_args().zone)
