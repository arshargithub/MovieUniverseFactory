import pytest

from movie_factory.revision_compiler import compile_supported_revision


@pytest.mark.parametrize("instruction", [
    "Move the coffee table 40 cm toward the sofa and make the helmet dark green. Do not change the cameras, sofa, room geometry, lighting, or composition.",
    "Please change the helmet shell from red to #163D2A, then move the coffee-table exactly 0.4 metres towards the sofa.",
    "Move only the coffee table 0.4 m toward sofa; also change only the helmet to dark-green.",
])
def test_supported_unambiguous_revision_compiles(instruction):
    result = compile_supported_revision(instruction)
    assert result["status"] == "compiled"
    assert [item["op"] for item in result["operations"]["operations"]] == ["translate_toward", "set_base_color"]


@pytest.mark.parametrize("instruction", [
    "Move the coffee table about 40 cm toward the sofa and make the helmet dark green.",
    "Move the coffee table 40 cm toward the sofa or the lamp and make the helmet dark green.",
    "Move the coffee table 40 cm toward the sofa and make the helmet blue.",
    "Move the coffee table 40 cm toward the sofa, make the helmet dark green, and brighten the key light.",
])
def test_ambiguous_or_out_of_scope_revision_escalates(instruction):
    result = compile_supported_revision(instruction)
    assert result["status"] == "escalate" and "operations" not in result
