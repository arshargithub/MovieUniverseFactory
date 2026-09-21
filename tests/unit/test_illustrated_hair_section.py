import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('hair_section', Path('src/movie_factory/adapters/blender/illustrated_hair_section.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec', 'candidate': 1},
    {'operation': 'preview', 'candidate': True}, {'operation': 'preview', 'candidate': 5},
    {'operation': 'preview', 'candidate': 1, 'code': 'arbitrary'}])
def test_rejects_invalid(job):
    with pytest.raises(ValueError):
        m.validate(job)


def test_pin_and_nonoverwrite(tmp_path, monkeypatch):
    p = tmp_path / 'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m, 'SOURCE', p); monkeypatch.setattr(m, 'SOURCE_SHA', m.digest(p))
    monkeypatch.setattr(m, 'BASE', tmp_path); monkeypatch.setattr(m, 'REFERENCES', {})
    out = m.validate({'operation': 'preview', 'candidate': 1}); out.mkdir()
    with pytest.raises(ValueError, match='exists'):
        m.validate({'operation': 'preview', 'candidate': 1})
    with pytest.raises(ValueError, match='Preview required'):
        m.validate({'operation': 'seal', 'candidate': 1})
    p.write_bytes(b'changed')
    with pytest.raises(ValueError, match='Pinned'):
        m.validate({'operation': 'preview', 'candidate': 2})


def test_local_relief_bounded():
    for x in (-1, -.5, 0, .5, 1):
        assert m.relief(x, .5, .8, 1) == 0
        assert m.relief(x, -.5, .1, 1) == 0
        for z in (.2, .5, .8, 1., 1.3, 1.6):
            assert 0 <= m.relief(x, -.5, z, 1) < .17


def test_wrapping_bounded_continuous():
    assert m.wrapped_x(.5) == .5
    assert m.wrapped_x(.9) == .9
    for x in (.91, 1., 1.2, 3.):
        assert .9 < m.wrapped_x(x) <= 1.05
        assert m.wrapped_x(-x) == -m.wrapped_x(x)
    assert abs(m.wrapped_x(.9000001) - .9) < .000001


def test_input_symlink_refused(tmp_path, monkeypatch):
    p = tmp_path / 'real'; p.write_bytes(b'fixed')
    link = tmp_path / 'link'; link.symlink_to(p)
    monkeypatch.setattr(m, 'SOURCE', link); monkeypatch.setattr(m, 'SOURCE_SHA', m.digest(p))
    with pytest.raises(ValueError, match='Pinned'):
        m.validate({'operation': 'preview', 'candidate': 1})


def test_reference_pin(tmp_path, monkeypatch):
    p = tmp_path / 'source'; p.write_bytes(b'fixed')
    ref = tmp_path / 'portrait.png'; ref.write_bytes(b'approved')
    monkeypatch.setattr(m, 'SOURCE', p); monkeypatch.setattr(m, 'SOURCE_SHA', m.digest(p))
    monkeypatch.setattr(m, 'BASE', tmp_path); monkeypatch.setattr(m, 'REFBASE', tmp_path)
    monkeypatch.setattr(m, 'REFERENCES', {'portrait.png': m.digest(ref)})
    m.validate({'operation': 'preview', 'candidate': 4})
    ref.write_bytes(b'changed')
    with pytest.raises(ValueError, match='Pinned'):
        m.validate({'operation': 'preview', 'candidate': 4})
