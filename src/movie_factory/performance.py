"""Pure timing and blinded-review rules for the frozen 3D-04 experiment."""
from __future__ import annotations

import math


def smootherstep(value:float)->float:
    if type(value) not in {int,float} or not math.isfinite(value):
        raise ValueError("smootherstep requires one finite number")
    x=min(1.0,max(0.0,float(value)))
    return 6*x**5-15*x**4+10*x**3


def edit_envelope(frame:float,start:float=40,end:float=70,width:float=6)->float:
    if not all(type(value) in {int,float} and math.isfinite(value) for value in (frame,start,end,width)):
        raise ValueError("edit envelope values must be finite numbers")
    if width<=0 or end-start<2*width:
        raise ValueError("edit envelope has an invalid interval or blend width")
    if frame<=start or frame>=end: return 0.0
    if frame<start+width: return smootherstep((frame-start)/width)
    if frame>end-width: return smootherstep((end-frame)/width)
    return 1.0


def repeated_source_frame(timeline_frame:float,unique_frames:int=16)->float:
    if type(timeline_frame) not in {int,float} or not math.isfinite(timeline_frame):
        raise ValueError("timeline frame must be finite")
    if type(unique_frames) is not int or unique_frames<=0:
        raise ValueError("unique frame count must be a positive integer")
    return 1+(timeline_frame-1)%unique_frames


def required_sample_times(config:dict)->list[float]:
    baseline=config["baseline"]; sampling=config["sampling"]
    start=float(baseline["timeline_frame_start"]); end=float(baseline["timeline_frame_end"])
    regular=float(sampling["regular_step_frames"]); boundary=float(sampling["boundary_step_frames"])
    if regular<=0 or boundary<=0: raise ValueError("sample steps must be positive")
    values=set()
    count=round((end-start)/regular)
    values.update(round(start+i*regular,9) for i in range(count+1))
    for low,high in sampling["boundary_windows"]:
        count=round((high-low)/boundary)
        values.update(round(low+i*boundary,9) for i in range(count+1))
    return sorted(value for value in values if start<=value<=end)


def validate_director_review(review:dict,assignment:dict,config:dict)->dict:
    checks=[]
    def check(name,passed,details=None): checks.append({"name":name,"passed":bool(passed),"details":details})
    check("review.status",review.get("status") in {"ACCEPTED","REJECTED"},review.get("status"))
    check("review.assignment",review.get("blind_assignment_id")==assignment.get("blind_assignment_id"))
    labels=assignment.get("labels",{})
    check("review.mapping",set(labels)=={"A","B"} and set(labels.values())=={"baseline","candidate"},labels)
    clips=review.get("clips",{})
    def valid_score(value): return type(value) in {int,float} and 1<=value<=5 and abs(value*2-round(value*2))<=1e-12
    for label in ("A","B"):
        item=clips.get(label,{})
        for field in ("run_readability","foot_contact_quality","transition_smoothness"):
            check(f"review.{label}.{field}",valid_score(item.get(field)),item.get(field))
        check(f"review.{label}.visible_defects",isinstance(item.get("visible_defects"),list))
    if any(not item["passed"] for item in checks):
        return {"schema_version":"1.0","passed":False,"checks":checks,
                "errors":[item["name"] for item in checks if not item["passed"]],"candidate_label":None}
    candidate_label=next(label for label,role in labels.items() if role=="candidate")
    baseline_label=next(label for label,role in labels.items() if role=="baseline")
    candidate=clips[candidate_label]; baseline=clips[baseline_label]; gate=config["director_gate"]
    check("creative.readability_improved",
          candidate["run_readability"]-baseline["run_readability"]>=gate["minimum_readability_improvement"],
          {"baseline":baseline["run_readability"],"candidate":candidate["run_readability"]})
    check("creative.contact_quality",
          candidate["foot_contact_quality"]>=gate["minimum_candidate_contact_quality"] and
          (not gate["candidate_contact_must_not_regress"] or candidate["foot_contact_quality"]>=baseline["foot_contact_quality"]),
          {"baseline":baseline["foot_contact_quality"],"candidate":candidate["foot_contact_quality"]})
    check("creative.transition_smoothness",
          candidate["transition_smoothness"]>=gate["minimum_candidate_transition_smoothness"],candidate["transition_smoothness"])
    check("creative.preference",not gate["candidate_preference_required"] or review.get("preference")==candidate_label,
          {"preference":review.get("preference"),"candidate_label":candidate_label})
    defects=review.get("major_defects",[])
    check("creative.major_defects",isinstance(defects,list) and len(defects)<=gate["major_defects_allowed"],defects)
    errors=[item["name"] for item in checks if not item["passed"]]
    return {"schema_version":"1.0","passed":not errors,"checks":checks,"errors":errors,
            "candidate_label":candidate_label,"baseline_label":baseline_label}
