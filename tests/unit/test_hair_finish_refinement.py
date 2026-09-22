import importlib.util
import math
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('hair_finish',Path('src/movie_factory/adapters/blender/hair_finish_refinement.py'))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':4}, {'operation':'preview','candidate':1,'path':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError): m.validate(job)


def test_validation(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p)); monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    m.validate({'operation':'preview','candidate':1}).mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview'): m.validate({'operation':'package','candidate':3})
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})


def test_hair_uv_and_lift():
    for x in (-1,-.7,-.3,0,.3,.7,1):
        for z in (-1,.1,.5,.8,1.1,1.4):
            u,v=m.hair_uv(x,z); py=1647*(1-v); px=955*u
            assert .2<u<.8 and .5<v<.9
            assert 200<py<700
            assert 0<=m.lift(x,-.6,z)<=.046
    assert m.lift(-.38,-.71,1.05)>m.lift(.38,-.71,1.05)*10


def test_guides_bounded_and_unequal():
    guides=[m.guide(i) for i in range(17)]
    assert len({round(g[-1][2],3) for g in guides})>10
    for g in guides:
        assert len(g)==7
        for x,y,z in g:
            assert all(math.isfinite(v) for v in (x,y,z))
            assert abs(x)<1.3 and abs(y)<1.3 and -2<z<1.3


def test_repair_scope():
    with pytest.raises(ValueError,match='Only third'):
        m.validate({'operation':'repair','candidate':2})


def test_package_needs_current_successful_repair(tmp_path,monkeypatch):
    import json
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    preview=tmp_path/'hair-finish-finish-03'; preview.mkdir()
    result=preview/'result.json'
    for sha,protected in [('old',True),(m.digest(Path(m.__file__)),False)]:
        result.write_text(json.dumps({'handler_sha256':sha,'protected_exact':protected}))
        with pytest.raises(ValueError,match='Stale'):
            m.validate({'operation':'package','candidate':3})
    result.write_text(json.dumps({'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True}))
    assert m.validate({'operation':'package','candidate':3}).name=='hair-finish-package-03'


def test_source_symlink_refused(tmp_path,monkeypatch):
    p=tmp_path/'data'; p.write_bytes(b'fixed')
    link=tmp_path/'link'; link.symlink_to(p)
    monkeypatch.setattr(m,'SOURCE',link); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    with pytest.raises(ValueError,match='Pinned'):
        m.validate({'operation':'preview','candidate':1})
