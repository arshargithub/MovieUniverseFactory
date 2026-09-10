import pytest

from movie_factory.cli import normalize_director_review


def review():
    return {
        "reviewer":"Director","accepted":True,"notes":"Accepted with minor faceting.",
        "scores":{"brief_fulfillment":5,"cinematography":5,"lighting_materials":5,"physical_finish":4,"continuity_revision":5},
    }


def test_director_review_normalizes_complete_accepted_scorecard():
    result=normalize_director_review(review())
    assert result["status"]=="ACCEPTED" and result["mean_score"]==4.8
    assert len(result["scores"])==5 and result["hands_on_edits"] is False


def test_director_review_preserves_half_point_scores():
    value=review()
    value["scores"].update(cinematography=4.5,physical_finish=4.5)
    result=normalize_director_review(value)
    assert result["mean_score"]==4.8
    assert {item["dimension"]:item["score"] for item in result["scores"]}["cinematography"]==4.5


@pytest.mark.parametrize("mutation",[
    lambda value:value["scores"].pop("physical_finish"),
    lambda value:value["scores"].update(physical_finish=2),
    lambda value:value["scores"].update(physical_finish=4.25),
    lambda value:value.update(hands_on_edits=True),
])
def test_invalid_accepted_director_review_is_rejected(mutation):
    value=review(); mutation(value)
    with pytest.raises(ValueError): normalize_director_review(value)
