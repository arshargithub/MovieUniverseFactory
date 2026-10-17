import datetime,importlib.util,sys,types
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load_guard(monkeypatch,instances):
    class EC2:
        terminated=[]
        filters=None
        def describe_instances(self,**kw):self.filters=kw;return {'Reservations':[{'Instances':instances}]}
        def terminate_instances(self,**kw):self.terminated+=kw['InstanceIds']
    ec2=EC2();monkeypatch.setitem(sys.modules,'boto3',types.SimpleNamespace(client=lambda *a,**k:ec2))
    spec=importlib.util.spec_from_file_location('guard293',ROOT/'scripts/trellis293_watchdog.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,ec2
def instance(age=0,expiry=3600):
    now=datetime.datetime.now(datetime.timezone.utc)
    return {'InstanceId':'i-test','LaunchTime':now-datetime.timedelta(seconds=age),
            'Tags':[{'Key':'ExpiresAt','Value':(now+datetime.timedelta(seconds=expiry)).isoformat()}]}
def test_guard_scopes_filter(monkeypatch):
    g,e=load_guard(monkeypatch,[]);assert g.handler({},None)['terminated']==[]
    assert e.filters['Filters'][0]=={'Name':'tag:MovieFactoryJob','Values':['trellis293-synthetic']}
def test_guard_preserves_unexpired(monkeypatch):
    g,e=load_guard(monkeypatch,[instance()]);g.handler({},None);assert not e.terminated
def test_guard_expires(monkeypatch):
    g,e=load_guard(monkeypatch,[instance(expiry=-1)]);g.handler({},None);assert e.terminated==['i-test']
def test_guard_hard_limit_not_extendable(monkeypatch):
    g,e=load_guard(monkeypatch,[instance(age=7201,expiry=99999)]);g.handler({},None);assert e.terminated==['i-test']
def test_missing_expiry_fails_closed(monkeypatch):
    row=instance();row['Tags']=[];g,e=load_guard(monkeypatch,[row]);g.handler({},None);assert e.terminated==['i-test']
