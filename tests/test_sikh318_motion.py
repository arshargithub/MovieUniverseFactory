import numpy as np
import pytest
from movie_factory import sikh318_motion as m

def test_continuous_interior_velocity_and_bounds():
    for t,_ in m.REAR[2:4]:
        e=1e-5;l=(m.rear(t)-m.rear(t-e))/e;r=(m.rear(t+e)-m.rear(t))/e
        assert l>0.1 and abs(l-r)<.002
    a=np.array([m.rear(t) for t in np.linspace(13,18,1001)])
    assert a.min()>=-1e-8 and a.max()<=1.000001

def test_brief_crest_and_coherent_fold():
    ts=np.linspace(13,18,10001)
    assert np.sum([m.rear(t)>.97 for t in ts])*.0005/m.RATE<.22
    for side in ('L','R'):
        for t in (13,18,29):
            p=m.pose(t,side);assert abs(p['wrist'])<1e-8 and abs(p['elbow'])<1e-8

def test_unchanged_travel_and_crowd():
    from movie_factory import sikh317_motion as old
    for t in np.linspace(0,34,100):
        assert m.travel(t)==old.travel(t)
        assert m.crowd_step(t,3,0)==old.crowd_step(t,3,0)
