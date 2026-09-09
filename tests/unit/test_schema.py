from pathlib import Path

from movie_factory.plans import canonical_revision, fixture_plan
from movie_factory.schema import validate


ROOT = Path(__file__).resolve().parents[2]


def test_fixture_matches_strict_scene_schema():
    assert validate(ROOT, "scene-plan.schema.json", fixture_plan()) == []


def test_scene_schema_rejects_unknown_field():
    plan = fixture_plan(); plan["surprise"] = True
    assert validate(ROOT, "scene-plan.schema.json", plan)


def test_revision_schema_is_exact():
    assert validate(ROOT, "operations.schema.json", canonical_revision()) == []
    bad = canonical_revision(); bad["operations"][0]["distance_m"] = 0.04
    assert validate(ROOT, "operations.schema.json", bad)
