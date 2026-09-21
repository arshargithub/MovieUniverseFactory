import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('dressing_fit',Path('src/movie_factory/adapters/blender/dressing_motion_fit.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':0},{'operation':'inspect','candidate':False},{'operation':'inspect','candidate':1},{'operation':'inspect','candidate':0,'path':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError):m.validate(job)

def test_pinned_and_overwrite(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',source);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source));monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'inspect','candidate':0};m.validate(job).mkdir()
    with pytest.raises(ValueError):m.validate(job)
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)

def test_hairline_and_taper():
    assert .80<m.hairline(0,-.8)<.9
    assert .5<m.hairline(.6,-.5)<.65
    assert m.hairline(.9,-.2)>.25
    assert m.smooth(-1)==0 and m.smooth(2)==1

def test_selected_pin(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'fixed');selected=tmp_path/'selected';selected.write_bytes(b'selected')
    monkeypatch.setattr(m,'SOURCE',source);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'SELECTED',selected);monkeypatch.setattr(m,'SELECTED_SHA',m.digest(selected))
    assert m.validate({'operation':'verify','candidate':4}).name=='dressing-motion-verify-04'
    selected.write_bytes(b'bad')
    with pytest.raises(ValueError,match='Selected'):m.validate({'operation':'verify','candidate':4})
