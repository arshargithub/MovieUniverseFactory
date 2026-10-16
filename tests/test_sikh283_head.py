import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('sikh283',Path(__file__).parents[1]/'scripts/sikh283_head.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('operation',['build','motion','verify'])
def test_fixed_operations(operation):
    assert m.validate({'operation':operation,'attempt':1}).name=='control-01'

@pytest.mark.parametrize('job',[{}, {'operation':'exec','attempt':1},{'operation':'build','attempt':True},{'operation':'build','attempt':0},{'operation':'build','attempt':13},{'operation':'build','attempt':1,'code':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_sources():
    for p,digest in m.EXPECTED.items():assert m.sha(p)==digest

def test_beard_boundary_is_finite_bounded_and_not_perfectly_mirrored():
    import math
    values=[m.beard_top(i/1000) for i in range(-220,221)]
    assert all(math.isfinite(v) and -.02<v<.15 for v in values)
    assert m.beard_top(.12)!=m.beard_top(-.12)
