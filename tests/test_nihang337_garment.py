import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_look


@pytest.mark.parametrize('dtype', [np.float32, np.float64])
def test_garment_envelope_endpoints_are_finite_and_supported(dtype):
    u = np.array([-1, 0, 1e-8, .25, .5, .75, 1-1e-8, 1, 2], dtype=dtype)
    values = nihang_look.garment_envelope(u)
    assert np.isfinite(values).all()
    assert ((0 <= values) & (values <= 1)).all()
    assert values[0] == values[1] == values[-2] == values[-1] == 0
    assert values[4] == pytest.approx(1)


def test_garment_envelope_rejects_invalid_input():
    with pytest.raises(ValueError, match='ENVELOPE_NONFINITE'):
        nihang_look.garment_envelope(np.array([float('nan')], dtype=np.float32))


def test_crown_is_finite_and_has_no_constant_cone_profile():
    import math
    values=[nihang_look.crown_point(a,z,.270,.114) for a in (0,1,2,3,4,5,math.tau)
            for z in np.linspace(.02,.34,60)]
    assert np.isfinite(values).all()
    assert all(abs(p[0])<.15 and abs(p[1])<.17 for p in values)
    a=nihang_look.crown_point(0,.10,.270,.114)
    b=nihang_look.crown_point(0,.05,.270,.114)
    assert abs(a[1]-.012)>abs(b[1]-.012)


def test_diagnostic_views_are_enumerated_not_arbitrary_camera_code():
    from movie_factory.adapters.blender.nihang_control import validate
    recipe={'operation':'nihang_frames','frame':283,'width':540,'height':960,'samples':8,'frames':[283]}
    for view in ('production','leader_front','leader_reverse','crowd_front'):
        assert validate(recipe|{'view':view})['view']==view
    for view in ('anything', '../camera.py', 'eval()', 1):
        with pytest.raises(ValueError):validate(recipe|{'view':view})
    with pytest.raises(ValueError):validate(recipe|{'view':'leader_front','camera':{}})
