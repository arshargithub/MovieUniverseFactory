import importlib,sys,types,zipfile,datetime
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    sys.modules.pop('trellis294_cloud',None);sys.modules.pop('trellis293_cloud',None)
    m=importlib.import_module('trellis294_cloud');m.configure();return m
def test_cumulative_cap(controller,monkeypatch):
    m=controller
    ledger=lambda value:types.SimpleNamespace(summary=lambda:{'committed_usd':value})
    monkeypatch.setattr(m,'OLD_LEDGER',lambda:ledger(10));monkeypatch.setattr(m,'ledger',lambda:ledger(0))
    assert m.aggregate(5)['committed_plus_proposed_usd']==15
    with pytest.raises(RuntimeError):m.aggregate(5.01)
def test_region_explicit(controller,monkeypatch):
    calls=[];monkeypatch.setattr(controller,'BASE_AWS',lambda *a,**kw:calls.append(kw))
    controller.aws('ec2','describe-instances');assert calls[0]['region']=='us-east-1'
def test_prior_worker_cannot_retry(controller,monkeypatch):
    monkeypatch.setattr(controller.c,'state',lambda:{'guard_verified':True,'worker_created':True})
    with pytest.raises(AssertionError):controller.launch()
def test_us_guard_exact_scope(monkeypatch):
    calls=[]
    class EC2:
        def describe_instances(self,**kw):calls.append(kw);return {'Reservations':[]}
    monkeypatch.setitem(sys.modules,'boto3',types.SimpleNamespace(client=lambda *a,**kw:(calls.append(kw) or EC2())))
    with zipfile.ZipFile(ROOT/'.runtime/trellis294/watchdog.zip') as z:source=z.read('watchdog.py')
    ns={};exec(compile(source,'reviewed-watchdog','exec'),ns);ns['handler']({},None)
    assert calls[0]['region_name']=='us-east-1'
    assert calls[1]['Filters'][0]['Values']==['trellis294-synthetic']

def test_nested_venv_reproduces_and_corrects_parent_visibility(tmp_path,monkeypatch):
    import subprocess,venv
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    from trellis294_runtime import describe,link_parent_packages
    parent=tmp_path/'parent';child=tmp_path/'child'
    venv.EnvBuilder(with_pip=False,symlinks=True).create(parent);pp=parent/'bin/python'
    info=describe(pp);module=Path(info['purelib'])/'mf_parent_only_probe.py';module.write_text('VALUE = 294\n')
    subprocess.run([str(pp),'-m','venv','--without-pip','--system-site-packages',str(child)],check=True)
    cp=child/'bin/python'
    assert subprocess.run([str(cp),'-c','import mf_parent_only_probe'],capture_output=True).returncode!=0
    link_parent_packages(pp,cp,parent,child)
    subprocess.run([str(cp),'-c','import mf_parent_only_probe; assert mf_parent_only_probe.VALUE == 294'],check=True)
    with pytest.raises(ValueError):link_parent_packages(pp,cp,parent,child)

def test_runtime_link_rejects_wrong_prefix(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    import trellis294_runtime as r
    monkeypatch.setattr(r,'describe',lambda p:{'prefix':'/unexpected','purelib':'/unexpected/site-packages','version':[3,12]})
    with pytest.raises(ValueError):r.link_parent_packages('a','b',tmp_path/'parent',tmp_path/'child')
