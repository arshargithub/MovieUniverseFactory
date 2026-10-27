import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_bind386 import validate,solve_step,crossing_pairs,probe_tolerance
from movie_factory.adapters.blender import nihang_patch

def test_closed_binding_operation_accepts_zero_but_not_code_or_excess():
    e=dict(kind='mounted_anatomy386_bind_preserve',target='horse',strength=0.)
    assert validate(e)==e
    nihang_patch.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
    for bad in [dict(e,strength=.8),dict(e,strength=float('nan')),dict(e,code='x')]:
        with pytest.raises(ValueError):validate(bad)

def test_actual_response_inverse_and_singular_rejection():
    J=np.array([[[1.,.2,0],[0,.9,0],[0,0,1.1]],[[0.,-1,0],[1,0,0],[0,0,1]]])
    want=np.array([[.02,-.03,.01],[-.01,.04,.02]])
    error=np.einsum('nij,nj->ni',J,want);got,condition=solve_step(J,error)
    assert np.allclose(got,want) and condition<2
    with pytest.raises(ValueError,match='CONDITION'):solve_step(np.zeros_like(J),error)

def test_native_surface_diagnostic_detects_nonadjacent_crossing():
    p=np.array([[0.,0,0],[1,0,0],[0,1,0],[.2,.2,-1],[.2,.2,1],[.7,.2,.2]])
    faces=np.array([[0,1,2],[3,4,5]])
    assert crossing_pairs(p,faces,np.array([True,True]))=={(0,1)}
    p[3:]+=np.array([4.,0,0])
    assert not crossing_pairs(p,faces,np.array([True,True]))

def test_smaller_probe_cannot_pass_by_relaxing_absolute_error():
    fixed_error=.00003
    assert fixed_error<probe_tolerance(.001)
    assert fixed_error>probe_tolerance(.000125)
    assert probe_tolerance(.000125)<probe_tolerance(.001)

def test_core_binding_is_separate_closed_operation():
    e=dict(kind='mounted_anatomy386_bind_core',target='horse',strength=.6)
    nihang_patch.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
    with pytest.raises(ValueError):validate(dict(e,strength=.9))
