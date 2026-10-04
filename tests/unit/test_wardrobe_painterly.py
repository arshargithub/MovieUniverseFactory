import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_painterly',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_painterly.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('x',[-100,-3.1,0,.5,1,2,27.4])
def test_fold_stays_in_unit_range(x):assert 0<=module.pingpong(x)<=1

def test_cloth_sampling_never_reaches_head_or_upper_image():
    for x in range(-20,21):
        for z in range(-20,3):
            u,v,w=module.fabric_uv(x,z)
            assert .22<=u<=.78 and .02<=v<=.20 and w==0
