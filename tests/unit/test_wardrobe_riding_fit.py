import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('wardrobe_riding_fit', Path(__file__).resolve().parents[2] / 'src/movie_factory/adapters/blender/wardrobe_riding_fit.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec'}, {'operation': 'inspect01', 'path': '/tmp'}, {'operation': 'inspect01', 'code': 'x'}])
def test_fixed_operations_only(job):
    with pytest.raises(ValueError):
        module.validate(job)


def test_pins_and_no_overwrite(monkeypatch, tmp_path):
    body, horse = tmp_path / 'body.blend', tmp_path / 'horse.blend'
    body.touch(); horse.touch()
    monkeypatch.setattr(module, 'BODY', body)
    monkeypatch.setattr(module, 'HORSE', horse)
    monkeypatch.setattr(module, 'BASE', tmp_path)
    monkeypatch.setattr(module, 'digest', lambda p: module.BODY_SHA if p == body else module.HORSE_SHA)
    out = module.validate({'operation': 'inspect01'})
    out.mkdir()
    with pytest.raises(ValueError, match='overwrite'):
        module.validate({'operation': 'inspect01'})
    monkeypatch.setattr(module, 'digest', lambda p: '0' * 64)
    with pytest.raises(ValueError, match='Pinned'):
        module.validate({'operation': 'inspect01'})
