import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('bust_detail',Path('src/movie_factory/adapters/blender/bust_skin_detail.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'build','candidate':True}, {'operation':'build','candidate':0}, {'operation':'build','candidate':8}, {'operation':'build','candidate':1,'path':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_guards(tmp_path,monkeypatch):
    p=tmp_path/'input';p.write_bytes(b'pinned')
    monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.hashlib.sha256(b'pinned').hexdigest());monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'build','candidate':1};m.validate(job).mkdir()
    with pytest.raises(ValueError,match='Existing'):m.validate(job)
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)

def test_face_restores_chin_and_forehead_and_excludes_nape():
    for p in [(0,-1,.8),(0,-1,-.6),(.4,-.8,-.35),(.3,-.8,.4)]:assert m.original_face_weight(*p)==1
    for p in [(0,.5,.5),(0,-1,-1.2),(1.,-.5,.3)]:assert m.original_face_weight(*p)==0
    for x in (-1.,-.8,-.4,0,.4,.8,1.):
        for y in (-1.,-.6,-.3,0,.5):
            for z in (-2,-.8,-.5,0,.5,.8,1.3):assert 0<=m.original_face_weight(x,y,z)<=1

def test_corrected_mask_preserves_skin_but_excludes_hair_and_nape():
    for p in [(0,-1,.8),(0,-1,-.6),(.4,-.8,-.35),(.3,-.8,.4)]:assert m.corrected_face_weight(*p)==1
    for p in [(0,-1,1.1),(.7,-.3,.1),(0,.5,.5),(0,-1,-1.2)]:assert m.corrected_face_weight(*p)==0

def test_clean_edge_preserves_chin_not_hair():
    for p in [(0,-1,-.6),(.4,-.8,-.35),(.3,-.8,.4)]:assert m.clean_edge_face_weight(*p)==1
    for p in [(0,-1,1.1),(.7,-.3,.1),(0,.5,.5),(0,-1,-1.2)]:assert m.clean_edge_face_weight(*p)==0
