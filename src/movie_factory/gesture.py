"""Pure 3D-06A timing and qualification checks."""
import math


def source_time(frame):
    if frame <= 24 or frame >= 72:
        return frame
    x = min(1.0, (frame-24)/8, (72-frame)/8)
    return frame+4*(6*x**5-15*x**4+10*x**3)


def validate(metrics):
    checks = {
        'baseline_cue': metrics['baseline_cue_frame'] is not None and abs(metrics['baseline_cue_frame']-48) <= 1,
        'candidate_cue': metrics['candidate_cue_frame'] is not None and abs(metrics['candidate_cue_frame']-44) <= 1,
        'outside_preserved': metrics['outside_max_vertex_delta_m'] <= 1e-6 and metrics['outside_max_rotation_delta_rad'] <= 1e-5,
        'boundary_position': metrics['boundary_position_delta_m'] <= 1e-5,
        'boundary_velocity': metrics['boundary_velocity_delta_m_s'] <= .02 and metrics['boundary_angular_velocity_delta_deg_s'] <= 10,
        'support': metrics['support_displacement_m'] <= .003,
        'grounding': metrics['min_z_m'] >= -.002,
        'deformation': metrics['elbow_min'] >= .35 and metrics['elbow_max'] <= 1.5,
        'reference_fidelity': metrics['landmark_position_rms_m'] <= .02 and metrics['landmark_rotation_error_deg'] <= 5,
        'finite': metrics['finite'],
        'protected': metrics['protected'],
    }
    return {'passed': all(checks.values()), 'checks': checks,
            'errors': [name for name, passed in checks.items() if not passed]}
