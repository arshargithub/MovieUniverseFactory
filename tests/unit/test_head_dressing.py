import importlib.util
from pathlib import Path
import math
import pytest

spec=importlib.util.spec_from_file_location('dressing',Path('src/movie_factory/adapters/blender/head_dressing.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{},None,{'operation':'code','output_name':'dressing-x'}, {'operation':'static_dressing','output_name':'../x'}])
def test_reject(job):
    with pytest.raises(ValueError): m.validate(job)

def test_surface_bounded():
    for i in range(81):
        for j in range(17):
            x,y,z=m.hood_point(-2+4*i/80,j/16)
            assert all(math.isfinite(v) for v in (x,y,z))
            assert abs(x)<1.5 and -.3<=y<=1.2 and -1.8<=z<=1.6
    assert m.hood_point(0,0)[2]>1.33
