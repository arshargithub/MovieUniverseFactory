import importlib.util
import math
from pathlib import Path
import pytest

s = importlib.util.spec_from_file_location('hair_sculpt',Path('src/movie_factory/adapters/blender/hair_volume_sculpt.py'))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':4}, {'operation':'preview','candidate':1,'path':'x'}, {'operation':'repair','candidate':2}])
def test_invalid_job(job):
    with pytest.raises(ValueError): m.validate(job)


def test_pins_and_overwrite(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    m.validate({'operation':'preview','candidate':1}).mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview required'): m.validate({'operation':'package','candidate':1})
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})


def test_profile_tapers_and_is_finite():
    for t in (0,.1,.4,.8,1):
        for j in range(25):
            x,y=m.profile(t,j*math.pi/12,.2,.09)
            assert math.isfinite(x) and math.isfinite(y)
            assert abs(x)<=.201 and abs(y)<.11
            if t in (0,1): assert abs(x)+abs(y)<1e-7


def test_guides_and_spline():
    for points,w,d in m.guides(1):
        assert .04<d<w<.25
        assert m.spline(points,0)==points[0]
        assert max(abs(a-b) for a,b in zip(m.spline(points,1),points[-1]))<1e-7
        for k in range(101):
            x,y,z=m.spline(points,k/100)
            assert 0<x<1.1 and -1.15<y<.95 and -.15<z<1.6


def test_source_symlink_refused(tmp_path,monkeypatch):
    p=tmp_path/'real'; p.write_bytes(b'fixed'); link=tmp_path/'link'; link.symlink_to(p)
    monkeypatch.setattr(m,'SOURCE',link); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':1})


def test_reference_change_refused(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed'); r=tmp_path/'front.png'; r.write_bytes(b'approved')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFBASE',tmp_path)
    monkeypatch.setattr(m,'REFERENCES',{'front.png':m.digest(r)})
    m.validate({'operation':'repair','candidate':3})
    r.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'repair','candidate':3})
