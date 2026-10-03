import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_correction',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_correction.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'}, {'operation':'inspect01','path':'/tmp'}, {'operation':'preview01','code':'x'}, {'operation':'preview99'}])
def test_fixed_operations(job):
    with pytest.raises(ValueError):module.validate(job)

def test_source_and_output_protection(monkeypatch,tmp_path):
    path=tmp_path/'source.blend';path.touch()
    monkeypatch.setattr(module,'SOURCE',path);monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA)
    out=module.validate({'operation':'inspect01'});out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':'inspect01'})
    monkeypatch.setattr(module,'digest',lambda p:'0'*64)
    with pytest.raises(ValueError,match='Pinned'):module.validate({'operation':'preview01'})

def test_face_preserving_skin_blend():
    assert all(module.body_skin_blend(z)==0 for z in (-.35,0,1,4))
    assert module.body_skin_blend(-1.2)==1
    values=[module.body_skin_blend(-.35-i*.085) for i in range(11)]
    assert values==sorted(values)
    assert module.body_skin_blend(-.775)==pytest.approx(.5)

def test_selected_native_hash_required(monkeypatch,tmp_path):
    import json
    source=tmp_path/'source.blend';source.touch()
    selected=tmp_path/'wardrobe171-seal01';selected.mkdir()
    (selected/'result.json').write_text(json.dumps({'native_sha256':'expected'}))
    (selected/'dressed-fit.blend').touch()
    monkeypatch.setattr(module,'SOURCE',source);monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==source else 'wrong')
    with pytest.raises(ValueError,match='Selected native'):module.validate({'operation':'verify01'})
