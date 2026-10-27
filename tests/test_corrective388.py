import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_corrective388 import isolate,local_mask,validate

def test_zero_and_local():
    a=np.arange(36,dtype=np.float32).reshape(4,3,3)/10;m=np.array([0,1,.5]);assert np.array_equal(isolate(a,m,0),a)
    b=isolate(a,m,1);assert np.array_equal(b[0],a[0]);assert np.array_equal(b[:,0],a[:,0]);assert np.array_equal(b[1:,1],np.tile(a[0,1],(3,1)));assert np.allclose(b[1:,2],(a[1:,2]+a[0,2])/2)

def test_domain():
    r=np.array([[0,-1,1.5],[0,-1,1.9],[0,-1,.5],[0,0,1.5]])
    m=local_mask(r,np.ones(4));assert m[0]==1;assert np.array_equal(m[1:],np.zeros(3))

@pytest.mark.parametrize('bad',[True,2,-1,'1'])
def test_mode_rejected(bad):
    with pytest.raises(ValueError):validate(dict(kind='mounted_anatomy388_corrective_control',target='horse',mode=bad))

def test_recipe_code_rejected():
    with pytest.raises(ValueError):validate(dict(kind='mounted_anatomy388_corrective_control',target='horse',mode=1,code='x'))
