import pytest

from movie_factory.animation_timing import action_time_scale,physical_duration_seconds,source_frame_at_timeline_frame


def test_common_timeline_scale_preserves_idle_and_run_duration():
    assert action_time_scale(30,24)==.8
    assert action_time_scale(24,24)==1
    assert physical_duration_seconds(1,33,30)==pytest.approx(32/30)
    assert source_frame_at_timeline_frame(1,1,26.6,30,24)==pytest.approx(33)
    assert source_frame_at_timeline_frame(1,1,17,24,24)==17


@pytest.mark.parametrize("values",[(0,24),(30,0),(float("nan"),24)])
def test_common_timeline_rejects_invalid_rates(values):
    with pytest.raises(ValueError): action_time_scale(*values)
