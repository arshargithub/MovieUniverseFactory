"""Independent deterministic gates for the frozen 3D-05 interaction."""
from __future__ import annotations

import math

from ..interaction import expected_owner, expected_state, required_sample_times


PROTECTED_FLAGS = (
    "source_actions_equal", "character_identity_equal", "character_topology_equal",
    "character_weights_equal", "character_materials_equal", "character_rig_equal",
    "lights_equal", "world_equal",
)

CONTROL_EXPECTATIONS = {
    "early_attachment": {"ownership.influence"},
    "attachment_teleportation": {"attachment.candidate.position_continuity"},
    "hand_sword_sliding": {"grip.translation"},
    "penetration": {"clearance.body"},
    "edit_leakage": {"preservation.outside_character_max", "preservation.outside_sword_translation"},
    "open_hand_attachment": {"grasp.candidate.enclosure"},
    "oversized_handle": {"grasp.candidate.penetration"},
    "thumb_down_grasp": {"anatomy.candidate.thumb_up"},
    "locked_forearm_roll": {"anatomy.candidate.wrist_twist"},
    "hand_support_penetration": {"grasp.candidate.support_penetration"},
}


def _check(checks, name, passed, details=None):
    checks.append({"name": name, "passed": bool(passed), "details": details})


def validate_interaction_metrics(raw: dict, config: dict) -> dict:
    checks = []
    thresholds = config["thresholds"]
    _check(checks, "identity.experiment", raw.get("experiment_id") == "3D-05")
    _check(checks, "identity.timeline", raw.get("timeline") == {"fps": 24, "frame_start": 1, "frame_end": 96})
    protected = raw.get("protected", {})
    for name in PROTECTED_FLAGS:
        _check(checks, "protected."+name, protected.get(name) is True)
    rows = raw.get("samples", [])
    observed = [round(row.get("frame", math.nan), 9) for row in rows]
    expected = required_sample_times(config)
    _check(checks, "sampling.coverage", observed == expected, {"observed": len(observed), "expected": len(expected)})
    numeric_keys = (
        "candidate_grip_translation_error_m", "candidate_grip_orientation_error_degrees",
        "candidate_sword_min_z_m", "candidate_character_min_z_m",
        "candidate_sword_support_separation_m", "candidate_non_handle_body_clearance_m",
        "candidate_character_root_translation_m", "character_max_vertex_delta_m",
        "character_rms_vertex_delta_m", "sword_translation_delta_m",
        "sword_orientation_delta_degrees",
    )
    numeric = [row.get(key) for row in rows for key in numeric_keys]
    _check(checks, "sampling.finite", bool(rows) and all(type(value) in {int, float} and math.isfinite(value) for value in numeric))
    if rows:
        for role in ("baseline", "candidate"):
            held_rows = [row for row in rows if expected_owner(row["frame"], role).endswith("right_hand")]
            anatomy_limits = {"wrist_swing": "maximum_wrist_swing_degrees",
                              "wrist_twist": "maximum_wrist_twist_degrees",
                              "forearm_twist": "maximum_forearm_twist_degrees"}
            for metric, limit in anatomy_limits.items():
                values = [row.get(role+"_"+metric+"_degrees") for row in rows]
                finite = all(type(value) in (int, float) and math.isfinite(value) and value >= 0 for value in values)
                _check(checks, f"anatomy.{role}.{metric}", finite and max(values) <= thresholds[limit], max(values) if finite else "missing/nonfinite")
            bend = [row.get(role+"_wrist_swing_degrees") for row in held_rows]
            finite_bend = bool(bend) and all(type(value) in (int,float) and math.isfinite(value) for value in bend)
            _check(checks, f"anatomy.{role}.attached_wrist_swing", finite_bend and max(bend) <= thresholds["maximum_attached_wrist_swing_degrees"], max(bend) if finite_bend else "missing/nonfinite")
            up = [row.get(role+"_thumb_side_up_dot") for row in rows if row["frame"] >= 24]
            finite_up = bool(up) and all(type(value) in (int,float) and math.isfinite(value) and -1 <= value <= 1 for value in up)
            _check(checks, f"anatomy.{role}.thumb_up", finite_up and min(up) >= thresholds["minimum_acquisition_thumb_side_up_dot"], min(up) if finite_up else "missing/nonfinite")
            supported_rows = [row for row in rows if expected_owner(row["frame"], role) == "sword_support_01"]
            stationary = max((row.get(role+"_supported_translation_error_m", math.inf) for row in supported_rows), default=math.inf)
            _check(checks, f"support.{role}.stationary", stationary <= thresholds["maximum_supported_translation_error_m"], stationary)
            for metric in ("supported_translation_error_m", "thumb_contact_distance_m", "finger_contact_distance_m", "maximum_hand_penetration_m", "contact_angular_coverage_degrees"):
                _check(checks, f"grasp.{role}.finite.{metric}", all(type(row.get(role+"_"+metric)) in (int,float) and math.isfinite(row[role+"_"+metric]) for row in rows))
            for part in ("thumb", "finger"):
                distance = max((row.get(role+"_"+part+"_contact_distance_m", math.inf) for row in held_rows), default=math.inf)
                _check(checks, f"grasp.{role}.{part}_contact", distance <= thresholds["maximum_digit_contact_distance_m"], distance)
            coverage = min((row.get(role+"_contact_angular_coverage_degrees", 0.0) for row in held_rows), default=0.0)
            _check(checks, f"grasp.{role}.enclosure", coverage >= thresholds["minimum_contact_angular_coverage_degrees"], coverage)
            penetration = max((row.get(role+"_maximum_hand_penetration_m", math.inf) for row in rows), default=math.inf)
            _check(checks, f"grasp.{role}.penetration", penetration <= thresholds["maximum_hand_penetration_m"], penetration)
            support_values = [row.get(role+"_maximum_hand_support_penetration_m") for row in rows]
            finite_support = all(type(value) in (int,float) and math.isfinite(value) and value >= 0 for value in support_values)
            _check(checks, f"grasp.{role}.support_penetration", finite_support and max(support_values) <= thresholds["maximum_hand_support_penetration_m"], max(support_values) if finite_support else "missing/nonfinite")
        _check(checks, "states.sequence", all(row["candidate_state"] == expected_state(row["frame"], "candidate") and
                                               row["baseline_state"] == expected_state(row["frame"], "baseline") for row in rows))
        _check(checks, "ownership.single", all(row["candidate_owner"] == expected_owner(row["frame"], "candidate") and
                                                row["baseline_owner"] == expected_owner(row["frame"], "baseline") for row in rows))
        _check(checks, "ownership.influence", all(abs(row["candidate_attachment_influence"]-
                                                        (1.0 if expected_owner(row["frame"], "candidate").endswith("right_hand") else 0.0)) <= 1e-8
                                                   for row in rows))
        initial = rows[0]
        _check(checks, "support.initial_contact", abs(initial["candidate_sword_support_separation_m"]) <= thresholds["support_contact_error_m"],
               initial["candidate_sword_support_separation_m"])
        attached = [row for row in rows if expected_owner(row["frame"], "candidate").endswith("right_hand")]
        _check(checks, "grip.translation", bool(attached) and max(row["candidate_grip_translation_error_m"] for row in attached) <= thresholds["grip_translation_error_m"],
               max((row["candidate_grip_translation_error_m"] for row in attached), default=None))
        _check(checks, "grip.orientation", bool(attached) and max(row["candidate_grip_orientation_error_degrees"] for row in attached) <= thresholds["grip_orientation_error_degrees"],
               max((row["candidate_grip_orientation_error_degrees"] for row in attached), default=None))
        _check(checks, "clearance.body", min(row["candidate_non_handle_body_clearance_m"] for row in rows) >= thresholds["minimum_blade_body_clearance_m"],
               min(row["candidate_non_handle_body_clearance_m"] for row in rows))
        _check(checks, "clearance.floor", min(min(row["candidate_sword_min_z_m"], row["candidate_character_min_z_m"]) for row in rows) >= -thresholds["floor_penetration_tolerance_m"])
        lifting_samples = [row for row in rows if row["frame"] in {48.0, 52.0}]
        _check(checks, "support.lifting_separation", len(lifting_samples) == 2 and
               all(row["candidate_sword_support_separation_m"] >= thresholds["minimum_lifting_support_separation_m"] for row in lifting_samples), lifting_samples)
        held = [row for row in rows if row["frame"] >= 64]
        _check(checks, "support.held_separation", bool(held) and min(row["candidate_sword_support_separation_m"] for row in held) >= thresholds["minimum_held_support_separation_m"],
               min((row["candidate_sword_support_separation_m"] for row in held), default=None))
        _check(checks, "stationary.character_root", max(row["candidate_character_root_translation_m"] for row in rows) <= thresholds["stationary_root_translation_m"])
        outside = [row for row in rows if row["frame"] <= 28 or row["frame"] >= 76]
        _check(checks, "preservation.outside_character_max", max(row["character_max_vertex_delta_m"] for row in outside) <= thresholds["outside_character_max_vertex_delta_m"])
        _check(checks, "preservation.outside_character_rms", max(row["character_rms_vertex_delta_m"] for row in outside) <= thresholds["outside_character_rms_vertex_delta_m"])
        _check(checks, "preservation.outside_sword_translation", max(row["sword_translation_delta_m"] for row in outside) <= thresholds["outside_sword_translation_delta_m"])
        _check(checks, "preservation.outside_sword_orientation", max(row["sword_orientation_delta_degrees"] for row in outside) <= thresholds["outside_sword_orientation_delta_degrees"])
    steps = raw.get("half_frame_steps", [])
    _check(checks, "continuity.character", bool(steps) and max(row["character_rms_m"] for row in steps) <= thresholds["maximum_character_rms_half_frame_step_m"],
           max((row["character_rms_m"] for row in steps), default=None))
    _check(checks, "continuity.sword", bool(steps) and max(row["sword_translation_m"] for row in steps) <= thresholds["maximum_sword_half_frame_step_m"],
           max((row["sword_translation_m"] for row in steps), default=None))
    for role in ("baseline", "candidate"):
        item = raw.get("attachment_discontinuities", {}).get(role, {})
        _check(checks, f"attachment.{role}.position_continuity",
               type(item.get("position_second_difference_m")) in {int, float} and
               item["position_second_difference_m"] <= thresholds["attachment_position_second_difference_m"], item)
        _check(checks, f"attachment.{role}.orientation_continuity",
               type(item.get("orientation_second_difference_degrees")) in {int, float} and
               item["orientation_second_difference_degrees"] <= thresholds["attachment_orientation_second_difference_degrees"], item)
    for frame in (28, 76):
        item = raw.get("boundaries", {}).get(str(frame), {})
        _check(checks, f"boundary.{frame}.character_velocity",
               type(item.get("character_rms_velocity_delta_m_per_s")) in {int, float} and
               item["character_rms_velocity_delta_m_per_s"] <= thresholds["boundary_character_rms_velocity_delta_m_per_s"], item)
        _check(checks, f"boundary.{frame}.sword_velocity",
               type(item.get("sword_velocity_delta_m_per_s")) in {int, float} and
               item["sword_velocity_delta_m_per_s"] <= thresholds["boundary_sword_velocity_delta_m_per_s"], item)
    timing = raw.get("timing", {})
    for state in ("grasp", "lift", "held"):
        shift = timing.get(f"baseline_{state}_frame", math.nan)-timing.get(f"candidate_{state}_frame", math.nan)
        _check(checks, f"timing.{state}", math.isfinite(shift) and
               abs(shift-thresholds["required_timing_shift_frames"]) <= thresholds["timing_shift_tolerance_frames"], shift)
    persistence = raw.get("persistence", {})
    for name in ("checkpoints_exact", "save_reopen_semantic_exact", "offline_replay_semantic_exact", "offline_replay_geometry_within_tolerance"):
        _check(checks, "persistence."+name, persistence.get(name) is True)
    errors = [item["name"] for item in checks if not item["passed"]]
    return {"schema_version": "1.0", "passed": not errors, "checks": checks, "errors": errors,
            "authority": "deterministic_outer_validator", "provider_can_override": False}


def interaction_protected_flags(parent: dict, current: dict) -> dict:
    source_actions = ("character_action_idle", "character_action_run", "character_action_jump")
    source_equal = all(parent.get("actions", {}).get(name) == current.get("actions", {}).get(name) for name in source_actions)
    parent_mesh = parent.get("objects", {}).get("character_01_mesh", {})
    current_mesh = current.get("objects", {}).get("character_01_mesh", {})
    parent_armature = parent.get("objects", {}).get("character_01_armature", {})
    current_armature = current.get("objects", {}).get("character_01_armature", {})
    parent_root = parent.get("objects", {}).get("character_01", {})
    current_root = current.get("objects", {}).get("character_01", {})
    root_fields = ("location", "rotation_euler", "scale", "matrix_world", "source_geometry")
    rig_fields = ("source_geometry", "matrix_world", "matrix_parent_inverse", "modifiers")
    return {
        "source_actions_equal": source_equal,
        "character_identity_equal": parent_root.get("custom_properties", {}).get("mf_creation_id") == current_root.get("custom_properties", {}).get("mf_creation_id"),
        "character_topology_equal": parent_mesh.get("source_geometry") == current_mesh.get("source_geometry"),
        "character_weights_equal": parent_mesh.get("vertex_groups") == current_mesh.get("vertex_groups"),
        "character_materials_equal": parent_mesh.get("material_ids") == current_mesh.get("material_ids"),
        "character_rig_equal": all(parent_armature.get(key) == current_armature.get(key) for key in rig_fields) and
                               all(parent_armature.get("armature", {}).get(key) == current_armature.get("armature", {}).get(key)
                                   for key in parent_armature.get("armature", {}) if key != "sampled_pose_matrices") and
                               all(parent_root.get(key) == current_root.get(key) for key in root_fields),
        "lights_equal": parent.get("lights") == current.get("lights"),
        "world_equal": parent.get("world") == current.get("world"),
    }


def validate_control_sensitivity(results: dict) -> dict:
    checks = []
    _check(checks, "controls.exact_set", set(results) == set(CONTROL_EXPECTATIONS), sorted(results))
    for name, expected in CONTROL_EXPECTATIONS.items():
        result = results.get(name, {})
        errors = set(result.get("errors", []))
        _check(checks, "controls."+name, result.get("passed") is False and expected <= errors,
               {"expected_errors": sorted(expected), "observed_errors": sorted(errors)})
    errors = [item["name"] for item in checks if not item["passed"]]
    return {"schema_version": "1.0", "passed": not errors, "checks": checks, "errors": errors}
