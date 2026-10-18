import math
import pytest
from movie_factory import sikh304_motion as m

def test_recovery_and_second_skid():
    assert abs(m.lean(5.8))>.10
    assert abs(m.lean(6.4))<.001
    assert abs(m.lean(7.0))<.035
    assert math.degrees(m.yaw(8))==pytest.approx(42)

def test_monotone_and_continuous_travel():
    times=[i/240 for i in range(26*240)]
    values=[m.travel(t) for t in times]
    assert all(b<=a+1e-9 for a,b in zip(values,values[1:]))
    for t in (3.6,6.15,6.5,7.5,21.4,21.95,22.1,23.3):assert abs(m.travel(t-1e-6)-m.travel(t+1e-6))<.0001

def test_stop_deceleration_and_crowd_clearance():
    dt=.001
    times=[3.601+i*.001 for i in range(3898)]
    acceleration=[-(m.travel(t+dt)-2*m.travel(t)+m.travel(t-dt))/dt**2*m.RATE**2 for t in times]
    assert min(acceleration)>-7.4
    assert max(acceleration)<.01
    assert m.travel(7.5)==pytest.approx(-3.6)
    assert m.travel(18.4)==pytest.approx(-3.6)
    assert -(m.travel(1+dt)-m.travel(1-dt))/(2*dt)*m.RATE>18

def test_wheel_lock_and_bounded_launch():
    for a,b in ((5.6,6.1),(6.75,7.45)):assert m.rear_distance(a)==pytest.approx(m.rear_distance(b))
    assert m.rear_distance(6.5)<m.rear_distance(6.2)
    assert max(m.lateral(t/100) for t in range(2100,2400))<=.231
    assert abs(m.yaw(21.95))<math.radians(7)

def test_launch_acceleration_not_position_patch():
    dt=.001
    accelerations=[-(m.travel(t+dt)-2*m.travel(t)+m.travel(t-dt))/dt**2*m.RATE**2 for t in [21.41+i*.01 for i in range(450)]]
    assert min(accelerations)>=-.01
    assert max(accelerations)<3.65
    assert -(m.travel(26)-m.travel(25.999))/.001*m.RATE<20.1

def test_job_fail_closed():
    with pytest.raises(ValueError):m.validate({'operation':'eval','version':1})
    with pytest.raises(ValueError):m.validate({'operation':'build','version':1,'code':'x'})
