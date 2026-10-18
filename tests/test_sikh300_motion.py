import math
import pytest
from movie_factory.sikh300_motion import yaw,lean,slip,rear_distance,ground_height,validate

def test_stop_yaw():
    assert math.degrees(yaw(9))==pytest.approx(42)
    assert 40<=math.degrees(yaw(7.5))<=45
def test_release_visibly_recovers():
    assert abs(math.degrees(lean(5.9)))<10
    assert abs(math.degrees(lean(6.50)))<.5
    assert abs(lean(6.8))>abs(lean(6.50))*10
    assert lean(8)==pytest.approx(0,abs=1e-8)
def test_lock_and_release():
    assert rear_distance(6.1)==pytest.approx(rear_distance(5.6))
    assert rear_distance(6.50)<rear_distance(6.2)
    assert rear_distance(7.4)==pytest.approx(rear_distance(6.6))
    assert not slip(6.5) and slip(6.6)
def test_swale_and_crown():
    assert ground_height(0,0)>ground_height(2.68,0)+.15
    assert ground_height(3.4,0)>ground_height(2.68,0)+.15
    assert ground_height(4,0)>0
    for x in [i*.05 for i in range(-100,101)]:assert abs(ground_height(x+.001,0)-ground_height(x,0))<.002
def test_strict_job():
    assert validate({'operation':'inspect','version':1})
    with pytest.raises(ValueError):validate({'operation':'eval','version':1})
    with pytest.raises(ValueError):validate({'operation':'controls','version':True})
