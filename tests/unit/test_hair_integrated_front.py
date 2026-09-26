import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('integrated',Path('src/movie_factory/adapters/blender/hair_integrated_front.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':4}, {'operation':'preview','candidate':1,'code':'x'}])
def test_rejects_unstructured(job):
    with pytest.raises(ValueError): m.validate(job)

@pytest.mark.parametrize('candidate',[1,2,3])
def test_bounds_and_unequal_guides(candidate):
    assert len(m.SECTIONS)==14
    for k in range(14):
        for i in range(73):
            for w in (-1,-.5,0,.5,1):
                co,uv,width=m.section_vertex(k,i/72,w,candidate)
                assert all(math.isfinite(v) for v in (*co,*uv,width))
                assert abs(co[0])<1.3 and -1.3<co[1]<.3 and -.4<co[2]<1.6
                assert 0<uv[0]<1 and 0<uv[1]<1 and width>=0
    assert m.SECTIONS[0][0][1][0] != 976-m.SECTIONS[7][0][1][0]

def test_output_and_pin_guards(tmp_path,monkeypatch):
    source=tmp_path/'source'; source.write_bytes(b'pinned')
    monkeypatch.setattr(m,'SOURCE',source); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    out=m.validate({'operation':'preview','candidate':1}); out.mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Unsupported'): m.validate({'operation':'package','candidate':1})
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})

def test_mask_excludes_forehead_not_hair():
    assert m.hair_pixel_mask(490/955,1-350/1647)==0
    assert m.hair_pixel_mask(490/955,1-300/1647)==1
    for x in range(235,742,10):
        for y in range(210,600,10):
            assert 0<=m.hair_pixel_mask(x/955,1-y/1647)<=1
