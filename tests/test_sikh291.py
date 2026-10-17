import math
import pytest
from movie_factory.sikh291_motion import *

def test_continuous_position_speed():
    for t in (4.5,7.5,18.5,20,21.5,23):
        e=1e-5
        assert abs(travel(t-e)-travel(t+e))<.001
        left=(travel(t)-travel(t-e))/e;right=(travel(t+e)-travel(t))/e
        assert abs(left-right)<.002
def test_approach_speed_and_clearance():
    assert 16*RATE*3.6>65
    assert travel(8)==pytest.approx(-9.6)
    assert abs(-17.76-(STOP-1.2))>6
    # Screen-clock deceleration below 0.8g; no one-second stop from 68km/h.
    assert (16/3)*RATE**2<.8*9.81
    assert travel(4.5)-travel(7.5)==pytest.approx(24)
def test_pause_and_uncover():
    assert uncover_amount(9.7)==0
    assert uncover_amount(10.5)>0
    assert uncover_amount(11.4)==1
    assert greeting(11.4)==0
    assert greeting(12.3)==pytest.approx(1)
def test_spear_strike_during_rear():
    assert spear_lift(15.2)==pytest.approx(.65)
    assert spear_lift(15.5)==0
    assert rear_amount(15.47)>.95
def test_known_stationary_parts_do_not_roll():
    assert {265,266,296,297,606,607}<=FRONT_FIXED
    assert {95,96}<=REAR_FIXED
    assert {158,278,279,285}<=PARKED
def test_all_samples_finite():
    for f in range(FRAMES):
        t=f/FPS*RATE
        assert all(math.isfinite(v) for v in (*bike_position(t),wheel_angle(t,True),spear_lift(t)))
def test_crowd_clear_before_launch():
    for i in range(10):
        assert sum(crowd_step(21.4,i,j)[0] for j in (0,1))/2>=1.6
def test_dispatch():
    assert validate_job({'operation':'diagnose','version':1})
    with pytest.raises(ValueError):validate_job({'operation':'python','version':1})
