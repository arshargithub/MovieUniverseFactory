"""Read-only cloud teardown verification and honest qualification handoff record."""
import hashlib,json
from pathlib import Path
from trellis293_cloud import ROOT,OUT,JOB,BUCKET,ROLE,GUARD,aws,dump,state
from movie_factory import production_knowledge as pk
def ev(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    instances=aws('ec2','describe-instances','--filters',json.dumps([{'Name':'tag:MovieFactoryJob','Values':[JOB]}]))['Reservations']
    buckets=aws('s3api','list-buckets')['Buckets'];roles=aws('iam','list-roles')['Roles']
    profiles=aws('iam','list-instance-profiles')['InstanceProfiles'];functions=aws('lambda','list-functions')['Functions']
    rules=aws('events','list-rules','--name-prefix',GUARD)['Rules']
    groups=aws('ec2','describe-security-groups','--filters',json.dumps([{'Name':'group-name','Values':[JOB]}]))['SecurityGroups']
    volumes=aws('ec2','describe-volumes','--filters',json.dumps([{'Name':'tag:MovieFactoryJob','Values':[JOB]}]))['Volumes']
    remaining={'instances':instances,'buckets':[b['Name'] for b in buckets if b['Name']==BUCKET],
        'roles':[r['RoleName'] for r in roles if r['RoleName'] in {ROLE,GUARD}],
        'profiles':[r['InstanceProfileName'] for r in profiles if r['InstanceProfileName']==ROLE],
        'functions':[f['FunctionName'] for f in functions if f['FunctionName']==GUARD],
        'rules':rules,'security_groups':groups,'volumes':volumes}
    assert not any(remaining.values()),remaining
    dump(OUT/'teardown-verification.json',{'remaining':remaining,'gpu_instance_ever_created':False,
        'synthetic_gpu_probe':'NOT_RUN_CAPACITY_UNAVAILABLE','compute_cost_usd':0,'support_services_actual_usd':None})
    packet=json.loads((OUT/'packet.json').read_text())
    evidence=[ev(OUT/n) for n in ('STRATEGY.md','README.md','preflight.json','guard-test.json','teardown-verification.json','tests.xml')]
    process={'authority','strategy','versioning','economics','current_state','sikh_scope'}
    checks=[{'id':o['id'],'kind':o['check_kind'],'status':'PASS' if o['id'] in process else 'NOT_RUN',
        'action_taken':'Applied approved synthetic-only scope, exact source payload, private resource controls, budget reservation and teardown; retained all unrun production gates.',
        'observation':'Scoped process evidence is recorded; no production acceptance.' if o['id'] in process else 'GPU execution blocked by regional capacity. No new asset, performance, full runtime rights or production quality claim.',
        'evidence':evidence} for o in packet['obligations']]
    review={'packet_digest':packet['packet_digest'],'checks':checks,
      'hypotheses':[{'prediction':'Quota approval may not ensure available hardware.','observation':'Live quota8; five type/zone requests rejected for capacity; no instance created.','response':'Preserve fixture package, stop retries, verify full support-resource teardown.','result':'resolved'}],
      'adjacent_regressions':'Production masters unchanged. No model images/weights or credentials uploaded. Temporary synthetic input removed after retaining local payload.',
      'stopping_reason':'Genuine regional capacity blocker after all offered L4 and A10G zones; no US launch authority inferred. GPU qualification and production remain blocked.'}
    dump(OUT/'review.json',review);gate=pk.check_review(ROOT,packet,review);dump(OUT/'gate.json',gate)
    print(json.dumps({'teardown_verified':True,'production_ready':gate['ready_for_review'],'failures':gate['failures']}))
    return 2
if __name__=='__main__':raise SystemExit(main())
