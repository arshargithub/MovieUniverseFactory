"""Independent every-frame gates for the frozen 3D-03 motion addendum."""
from __future__ import annotations

import math


EXPECTED={"idle":(1,33),"run":(1,17),"jump":(1,13)}
EXPECTED_LIMBS={"LeftUpLeg","LeftLeg","LeftFoot","RightUpLeg","RightLeg","RightFoot",
                "LeftArm","LeftForeArm","RightArm","RightForeArm"}


def _check(checks,name,passed,details=None):
    checks.append({"name":name,"passed":bool(passed),"details":details})


def validate_character_motion(raw:dict,config:dict)->dict:
    checks=[]; thresholds=config["thresholds"]
    _check(checks,"identity.experiment",raw.get("experiment_id")=="3D-03-TEMPORAL")
    _check(checks,"identity.camera",raw.get("camera_id")=="camera_B",raw.get("camera_id"))
    clips=raw.get("clips",{})
    _check(checks,"clips.exact_set",set(clips)==set(EXPECTED),sorted(clips))
    for clip,(first,last) in EXPECTED.items():
        item=clips.get(clip,{})
        frames=item.get("frames",[])
        expected_frames=list(range(first,last+1))
        _check(checks,f"{clip}.frame_coverage",[frame.get("frame") for frame in frames]==expected_frames,
               {"observed":len(frames),"expected":len(expected_frames)})
        if not frames: continue
        finite_frames=[frame for frame in frames if frame.get("finite")]
        numeric=[]
        for frame in frames:
            numeric.extend(frame.get("bounds",{}).get("min",[])); numeric.extend(frame.get("bounds",{}).get("max",[]))
            numeric.extend(frame.get("bounds",{}).get("dimensions",[])); numeric.extend(frame.get("centroid",[]))
            numeric.extend(frame.get("foot_min_z_m",{}).values()); numeric.extend(frame.get("limb_length_ratios",{}).values())
            if frame.get("step_from_previous"): numeric.extend(frame["step_from_previous"].values())
            numeric.append(frame.get("timestamp_seconds",0))
        numeric_finite=all(type(value) in {int,float} and math.isfinite(value) for value in numeric)
        _check(checks,f"{clip}.finite",len(finite_frames)==len(frames) and numeric_finite)
        timestamps=[frame.get("timestamp_seconds") for frame in frames]
        source_fps=item.get("source_fps")
        timestamp_ok=(type(source_fps) in {int,float} and source_fps>0 and all(type(value) in {int,float} for value in timestamps)
                      and all(abs((timestamps[index]-timestamps[index-1])-1/source_fps)<=1e-9 for index in range(1,len(timestamps))))
        _check(checks,f"{clip}.timing",timestamp_ok,{"source_fps":source_fps,"timestamps":timestamps})
        bottoms=[frame["bounds"]["min"][2] for frame in finite_frames]
        dimensions=[value for frame in finite_frames for value in frame["bounds"]["dimensions"]]
        heights=[frame["bounds"]["dimensions"][2] for frame in finite_frames]
        _check(checks,f"{clip}.no_floor_penetration",bool(bottoms) and min(bottoms)>=-thresholds["floor_penetration_tolerance_m"],
               {"minimum_z_m":min(bottoms) if bottoms else None})
        _check(checks,f"{clip}.bounded_extent",bool(dimensions) and max(dimensions)<=thresholds["maximum_dimension_m"],
               {"maximum_dimension_m":max(dimensions) if dimensions else None})
        _check(checks,f"{clip}.plausible_height",bool(heights) and min(heights)>=thresholds["minimum_height_m"] and max(heights)<=thresholds["maximum_height_m"],
               {"range_m":[min(heights),max(heights)] if heights else None})
        limb_sets=[set(frame.get("limb_length_ratios",{})) for frame in finite_frames]
        ratios=[ratio for frame in finite_frames for ratio in frame.get("limb_length_ratios",{}).values()]
        _check(checks,f"{clip}.limb_lengths",bool(ratios) and all(names==EXPECTED_LIMBS for names in limb_sets) and max(abs(value-1) for value in ratios)<=thresholds["maximum_limb_length_relative_error"],
               {"maximum_relative_error":max((abs(value-1) for value in ratios),default=None)})
        steps=[frame["step_from_previous"] for frame in finite_frames if frame.get("step_from_previous")]
        _check(checks,f"{clip}.continuous_max_vertex",bool(steps) and max(step["max_vertex_m"] for step in steps)<=thresholds["maximum_vertex_step_m"],
               {"maximum_m":max((step["max_vertex_m"] for step in steps),default=None)})
        _check(checks,f"{clip}.continuous_rms",bool(steps) and max(step["rms_vertex_m"] for step in steps)<=thresholds["maximum_rms_vertex_step_m"],
               {"maximum_m":max((step["rms_vertex_m"] for step in steps),default=None)})
        seam=item.get("loop_seam",{})
        seam_rms=seam.get("rms_vertex_m")
        _check(checks,f"{clip}.loop_seam",type(seam_rms) in {int,float} and seam_rms<=thresholds["maximum_loop_seam_rms_m"],seam)
        feet={side:[frame["foot_min_z_m"][side] for frame in finite_frames] for side in ("left","right")}
        if len(finite_frames)!=len(frames): continue
        contact=thresholds["contact_clearance_m"]
        if clip=="idle":
            ungrounded=sum(min(left,right)>contact for left,right in zip(feet["left"],feet["right"]))
            _check(checks,"idle.grounding",ungrounded<=thresholds["idle_max_ungrounded_frames"],{"ungrounded_frames":ungrounded})
        elif clip=="run":
            contacts={side:sum(value<=contact for value in values) for side,values in feet.items()}
            support=[]
            for left,right in zip(feet["left"],feet["right"]):
                support.append("left" if left<=contact<right else "right" if right<=contact<left else "both" if max(left,right)<=contact else "none")
            alternating=("left" in support and "right" in support and
                         any(a!=b for a,b in zip([x for x in support if x in {"left","right"}],
                                                [x for x in support if x in {"left","right"}][1:])))
            _check(checks,"run.alternating_contact",all(value>=thresholds["run_min_contact_frames_each_foot"] for value in contacts.values()) and alternating,
                   {"contacts":contacts,"support":support})
            peak=max((step["rms_vertex_m"] for step in steps),default=0)
            _check(checks,"run.motion_present",peak>=thresholds["run_min_rms_vertex_step_m"],{"peak_rms_m":peak})
        else:
            endpoint=thresholds["jump_endpoint_contact_m"]
            endpoint_contact=min(feet["left"][0],feet["right"][0])<=endpoint and min(feet["left"][-1],feet["right"][-1])<=endpoint
            airborne=[frame["frame"] for frame,left,right in zip(frames,feet["left"],feet["right"])
                      if min(left,right)>=thresholds["jump_min_airborne_clearance_m"]]
            _check(checks,"jump.takeoff_landing_contact",endpoint_contact,
                   {"first":[feet["left"][0],feet["right"][0]],"last":[feet["left"][-1],feet["right"][-1]]})
            _check(checks,"jump.airborne_phase",len(airborne)>=thresholds["jump_min_airborne_frames"],{"airborne_frames":airborne})
    errors=[item["name"] for item in checks if not item["passed"]]
    return {"schema_version":"1.0","passed":not errors,"checks":checks,"errors":errors,
            "authority":"deterministic_outer_validator","api_can_override":False}
