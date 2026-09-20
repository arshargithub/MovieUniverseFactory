import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('reference',Path('src/movie_factory/adapters/blender/reference_dressing.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','variant':1},{'operation':'portrait_dressing','variant':True},
    {'operation':'portrait_dressing','variant':19},{'operation':'portrait_dressing','variant':1,'path':'/tmp/arbitrary'}])
def test_deny(job):
    with pytest.raises(ValueError):m.validate(job)

def test_panel_diagonal_and_clear_face():
    assert m.panel_point(1,0)[2]>m.panel_point(0,0)[2]
    for layer in (0,1):
        for i in range(101):
            for j in range(61):
                point=m.panel_point(i/100,j/60,layer)
                assert all(math.isfinite(v) for v in point)
                assert point[2]<-.75

def test_hair_frame():
    for side in (-1,1):
        for lock in range(12):
            for j in range(49):
                p=m.lock_point(side,lock,j/48)
                assert all(math.isfinite(v) for v in p)
                assert abs(p[0])>.68

def test_hood_crown_and_changed_source(tmp_path,monkeypatch):
    assert m.hood_point((0,0,2.49))[2]==pytest.approx(1.541)
    p=tmp_path/'changed';p.write_bytes(b'bad');monkeypatch.setattr(m,'HEAD',p)
    with pytest.raises(ValueError,match='Changed source'):m.validate({'operation':'portrait_dressing','variant':1})

def test_second_pattern_wraps_ends_behind_shoulders():
    assert m.panel_point(0,0,variant=2)[1]>0
    assert m.panel_point(1,0,variant=2)[1]>0
    assert m.panel_point(.5,0,variant=2)[1]<-.7
    for side in (-1,1):
        for lock in range(12):
            for j in range(49):
                assert all(math.isfinite(v) for v in m.lock_point(side,lock,j/48,variant=2))

def test_donor_wrap_has_diagonal_slope():
    assert m.donor_wrap_point((1,0,0))[2]>m.donor_wrap_point((-1,0,0))[2]
    assert m.donor_wrap_point((0,-1,0))[1]<-1

def test_final_hood_lip_returns_over_upper_hair_not_neck():
    point=(.9,-.8,1.5)
    assert m.hood_point(point,15)[1]<m.hood_point(point,14)[1]
    point=(.9,-.8,.4)
    assert m.hood_point(point,15)==pytest.approx(m.hood_point(point,14))

@pytest.mark.parametrize('operation',['portrait_dressing','verify_portrait_dressing','render_portrait_dressing','inspect_portrait_dressing'])
def test_valid_fixed_source_job_and_no_overwrite(tmp_path,monkeypatch,operation):
    monkeypatch.setattr(m,'BASE',tmp_path)
    source=tmp_path/'source';source.write_bytes(b'unit-test-source')
    digest=m.hashlib.sha256(source.read_bytes()).hexdigest()
    for path_key,digest_key in [('HEAD','HEAD_SHA'),('DONOR','DONOR_SHA'),('REFERENCE','REFERENCE_SHA'),('HAIR_TEXTURE','HAIR_SHA'),('SIDE_REFERENCE','SIDE_SHA')]:
        monkeypatch.setattr(m,path_key,source)
        monkeypatch.setattr(m,digest_key,digest)
    output=m.validate({'operation':operation,'variant':18})
    assert output.parent==tmp_path
    output.mkdir()
    with pytest.raises(ValueError,match='Output exists'):
        m.validate({'operation':operation,'variant':18})

def test_latest_shoulder_correction_does_not_raise_neckline():
    for x in (-2,-1,0,1,2):
        for z in (-3,-1,0,.65):
            old=m.donor_wrap_point((x,0,z),17)
            new=m.donor_wrap_point((x,0,z),18)
            assert all(math.isfinite(v) for v in new)
            assert new[2]<=old[2]
