import math
import pytest
from movie_factory.sikh290_motion import *

def test_full_clock():
    assert FRAMES/FPS==22
    assert RATE*22==26

def test_continuous_speed_and_position():
    h=1e-6
    for t in (8,10,18.5,20,21.5,23.1):
        assert abs(travel(t-h)-travel(t+h))<.00004
        assert abs((travel(t)-travel(t-h))/h-(travel(t+h)-travel(t))/h)<.0001

def test_new_speed_and_acceleration():
    assert (travel(0)-travel(1))*RATE>12
    speed=lambda t:(travel(t-.001)-travel(t+.001))/.002*RATE
    assert speed(22.5)>11
    assert speed(23.5)>17
    assert travel(14)==-13

def test_launch_after_crowd_clear():
    assert travel(21.5)==pytest.approx(-18.4)
    for i in range(10):
        for foot in (0,1):assert crowd_step(21.4,i,foot)==pytest.approx((1.7,0))

def test_short_bounded_slip():
    assert launch_amount(21)==0
    assert launch_amount(22.4)==0
    assert abs(yaw(21.6))<.2
    assert abs(wheel_angle(21.8,True)-wheel_angle(21.7,True))>abs(wheel_angle(21.8)-wheel_angle(21.7))*2

def test_all_frames_finite():
    for i in range(FRAMES):
        t=i/FPS*RATE
        assert all(math.isfinite(x) for x in (*bike_position(t),wheel_angle(t,True),rear_amount(t)))

@pytest.mark.parametrize('job',[{'operation':'eval','version':1},{'operation':'movie','version':True},{'operation':'movie','version':0},{'operation':'movie','version':1,'code':'x'}])
def test_exact_dispatch(job):
    with pytest.raises(ValueError):validate_job(job)
