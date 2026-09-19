import importlib.util
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('donor',Path('src/movie_factory/adapters/blender/hair_donor.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'hair_fit','output_name':'../escape'}, {'operation':'python','code':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)
