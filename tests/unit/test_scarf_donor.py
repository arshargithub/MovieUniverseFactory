import importlib.util
from pathlib import Path
import pytest
s=importlib.util.spec_from_file_location('scarf',Path('src/movie_factory/adapters/blender/scarf_donor.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
@pytest.mark.parametrize('job',[None,{}, {'operation':'scarf_fit','output_name':'../bad'}, {'operation':'exec','output_name':'scarf-fit-01'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)
