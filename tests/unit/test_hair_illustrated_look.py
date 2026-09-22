import importlib.util
import math
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('hair_look',Path('src/movie_factory/adapters/blender/hair_illustrated_look.py'))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':7}, {'operation':'preview','candidate':1,'code':'x'}, {'operation':'retry','candidate':1}])
def test_invalid(job):
    with pytest.raises(ValueError): m.validate(job)


def test_validation(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    m.validate({'operation':'preview','candidate':1}).mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview'): m.validate({'operation':'package','candidate':1})
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})


def test_envelope():
    assert m.envelope(0)==0
    assert m.envelope(1)<1e-6
    assert m.envelope(.5)==1
    assert all(math.isfinite(m.envelope(i/100)) for i in range(101))


def test_hair_only_uv_bounds():
    for x in (-1,-.7,0,.7,1):
        for z in (.1,.4,.8,1.1,1.4):
            u,v=m.reference_uv(x,z)
            assert .2<u<.78 and .57<v<.88


def test_symlink(tmp_path,monkeypatch):
    p=tmp_path/'real'; p.write_bytes(b'fixed'); link=tmp_path/'link'; link.symlink_to(p)
    monkeypatch.setattr(m,'SOURCE',link); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':1})


def test_reference_pin(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed'); r=tmp_path/'front.png'; r.write_bytes(b'approved')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFBASE',tmp_path)
    monkeypatch.setattr(m,'REFERENCES',{'front.png':m.digest(r)})
    m.validate({'operation':'repair','candidate':6})
    r.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'repair','candidate':6})


def test_package_requires_current_protected_preview(tmp_path,monkeypatch):
    import json
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    report=tmp_path/'hair-look-repair-06/result.json'; report.parent.mkdir()
    for record in ({'protected_exact':False,'handler_sha256':m.digest(Path(m.__file__))}, {'protected_exact':True,'handler_sha256':'stale'}):
        report.write_text(json.dumps(record))
        with pytest.raises(ValueError,match='Stale'): m.validate({'operation':'package','candidate':6})
    report.write_text(json.dumps({'protected_exact':True,'handler_sha256':m.digest(Path(m.__file__))}))
    assert m.validate({'operation':'package','candidate':6})==tmp_path/'hair-look-package-06'
