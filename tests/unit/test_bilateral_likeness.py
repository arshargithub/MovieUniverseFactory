import importlib.util
from pathlib import Path
import pytest
s=importlib.util.spec_from_file_location('bilateral',Path('src/movie_factory/adapters/blender/bilateral_likeness.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
@pytest.mark.parametrize('p',[(-.8,-.8,-.3),(0,-1,-.3),(.7,-.7,.5),(.7,-.7,-1.1),(.7,.4,-.3)])
def test_protected(p):assert m.mask(*p)==0
def test_right_cheek():assert m.mask(.7,-.7,-.3)==1
@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','output_name':'bilateral-01'}])
def test_invalid(job):
    with pytest.raises(ValueError):m.validate(job)

def test_continuous_mask_protects_left_and_extends_past_jaw():
    for x in [-.9,-.3,0,.02]:assert m.continuous_mask(x,-.8,-.3)==0
    assert m.continuous_mask(.3,-.8,-.1)==1
    assert m.continuous_mask(.6,-.8,-1.1)==1
    assert m.continuous_mask(.6,-.8,.5)==0

def test_jaw_infill_is_bounded_and_protects_other_features():
    assert m.jaw_infill_mask(.6,-.8,-.53)==pytest.approx(.6)
    for p in [(-.6,-.8,-.53),(0,-.8,-.77),(.6,-.8,0),(.95,-.8,-.4),(.6,0,-.53)]:
        assert m.jaw_infill_mask(*p)==0
