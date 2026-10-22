import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_whole347 import relaxed_points,fold_field
from movie_factory.adapters.blender.nihang_patch import validate

def test_relaxation_keeps_frozen_boundaries_and_finite_shape():
    p=np.array([[0,0,0],[1,0,0],[0,1,0],[.2,.2,1.]])
    q=relaxed_points(p,[(0,3),(1,3),(2,3)],[0,0,0,1])
    assert np.array_equal(q[:3],p[:3]) and 0<q[3,2]<1
    with pytest.raises(ValueError):relaxed_points(p,[(0,4)],[0,0,0,1])
    with pytest.raises(ValueError):relaxed_points(p,[(0,3)],[0,0,0,2])

def test_fold_amplitude_is_small_and_fades_above_chest():
    p=np.array([[.1,-.15,1.22],[.1,-.15,1.6],[.1,0,1.22]])
    d=fold_field(p)
    assert np.abs(d).max()<.020 and np.linalg.norm(d[1])<.0001
    assert np.allclose(d[2],0)
    assert np.allclose(fold_field(np.array([[.1,-.15,1.14],[.1,-.15,1.22]])),0)

def test_anatomy_diagnostic_is_explicit_not_production_hide():
    from movie_factory.adapters.blender.nihang_control import validate as control
    r=dict(operation='nihang_frames',frame=283,frames=[283,327,350],view='leader_anatomy',width=540,height=960,samples=16)
    assert control(r)==r
    with pytest.raises(ValueError):control(r|{'hide':'anything'})

def test_whole_recipe_is_fixed_no_arbitrary_options():
    r=dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,
        edits=[dict(kind='mounted_whole347',target='mounted leader')])
    assert validate(r)==r
    with pytest.raises(ValueError):validate(r|{'edits':[r['edits'][0]|{'path':'anything'}]})
