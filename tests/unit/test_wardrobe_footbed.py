import importlib.util
from pathlib import Path
import pytest

def test_boot_flex_is_local_not_uniform_noise():
    spec=importlib.util.spec_from_file_location('wardrobe_finish',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_finish.py')
    finish=importlib.util.module_from_spec(spec);spec.loader.exec_module(finish)
    assert abs(finish.boot_flex(-11.3,0))<.00001
    assert abs(finish.boot_flex(-12.3,0))<=.035

spec=importlib.util.spec_from_file_location('wardrobe_footbed',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_footbed.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_hull_removes_interior_and_duplicates():
    hull=module.footprint([(-1,-2),(1,-2),(1,2),(-1,2),(0,0),(-1,-2)])
    assert len(hull)==4 and module.center(hull)==(0,0)
    assert module.radius(hull,(0,0),(1,0))==pytest.approx(1)
    assert module.radius(hull,(0,0),(0,-1))==pytest.approx(2)

def test_convex_toe_silhouette_is_not_a_single_height_slice():
    hull=module.footprint([(-.4,.5),(.4,.5),(.5,-1.2),(0,-1.5),(-.5,-1.2)])
    assert module.radius(hull,(0,0),(0,-1))==pytest.approx(1.5)

def test_degenerate_support_is_rejected():
    with pytest.raises(ValueError):module.footprint([(0,0),(1,0),(2,0)])
