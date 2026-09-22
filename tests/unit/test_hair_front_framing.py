import importlib.util
import json
import math
from pathlib import Path
import pytest
import sys
sys.path.insert(0,str(Path('src/movie_factory/adapters/blender').resolve()))

s=importlib.util.spec_from_file_location('framing',Path('src/movie_factory/adapters/blender/hair_front_framing.py'))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1},{'operation':'preview','candidate':True},{'operation':'preview','candidate':4},{'operation':'preview','candidate':1,'path':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError): m.validate(job)


def test_validation(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    m.validate({'operation':'preview','candidate':1}).mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview'): m.validate({'operation':'package','candidate':1})
    r=tmp_path/'framing-preview-01/result.json'
    for h,ok in [('stale',True),(m.digest(Path(m.__file__)),False)]:
        r.write_text(json.dumps({'handler_sha256':h,'protected_exact':ok}))
        with pytest.raises(ValueError,match='Stale'): m.validate({'operation':'package','candidate':1})
    r.write_text(json.dumps({'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True}))
    assert m.validate({'operation':'package','candidate':1}).name=='framing-package-01'
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})


@pytest.mark.parametrize('candidate',[1,2,3])
def test_bounded_hair_warp_and_guides(candidate):
    for x in (-1,0,1):
        for y in (-1,0,1):
            for z in (-2,0,.5,1,2):
                p=m.warp(x,y,z,candidate)
                assert all(math.isfinite(v) for v in p)
                assert math.dist(p,(x,y,z)) < .30
    for layer in range(3):
        a,b=m.guide(layer,-1),m.guide(layer,1)
        assert len(a)==len(b)
        assert all(p[0]<0 for p in a) and all(p[0]>0 for p in b)


def test_upper_uv_and_repair_guard():
    for x in (-1,-.5,0,.5,1):
        for z in (1.02,1.2,1.4):
            assert all(0<v<1 for v in m.upper_reference_uv(x,z))
    with pytest.raises(ValueError,match='third-candidate'):
        m.validate({'operation':'repair','candidate':1})
