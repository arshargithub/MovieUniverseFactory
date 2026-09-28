import pytest
from movie_factory.adapters.blender import character_assembly as a


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec'}, {'operation': 'inventory', 'path': '/tmp/a'}, {'operation': 1}])
def test_no_unstructured_input(job):
    with pytest.raises(ValueError):
        a.validate(job)


def test_pinned_sources():
    assert len(a.SOURCE_SHA) == 64
    assert a.SOURCE.name == 'natural-hair.blend'
    assert all(len(sha) == 64 for _, sha in a.DONORS.values())
