import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('groom',Path('src/movie_factory/adapters/blender/hair_native_groom.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':0}, {'operation':'inspect','candidate':1}, {'operation':'inspect','candidate':False}, {'operation':'inspect','candidate':0,'code':'x'}, {'operation':'field','candidate':'2'}, {'operation':'clumps','candidate':4}, {'operation':'verify','candidate':1}, {'operation':'checkpoint','candidate':True}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_pinned_inputs_and_output(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'pin')
    monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p));monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'LIB',p);monkeypatch.setattr(m,'LIB_SHA',m.digest(p));monkeypatch.setattr(m,'REFERENCES',{})
    out=m.validate({'operation':'inspect','candidate':0});out.mkdir()
    with pytest.raises(ValueError,match='exists'):m.validate({'operation':'inspect','candidate':0})
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate({'operation':'inspect','candidate':0})

@pytest.mark.parametrize('candidate',[1,2,3,4,5])
def test_guides_and_palette(candidate):
    import math
    for side in (-1,1):
        for i in range(81):
            f=i/80;root=(side*.04,-.95+f,1.1)
            pts=m.guide_points(side,f,root,candidate)
            assert pts[0]==root and len(pts)==8
            assert all(math.isfinite(v) for p in pts for v in p)
            for j in range(10):
                color=m.tint(f,j/9,side,candidate)
                assert 0<color[2]<color[1]<color[0]<.2 and color[3]==1

@pytest.mark.parametrize('operation,candidate',[('preview',1),('preview',2),('preview',3),('field',2),('field',3),('field-retry',2),('clumps',1),('clumps',2),('clumps',3),('checkpoint',2),('verify',2)])
def test_fixed_operations(operation,candidate,tmp_path,monkeypatch):
    p=tmp_path/'source';p.write_bytes(b'pin')
    monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'LIB',p);monkeypatch.setattr(m,'LIB_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path);monkeypatch.setattr(m,'REFERENCES',{})
    out=m.validate({'operation':operation,'candidate':candidate})
    assert out.parent==tmp_path and not out.exists()
    out.symlink_to(tmp_path/'absent')
    with pytest.raises(ValueError):m.validate({'operation':operation,'candidate':candidate})

def test_guide_tip_variation():
    lengths=[m.guide_points(1,i/20,(.02,-.5,1.2),4)[-1][2] for i in range(21)]
    assert max(lengths)-min(lengths)>.20

@pytest.mark.parametrize('operation,candidate',[('brush-inspect',0),('brush-inspect',1),('brush-inspect',2),('brush-preview',1),('brush-preview',2),('brush-preview',3),('brush-retry',3)])
def test_specialist_resource_pin(operation,candidate,tmp_path,monkeypatch):
    p=tmp_path/'resource';p.write_bytes(b'pin')
    for name in ('SOURCE','LIB','BRUSH_LIB'):monkeypatch.setattr(m,name,p)
    for name in ('SOURCE_SHA','LIB_SHA','BRUSH_SHA'):monkeypatch.setattr(m,name,m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path);monkeypatch.setattr(m,'REFERENCES',{})
    assert m.validate({'operation':operation,'candidate':candidate}).parent==tmp_path
    monkeypatch.setattr(m,'BRUSH_SHA','0'*64)
    with pytest.raises(ValueError,match='Pinned brush'):m.validate({'operation':operation,'candidate':candidate})
