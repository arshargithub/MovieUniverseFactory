import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('atlas',Path('src/movie_factory/adapters/blender/bust_skin_atlas.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'build','candidate':True}, {'operation':'build','candidate':3}, {'operation':'prepare','candidate':2}, {'operation':'prepare','candidate':1,'code':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError):m.validate(job)

def test_pinning_and_output(tmp_path,monkeypatch):
    p=tmp_path/'anatomy';p.write_bytes(b'original')
    monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'TEXTURE_SHA',None)
    with pytest.raises(ValueError,match='texture'):m.validate({'operation':'build','candidate':1})
    m.validate({'operation':'prepare','candidate':1}).mkdir()
    with pytest.raises(ValueError,match='Existing'):m.validate({'operation':'prepare','candidate':1})
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='anatomy'):m.validate({'operation':'prepare','candidate':1})

def test_mapping():
    assert m.uv_point(0,-1,m.ZMIN)==(.5,0)
    assert m.uv_point(1,0,m.ZMAX)==(.75,1)
    assert m.uv_point(-1,0,m.ZMIN)==(.25,0)

def test_separate_pinned_texture_and_output(tmp_path,monkeypatch):
    source=tmp_path/'anatomy';source.write_bytes(b'original')
    texture=tmp_path/'texture02';texture.write_bytes(b'new')
    monkeypatch.setattr(m,'SOURCE',source);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'CHEEK_TEXTURE',texture);monkeypatch.setattr(m,'CHEEK_TEXTURE_SHA',m.digest(texture))
    assert m.texture_source(1)==(m.TEXTURE,m.TEXTURE_SHA)
    assert m.validate({'operation':'build','candidate':2}).name=='bust-atlas-build-02'
    texture.write_bytes(b'changed')
    with pytest.raises(ValueError,match='texture'):m.validate({'operation':'build','candidate':2})
    with pytest.raises(ValueError):m.texture_source(3)

def test_core_face_protection():
    for xyz in [(0,-.9,0),(.3,-.7,.32),(0,-.8,-.4)]:assert m.core_weight(*xyz)==1
    for xyz in [(.7,-.3,.7),(0,.5,0),(0,-.4,-1.5)]:assert m.core_weight(*xyz)==0
    for x in (-1,-.5,0,.5,1):
        for y in (-1,0,1):
            for z in (-2,-.5,0,.5,1):assert 0<=m.core_weight(x,y,z)<=1
