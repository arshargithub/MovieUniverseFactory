from movie_factory.evaluator import RUBRIC_DIMENSIONS, score_candidate


THRESHOLDS = {
    "positive_pass_rate_min": 1.0,
    "negative_sensitivity_min": 1.0,
    "negative_critical_finding_rate_min": 1.0,
    "accepted_dimension_mae_max": 1.0,
    "accepted_scores_within_one_min": 0.8,
    "response_valid_rate_min": 1.0,
}


def review(*, passing, scores=None):
    values = scores or {name: 5 for name in RUBRIC_DIMENSIONS}
    return {"error":None,"cost_usd":.001,"data":{
        "scores":[{"dimension":name,"score":values[name],"evidence":"visible evidence"} for name in sorted(RUBRIC_DIMENSIONS)],
        "critical_findings":[] if passing else ["visible injected defect"],
        "confidence":.9,"recommendation":"pass" if passing else "repair",
    }}


def test_balanced_evaluator_requires_positive_agreement_and_negative_sensitivity():
    director={name:5 for name in RUBRIC_DIMENSIONS}
    labels={"positive":{"expected":"pass","category":"accepted","director_scores":director},"negative":{"expected":"non_pass","category":"camera_drift"}}
    result=score_candidate({"positive":review(passing=True),"negative":review(passing=False)},labels,THRESHOLDS)
    assert result["qualified"] is True
    assert result["metrics"]["negative_sensitivity"] == 1


def test_indiscriminate_all_pass_evaluator_is_rejected():
    director={name:5 for name in RUBRIC_DIMENSIONS}
    labels={"positive":{"expected":"pass","category":"accepted","director_scores":director},"negative":{"expected":"non_pass","category":"missing_object"}}
    result=score_candidate({"positive":review(passing=True),"negative":review(passing=True)},labels,THRESHOLDS)
    assert result["qualified"] is False
    assert result["metrics"]["negative_sensitivity"] == 0
