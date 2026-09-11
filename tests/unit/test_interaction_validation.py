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
        rows.append({**{role+"_"+key:value for role in ("baseline","candidate") for key,value in {"supported_translation_error_m":0,"thumb_contact_distance_m":.002,"finger_contact_distance_m":.002,"maximum_hand_penetration_m":0,"maximum_hand_support_penetration_m":0,"contact_angular_coverage_degrees":190,"wrist_swing_degrees":20,"wrist_twist_degrees":5,"forearm_twist_degrees":40,"thumb_side_up_dot":.7}.items()}, "frame":frame,"baseline_state":expected_state(frame,"baseline"),"candidate_state":expected_state(frame,"candidate"),
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
        "hand_support_penetration":lambda value:value["samples"][0].update(candidate_maximum_hand_support_penetration_m=.1),
        "thumb_down_grasp":lambda value:value["samples"][-1].update(candidate_thumb_side_up_dot=-.7),
        "locked_forearm_roll":lambda value:value["samples"][-1].update(candidate_wrist_twist_degrees=150),
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


def test_anatomy_measurements_fail_closed_when_absent_or_nonfinite():
    for key in ("wrist_swing_degrees", "wrist_twist_degrees", "forearm_twist_degrees", "thumb_side_up_dot"):
        for value in (None, float("nan"), float("inf")):
            raw = passing_metrics()
            raw["samples"][-1]["candidate_"+key] = value
            result = validate_interaction_metrics(raw, CONFIG)
            assert not result["passed"]
            assert any(error.startswith("anatomy.candidate.") for error in result["errors"])


def coordinated_metrics():
    config=json.loads((ROOT/'feasibility/3d/3d-05/prototypes/coordinated-lift/campaign.json').read_text())
    raw=passing_metrics()
    for row in raw['samples']:
        for role in ('baseline','candidate'):
            t=config['baseline'][role+'_transitions']
            w=max(0,min(1,(row['frame']-t['lift'])/(t['held']-t['lift'])))
            row.update({role+'_'+k:v for k,v in {
                'hand_radial_up_dot':.9,'hand_pitch_degrees':25*w,
                'forearm_pitch_degrees':40*w,'elbow_flexion_degrees':50+20*w,
                'head_attention_gain_degrees':30,'elbow_edge_ratio_min':.8,
                'elbow_edge_ratio_max':1.2,'elbow_reference_edge_count':20}.items()})
    return raw,config


def test_coordinated_probes_fail_closed_and_detect_no_motion():
    raw,config=coordinated_metrics()
    assert validate_interaction_metrics(raw,config)['passed']
    for key in ('hand_pitch_degrees','forearm_pitch_degrees','elbow_flexion_degrees',
                'head_attention_gain_degrees','elbow_edge_ratio_min','elbow_edge_ratio_max',
                'elbow_reference_edge_count','hand_radial_up_dot'):
        for value in (None,float('nan'),float('inf')):
            broken=deepcopy(raw);broken['samples'][-1]['candidate_'+key]=value
            assert not validate_interaction_metrics(broken,config)['passed'],key
    broken=deepcopy(raw)
    for row in broken['samples']:
        row['candidate_forearm_pitch_degrees']=0
    assert 'motion.candidate.forearm_pitch' in validate_interaction_metrics(broken,config)['errors']
    broken=deepcopy(raw);broken['samples'][0]['candidate_elbow_edge_ratio_max']=2.5
    assert 'motion.candidate.elbow_skin' in validate_interaction_metrics(broken,config)['errors']


def test_coordinated_controls_cannot_be_omitted():
    from movie_factory.validators.interaction import MOTION_CONTROL_EXPECTATIONS
    controls={name:{'passed':False,'errors':list(errors)} for name,errors in CONTROL_EXPECTATIONS.items()}
    assert not validate_control_sensitivity(controls,coordinated=True)['passed']
    controls.update({name:{'passed':False,'errors':list(errors)} for name,errors in MOTION_CONTROL_EXPECTATIONS.items()})
    assert validate_control_sensitivity(controls,coordinated=True)['passed']


def test_lift_skin_control_is_distinct_from_preexisting_reach_failure():
    raw,config=coordinated_metrics()
    raw['samples'][0]['candidate_elbow_edge_ratio_max']=1.82
    errors=validate_interaction_metrics(raw,config)['errors']
    assert 'motion.candidate.elbow_skin' in errors
    assert 'motion.candidate.lift_elbow_skin' not in errors
    next(row for row in raw['samples'] if row['frame']==60)['candidate_elbow_edge_ratio_max']=2.5
    assert 'motion.candidate.lift_elbow_skin' in validate_interaction_metrics(raw,config)['errors']


def test_controls_do_not_take_credit_for_positive_case_failures():
    controls={name:{'passed':False,'errors':list(errors)} for name,errors in CONTROL_EXPECTATIONS.items()}
    result=validate_control_sensitivity(controls,positive_result={'errors':['grip.translation']})
    assert not result['passed']
    assert 'controls.hand_sword_sliding' in result['errors']


def surface_metrics():
    from movie_factory.interaction import expected_owner
    raw=passing_metrics();config=deepcopy(CONFIG)
    config['surface_ownership_thresholds']={'minimum_nonhandle_body_clearance_m':.04,'minimum_handle_body_clearance_m':.01,'minimum_head_staging_clearance_m':.12,'maximum_forbidden_triangle_intersections':0,'maximum_forbidden_contained_vertices':0,'minimum_nonhandle_hand_clearance_m':0}
    for row in raw['samples']:
        for role in ('baseline','candidate'):
            held=expected_owner(row['frame'],role).endswith('right_hand')
            row[role+'_grip_translation_error_m']=0;row[role+'_grip_orientation_error_degrees']=0
            row[role+'_evaluated_constraints']=[{'type':'CHILD_OF','target':'character_01_armature' if held else 'sword_support_01','bone':'RightHand' if held else '', 'muted':False,'valid':True,'influence':1.0}]
            row[role+'_surface_validation']={'protected_body_clearance_lower_bound_m':.05,'head_clearance_lower_bound_m':.15,'nonhandle_hand_clearance_lower_bound_m':.01,'forbidden_triangle_intersections':0,'forbidden_contained_vertices':0,'surface_sample_count':100,'maximum_surface_cover_radius_m':.015,'region_triangle_counts':{'1':10,'2':20,'3':20},'region_body_clearance_lower_bound_m':{'1':.02,'2':.05,'3':.06}}
    return raw,config


def test_actual_owner_required_even_when_schedule_and_grip_are_perfect():
    raw,config=surface_metrics();assert validate_interaction_metrics(raw,config)['passed']
    for mode in ('dual','missing','wrong_bone','muted','invalid','nan'):
        broken=deepcopy(raw);constraints=broken['samples'][-1]['candidate_evaluated_constraints']
        if mode=='dual':constraints.append({**constraints[0],'target':'sword_support_01','bone':''})
        elif mode=='missing':constraints[0]['influence']=0
        elif mode=='wrong_bone':constraints[0]['bone']='LeftHand'
        elif mode=='muted':constraints[0]['muted']=True
        elif mode=='invalid':constraints[0]['valid']=False
        else:constraints[0]['influence']=float('nan')
        assert 'ownership.candidate.evaluated_owner' in validate_interaction_metrics(broken,config)['errors']


def test_surface_validation_is_symmetric_and_fails_closed():
    raw,config=surface_metrics()
    for role in ('baseline','candidate'):
        for key,value,error in [('forbidden_triangle_intersections',1,'intersections'),('forbidden_contained_vertices',1,'containment'),('head_clearance_lower_bound_m',.08,'head_comfort')]:
            broken=deepcopy(raw);broken['samples'][0][role+'_surface_validation'][key]=value
            assert f'surface.{role}.{error}' in validate_interaction_metrics(broken,config)['errors']
        for value in (None,float('nan'),float('inf')):
            broken=deepcopy(raw);broken['samples'][0][role+'_surface_validation']['head_clearance_lower_bound_m']=value
            assert f'surface.{role}.coverage' in validate_interaction_metrics(broken,config)['errors']
    broken=deepcopy(raw);broken['samples'][0]['candidate_surface_validation']['region_triangle_counts'].pop('3')
    assert 'surface.candidate.coverage' in validate_interaction_metrics(broken,config)['errors']
