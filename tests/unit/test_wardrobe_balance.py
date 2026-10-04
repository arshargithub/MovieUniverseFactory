import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_balance',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_balance.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'}, {'operation':'inspect01','path':'/tmp'}, {'operation':'inspect01','code':'x'}])
def test_fixed_operations(job):
    with pytest.raises(ValueError):module.validate(job)

def test_immutable_output_and_input(monkeypatch,tmp_path):
    source=tmp_path/'source.blend';source.touch()
    monkeypatch.setattr(module,'SOURCE',source);monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA)
    out=module.validate({'operation':'inspect01'});out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':'inspect01'})
    monkeypatch.setattr(module,'digest',lambda p:'bad')
    with pytest.raises(ValueError,match='Pinned'):module.validate({'operation':'inspect01'})

def test_selected_native_pin(monkeypatch,tmp_path):
    import json
    source=tmp_path/'source.blend';source.touch()
    selected=tmp_path/'wardrobe172-seal01';selected.mkdir()
    (selected/'dressed-fit.blend').touch()
    (selected/'result.json').write_text(json.dumps({'native_sha256':'expected'}))
    monkeypatch.setattr(module,'SOURCE',source);monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==source else 'wrong')
    with pytest.raises(ValueError,match='Selected native'):module.validate({'operation':'verify01'})

class RayVector:
    def __init__(self,value):self.value=value
    def __add__(self,other):return RayVector(self.value+other.value)
    def __sub__(self,other):return RayVector(self.value-other.value)
    def __mul__(self,value):return RayVector(self.value*value)
    @property
    def length(self):return abs(self.value)

class RayTree:
    def __init__(self,hits):self.hits=hits
    def ray_cast(self,start,direction,maximum):
        hits=[v for v in self.hits if start.value<=v<=start.value+maximum]
        return (RayVector(min(hits)),None,None,None) if hits else (None,None,None,None)

def test_sleeve_entry_is_not_exterior():
    assert module.outer_ray_radius(RayTree([1.5,1.518,2.5,2.518]),RayVector(0),RayVector(1))==pytest.approx(2.518)

def test_ray_no_hit_and_bounded_distance():
    assert module.outer_ray_radius(RayTree([]),RayVector(0),RayVector(1)) is None
    assert module.outer_ray_radius(RayTree([1.5,9.]),RayVector(0),RayVector(1))==pytest.approx(1.5)

def test_scarf_harness_correction_preserves_waist():
    assert module.harness_refit_weight(-5.2)==0
    assert module.harness_refit_weight(-4.5)==0
    assert module.harness_refit_weight(-3.8)==pytest.approx(1)
    assert module.harness_refit_weight(-4.15)==pytest.approx(.5)
