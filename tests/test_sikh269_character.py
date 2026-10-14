import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('sikh269',Path(__file__).parents[1]/'scripts/sikh269_character.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'build','attempt':True},
    {'operation':'build','attempt':31},{'operation':'exec','attempt':1},
    {'operation':'build','attempt':1,'code':'print(1)'}])
def test_reject_unbounded(job):
    with pytest.raises(ValueError):module.validate(job)

def test_scoped_and_targets():
    assert module.validate({'operation':'build','attempt':1}).name=='candidate-01'
    assert all((module.INSTALLED/'data/targets'/f'{name}.target.gz').is_file() for name in module.MORPHS)

def test_cloth_finite():
    for i in range(701):
        for v in (-.5,0,.5):
            p=module.wrap_point(i*math.tau/100+math.pi/2,i/100,v,1.77)
            assert all(math.isfinite(c) for c in p)
            assert max(abs(p[0]),abs(p[1]))<.20
            assert 1.6<p[2]<2.1
