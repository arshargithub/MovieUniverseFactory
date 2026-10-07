import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
spec = importlib.util.spec_from_file_location('entrance187', ROOT / 'scripts/entrance187.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
spec = importlib.util.spec_from_file_location('entrance187_context', ROOT / 'scripts/entrance187_context.py')
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'arbitrary'}, {'operation': 'look01', 'code': 'no'}])
def test_job_contract(job):
    with pytest.raises(ValueError):
        module.validate(job)


def test_bound_source_and_preserved_evidence(tmp_path, monkeypatch):
    source = tmp_path / 'actor.blend'
    source.write_bytes(b'fixture')
    monkeypatch.setattr(module, 'SOURCE', source)
    monkeypatch.setattr(module, 'SOURCE_SHA', module.actor.base.digest(source))
    monkeypatch.setattr(module.actor.base, 'BASE', tmp_path)
    output = module.validate({'operation': 'inspect01'})
    output.mkdir()
    with pytest.raises(ValueError):
        module.validate({'operation': 'inspect01'})
    source.write_bytes(b'changed')
    with pytest.raises(ValueError):
        module.validate({'operation': 'look01'})


def test_traversable_corridor_is_flat_and_side_slopes_do_not_penetrate():
    floor = -19.86
    for y in range(-900, 901, 15):
        center = context.road_center(y)
        for offset in (-23, -12, 0, 12, 23):
            assert context.height(center + offset, y, floor) == floor
        for offset in (-300, -100, -25, 25, 100, 300):
            assert context.height(center + offset, y, floor) >= floor
