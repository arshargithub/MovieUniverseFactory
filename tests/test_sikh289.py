import math
import pytest
from movie_factory.sikh289_motion import *

def test_travel_continuity_and_forward():
    for t in (8,10,18.5,20,22):
        assert abs(travel(t-1e-7)-travel(t+1e-7))<2e-6
    ys=[travel(i/120) for i in range(3121)]
    assert all(b<=a for a,b in zip(ys,ys[1:]))
    assert travel(18)==travel(10)

def test_front_contact_lateral_anchor():
    for i in range(312):
        t=i/FPS
        assert abs(bike_position(t)[0]+.7*math.sin(yaw(t)))<1e-12

def test_roll_direction_and_lock():
    assert wheel_angle(2)<wheel_angle(1)
    assert wheel_angle(9,True)==wheel_angle(9.5,True)
    assert wheel_angle(9)!=wheel_angle(9.5)
    for t in (8.7,10):
        assert abs(wheel_angle(t-1e-7,True)-wheel_angle(t+1e-7,True))<1e-5

def test_crowd_clear_before_passage():
    assert travel(20)>-19
    for i in range(12):
        for foot in (0,1):
            d,h=crowd_step(21,i,foot)
            assert d==pytest.approx(1.7)
            assert abs(h)<1e-12

def test_rear_settles():
    assert rear_amount(15)==0
    assert rear_amount(16.7)==pytest.approx(1)
    assert rear_amount(18.2)==0

def test_opening_has_real_travel_preroll():
    assert travel(-2)==pytest.approx(travel(0)+14)
    assert travel(-.01)-travel(.01)==pytest.approx(.14)

def test_stationary_foot_does_not_slide_between_steps():
    # First foot moves in step zero; second remains planted for that interval.
    for dt in (.01,.10,.25,.47):
        assert crowd_step(17.7+dt,0,1)==(0.,0.)
    assert crowd_step(17.7+.48,0,0)[0]==pytest.approx(.85)
    assert crowd_step(17.7+.70,0,0)[0]==pytest.approx(.85)

def test_travel_speed_is_continuous_at_splices():
    h=1e-5
    for t in (8,10,18.5,20,22):
        left=(travel(t)-travel(t-h))/h;right=(travel(t+h)-travel(t))/h
        assert abs(left-right)<1e-3

def test_all_staging_samples_are_finite():
    assert FRAMES/FPS==26
    for i in range(FRAMES):
        t=i/FPS
        assert all(math.isfinite(v) for v in (*bike_position(t),wheel_angle(t),wheel_angle(t,True),rear_amount(t)))

@pytest.mark.parametrize('job',[{'operation':'eval','version':1},{'operation':'movie','version':True},{'operation':'movie','version':0},{'operation':'movie','version':1,'code':'x'}])
def test_dispatch_closed(job):
    with pytest.raises(ValueError): validate_job(job)
