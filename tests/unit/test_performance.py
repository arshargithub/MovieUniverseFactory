from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from movie_factory.performance import edit_envelope,repeated_source_frame,required_sample_times,validate_director_review
from movie_factory.validators.performance import (inject_performance_control,protected_snapshot_flags,
                                                  validate_control_sensitivity,validate_performance_metrics)


ROOT=Path(__file__).resolve().parents[2]
CONFIG=json.loads((ROOT/"feasibility/3d/3d-04/campaign.json").read_text())


def metrics():
    samples=[]
    for frame in required_sample_times(CONFIG):
        inside=40<frame<70
        samples.append({"frame":frame,"max_vertex_delta_m":.03 if inside else 0,
                        "rms_vertex_delta_m":.013 if inside else 0,"candidate_min_z_m":0,
                        "maximum_limb_length_relative_error":0,
                        "candidate_step_max_vertex_m":.2,"candidate_step_rms_vertex_m":.08})
    return {"experiment_id":"3D-04","baseline_native_sha256":CONFIG["baseline"]["sha256"],
            "timeline":{"fps":24,"frame_start":1,"frame_end":96,"unique_source_frames":16},
            "protected":{name:True for name in ("source_action_equal","semantic_state_equal","topology_equal","weights_equal",
                "materials_equal","cameras_equal","lights_equal","world_equal","render_settings_equal","character_root_equal","armature_object_equal")},
            "samples":samples,"boundaries":{"40":{"max_vertex_delta_m":0,"rms_velocity_delta_m_per_s":0,"max_velocity_delta_m_per_s":0},
                                               "70":{"max_vertex_delta_m":0,"rms_velocity_delta_m_per_s":0,"max_velocity_delta_m_per_s":0}},
            "support_segments":[{"foot":"left","baseline_slide_m":.2,"candidate_slide_m":.201,"candidate_induced_slide_m":.001,"candidate_contact_retained":True},
                                {"foot":"right","baseline_slide_m":.2,"candidate_slide_m":.201,"candidate_induced_slide_m":.001,"candidate_contact_retained":True}],
            "achieved":{"peak_absolute_pelvis_correction_m":.035,"peak_chest_lean_degrees":6},
            "persistence":{"save_reopen_semantic_exact":True,"save_reopen_geometry_within_tolerance":True,
                           "offline_replay_semantic_exact":True,"offline_replay_geometry_within_tolerance":True}}


def test_quintic_envelope_and_repeated_phase_are_exact_at_boundaries():
    assert edit_envelope(40)==edit_envelope(70)==0
    assert edit_envelope(46)==edit_envelope(64)==1
    h=1e-5
    assert (edit_envelope(40+h)-edit_envelope(40))/h==pytest.approx(0,abs=1e-8)
    assert (edit_envelope(70)-edit_envelope(70-h))/h==pytest.approx(0,abs=1e-8)
    assert [repeated_source_frame(frame) for frame in (1,16,17,32,33,96)]==[1,16,1,16,1,16]


def test_sampling_is_dense_at_boundaries():
    samples=required_sample_times(CONFIG)
    assert samples[0]==1 and samples[-1]==96
    assert 40.125 in samples and 69.875 in samples
    assert all(round(38+i*.125,9) in samples for i in range(33))


def test_candidate_metrics_and_failure_controls_are_sensitive():
    passing=metrics(); assert validate_performance_metrics(passing,CONFIG)["passed"]
    controls={name:validate_performance_metrics(inject_performance_control(passing,name),CONFIG)
              for name in CONFIG["negative_controls"]}
    assert validate_control_sensitivity(controls)["passed"]


def test_protected_snapshot_comparison_ignores_only_authorized_timeline_state():
    action={"curves":{"x":1}}; obj={"location":[0,0,0],"rotation_euler":[0,0,0],"rotation_mode":"XYZ","scale":[1,1,1],
        "matrix_local":[],"matrix_world":[],"matrix_parent_inverse":[],"custom_properties":{},"parent_id":None,
        "modifiers":[],"constraints":[],"drivers":[],"visibility":{},"visible_render":True,"source_geometry":{"hash":"mesh"},
        "vertex_groups":{"Hips":{}},"armature":{"bones":[{"name":"Hips"}]}}
    parent={"actions":{name:deepcopy(action) for name in ("character_action_idle","character_action_run","character_action_jump")},
        "objects":{"character_01":deepcopy(obj),"character_01_mesh":deepcopy(obj),"character_01_armature":deepcopy(obj)},
        "materials":{},"images":{},"cameras":{},"lights":{},"world":{},"render":{key:{} for key in
        ("settings","image_settings","cycles","view_settings","display_settings","sequencer_colorspace","compositor","shot_bindings","unit_settings","collections")}}
    current=deepcopy(parent); current["actions"]["character_action_run_3d04_candidate_96"]={}
    assert all(protected_snapshot_flags(parent,current).values())
    current["materials"]["changed"]={}
    assert protected_snapshot_flags(parent,current)["materials_equal"] is False


def test_director_gate_resolves_blind_labels_and_requires_improvement():
    assignment={"blind_assignment_id":"0123456789abcdef","labels":{"A":"candidate","B":"baseline"}}
    review={"status":"ACCEPTED","blind_assignment_id":assignment["blind_assignment_id"],"preference":"A",
            "major_defects":[],"notes":"","clips":{
                "A":{"run_readability":4.5,"foot_contact_quality":4,"transition_smoothness":4.5,"visible_defects":[]},
                "B":{"run_readability":4,"foot_contact_quality":4,"transition_smoothness":4,"visible_defects":[]}}}
    assert validate_director_review(review,assignment,CONFIG)["passed"]
    review["preference"]="tie"
    assert "creative.preference" in validate_director_review(review,assignment,CONFIG)["errors"]


def test_director_schema_is_valid():
    schema=json.loads((ROOT/"feasibility/3d/3d-04/director-review.schema.json").read_text())
    Draft202012Validator.check_schema(schema)


def test_recorded_campaign_digest_matches_canonical_configuration():
    from movie_factory.packages import content_id
    assert (ROOT/"feasibility/3d/3d-04/campaign.sha256").read_text().strip()==content_id(CONFIG)
