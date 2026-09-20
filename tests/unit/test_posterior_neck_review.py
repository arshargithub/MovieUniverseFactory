import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('posterior',Path('src/movie_factory/adapters/blender/posterior_neck_review.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{},None,{'operation':'exec','candidate':16},{'operation':'build','candidate':True},{'operation':'build','candidate':19},{'operation':'build','candidate':16,'path':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_patch_excludes_face_anterior_clavicle_and_shoulders():
    for c in (16,17,18):
        for x in (-1.,-.4,0,.4,1.):
            for y in (-1.,-.5,0,.5,1.):
                for z in (-2,-1.6,-1.45,-1.,-.5,0,1.):
                    p=m.point(x,y,z,c)
                    if y<=0 or z>=-.5 or z<=-1.45:assert p==(x,y,z)
                    assert p[2]==z

def test_compact_falloff_and_displacement_bound():
    for i in range(101):
        z=-1.5+i*.011
        for j in range(101):
            a=j*2*math.pi/100;x=.65*math.sin(a);y=.1+.65*math.cos(a)
            p=m.point(x,y,z,16)
            assert 0<=m.weight(x,y,z)<=1
            assert math.dist((x,y,z),p)<=.04500001
            assert all(math.isfinite(v) for v in p)
    assert m.weight(0,.75,-.975)==pytest.approx(1.)
    for z in (-1.45,-.5):
        assert m.weight(0,.75,z)==0
        assert m.weight(0,.75,z+1e-5)<1e-12
        assert m.weight(0,.75,z-1e-5)<1e-12

def test_source_and_output_guard(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'pinned');monkeypatch.setattr(m,'SOURCE',source)
    monkeypatch.setattr(m,'SOURCE_SHA',m.hashlib.sha256(b'pinned').hexdigest());monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'build','candidate':16};m.validate(job).mkdir()
    with pytest.raises(ValueError,match='Existing'):m.validate(job)
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)
