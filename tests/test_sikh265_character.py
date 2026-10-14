import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('sikh265',Path(__file__).parents[1]/'scripts/sikh265_character.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'build','attempt':True},
    {'operation':'build','attempt':21}, {'operation':'exec','attempt':1},
    {'operation':'build','attempt':1,'path':'/tmp/out'}])
def test_reject_unbounded(job):
    with pytest.raises(ValueError):module.validate(job)

def test_scoped_output():
    assert module.validate({'operation':'build','attempt':1}).name=='candidate-01'

def test_target_inventory():
    assert all((module.INSTALLED/'data/targets'/f'{name}.target.gz').is_file() for name in module.MORPHS)
