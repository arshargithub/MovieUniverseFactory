import importlib,json,sys,types
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    for name in ('trellis295_cloud','trellis294_cloud','trellis293_cloud'):
        sys.modules.pop(name,None)
    m=importlib.import_module('trellis295_cloud');m.configure('a');return m

def test_total_cap_and_unknown_cost(controller,monkeypatch):
    m=controller
    monkeypatch.setattr(m,'ledger',lambda:types.SimpleNamespace(summary=lambda:{'committed_usd':9}))
    result=m.aggregate(4)
    assert result['admission_total_usd']==15
    assert result['closed_actual_bill_usd'] is None
    assert result['conditional_extra_usd_activated']==0
    with pytest.raises(RuntimeError):m.aggregate(4.01)

def test_attempt_isolation(controller):
    m=controller;m.configure('b')
    assert m.c.JOB=='trellis295b-synthetic'
    assert m.c.STATE.parent.name=='trellis295b'
    assert m.c.BUCKET=='mf-trellis295b-281482331395'

def test_overlap_blocks(controller,monkeypatch):
    monkeypatch.setattr(controller.t,'aws',lambda *a,**kw:{'Reservations':[{'Instances':[{}]}]})
    with pytest.raises(AssertionError):controller.no_prior_active()

def test_fixed_entrypoint(controller,monkeypatch):
    m=controller;seen={}
    monkeypatch.setattr(m,'no_prior_active',lambda:None)
    monkeypatch.setattr(m.c,'userdata',lambda:'python scripts/trellis293_worker.py')
    monkeypatch.setattr(m.t,'launch',lambda *a,**kw:seen.update(script=m.c.userdata(),**kw))
    m.launch('us-east-1a')
    assert seen=={'script':'python scripts/trellis294_worker.py','reserved_usd':4,'client_token':'trellis295a-one-worker'}

def test_cleanup_inventory_catches_untagged_named_group(controller,monkeypatch,tmp_path):
    sys.modules.pop('trellis295_verify_cleanup',None)
    v=importlib.import_module('trellis295_verify_cleanup');m=controller
    monkeypatch.setattr(m,'configure',lambda attempt:None)
    monkeypatch.setattr(m.c,'OUT',tmp_path)
    monkeypatch.setattr(m.c,'state',lambda:{'retrieved':True,'rate':.9776})
    monkeypatch.setattr(m,'aggregate',lambda:{'admission_total_usd':6})
    (tmp_path/'launch.json').write_text(json.dumps({'LaunchTime':'2026-10-17T19:43:00+00:00'}))
    def aws(service,op,*args):
        keys={'describe-instances':'Reservations','list-buckets':'Buckets','list-roles':'Roles',
              'list-instance-profiles':'InstanceProfiles','list-functions':'Functions','list-rules':'Rules',
              'describe-volumes':'Volumes'}
        if op=='describe-security-groups':
            filters=json.loads(args[1]);assert filters[0]['Name']=='group-name'
            return {'SecurityGroups':[{'GroupId':'sg-residual'}]}
        return {keys[op]:[]}
    monkeypatch.setattr(m.t,'aws',aws)
    with pytest.raises(AssertionError,match='Residual owned resources'):v.main('a')
