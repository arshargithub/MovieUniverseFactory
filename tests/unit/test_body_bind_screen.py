import pytest
from movie_factory.adapters.blender import body_bind_screen as b


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'}, {'operation':'bind01','path':'x'}])
def test_fixed_bind_operation(job):
    with pytest.raises(ValueError):b.validate(job)


def test_trousers_cannot_follow_fingers_or_other_leg():
    names=['root','spine05','upperleg01.L','upperleg01.R','finger1-1.L','wrist.L']
    assert b.allowed_bones('MF_body154_trouser_1',names)=={'root','spine05','upperleg01.L'}


def test_sleeves_are_side_specific():
    names=['upperarm01.L','upperarm01.R','lowerarm01.R','spine02','upperleg01.R']
    assert b.allowed_bones('MF_loose_tunic_sleeve_-1',names)=={'upperarm01.R','lowerarm01.R'}


def test_proxy_hands_rigid_to_wrist():
    assert b.allowed_bones('MF_body154_finger_-1_2',[])=={'wrist.R'}
