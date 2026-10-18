"""Same single approved worker in alternate zones after explicit capacity failure."""
import datetime
import trellis303_cloud as m


def main():
    m.configure();m.frozen()
    c,t=m.c,m.t
    for zone in ('us-east-1b','us-east-1c','us-east-1d'):
        m.no_active()
        if t.aws('ec2','describe-instances','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':[c.JOB]}]))['Reservations']:
            raise RuntimeError('Any created instance consumes the one-worker authority')
        subnets=t.aws('ec2','describe-subnets','--filters',c.j([{'Name':'vpc-id','Values':[c.VPC]},
            {'Name':'availability-zone','Values':[zone]},{'Name':'default-for-az','Values':['true']}]))['Subnets']
        if len(subnets)!=1:raise RuntimeError('Ambiguous subnet')
        c.dump(m.OUT/('capacity-'+zone+'.json'),{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'subnet':subnets[0], 'reason':'Same approved48GB worker; previous zone capacity failure created no instance',
            'source_sha256':c.sha(__import__('pathlib').Path(__file__)), 'aggregate':m.aggregate()})
        c.save('subnet',subnets[0]['SubnetId'])
        try:
            m.launch(True)
        except RuntimeError as exc:
            c.dump(m.OUT/('capacity-failure-'+zone+'.json'),{'error':str(exc)})
            if 'InsufficientInstanceCapacity' not in str(exc):raise
            continue
        return
    raise RuntimeError('No capacity; no additional instance or budget authorized')


if __name__=='__main__':main()
