import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('region_skin',Path('src/movie_factory/adapters/blender/bust_skin_regions.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{},None,{'operation':'exec','candidate':1},{'operation':'build','candidate':True},{'operation':'build','candidate':4},{'operation':'build','candidate':1,'path':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_guards(tmp_path,monkeypatch):
    p=tmp_path/'input';p.write_bytes(b'pinned');monkeypatch.setattr(m,'SOURCE',p);monkeypatch.setattr(m,'SOURCE_SHA',m.hashlib.sha256(b'pinned').hexdigest());monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'build','candidate':1};m.validate(job).mkdir()
    with pytest.raises(ValueError):m.validate(job)
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)

def test_temple_mask_excludes_central_face_and_eye():
    for p in [(0,-.9,.6),(.3,-.8,.4),(.6,-.8,.2),(0,0,0)]:assert m.temple_weight(*p)==0
    assert m.temple_weight(.65,-.7,.6)==1
    assert m.temple_weight(-.65,-.7,.6)==1
    for x in (-1,-.6,0,.6,1):
        for y in (-1,-.4,0,.5):
            for z in (-2,0,.4,.6,1.5):
                assert 0<=m.temple_weight(x,y,z)<=1
                assert 0<=m.face_weight(x,y,z)<=1

def test_lower_cleanup_keeps_inner_brow_and_eye():
    for p in [(0,-.9,.6),(.3,-.8,.4),(.6,-.8,.2)]:assert m.temple_weight_lower(*p)==0
    assert m.temple_weight_lower(.65,-.7,.4)==1
