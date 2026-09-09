from movie_factory.controller import _revision_prompt


def test_revision_prompt_reads_native_snapshot_object_map():
    snapshot = {"objects": {"sofa_01": {"id": "sofa_01"}, "helmet_01": {"id": "helmet_01"}}}
    prompt = _revision_prompt({"instruction": "perform the bounded revision"}, snapshot)
    assert "helmet_01" in prompt
    assert "sofa_01" in prompt
