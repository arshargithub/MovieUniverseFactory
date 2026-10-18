import math
import pytest
from movie_factory.sikh299_motion import travel,yaw,lean,rear_distance,slip,validate
def test_final_angle():assert 45<=math.degrees(yaw(8))<=60
def test_two_locks_and_release():
    assert rear_distance(5.8)==pytest.approx(rear_distance(6.))
    assert rear_distance(6.7)==pytest.approx(rear_distance(7.2))
    assert rear_distance(6.4)<rear_distance(6.2)
def test_lean_and_settle():
    assert math.degrees(lean(5.9))<-12
    assert abs(lean(8))<1e-9
def test_monotone_continuous_travel():
    points=[travel(i/1000) for i in range(4000,8001)]
    assert all(b<=a+1e-8 for a,b in zip(points,points[1:]))
    for t in (4.5,5.4,6.15,6.5,7.5):assert abs(travel(t+1e-7)-travel(t-1e-7))<1e-4
def test_validation():
    with pytest.raises(ValueError):validate({'operation':'exec','version':1})
    with pytest.raises(ValueError):validate({'operation':'movie','version':True})
