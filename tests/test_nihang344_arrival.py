import pytest
from movie_factory.adapters.blender.nihang_motion import arrival_position

def test_actual_arrival_accelerates_to_ground_without_airborne_ease():
    start=[7,-28,4.184737];previous=[7,-28,4.272452];end=[7.12,-28.43,3.28283]
    samples=[arrival_position(start,previous,end,i/24,7/24) for i in range(8)]
    velocities=[(b[2]-a[2])*24 for a,b in zip(samples,samples[1:])]
    assert samples[0]==start and samples[-1]==pytest.approx(end)
    assert all(b<a<0 for a,b in zip(velocities,velocities[1:]))
    assert velocities[-1]<-3.5

def test_arrival_rejects_upward_or_decelerating_path():
    with pytest.raises(ValueError):arrival_position([0,0,2],[0,0,1],[0,0,0],.1,.3)
    with pytest.raises(ValueError):arrival_position([0,0,2],[0,0,3],[0,0,1.9],.1,.3)
