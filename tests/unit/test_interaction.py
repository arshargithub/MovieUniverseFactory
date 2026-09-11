import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from movie_factory.interaction import (expected_owner,expected_state,interaction_time,required_sample_times,
                                       timing_envelope,validate_director_review)
from movie_factory.packages import content_id,file_digest


ROOT=Path(__file__).resolve().parents[2]
CONFIG=json.loads((ROOT/"feasibility/3d/3d-05/campaign.json").read_text())


def test_state_machine_and_timing_revision_are_exact():
    assert [expected_state(frame,"baseline") for frame in (16,16.5,40,48,68)]==["supported","reaching","grasped","lifting","held"]
    assert [expected_state(frame,"candidate") for frame in (16,16.5,36,44,64)]==["supported","reaching","grasped","lifting","held"]
    assert expected_owner(39.875,"baseline")=="sword_support_01"
    assert expected_owner(40,"baseline")=="character_01/right_hand"
    assert expected_owner(36,"candidate")=="character_01/right_hand"
    assert interaction_time(28,"candidate")==28 and interaction_time(76,"candidate")==76
    assert interaction_time(36,"candidate")==40 and interaction_time(64,"candidate")==68


def test_timing_envelope_has_zero_boundary_value_and_slope():
    assert timing_envelope(28)==timing_envelope(76)==0
    h=1e-5
    assert timing_envelope(28+h)/h==pytest.approx(0,abs=1e-8)
    assert timing_envelope(76-h)/h==pytest.approx(0,abs=1e-8)


def test_dense_samples_cover_boundaries_and_transitions():
    samples=required_sample_times(CONFIG)
    assert samples[0]==1 and samples[-1]==96
    assert all(value in samples for value in (28,35.875,36,36.125,39.875,40,40.125,44,48,64,68,75.875,76,76.125))


def test_frozen_inputs_and_campaign_digest_are_exact():
    baseline=ROOT/CONFIG["baseline"]["character_relative_path"]
    sword=ROOT/CONFIG["baseline"]["sword_asset_relative_path"]
    assert file_digest(baseline)==CONFIG["baseline"]["character_sha256"]
    assert file_digest(sword)==CONFIG["baseline"]["sword_asset_sha256"]
    assert (ROOT/"feasibility/3d/3d-05/campaign.sha256").read_text().strip()==content_id(CONFIG)


def test_director_review_requires_recorded_time_and_candidate_improvement():
    assignment={"blind_assignment_id":"0123456789abcdef","labels":{"A":"candidate","B":"baseline"}}
    clip=lambda readability:{"interaction_readability":readability,"grasp_contact_believability":5,
                             "transition_smoothness":5,"hold_clearance":5,"visible_defects":[]}
    review={"status":"ACCEPTED","blind_assignment_id":assignment["blind_assignment_id"],"clips":{"A":clip(5),"B":clip(4.5)},
            "preference":"A","major_defects":[],"notes":"","review_seconds":60}
    assert validate_director_review(review,assignment,CONFIG)["passed"]
    review["review_seconds"]=None
    assert "review.duration" in validate_director_review(review,assignment,CONFIG)["errors"]


def test_director_schema_is_valid():
    Draft202012Validator.check_schema(json.loads((ROOT/"feasibility/3d/3d-05/director-review.schema.json").read_text()))
