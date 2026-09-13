import pytest
from movie_factory.adapters.blender.fullpace_math import target,PERIOD,SPEED,TOUCHDOWN,DUTY,body_z

@pytest.mark.parametrize('leg',list(TOUCHDOWN))
def test_ground_anchor_and_cycle_translation(leg):
    t=(TOUCHDOWN[leg]+DUTY*.2)*PERIOD
    a,s=target(t,leg);b,_=target(t+DUTY*.5*PERIOD,leg)
    assert s and b==pytest.approx(a)
    c,_=target(t+PERIOD,leg)
    assert c==pytest.approx((a[0],a[1]-SPEED*PERIOD,a[2]))

@pytest.mark.parametrize('leg',list(TOUCHDOWN))
def test_contact_velocity_is_continuous(leg):
    eps=1e-7
    for t in ((TOUCHDOWN[leg]+DUTY)*PERIOD,(TOUCHDOWN[leg]+1)*PERIOD):
        a,_=target(t-eps,leg);b,_=target(t+eps,leg)
        assert max(abs(x-y)/(2*eps) for x,y in zip(a,b))<.01

def test_body_is_periodic_and_bounded():
    zs=[body_z(i*PERIOD/1000) for i in range(1001)]
    assert zs[0]==pytest.approx(zs[-1]);assert max(zs)-min(zs)<.15
