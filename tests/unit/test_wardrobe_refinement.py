import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('wardrobe_refinement', Path(__file__).resolve().parents[2] / 'src/movie_factory/adapters/blender/wardrobe_refinement.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec'}, {'operation': 'inspect01', 'path': '/tmp'}, {'operation': 'preview01', 'code': 'x'}, {'operation': 'preview99'}])
def test_fixed_operations_only(job):
    with pytest.raises(ValueError):
        module.validate(job)


def test_pins_and_output_immutability(monkeypatch, tmp_path):
    expected = {}
    for name in ('SOURCE', 'BODY', 'HORSE'):
        path = tmp_path / (name + '.blend'); path.touch()
        monkeypatch.setattr(module, name, path)
        expected[path] = getattr(module, name + '_SHA')
    monkeypatch.setattr(module, 'BASE', tmp_path)
    monkeypatch.setattr(module, 'digest', lambda path: expected[path])
    out = module.validate({'operation': 'inspect01'}); out.mkdir()
    with pytest.raises(ValueError, match='overwrite'):
        module.validate({'operation': 'inspect01'})
    monkeypatch.setattr(module, 'digest', lambda path: '0'*64)
    with pytest.raises(ValueError, match='Pinned'):
        module.validate({'operation': 'preview01'})
