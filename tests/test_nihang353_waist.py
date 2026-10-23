import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_waist353 import torso_faces,check_envelope
from movie_factory.adapters.blender.nihang_patch import validate

def test_sleeves_cannot_be_waist_support():
    weights=[[('spine05',1.)]]*3+[[('upperarm01.L',1.)]]*3
    assert torso_faces([(0,1,2),(3,4,5),(0,1,3)],weights)==[0]

def test_mixed_arm_weight_is_not_trunk():
    with pytest.raises(ValueError):torso_faces([(0,1,2)],[[('spine05',.8),('lowerarm01.L',.2)]]*3)

def test_radial_spike_and_nonfinite_fail_closed():
    r=np.full((9,96),.18);assert check_envelope(r)['max_step']==0
    r[2,5]=.24
    with pytest.raises(ValueError):check_envelope(r)
    r[2,5]=np.nan
    with pytest.raises(ValueError):check_envelope(r)

def test_only_fixed_recipe():
    r=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_waist353',target='mounted leader')])
    assert validate(r)==r
    r['edits'][0]['code']='bad'
    with pytest.raises(ValueError):validate(r)
