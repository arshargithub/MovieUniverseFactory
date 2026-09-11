from copy import deepcopy

from movie_factory.validators.character_motion import validate_character_motion


CONFIG={"thresholds":{
    "floor_penetration_tolerance_m":.015,"minimum_height_m":.8,"maximum_height_m":2.4,"maximum_dimension_m":3,
    "maximum_limb_length_relative_error":.01,"maximum_vertex_step_m":.45,"maximum_rms_vertex_step_m":.18,
    "maximum_loop_seam_rms_m":.18,"contact_clearance_m":.06,"idle_max_ungrounded_frames":0,
    "run_min_contact_frames_each_foot":1,"run_min_rms_vertex_step_m":.005,"jump_endpoint_contact_m":.08,
    "jump_min_airborne_clearance_m":.06,"jump_min_airborne_frames":2}}
LIMBS=("LeftUpLeg","LeftLeg","LeftFoot","RightUpLeg","RightLeg","RightFoot",
       "LeftArm","LeftForeArm","RightArm","RightForeArm")


def evidence():
    clips={}
    for clip,last in (("idle",33),("run",17),("jump",13)):
        frames=[]
        for frame in range(1,last+1):
            left=right=.01
            if clip=="run": left,right=(.01,.12) if frame%2 else (.12,.01)
            if clip=="jump" and frame in {6,7,8}: left=right=.12
            frames.append({"frame":frame,"timestamp_seconds":(frame-1)/24,"finite":True,"bounds":{"min":[-.4,-.2,0],"max":[.4,.2,1.75],"dimensions":[.8,.4,1.75]},
                           "centroid":[0,0,.9],"foot_min_z_m":{"left":left,"right":right},
                           "limb_length_ratios":{name:1.0 for name in LIMBS},
                           "step_from_previous":None if frame==1 else {"delta_seconds":1/24,"max_vertex_m":.04,"rms_vertex_m":.01,
                               "max_vertex_m_per_s":.96,"rms_vertex_m_per_s":.24}})
        clips[clip]={"source_fps":24,"frame_start":1,"frame_end":last,"frame_count":last,"frames":frames,
                     "loop_seam":{"max_vertex_m":.02,"rms_vertex_m":.005}}
    return {"schema_version":"1.0","experiment_id":"3D-03-TEMPORAL","camera_id":"camera_B","clips":clips}


def test_complete_grounded_motion_with_airborne_jump_passes():
    result=validate_character_motion(evidence(),CONFIG)
    assert result["passed"] and not result["errors"] and result["api_can_override"] is False


def test_missing_frame_penetration_discontinuity_and_grounded_jump_fail():
    raw=deepcopy(evidence())
    raw["clips"]["idle"]["frames"].pop()
    raw["clips"]["run"]["frames"][4]["bounds"]["min"][2]=-.1
    raw["clips"]["run"]["frames"][4]["step_from_previous"]["max_vertex_m"]=1.0
    for frame in raw["clips"]["jump"]["frames"]: frame["foot_min_z_m"]={"left":.01,"right":.01}
    result=validate_character_motion(raw,CONFIG)
    assert not result["passed"]
    assert {"idle.frame_coverage","run.no_floor_penetration","run.continuous_max_vertex","jump.airborne_phase"}<=set(result["errors"])


def test_missing_limb_nonfinite_value_and_both_feet_contact_are_rejected():
    raw=deepcopy(evidence())
    raw["clips"]["idle"]["frames"][0]["limb_length_ratios"].pop("LeftArm")
    raw["clips"]["jump"]["frames"][2]["centroid"][0]=float("nan")
    for frame in raw["clips"]["run"]["frames"]: frame["foot_min_z_m"]={"left":.01,"right":.01}
    result=validate_character_motion(raw,CONFIG)
    assert not result["passed"]
    assert {"idle.limb_lengths","run.alternating_contact","jump.finite"}<=set(result["errors"])


def test_fragmented_airborne_samples_do_not_satisfy_contiguous_jump_gate():
    raw=deepcopy(evidence())
    for frame in raw["clips"]["jump"]["frames"]:
        frame["foot_min_z_m"]={"left":.12,"right":.12} if frame["frame"] in {4,8} else {"left":.01,"right":.01}
    config=deepcopy(CONFIG); config["thresholds"]["jump_min_airborne_frames"]=2
    result=validate_character_motion(raw,config)
    assert "jump.airborne_phase" in result["errors"]
