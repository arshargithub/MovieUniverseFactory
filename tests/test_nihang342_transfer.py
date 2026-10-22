import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_transfer as t,nihang_patch as p

def recipe(phase):
    return dict(operation='nihang_patch',frame=283,width=640,height=640,samples=16,
                edits=[dict(kind='neutral_actor_transfer',target='mounted leader',phase=phase)])

@pytest.mark.parametrize('phase',['leader','near_crowd'])
def test_fixed_transfer(phase):assert p.validate(recipe(phase))==recipe(phase)

@pytest.mark.parametrize('phase',['exec','all_crowd','/tmp/scene.blend'])
def test_no_unreviewed_transfer_phase(phase):
    with pytest.raises(ValueError):p.validate(recipe(phase))

def test_segment_exact_anchors_and_radial_preservation():
    pts=np.array([[0,0,0],[0,0,.3],[.02,0,.15]])
    result=t.segment_points(pts,[0,0,0],[0,0,.3],[1,0,0],[1,.4,0])
    np.testing.assert_allclose(result[:2],[[1,0,0],[1,.4,0]],atol=1e-12)
    assert np.linalg.norm(result[2]-[1,.2,0])==pytest.approx(.02)

def test_segment_identity():
    pts=np.array([[.1,.2,.3],[.3,.2,.2]])
    np.testing.assert_allclose(t.segment_points(pts,[0,0,0],[0,0,.3],[0,0,0],[0,0,.3]),pts)

def test_degenerate_segment_blocks():
    with pytest.raises(ValueError):t.segment_points(np.zeros((2,3)),[0,0,0],[0,0,.3],[0,0,0],[0,0,0])

def test_direction_reversal_is_not_guessed():
    with pytest.raises(ValueError):t.segment_points(np.zeros((2,3)),[0,0,0],[0,0,.3],[0,0,0],[0,0,-.3])

def test_fixed_finish_import_without_blender():
    import importlib.util
    from pathlib import Path
    source=Path(t.__file__).with_name('nihang_finish.py')
    spec=importlib.util.spec_from_file_location('standalone_finish_control',source)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    assert callable(mod.run)
    r=recipe('leader');r['edits']=[dict(kind='supporting_finish',target='mounted leader')]
    assert p.validate(r)==r
    r['edits'][0]['path']='/tmp/arbitrary'
    with pytest.raises(ValueError):p.validate(r)

def test_ribbon_preserves_cross_slope_and_clearance():
    from movie_factory.adapters.blender.nihang_finish import supported_ribbon
    a=np.tile(np.linspace(-.10,-.04,9),(61,1))
    result=supported_ribbon(a,-1)
    np.testing.assert_allclose(result,a-.007,atol=1e-12)
    assert np.ptp(result[30])==pytest.approx(.06)

def test_ribbon_missing_support_blocks():
    from movie_factory.adapters.blender.nihang_finish import supported_ribbon
    with pytest.raises(ValueError):supported_ribbon(np.full((61,9),np.nan),1)

def test_ribbon_fills_small_edge_gaps_without_flattening():
    from movie_factory.adapters.blender.nihang_finish import supported_ribbon
    a=np.tile(np.linspace(.04,.10,9),(61,1));a[0,0]=np.nan
    result=supported_ribbon(a,1)
    assert np.isfinite(result).all()
    assert np.ptp(result[30])>.05
