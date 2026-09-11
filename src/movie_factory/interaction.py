"""Pure state, timing, sampling, and Director gates for 3D-05."""
from __future__ import annotations

import math


def smootherstep(value:float)->float:
    if type(value) not in {int,float} or not math.isfinite(value): raise ValueError("finite value required")
    x=min(1.0,max(0.0,float(value))); return 6*x**5-15*x**4+10*x**3


def timing_envelope(frame:float,start:float=28,end:float=76,width:float=8)->float:
    if frame<=start or frame>=end: return 0.0
    if frame<start+width: return smootherstep((frame-start)/width)
    if frame>end-width: return smootherstep((end-frame)/width)
    return 1.0


def interaction_time(frame:float,role:str)->float:
    if role=="baseline": return float(frame)
    if role=="candidate": return float(frame)+4*timing_envelope(frame)
    raise ValueError("role must be baseline or candidate")


def interaction_state(source_time:float)->str:
    if source_time<=16: return "supported"
    if source_time<40: return "reaching"
    if source_time<48: return "grasped"
    if source_time<68: return "lifting"
    return "held"


def expected_state(frame:float,role:str)->str: return interaction_state(interaction_time(frame,role))


def expected_owner(frame:float,role:str)->str:
    return "sword_support_01" if interaction_time(frame,role)<40 else "character_01/right_hand"


def required_sample_times(config:dict)->list[float]:
    baseline=config["baseline"]; sampling=config["sampling"]
    start=baseline["timeline_frame_start"]; end=baseline["timeline_frame_end"]
    values={round(start+i*sampling["regular_step_frames"],9)
            for i in range(round((end-start)/sampling["regular_step_frames"])+1)}
    step=sampling["dense_step_frames"]
    for low,high in sampling["dense_windows"]:
        values.update(round(low+i*step,9) for i in range(round((high-low)/step)+1))
    return sorted(value for value in values if start<=value<=end)


def validate_director_review(review:dict,assignment:dict,config:dict)->dict:
    checks=[]
    def check(name,passed,details=None): checks.append({"name":name,"passed":bool(passed),"details":details})
    check("review.status",review.get("status") in {"ACCEPTED","REJECTED"},review.get("status"))
    check("review.assignment",review.get("blind_assignment_id")==assignment.get("blind_assignment_id"))
    labels=assignment.get("labels",{}); check("review.mapping",set(labels)=={"A","B"} and set(labels.values())=={"baseline","candidate"},labels)
    fields=("interaction_readability","grasp_contact_believability","transition_smoothness","hold_clearance")
    clips=review.get("clips",{}); valid=lambda value:type(value) in {int,float} and 1<=value<=5 and abs(value*2-round(value*2))<1e-12
    for label in ("A","B"):
        for field in fields: check(f"review.{label}.{field}",valid(clips.get(label,{}).get(field)),clips.get(label,{}).get(field))
        check(f"review.{label}.visible_defects",isinstance(clips.get(label,{}).get("visible_defects"),list))
    check("review.duration",type(review.get("review_seconds")) in {int,float} and review["review_seconds"]>0,review.get("review_seconds"))
    if any(not item["passed"] for item in checks):
        return {"schema_version":"1.0","passed":False,"checks":checks,"errors":[item["name"] for item in checks if not item["passed"]]}
    candidate_label=next(label for label,role in labels.items() if role=="candidate"); baseline_label=next(label for label,role in labels.items() if role=="baseline")
    candidate=clips[candidate_label]; baseline=clips[baseline_label]; gate=config["director_gate"]
    check("creative.minimum_scores",all(candidate[field]>=gate["minimum_candidate_score"] for field in fields),candidate)
    check("creative.readability_improved",candidate["interaction_readability"]-baseline["interaction_readability"]>=gate["minimum_readability_improvement"])
    check("creative.no_regression",all(candidate[field]>=baseline[field] for field in fields if field!="interaction_readability"))
    check("creative.preference",review.get("preference")==candidate_label,{"preference":review.get("preference"),"candidate":candidate_label})
    check("creative.major_defects",len(review.get("major_defects",[]))<=gate["major_defects_allowed"],review.get("major_defects"))
    errors=[item["name"] for item in checks if not item["passed"]]
    return {"schema_version":"1.0","passed":not errors,"checks":checks,"errors":errors,
            "candidate_label":candidate_label,"baseline_label":baseline_label}
