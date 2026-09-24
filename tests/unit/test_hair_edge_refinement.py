import importlib.util
import json
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('edge',Path('src/movie_factory/adapters/blender/hair_edge_refinement.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':4}, {'operation':'preview','candidate':1,'path':'x'}])
def test_rejects_unstructured(job):
    with pytest.raises(ValueError): m.validate(job)


def test_pins_and_preview(tmp_path,monkeypatch):
    source = tmp_path/'source'; source.write_bytes(b'pinned')
    monkeypatch.setattr(m,'SOURCE',source); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    out=m.validate({'operation':'preview','candidate':1}); out.mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview'): m.validate({'operation':'package','candidate':1})
    report={'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True,'base_geometry_exact':True}
    (out/'result.json').write_text(json.dumps(report))
    assert m.validate({'operation':'package','candidate':1}).name=='edge-package-01'
    report['base_geometry_exact']=False; (out/'result.json').write_text(json.dumps(report))
    with pytest.raises(ValueError,match='Stale'): m.validate({'operation':'package','candidate':1})
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})


@pytest.mark.parametrize('candidate',[1,2,3])
def test_narrow_bounded_front_feather(candidate):
    for x in (-1,-.7,-.4,0,.4,.7,1):
        for z in (.5,.7,.9,1.1,1.5):
            assert 0<=m.opacity(x,-.8,z,.8,candidate)<=1
            assert m.opacity(x,0,z,.8,candidate)==1
        assert m.opacity(x,-.8,1.1,.8,candidate)==1
    assert m.opacity(.2,-.8,.8,.8,candidate)<.1


@pytest.mark.parametrize('candidate',[2,3])
def test_temple_feather_preserves_rear(candidate):
    for angle in (-3,-2,-1.5,1.5,2,3):
        assert m.temple_opacity(angle,.2,.8,candidate)==1
    for angle in (-1.3,-.5,0,.5,1.3):
        assert 0<=m.temple_opacity(angle,.8,.8,candidate)<=1
        assert m.temple_opacity(angle,1.,.8,candidate)==1
