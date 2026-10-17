"""Independent scoped teardown inventory, bounded cost estimate and evidence gate."""
import datetime,json,shutil
import trellis294_cloud as t
from movie_factory import production_knowledge as pk
def main():
    t.configure();c=t.c;aws=t.aws
    recovered=c.LOCAL/'retrieved/evidence'
    for name in ('build.log','nvidia-smi.txt','exit-code.txt'):
        source=recovered/name
        if source.exists():shutil.copyfile(source,c.OUT/name)
    instances=aws('ec2','describe-instances','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':[c.JOB]}]))['Reservations']
    active=[i for r in instances for i in r['Instances'] if i['State']['Name']!='terminated']
    remaining={'instances':active,
        'buckets':[b['Name'] for b in aws('s3api','list-buckets')['Buckets'] if b['Name']==c.BUCKET],
        'roles':[r['RoleName'] for r in aws('iam','list-roles')['Roles'] if r['RoleName'] in {c.ROLE,c.GUARD}],
        'profiles':[r['InstanceProfileName'] for r in aws('iam','list-instance-profiles')['InstanceProfiles'] if r['InstanceProfileName']==c.ROLE],
        'functions':[f['FunctionName'] for f in aws('lambda','list-functions')['Functions'] if f['FunctionName']==c.GUARD],
        'rules':aws('events','list-rules','--name-prefix',c.GUARD)['Rules'],
        'groups':aws('ec2','describe-security-groups','--filters',c.j([{'Name':'group-name','Values':[c.JOB]}]))['SecurityGroups'],
        'volumes':aws('ec2','describe-volumes','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':[c.JOB]}]))['Volumes']}
    assert not any(remaining.values()),remaining
    now=datetime.datetime.now(datetime.timezone.utc)
    launch=json.loads((c.OUT/'launch.json').read_text())
    elapsed=(now-datetime.datetime.fromisoformat(launch['LaunchTime'].replace('Z','+00:00'))).total_seconds()
    # Poll-confirmed bound includes time after actual shutdown; not an invoice.
    c.dump(c.OUT/'teardown-verification.json',{'remaining':remaining,'terminated_instances':[i['InstanceId'] for r in instances for i in r['Instances']],
        'verified_utc':now.isoformat(),'lifetime_upper_bound_seconds':elapsed,'compute_estimate_upper_usd':elapsed/3600*c.state()['rate'],
        'actual_total_billed_usd':None,'aggregate':t.aggregate()})
    packet=c.packet()
    paths=[c.OUT/n for n in ('STRATEGY.md','README.md','preflight.json','guard-test.json','teardown-verification.json','tests.xml','blender-verification.json') if (c.OUT/n).exists()]
    evidence=[{'path':str(p.relative_to(c.ROOT)),'sha256':c.sha(p)} for p in paths]
    process={'authority','strategy','versioning','economics','current_state','sikh_scope'}
    review={'packet_digest':packet['packet_digest'],'checks':[{'id':o['id'],'kind':o['check_kind'],'status':'PASS' if o['id'] in process else 'NOT_RUN',
        'action_taken':'Bound synthetic-only US authority, cumulative10+5 reservation, exact dependency payload, scoped resource guards and verified teardown.',
        'observation':'Process evidence recorded; no production admission.' if o['id'] in process else 'Character, full inference rights and production review outside this synthetic infrastructure test.',
        'evidence':evidence} for o in packet['obligations']],
        'hypotheses':[{'prediction':'US quota may permit hardware unavailable in Canada.','observation':'One US L4 worker launched; outcome recorded in README and retained logs.','response':'Retrieve evidence and fully tear down; assess exporter separately from inference.','result':'resolved'}],
        'adjacent_regressions':'No production master modification, protagonist upload, weights or secret payload; historical Canadian reservation unchanged.',
        'stopping_reason':'Scoped worker attempt finished and removed; any runtime failure is preserved, not waived by local tests. Downstream production remains unqualified.'}
    c.dump(c.OUT/'review.json',review);gate=pk.check_review(c.ROOT,packet,review);c.dump(c.OUT/'gate.json',gate)
    print(json.dumps({'teardown_verified':True,'production_ready':gate['ready_for_review'],'compute_upper_estimate':elapsed/3600*c.state()['rate']}))
    return 0 if gate['ready_for_review'] else 2
if __name__=='__main__':raise SystemExit(main())
