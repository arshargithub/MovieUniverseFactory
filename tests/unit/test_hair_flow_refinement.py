import importlib.util
import json
import math
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('flow',Path('src/movie_factory/adapters/blender/hair_flow_refinement.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':7}, {'operation':'preview','candidate':1,'path':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError): m.validate(job)

def test_validate(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    out=m.validate({'operation':'preview','candidate':1}); out.mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview'): m.validate({'operation':'package','candidate':1})
    r=out/'result.json'
    r.write_text(json.dumps({'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True,'hairline_geometry_exact':False}))
    with pytest.raises(ValueError,match='Stale'): m.validate({'operation':'package','candidate':1})
    r.write_text(json.dumps({'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True,'hairline_geometry_exact':True}))
    assert m.validate({'operation':'package','candidate':1}).name=='hairflow-package-01'
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})

@pytest.mark.parametrize('candidate',[1,2,3,4,5,6])
def test_root_and_lower_uv_exact_and_bounded(candidate):
    for i in range(17):
        for z in (.28,.5,1.2):
            p=(.5,.5,z)
            assert m.lower_wave(p,p,i,candidate)==p
        for z in (-2,-1,0):
            p=(.6,.6,z); q=m.lower_wave(p,p,i,candidate)
            assert all(math.isfinite(x) for x in q) and math.dist(p,q)<.4
    for x in (-1,0,1):
        assert m.crown_uv(x,-.8,.90,(.3,.8),candidate)==(.3,.8)
        for y in (-1,0,1):
            for z in (1.1,1.4,1.7):
                assert all(0<v<1 for v in m.crown_uv(x,y,z,(.3,.8),candidate))

def test_rear_art_uv_is_bounded():
    for i in range(21):
        for j in range(31):
            assert all(0<v<1 for v in m.rear_art_uv(i/20-.5,1.6-j*.13))

def test_texture_pin_and_symlink(tmp_path,monkeypatch):
    source=tmp_path/'source'; source.write_bytes(b'fixed')
    tex=tmp_path/'painted'; tex.write_bytes(b'painted')
    monkeypatch.setattr(m,'SOURCE',source); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source))
    monkeypatch.setattr(m,'REFERENCES',{}); monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'PAINTED_TEXTURE',tex); monkeypatch.setattr(m,'PAINTED_TEXTURE_SHA',m.digest(tex))
    assert m.validate({'operation':'preview','candidate':6}).name=='hairflow-preview-06'
    tex.write_bytes(b'changed')
    with pytest.raises(ValueError,match='texture'): m.validate({'operation':'preview','candidate':6})
    link=tmp_path/'link'; link.symlink_to(source); monkeypatch.setattr(m,'SOURCE',link)
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':3})
