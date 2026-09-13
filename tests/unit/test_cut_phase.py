import pytest
from movie_factory.adapters.blender.cut_phase_math import recovery_phase

def test_support_is_exact_and_swing_monotone():
 for td,duty in ((.32,.14),(.48,.15)):
  for u in (0,.01,.05,duty):assert recovery_phase(td+u,td,duty)==pytest.approx(td+u,abs=1e-14)
  pts=[recovery_phase(td+i/10000,td,duty) for i in range(10001)]
  assert all(b>a for a,b in zip(pts,pts[1:]))

def test_boundaries_are_c1_and_midpoint_is_faster():
 td=.32;d=.14;eps=1e-6
 for p in (td+d,td+1):
  derivative=(recovery_phase(p+eps,td,d)-recovery_phase(p-eps,td,d))/(2*eps)
  assert derivative==pytest.approx(1,abs=1e-5)
 p=td+d+(1-d)/2
 derivative=(recovery_phase(p+eps,td,d)-recovery_phase(p-eps,td,d))/(2*eps)
 assert derivative==pytest.approx(1.5,abs=1e-5)
