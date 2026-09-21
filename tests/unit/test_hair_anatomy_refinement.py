import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('hair_anatomy',Path('src/movie_factory/adapters/blender/hair_anatomy_refinement.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':0},{'operation':'inspect','candidate':False},{'operation':'inspect','candidate':1},{'operation':'inspect','candidate':0,'path':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError):m.validate(job)
def test_pin(tmp_path,monkeypatch):
    p=tmp_path/'source';p.write_bytes(b'fixed');monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p));monkeypatch.setattr(m,'BASE',tmp_path)
    m.validate({'operation':'inspect','candidate':0}).mkdir()
    with pytest.raises(ValueError):m.validate({'operation':'inspect','candidate':0})
    p.write_bytes(b'bad')
    with pytest.raises(ValueError,match='Pinned'):m.validate({'operation':'inspect','candidate':0})
def test_relief_guards():
    for x,y,z in [(0,-.5,-.8),(.5,.1,-1.2),(0,-.8,-1.91),(.8,-.2,.3)]:assert m.neck_relief(x,y,z)==0
    assert 0<m.neck_relief(.40,-.50,-1.20)<.06
    assert abs(m.neck_relief(.4,-.5,-1.2)-m.neck_relief(-.4,-.5,-1.2))<1e-12
def test_spline():
    points=[(0,0,0),(1,1,1),(2,2,2)]
    assert m.spline(points,0)==points[0]
    assert m.spline(points,.5)==points[1]
    assert abs(m.spline(points,1)[0]-2)<1e-8
def test_selected_pin(tmp_path,monkeypatch):
    p=tmp_path/'source';p.write_bytes(b'fixed');s=tmp_path/'selected';s.write_bytes(b'selected')
    monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'SELECTED',s);monkeypatch.setattr(m,'SELECTED_SHA',m.digest(s))
    m.validate({'operation':'verify','candidate':5})
    s.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Selected'):m.validate({'operation':'verify','candidate':5})

def test_review_pin(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'fixed')
    selected=tmp_path/'review';selected.write_bytes(b'review')
    monkeypatch.setattr(m,'SOURCE',source);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'REVIEW_SELECTED',selected);monkeypatch.setattr(m,'REVIEW_SHA',m.digest(selected))
    assert m.validate({'operation':'verify','candidate':7}).name=='hair-anatomy-verify-07'
    selected.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Selected'):m.validate({'operation':'verify','candidate':7})

def test_full_protected_region():
    # Face, posterior neck and lower cutoff remain exactly untouched.
    for x in (-1.5,-1,-.5,0,.5,1,1.5):
        for y in (-1,-.5,0,.5,1):
            for z in (-2.2,-1.91,-.8,-.5,0,.5,1,1.5):assert m.neck_relief(x,y,z)==0
        for z in (-1.85,-1.6,-1.2,-.9):
            assert m.neck_relief(x,.04,z)==0

def test_source_symlink_refused(tmp_path,monkeypatch):
    p=tmp_path/'real';p.write_bytes(b'source');link=tmp_path/'link';link.symlink_to(p)
    monkeypatch.setattr(m,'SOURCE',link);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    with pytest.raises(ValueError,match='Pinned'):m.validate({'operation':'inspect','candidate':0})

def test_final_pin(tmp_path,monkeypatch):
    p=tmp_path/'source';p.write_bytes(b'source');s=tmp_path/'final';s.write_bytes(b'final')
    monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'FINAL_SELECTED',s);monkeypatch.setattr(m,'FINAL_SHA',m.digest(s))
    assert m.validate({'operation':'verify','candidate':10}).name=='hair-anatomy-verify-10'
    s.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Selected'):m.validate({'operation':'verify','candidate':10})
