"""Independent numerical gates for the frozen 3D-04 timeline edit."""
from __future__ import annotations

from copy import deepcopy
import math

from ..performance import required_sample_times


PROTECTED_FLAGS=("source_action_equal","semantic_state_equal","topology_equal","weights_equal",
                 "materials_equal","cameras_equal","lights_equal","world_equal","render_settings_equal",
                 "character_root_equal","armature_object_equal")


def _check(checks,name,passed,details=None):
    checks.append({"name":name,"passed":bool(passed),"details":details})


def validate_performance_metrics(raw:dict,config:dict)->dict:
    checks=[]; thresholds=config["thresholds"]; baseline=config["baseline"]
    _check(checks,"identity.experiment",raw.get("experiment_id")=="3D-04")
    _check(checks,"identity.baseline_native",raw.get("baseline_native_sha256")==baseline["sha256"])
    _check(checks,"identity.timeline",raw.get("timeline") == {
        "fps":baseline["timeline_fps"],"frame_start":baseline["timeline_frame_start"],
        "frame_end":baseline["timeline_frame_end"],"unique_source_frames":baseline["action_unique_frames"]})
    protected=raw.get("protected",{})
    for name in PROTECTED_FLAGS: _check(checks,"protected."+name,protected.get(name) is True)
    samples=raw.get("samples",[]); observed=[round(item.get("frame",float("nan")),9) for item in samples]
    expected=required_sample_times(config)
    _check(checks,"sampling.coverage",observed==expected,{"observed":len(observed),"expected":len(expected)})
    numeric=[]
    for item in samples:
        numeric.extend(item.get(key) for key in ("max_vertex_delta_m","rms_vertex_delta_m","candidate_min_z_m",
                                                 "maximum_limb_length_relative_error","candidate_step_max_vertex_m",
                                                 "candidate_step_rms_vertex_m"))
    _check(checks,"sampling.finite",bool(samples) and all(type(value) in {int,float} and math.isfinite(value) for value in numeric))
    if samples:
        outside=[item for item in samples if item["frame"]<=40 or item["frame"]>=70]
        _check(checks,"preservation.outside_max",bool(outside) and max(item["max_vertex_delta_m"] for item in outside)<=thresholds["outside_max_vertex_delta_m"],
               max((item["max_vertex_delta_m"] for item in outside),default=None))
        _check(checks,"preservation.outside_rms",bool(outside) and max(item["rms_vertex_delta_m"] for item in outside)<=thresholds["outside_rms_vertex_delta_m"],
               max((item["rms_vertex_delta_m"] for item in outside),default=None))
        _check(checks,"geometry.no_floor_penetration",min(item["candidate_min_z_m"] for item in samples)>=-thresholds["floor_penetration_tolerance_m"],
               min(item["candidate_min_z_m"] for item in samples))
        _check(checks,"geometry.limb_lengths",max(item["maximum_limb_length_relative_error"] for item in samples)<=thresholds["maximum_limb_length_relative_error"],
               max(item["maximum_limb_length_relative_error"] for item in samples))
        _check(checks,"geometry.continuous_max",max(item["candidate_step_max_vertex_m"] for item in samples)<=thresholds["maximum_vertex_step_m"],
               max(item["candidate_step_max_vertex_m"] for item in samples))
        _check(checks,"geometry.continuous_rms",max(item["candidate_step_rms_vertex_m"] for item in samples)<=thresholds["maximum_rms_vertex_step_m"],
               max(item["candidate_step_rms_vertex_m"] for item in samples))
        core=[item for item in samples if 46<=item["frame"]<=64]
        _check(checks,"meaningful.core_max_vertex",bool(core) and max(item["max_vertex_delta_m"] for item in core)>=thresholds["minimum_core_max_vertex_delta_m"],
               max((item["max_vertex_delta_m"] for item in core),default=None))
        _check(checks,"meaningful.core_rms_vertex",bool(core) and max(item["rms_vertex_delta_m"] for item in core)>=thresholds["minimum_core_max_rms_vertex_delta_m"],
               max((item["rms_vertex_delta_m"] for item in core),default=None))
    boundaries=raw.get("boundaries",{})
    for frame in (40,70):
        item=boundaries.get(str(frame),{})
        _check(checks,f"boundary.{frame}.value",type(item.get("max_vertex_delta_m")) in {int,float} and
               item["max_vertex_delta_m"]<=thresholds["boundary_max_vertex_delta_m"],item)
        _check(checks,f"boundary.{frame}.velocity_rms",type(item.get("rms_velocity_delta_m_per_s")) in {int,float} and
               item["rms_velocity_delta_m_per_s"]<=thresholds["boundary_rms_velocity_delta_m_per_s"],item)
        _check(checks,f"boundary.{frame}.velocity_max",type(item.get("max_velocity_delta_m_per_s")) in {int,float} and
               item["max_velocity_delta_m_per_s"]<=thresholds["boundary_max_velocity_delta_m_per_s"],item)
    segments=raw.get("support_segments",[])
    _check(checks,"contacts.present",bool(segments))
    _check(checks,"contacts.retained",bool(segments) and all(item.get("candidate_contact_retained") for item in segments),segments)
    _check(checks,"contacts.induced_slide",bool(segments) and all(item.get("candidate_induced_slide_m",math.inf)<=thresholds["maximum_candidate_induced_support_slide_m"] for item in segments),segments)
    _check(checks,"contacts.slide_regression",bool(segments) and all(item.get("candidate_slide_m",math.inf)-item.get("baseline_slide_m",0)<=thresholds["maximum_slide_regression_m"] for item in segments),segments)
    achieved=raw.get("achieved",{})
    pelvis=achieved.get("peak_absolute_pelvis_correction_m"); lean=achieved.get("peak_chest_lean_degrees")
    _check(checks,"meaningful.pelvis",type(pelvis) in {int,float} and thresholds["minimum_peak_pelvis_correction_m"]<=pelvis<=thresholds["maximum_peak_pelvis_correction_m"],pelvis)
    _check(checks,"meaningful.chest_lean",type(lean) in {int,float} and thresholds["minimum_peak_chest_lean_degrees"]<=lean<=thresholds["maximum_peak_chest_lean_degrees"],lean)
    persistence=raw.get("persistence",{})
    for name in ("save_reopen_semantic_exact","save_reopen_geometry_within_tolerance","offline_replay_semantic_exact","offline_replay_geometry_within_tolerance"):
        _check(checks,"persistence."+name,persistence.get(name) is True)
    errors=[item["name"] for item in checks if not item["passed"]]
    return {"schema_version":"1.0","passed":not errors,"checks":checks,"errors":errors,
            "authority":"deterministic_outer_validator","provider_can_override":False}


CONTROL_EXPECTATIONS={
    "no_op":{"meaningful.core_max_vertex","meaningful.core_rms_vertex","meaningful.pelvis","meaningful.chest_lean"},
    "edit_every_cycle":{"preservation.outside_max","preservation.outside_rms"},
    "boundary_leakage":{"boundary.40.value","boundary.40.velocity_rms","boundary.40.velocity_max"},
    "support_foot_slide":{"contacts.induced_slide","contacts.slide_regression"},
}


def protected_snapshot_flags(parent:dict,current:dict)->dict:
    """Compare only state that 3D-04 does not authorize changing."""
    source_actions=("character_action_idle","character_action_run","character_action_jump")
    source_action_equal=all(parent.get("actions",{}).get(name)==current.get("actions",{}).get(name) for name in source_actions)
    parent_mesh=parent.get("objects",{}).get("character_01_mesh",{}); current_mesh=current.get("objects",{}).get("character_01_mesh",{})
    parent_armature=parent.get("objects",{}).get("character_01_armature",{}); current_armature=current.get("objects",{}).get("character_01_armature",{})
    parent_root=parent.get("objects",{}).get("character_01",{}); current_root=current.get("objects",{}).get("character_01",{})
    static_object_fields=("parent_id","matrix_parent_inverse","rotation_euler","rotation_mode","scale","modifiers","constraints","drivers","visibility","visible_render","source_geometry")
    armature_static=all(parent_armature.get(key)==current_armature.get(key) for key in static_object_fields)
    armature_bones=parent_armature.get("armature",{}).get("bones")==current_armature.get("armature",{}).get("bones")
    root_fields=("location","rotation_euler","rotation_mode","scale","matrix_local","matrix_world","matrix_parent_inverse","custom_properties")
    render_fields=("settings","image_settings","cycles","view_settings","display_settings","sequencer_colorspace","compositor","shot_bindings","unit_settings","collections")
    flags={
        "source_action_equal":source_action_equal,
        "topology_equal":parent_mesh.get("source_geometry")==current_mesh.get("source_geometry"),
        "weights_equal":parent_mesh.get("vertex_groups")==current_mesh.get("vertex_groups"),
        "materials_equal":parent.get("materials")==current.get("materials") and parent.get("images")==current.get("images"),
        "cameras_equal":parent.get("cameras")==current.get("cameras"),
        "lights_equal":parent.get("lights")==current.get("lights"),
        "world_equal":parent.get("world")==current.get("world"),
        "render_settings_equal":all(parent.get("render",{}).get(key)==current.get("render",{}).get(key) for key in render_fields),
        "character_root_equal":all(parent_root.get(key)==current_root.get(key) for key in root_fields),
        "armature_object_equal":armature_static and armature_bones,
    }
    flags["semantic_state_equal"]=all(flags.values())
    return flags


def inject_performance_control(raw:dict,name:str)->dict:
    """Apply a fast validator-unit control; Blender controls are run separately."""
    if name not in CONTROL_EXPECTATIONS: raise ValueError("Unknown 3D-04 negative control")
    value=deepcopy(raw)
    if name=="no_op":
        for item in value["samples"]: item["max_vertex_delta_m"]=item["rms_vertex_delta_m"]=0
        value["achieved"]={"peak_absolute_pelvis_correction_m":0,"peak_chest_lean_degrees":0}
    elif name=="edit_every_cycle":
        for item in value["samples"]:
            if item["frame"]<=40 or item["frame"]>=70:
                item["max_vertex_delta_m"]=.03; item["rms_vertex_delta_m"]=.013
    elif name=="boundary_leakage":
        value["boundaries"]["40"]={"max_vertex_delta_m":.01,"rms_vertex_delta_m":.01,
            "rms_velocity_delta_m_per_s":.2,"max_velocity_delta_m_per_s":.3}
    else:
        value["support_segments"][0]["candidate_induced_slide_m"]+=.08
        value["support_segments"][0]["candidate_slide_m"]+=.08
    return value


def validate_control_sensitivity(results:dict)->dict:
    checks=[]
    _check(checks,"controls.exact_set",set(results)==set(CONTROL_EXPECTATIONS),sorted(results))
    for name,expected in CONTROL_EXPECTATIONS.items():
        result=results.get(name,{})
        errors=set(result.get("errors",[]))
        _check(checks,"controls."+name,result.get("passed") is False and expected<=errors,
               {"expected_errors":sorted(expected),"observed_errors":sorted(errors)})
    errors=[item["name"] for item in checks if not item["passed"]]
    return {"schema_version":"1.0","passed":not errors,"checks":checks,"errors":errors}
