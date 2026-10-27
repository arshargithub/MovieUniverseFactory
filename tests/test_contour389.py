import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_contour389 import sculpt,validate

def test_fixed_recipe_and_no_payload():
    e=dict(kind='mounted_anatomy389_contour',target='horse');assert validate(e)==e
    with pytest.raises(ValueError):validate(dict(e,amount=.3))

def test_support_identity_limits_and_symmetry():
    p=np.array([[0.,-.94,1.27],[.2,-.94,1.27],[-.2,-.94,1.27],[0,-.8,.5],[0,-.8,2.]],np.float32)
    a,m=sculpt(p,p,np.ones(len(p),bool));assert np.array_equal(a[m==0],p[m==0]);assert np.linalg.norm(a-p,axis=1).max()<.2
    np.testing.assert_allclose(a[1,1:],a[2,1:]);assert a[0,1]>p[0,1] and a[0,2]>p[0,2]
    b,_=sculpt(p,p,np.zeros(len(p),bool));assert np.array_equal(b,p)
