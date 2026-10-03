import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS

spec=importlib.util.spec_from_file_location('static_tail_dock',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/static_tail_dock.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def fixture():
    point=NS(co=(1.,2.,3.,1.),radius=.5)
    spline=NS(type='POLY',points=[point],material_index=0)
    return NS(matrix_world=((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)),data=NS(dimensions='3D',bevel_depth=.01,bevel_resolution=1,splines=[spline]))


def test_exact_native_data_signature():
    assert module.data_signature(fixture())==module.data_signature(fixture())


def test_coordinate_and_radius_edits_are_detected():
    ob=fixture();before=module.data_signature(ob)
    ob.data.splines[0].points[0].radius=.6
    assert module.data_signature(ob)!=before
    ob=fixture();ob.data.splines[0].points[0].co=(1,2,4,1)
    assert module.data_signature(ob)!=before
