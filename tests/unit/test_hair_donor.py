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

@pytest.mark.parametrize('job',[None,{}, {'operation':'live-preview','candidate':True},
    {'operation':'live-preview','candidate':4},{'operation':'live-preview','candidate':1,'code':'x'},
    {'operation':'live-verify','candidate':1}])
def test_live_rejects_unbounded_jobs(authored,job):
    with pytest.raises(ValueError):m.validate_live(job)

def test_live_output_preservation(authored):
    out=m.validate_live({'operation':'live-preview','candidate':1});out.mkdir()
    with pytest.raises(ValueError):m.validate_live({'operation':'live-preview','candidate':1})

def test_live_shape_is_bounded_hair_only():
    import math
    assert m.live_shape((.1,-.5,.8),1)==(.1,-.5,.8)
    assert m.live_shape((.5,.9,-.3),2)==(.5,.9,-.3)
    for x in (-1.,-.5,0.,.5,1.):
        for y in (-1.,0.,1.):
            for z in (-1.,0.,1.,1.5):
                q=m.live_shape((x,y,z),2)
                assert all(math.isfinite(v) for v in q)
                assert max(abs(a-b) for a,b in zip(q,(x,y,z)))<=.3

def test_third_live_shape_does_not_raise_or_recede_roots():
    for p in ((-.3,-.6,.9),(0,-.5,1.),(.6,-.2,.5)):
        q=m.live_shape(p,3)
        assert q[1:]==p[1:]
        assert 0<=q[0]-p[0]<=.29

def test_live_verify_rejects_changed_checkpoint(authored):
    import json
    out=authored/'donor23-live-preview-03';out.mkdir()
    (out/'result.json').write_text(json.dumps({'native_sha256':'wrong'}))
    (out/'diagnostic-live-groom.blend').write_bytes(b'changed')
    with pytest.raises(ValueError,match='Checkpoint changed'):
        m.validate_live({'operation':'live-verify','candidate':3})
