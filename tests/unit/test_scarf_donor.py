import importlib.util
from pathlib import Path
import pytest
s=importlib.util.spec_from_file_location('scarf',Path('src/movie_factory/adapters/blender/scarf_donor.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
@pytest.mark.parametrize('job',[None,{}, {'operation':'scarf_fit','output_name':'../bad'}, {'operation':'exec','output_name':'scarf-fit-01'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_cheek_change_local_and_small():
    assert m.cheek_delta(0,-1,-.3)==(0.,0.,0.)
    assert m.cheek_delta(.7,-.8,.5)==(0.,0.,0.)
    assert m.cheek_delta(.7,-.8,-.8)==(0.,0.,0.)
    d=m.cheek_delta(.7,-.8,-.3)
    assert -.04<d[0]<0 and 0<d[1]<=.065 and d[2]==0
