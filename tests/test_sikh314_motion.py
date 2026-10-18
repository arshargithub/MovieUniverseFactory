import pytest
from movie_factory.sikh314_motion import pose,curve,validate

def test_joint_profiles_not_one_scaled_envelope():
    a,b=pose(15.30),pose(15.48)
    assert abs(a['rise']-b['rise'])<.03
    assert abs(a['elbow']-b['elbow'])>.06
    assert pose(15.90)['fold']<pose(15.90)['rise']

def test_preparation_and_recovery_independent_of_body_rise():
    assert pose(14.65)['neck']>.45 and pose(14.65)['rise']==0
    assert pose(16.16)['neck']>.3 and pose(16.16)['rise']==0

def test_profiles_return_to_baseline_and_sides_differ():
    assert pose(29)['rise']==pose(29)['head']==pose(29)['fold']==0
    assert pose(15.1,'L')['elbow']!=pose(15.1,'R')['elbow']
    assert curve(-1,[(0,1),(1,2)])==1

@pytest.mark.parametrize('job',[{},dict(operation='exec',version=1),dict(operation='build',version=True),dict(operation='build',version=999)])
def test_fail_closed(job):
    with pytest.raises(ValueError):validate(job)
