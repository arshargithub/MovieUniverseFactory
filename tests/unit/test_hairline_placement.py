import importlib.util
import json
import math
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('hairline',Path('src/movie_factory/adapters/blender/hairline_placement.py'))
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
    r=tmp_path/'hairline-preview-01/result.json'
    for h,ok in [('stale',True),(m.digest(Path(m.__file__)),False)]:
        r.write_text(json.dumps({'handler_sha256':h,'protected_exact':ok}))
        with pytest.raises(ValueError,match='Stale'): m.validate({'operation':'package','candidate':1})
    r.write_text(json.dumps({'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True}))
    assert m.validate({'operation':'package','candidate':1}).name=='hairline-package-01'
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})


def test_lift_localized():
    assert m.displacement(0,-.8,.6,1)==.15
    assert m.displacement(0,.5,.6,1)==0
    assert m.displacement(1,.0,.2,1)==0
    assert m.displacement(0,-.8,-.2,1)==0
    assert m.displacement(0,-.8,1.4,1)==0
    for x in (-1,0,1):
        for y in (-1,0,1):
            for z in (-1,0,.5,1,1.5):
                assert 0<=m.displacement(x,y,z,2)<=.15
                assert math.isfinite(m.crown_flow(x,y,z))
