import importlib.util
from pathlib import Path
import pytest
import hashlib
from types import SimpleNamespace

s=importlib.util.spec_from_file_location('donor',Path('src/movie_factory/adapters/blender/hair_donor.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'hair_fit','output_name':'../escape'}, {'operation':'python','code':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

@pytest.fixture
def authored(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(Path('src/movie_factory/adapters/blender').resolve()))
    import hair_native_groom as g
    source=tmp_path/'source.blend';source.write_bytes(b'native')
    reference=tmp_path/'reference.png';reference.write_bytes(b'approved')
    asset=tmp_path/'asset.obj';asset.write_bytes(b'mesh')
    demo=tmp_path/'demo.blend';demo.write_bytes(b'demo')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    monkeypatch.setattr(g,'SOURCE',source);monkeypatch.setattr(g,'SOURCE_SHA',digest(source))
    monkeypatch.setattr(g,'REFBASE',tmp_path);monkeypatch.setattr(g,'REFERENCES',{reference.name:digest(reference)})
    monkeypatch.setattr(m,'BASE',tmp_path);monkeypatch.setattr(m,'AUTHORED',tmp_path)
    monkeypatch.setattr(m,'AUTHORED_PINS',{asset.name:digest(asset)})
    monkeypatch.setattr(m,'DEMO',demo);monkeypatch.setattr(m,'DEMO_SHA',digest(demo))
    monkeypatch.setattr(m.shutil,'disk_usage',lambda p:SimpleNamespace(free=10_000_000_000))
    return tmp_path

@pytest.mark.parametrize('job',[None,{}, {'operation':'authored-fit','candidate':True},
    {'operation':'authored-fit','candidate':0},{'operation':'authored-fit','candidate':4},
    {'operation':'authored-fit','candidate':'1'}, {'operation':'exec','candidate':1},
    {'operation':'authored-fit','candidate':1,'code':'x'}])
def test_authored_rejects_unstructured_jobs(authored,job):
    with pytest.raises(ValueError):m.validate_authored(job)

def test_authored_allows_fresh_pinned_job(authored):
    assert m.validate_authored({'operation':'authored-fit','candidate':1})==authored/'authored-donor22-01'

@pytest.mark.parametrize('name',['source.blend','reference.png','asset.obj'])
def test_authored_rejects_changed_inputs(authored,name):
    (authored/name).write_bytes(b'changed')
    with pytest.raises(ValueError):m.validate_authored({'operation':'authored-fit','candidate':1})

@pytest.mark.parametrize('symlink',[False,True])
def test_authored_preserves_existing_outputs(authored,symlink):
    out=authored/'authored-donor22-01'
    if symlink:out.symlink_to(authored/'missing')
    else:out.mkdir()
    with pytest.raises(ValueError):m.validate_authored({'operation':'authored-fit','candidate':1})

def test_authored_rejects_low_disk(authored,monkeypatch):
    monkeypatch.setattr(m.shutil,'disk_usage',lambda p:SimpleNamespace(free=1))
    with pytest.raises(ValueError):m.validate_authored({'operation':'authored-fit','candidate':1})

@pytest.mark.parametrize('job',[None,{}, {'operation':'fit-demo','candidate':4},{'operation':'inspect-demo','code':'x'}])
def test_demo_rejects_extra_keys(authored,job):
    with pytest.raises(ValueError):m.validate_demo(job)

def test_demo_fit_shares_third_variant_output_guard(authored):
    assert m.validate_demo({'operation':'fit-demo'})==authored/'authored-donor22-03'
    (authored/'authored-donor22-03').mkdir()
    with pytest.raises(ValueError):m.validate_demo({'operation':'fit-demo'})

def test_demo_changed_native_rejected(authored):
    m.DEMO.write_bytes(b'changed')
    with pytest.raises(ValueError):m.validate_demo({'operation':'inspect-demo'})

def test_demo_symlink_rejected(authored):
    target=authored/'copy.blend';target.write_bytes(m.DEMO.read_bytes())
    m.DEMO.unlink();m.DEMO.symlink_to(target)
    with pytest.raises(ValueError):m.validate_demo({'operation':'inspect-demo'})
