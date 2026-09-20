import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('bust_skin',Path('src/movie_factory/adapters/blender/bust_skin_review.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{},None,{'operation':'exec','candidate':0},{'operation':'inspect','candidate':False},{'operation':'inspect','candidate':1},{'operation':'inspect','candidate':0,'path':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_source_and_output_guards(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'pinned');monkeypatch.setattr(m,'SOURCE',source)
    monkeypatch.setattr(m,'SOURCE_SHA',m.hashlib.sha256(b'pinned').hexdigest());monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'inspect','candidate':0};m.validate(job).mkdir()
    with pytest.raises(ValueError,match='Existing'):m.validate(job)
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)

def test_skin_masks_bounded_and_face_features_kept():
    for x in (-1.,-.7,-.3,0,.3,.7,1.):
        for y in (-1.,-.5,0,.5,1.):
            for z in (-1.9,-1.,-.6,-.3,0,.4,.8,1.2):
                assert 0<=m.face_weight(x,y,z)<=1
                assert 0<=m.feature_weight(x,y,z)<=1
                if y>=-.16 or z<=-1.:assert m.face_weight(x,y,z)==0
    assert m.face_weight(0,-1.,.4)==1
    assert m.feature_weight(.3,-1.,.4)==1
    assert m.feature_weight(0,-1.,-.2)==1

@pytest.mark.parametrize('fn',[m.soft_face_weight,m.inset_face_weight])
def test_soft_masks_are_bounded_and_remove_rear_and_low_neck(fn):
    for x in (-1.,-.7,-.3,0,.3,.7,1.):
        for y in (-1.,-.5,0,.5,1.):
            for z in (-1.9,-1.,-.6,-.3,0,.4,.8,1.2):
                assert 0<=fn(x,y,z)<=1
                if y>=-.16 or z<=-1.:assert fn(x,y,z)==0
    assert fn(0,-1.,.4)==1
    assert fn(0,-1.,-.2)==1

def test_inset_mask_excludes_lateral_projected_hair():
    assert m.inset_face_weight(.7,-.3,.2)==0
    assert m.inset_face_weight(-.7,-.3,.2)==0
