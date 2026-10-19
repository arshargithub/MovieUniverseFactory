import numpy as np
from movie_factory import sikh317_motion as m

def test_filter_retains_low_frequency_removes_chatter():
    x=np.arange(200);slow=.1*np.sin(x*.04);raw=slow+.012*(-1.)**x
    y=m.smooth_response(raw)
    assert np.max(abs(y[10:-10]-slow[10:-10]))<.002
    assert np.mean(np.diff(y,2)**2)<np.mean(np.diff(raw,2)**2)*.01

def test_stop_is_protected():
    assert all(m.travel_response(t)==0 for t in np.linspace(5.3,19.8,100))

def test_brief_apex_and_ground_recovery():
    t=np.arange(13.5,17.6,.001)
    assert sum(m.rear(x)>.94 for x in t)*.001/m.RATE<.65
    assert m.rear(17.1)==0
    assert max(m.pose(x)['wrist'] for x in t)<1.56

def test_planted_feet_and_clearance():
    starts=[]
    for i in range(10):
        starts.append(m.crowd_step(0,i,0)[3])
        for f in (0,1):
            assert m.crowd_step(17,i,f)[:2]==(0,0)
            assert m.crowd_step(21,i,f)[:2]==(1.7,0)
            last=0
            for t in np.linspace(17,21,500):
                d,h,_,_=m.crowd_step(t,i,f)
                assert d>=last-1e-9 and h>=0;last=d
    assert len(set(starts))==10

def test_step_width_does_not_require_split_stance():
    for i in range(10):
        for t in np.linspace(17,21,700):
            left=m.crowd_step(t,i,0);right=m.crowd_step(t,i,1)
            assert abs(left[0]-right[0])<=.425+1e-9
            assert max(left[1],right[1])<=.060+1e-9
