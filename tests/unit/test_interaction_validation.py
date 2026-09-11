import json
from copy import deepcopy
from pathlib import Path

from movie_factory.validators.interaction import (CONTROL_EXPECTATIONS, validate_control_sensitivity,
                                                   validate_interaction_metrics)


ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT/"feasibility/3d/3d-05/campaign.json").read_text())


def passing_metrics():
    from movie_factory.interaction import expected_owner, expected_state, required_sample_times
    rows=[]
    for frame in required_sample_times(CONFIG):
        owner=expected_owner(frame,"candidate")
        rows.append({**{role+"_"+key:value for role in ("baseline","candidate") for key,value in {"supported_translation_error_m":0,"thumb_contact_distance_m":.002,"finger_contact_distance_m":.002,"maximum_hand_penetration_m":0,"contact_angular_coverage_degrees":190}.items()}, "frame":frame,"baseline_state":expected_state(frame,"baseline"),"candidate_state":expected_state(frame,"candidate"),
            "baseline_owner":expected_owner(frame,"baseline"),"candidate_owner":owner,
            "candidate_attachment_influence":1.0 if owner.endswith("right_hand") else 0.0,
            "candidate_grip_translation_error_m":0,"candidate_grip_orientation_error_degrees":0,
            "candidate_sword_min_z_m":.6,"candidate_character_min_z_m":0,"candidate_sword_support_separation_m":.3 if frame>=48 else 0,
            "candidate_non_handle_body_clearance_m":.1,"candidate_character_root_translation_m":0,
            "character_max_vertex_delta_m":.02 if 28<frame<76 else 0,"character_rms_vertex_delta_m":.01 if 28<frame<76 else 0,
            "sword_translation_delta_m":.02 if 28<frame<76 else 0,"sword_orientation_delta_degrees":0})
    return {"experiment_id":"3D-05","timeline":{"fps":24,"frame_start":1,"frame_end":96},
        "protected":{name:True for name in ("source_actions_equal","character_identity_equal","character_topology_equal","character_weights_equal","character_materials_equal","character_rig_equal","lights_equal","world_equal")},
        "samples":rows,"half_frame_steps":[{"character_rms_m":.01,"sword_translation_m":.01}],
        "attachment_discontinuities":{role:{"position_second_difference_m":0,"orientation_second_difference_degrees":0} for role in ("baseline","candidate")},
        "boundaries":{str(frame):{"character_rms_velocity_delta_m_per_s":0,"sword_velocity_delta_m_per_s":0} for frame in (28,76)},
        "timing":{"baseline_grasp_frame":40,"candidate_grasp_frame":36,"baseline_lift_frame":48,"candidate_lift_frame":44,"baseline_held_frame":68,"candidate_held_frame":64},
        "persistence":{name:True for name in ("checkpoints_exact","save_reopen_semantic_exact","offline_replay_semantic_exact","offline_replay_geometry_within_tolerance")}}


def test_passing_metrics_and_controls():
    raw=passing_metrics(); assert validate_interaction_metrics(raw,CONFIG)["passed"]
    controls={}
    mutations={
        "open_hand_attachment":lambda value:value["samples"][-1].update(candidate_contact_angular_coverage_degrees=0),
        "oversized_handle":lambda value:value["samples"][-1].update(candidate_maximum_hand_penetration_m=.02),
        "early_attachment":lambda value:value["samples"][0].update(candidate_attachment_influence=1),
        "attachment_teleportation":lambda value:value["attachment_discontinuities"]["candidate"].update(position_second_difference_m=.1),
        "hand_sword_sliding":lambda value:value["samples"][-1].update(candidate_grip_translation_error_m=.1),
        "penetration":lambda value:value["samples"][-1].update(candidate_non_handle_body_clearance_m=0),
        "edit_leakage":lambda value:(value["samples"][0].update(character_max_vertex_delta_m=.1,sword_translation_delta_m=.1)),
    }
    for name,mutate in mutations.items():
        broken=deepcopy(raw); mutate(broken); controls[name]=validate_interaction_metrics(broken,CONFIG)
        assert CONTROL_EXPECTATIONS[name] <= set(controls[name]["errors"])
    assert validate_control_sensitivity(controls)["passed"]
