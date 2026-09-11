import pytest
from movie_factory.gesture import source_time, validate


def test_timing_has_exact_support_and_matches_declared_cue():
    assert source_time(44) == 48
    for frame in (-1, 0, 23.999, 24, 72, 72.001, 96):
        assert source_time(frame) == frame
    for boundary in (24, 72):
        h=.0001
        assert abs((source_time(boundary+h)-source_time(boundary-h))/(2*h)-1) < 1e-6


def test_cue_missing_is_not_a_pass():
    metric = {'baseline_cue_frame':48,'candidate_cue_frame':None,'outside_max_vertex_delta_m':0,
              'outside_max_rotation_delta_rad':0,'boundary_position_delta_m':0,'boundary_velocity_delta_m_s':0,
              'boundary_angular_velocity_delta_deg_s':0,'support_displacement_m':0,'min_z_m':0,
              'elbow_min':1,'elbow_max':1,'landmark_position_rms_m':0,'landmark_rotation_error_deg':0,
              'finite':True,'protected':True}
    assert validate(metric)['errors'] == ['candidate_cue']
