import math
import pytest
from movie_factory import sikh305_motion as c
from movie_factory import sikh304_motion as old

def test_stopped_location_and_first_brake_protected():
    for i in range(2141):
        t=i/100
        assert c.travel(t)==old.travel(t)
    assert math.isclose(c.travel(10),-3.6)

def test_departure_extended_and_continuous():
    assert c.FRAMES>528
    h=1e-4
    for t in (21.4,21.6,22.3,26.2):
        assert abs(c.travel(t+h)-c.travel(t-h))<.01
        left=(c.travel(t)-c.travel(t-h))/h
        right=(c.travel(t+h)-c.travel(t))/h
        assert abs(left-right)<.02
    assert c.travel((c.FRAMES-1)/24*c.RATE)<-230

def test_launch_velocity_and_acceleration():
    h=.001
    for i in range(100):
        t=21.41+i*.12
        v=(c.travel(t+h)-c.travel(t-h))/(2*h)*c.RATE
        a=(c.travel(t+h)-2*c.travel(t)+c.travel(t-h))/h**2*c.RATE**2
        assert -27<v<0
        assert -5.1<a<.02

def test_cloud_support_does_not_contract():
    states=[c.dust_state(i/24) for i in range(145)]
    assert all(b[0]>=a[0] for a,b in zip(states,states[1:]))
    assert states[-1][1]==0
    assert .1<c.dust_state(2)[1]<.5
    assert c.dust_state(3)[1]<c.dust_state(1)[1]/3

def test_rear_has_gather_and_quicker_rise():
    assert c.gather(14.8)>.9
    assert c.rear(14.8)==0
    assert c.rear(15.4)==1
    assert c.rear(16.4)==0
    assert c.landing(16.12)>.9

@pytest.mark.parametrize('job',[{}, {'operation':'exec','version':1},{'operation':'build','version':True},{'operation':'build','version':17}])
def test_fail_closed_jobs(job):
    with pytest.raises(ValueError):c.validate(job)

def test_refinements_bind_only_reviewed_parent_versions():
    for v in (5,6,8,9,10,11):assert c.validate({'operation':'refine','version':v})['version']==v
    for v in (1,4,7):
        with pytest.raises(ValueError):c.validate({'operation':'refine','version':v})

def test_expanding_dust_dilutes_after_formation():
    states=[c.dust_state(.4+i/24) for i in range(130)]
    assert all(b[0]>=a[0] and b[1]<=a[1] for a,b in zip(states,states[1:]))

def test_finish_is_exact_reviewed_derivative():
    for v in (7,12,13):assert c.validate({'operation':'finish','version':v})['version']==v
    for v in (1,6,8,11):
        with pytest.raises(ValueError):c.validate({'operation':'finish','version':v})

def test_spear_and_footwork_precede_rise():
    assert c.spear_lift(14.12)==.42
    assert c.spear_lift(14.28)==0
    assert c.fore_grip(14.32,'L')==1
    assert c.fore_grip(14.45,'R')==1
    assert c.rear(14.55)==0
    assert (15.30-14.86)/c.RATE<.4
    assert (15.48-15.30)/c.RATE<.2
    assert (16.02-15.48)/c.RATE<.5

def test_departure_camera_has_shared_position_aim_and_lens_endpoint():
    a=c.departure_camera(23-1e-6);b=c.departure_camera(23+1e-6)
    for x,y in zip(a[:2],b[:2]):assert max(abs(i-j) for i,j in zip(x,y))<.001
    assert abs(a[2]-b[2])<.001
