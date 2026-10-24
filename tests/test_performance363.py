"""Clock/interface controls; no motion, cloth or anatomy approval."""
import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_performance363 import edit_time

def inverse(new):
 lo,hi=252.,441.
 for _ in range(50):
  mid=(lo+hi)/2
  if edit_time(mid)<new:lo=mid
  else:hi=mid
 return (lo+hi)/2

def test_phased_clock_is_monotone_and_fast_through_contact():
 x=np.linspace(252,441,5000);y=np.array([edit_time(t) for t in x])
 assert np.diff(y).min()>0
 assert edit_time(300)==300 and edit_time(350)==327
 assert (edit_time(350)-edit_time(307))/(350-307)<.5
 assert (edit_time(350)-edit_time(349.999))/.001==pytest.approx(.5,abs=.001)
 assert edit_time(441)==418

def test_sparse_key_shift_does_not_commute_with_nonlinear_edit():
 # A scalar parent keyed only at interval endpoints and a world attachment
 # baked densely agree on the source linear trajectory. Moving their key
 # times independently creates different trajectories under a nonlinear edit.
 old=np.arange(252,442,dtype=float);new=np.arange(252,419,dtype=float)
 sparse=np.interp(new,[edit_time(252),edit_time(441)],[252,441])
 dense=np.interp(new,[edit_time(t) for t in old],old)
 shared=np.array([inverse(t) for t in new])
 assert np.max(np.abs(sparse-dense))>10
 assert np.max(np.abs(dense-shared))<.1
 assert np.max(np.abs(shared-sparse))>10
 assert shared[0]==pytest.approx(252) and shared[-1]==pytest.approx(441)


def test_director_readable_prep_is_exactly_identity_including_interior():
 for t in np.linspace(252,300,513):assert edit_time(float(t))==float(t)
