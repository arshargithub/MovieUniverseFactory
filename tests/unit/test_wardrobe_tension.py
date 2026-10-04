import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_tension',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_tension.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_open_curve_preserves_endpoints_without_hip_return():
    values=module.open_curve([0.,1.,2.],10)
    assert len(values)==21 and values[0]==0 and values[-1]==2
    assert all(a<=b for a,b in zip(values,values[1:]))

def test_dense_curve_no_large_jump_on_straight_anchors():
    values=module.open_curve([0.,1.,2.,3.],20)
    assert max(b-a for a,b in zip(values,values[1:]))<.07
    assert values[20]==pytest.approx(1)

def test_height_local_support_does_not_bridge_whole_leaning_torso():
    cloud=[(-5.,'waist'),(-3.1,'upper'),(-3.,'chest'),(-2.,'shoulder')]
    assert module.at_height(cloud,-3.)==['upper','chest']
    assert module.at_height(cloud,-5.)==['waist']

def test_superior_shoulder_transition_not_constant_height_ring():
    assert module.cap_weight(-3)==0 and module.cap_weight(-2.25)==1
    assert module.cap_weight(-2.375)==pytest.approx(.5)

def test_fair_leather_bridges_local_fold_noise_preserving_anchors():
    result=module.fair([0.,1.,.8,1.8,3.])
    assert result[0]==0 and result[-1]==3
    assert all(a<b for a,b in zip(result,result[1:]))

def test_shoulder_support_uses_actual_surfaces_not_a_neckline_tent():
    import inspect
    source=inspect.getsource(module.shoulder_envelope)
    assert 'convex_hull' not in source
    assert 'MF_fit_tunic_173_visible' in source
    assert 'single_surface_mesh' in source
    surface=inspect.getsource(module.surface)
    assert 'tree.find_nearest(query)' in surface
    assert 'cap_normal.dot(cap_hit-root)<0' in surface
    assert 'cap[0].find_nearest(vertex)' in inspect.getsource(module.harness)

def test_visible_cloth_pressure_is_bounded_not_full_sheet_projection():
    assert module.pressure_weight(0)==1
    assert module.pressure_weight(.18)==0
    assert module.pressure_weight(1)==0
    assert 0<module.pressure_weight(.09)<1
    import inspect
    source=inspect.getsource(module.press_visible_scarf)
    assert 'MF_173_open_scarf' in source
    assert 'local.z>-1.35' in source
    assert 'shirt.find_nearest(p)' in source
    assert source.index('if not changed:continue')<source.index('shirt.find_nearest(p)')
