import math
import pytest
from movie_factory import sikh315_motion as m
from movie_factory import sikh305_motion as old
def test_preserved_first_stop_and_rest():
    for i in range(370):
        t=i*.05
        assert m.travel(t)==old.travel(t)
        assert m.yaw(t)==old.yaw(t)
def test_spin_then_grip_acceleration():
    assert max(m.speed(t) for t in (21.4,21.7,22,22.3))<3.2
    assert m.speed(25)>4*m.speed(22)
    assert abs(m.yaw(22))>.30
    assert abs(m.yaw(23.4))<.001
    assert m.speed(23.4)<m.speed(25)
    assert abs(m.rear_distance(22.5)-m.rear_distance(21.4))>2*abs(m.travel(22.5)-m.travel(21.4))
def test_continuous_monotonic_travel():
    for i in range(360,690):
        t=i*.05
        assert m.travel(t+.001)<=m.travel(t)
        assert abs((m.travel(t+.0001)-m.travel(t-.0001))/.0002+m.speed(t))<.01
def test_active_apex_and_asymmetry():
    assert all(m.rear(t)>.85 for t in (15.3,15.8,16.2,16.6))
    assert m.rear(17.1)==0
    # Delayed paw trajectories may cross at an instant; compare the interval.
    differences=[abs(m.pose(t)['elbow']-m.pose(t,'R')['elbow']) for t in (15.35,15.55,15.7,15.9,16.1,16.3)]
    assert max(differences)>.10 and sum(differences)/len(differences)>.03
    assert m.gather(14.4)>.9 and m.landing(17.17)>.9

def test_bounded_render_jobs():
    from scripts.sikh315_run import validate_job
    assert validate_job({'operation':'movie','version':6,'start':1,'end':24})==('movie',6)
    for job in ({'operation':'movie','version':6,'start':1,'end':25},{'operation':'proof','version':6,'start':1,'end':24},{'operation':'movie','version':6,'start':True,'end':24},{'operation':'reopen','version':6,'code':'x'}):
        with pytest.raises(ValueError):validate_job(job)
