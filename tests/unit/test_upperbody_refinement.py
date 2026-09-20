import importlib.util
from pathlib import Path
import pytest
import math

spec=importlib.util.spec_from_file_location('upper',Path('src/movie_factory/adapters/blender/upperbody_refinement.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{},None,{'operation':'exec','variant':1},{'operation':'build','variant':True},
    {'operation':'build','variant':16},{'operation':'build','variant':1,'source':'elsewhere'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_neck_cannot_touch_jaw():
    for z in (-.86,-.8,-.7,0,1.5):assert m.neck_weight(z)==0
    assert m.neck_weight(-1.08)==1

def test_pinned_sources_and_output(tmp_path,monkeypatch):
    p=tmp_path/'source';p.write_bytes(b'pinned')
    monkeypatch.setattr(m,'BASE',tmp_path)
    for key in ('SOURCE','REF'):monkeypatch.setattr(m,key,p)
    for key in ('SOURCE_SHA','REF_SHA'):monkeypatch.setattr(m,key,m.hashlib.sha256(b'pinned').hexdigest())
    job={'operation':'audit','variant':1};out=m.validate(job);out.mkdir()
    with pytest.raises(ValueError,match='Existing'):m.validate(job)
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)

def test_relief_bounded_and_face_clear():
    for x in (-1,-.5,0,.5,1):
        for y in (-.6,0,.6):
            for z in (-2,-1.5,-1,-.86,-.5):
                value=m.muscle_relief(x,y,z)
                assert 0<=value<=.028
                if z>=-.86:assert value==0

def test_torso_finite_bounded():
    for i in range(97):
        for z in (-1.5,-2,-3,-4,-5.8):
            p=m.torso_point(i*2*math.pi/96,z)
            assert all(math.isfinite(v) for v in p)
            assert abs(p[0])<2.1 and abs(p[1])<1.25
