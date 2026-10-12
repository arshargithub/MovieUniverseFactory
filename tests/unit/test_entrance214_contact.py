import importlib.util
from pathlib import Path
import pytest
import numpy as np

spec=importlib.util.spec_from_file_location('contact214',Path(__file__).resolve().parents[2]/'scripts/entrance214_contact.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def test_closed_operation():
    assert mod.validate({'operation':'inspect01'})=='opening'
    for value in ({'operation':'unknown'}, {'operation':'inspect01','code':'print(1)'}, [], {'path':'/tmp/x'}):
        with pytest.raises(ValueError):mod.validate(value)

def test_return_preserves_endpoints():
    a=np.array([1.,0.,1.]);b=np.array([0.,.5,.3])
    p=mod.return_path(a,[0,0,1],b)
    assert p.shape==(18,3) and np.isfinite(p).all()
    np.testing.assert_allclose(p[0],a);np.testing.assert_allclose(p[-1],b)
    assert p[1,2]>a[2]

@pytest.mark.parametrize('tangent',[[0,0,0],[np.nan,0,1],[1,2]])
def test_bad_return_is_rejected(tangent):
    with pytest.raises(ValueError):mod.return_path([0,0,0],tangent,[1,1,1])

def test_review_clock_and_authority_boundary():
    spec=importlib.util.spec_from_file_location('review214',Path(__file__).resolve().parents[2]/'scripts/entrance214_review.py')
    review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
    assert review.validate({'operation':'motion11'})[1]==tuple(range(217,361))
    assert review.validate({'operation':'motion12'})[1]==tuple(range(361,649))
    assert review.validate({'operation':'motion18'})[1]==tuple(range(217,361))
    assert review.validate({'operation':'motion19'})[1]==tuple(range(361,649))
    with pytest.raises(ValueError):review.validate({'operation':'motion11','source':'/tmp/untrusted.blend'})
