import pytest
from movie_factory.adapters.blender.source_gallop_math import LEGS,SPEED,HZ,source_phase,leg_for

def difference(a,b):return (a-b+5)%10-5

@pytest.mark.parametrize('leg',LEGS)
def test_event_map_monotone_periodic_and_c1(leg):
 _,_,a,b,td,stroke=LEGS[leg];d=stroke/(SPEED/HZ);eps=1e-6
 assert abs(difference(source_phase(td,leg),a))<1e-8
 assert abs(difference(source_phase(td+d,leg),b))<1e-8
 for phase in [td,td+d]:
  left=difference(source_phase(phase,leg),source_phase(phase-eps,leg))/eps
  right=difference(source_phase(phase+eps,leg),source_phase(phase,leg))/eps
  assert left==pytest.approx(right,rel=.001)
 for i in range(1000):
  p=i/1000
  assert difference(source_phase(p+.001,leg),source_phase(p,leg))>0
  assert difference(source_phase(p+1,leg),source_phase(p,leg))==pytest.approx(0,abs=1e-10)

def test_complete_distal_controls_share_leg_clock():
 for n in ('forefoot_ik.R','forefoot_heel_ik.R','f_toe_ik.R','f_hoof.R'):assert leg_for(n)=='RF'
 assert leg_for('torso') is None
