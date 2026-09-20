import numpy as np
import pytest
from movie_factory.upperbody_review import differences,measure

def test_face_region_excludes_neck():
    a=np.zeros((800,640,3),dtype=np.uint8);b=a.copy();b[592:]=255
    assert differences(a,b)['rgb_max_0_255']==0
    b[100,100]=3
    assert differences(a,b)['pixels_over_2']==1

def test_shape_and_variant_guards():
    with pytest.raises(ValueError):differences(np.zeros((3,3)),np.zeros((3,3)))
    for variant in (True,0,28,'../'):
        with pytest.raises(ValueError):measure(variant)
