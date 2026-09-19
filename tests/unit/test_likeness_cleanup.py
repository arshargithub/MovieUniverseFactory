import importlib.util
from pathlib import Path
import pytest
import hashlib


@pytest.fixture
def handler():
    path = Path('src/movie_factory/adapters/blender/likeness_cleanup.py')
    spec = importlib.util.spec_from_file_location('likeness_cleanup', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('job', [None, {}, {'operation': 'python', 'output_name': 'cleanup-test'},
    {'operation': 'inspect', 'output_name': '../escape'},
    {'operation': 'inspect', 'output_name': 'cleanup-/escape'},
    {'operation': 'inspect', 'output_name': 'cleanup-test', 'code': 'print(1)'}])
def test_reject_invalid(handler, job):
    with pytest.raises(ValueError):
        handler.validate(job)


def test_accept_pinned_source(handler, monkeypatch, tmp_path):
    source = tmp_path / 'base.blend'
    source.write_bytes(b'test')
    monkeypatch.setattr(handler, 'SOURCE', source)
    monkeypatch.setattr(handler, 'BASE', tmp_path)
    monkeypatch.setattr(handler, 'DIGEST', hashlib.sha256(b'test').hexdigest())
    assert handler.validate({'operation': 'inspect', 'output_name': 'cleanup-unit-unused'}).name == 'cleanup-unit-unused'
    assert handler.validate({'operation': 'jaw_diagnostic', 'output_name': 'cleanup-jaw-unit'}).name == 'cleanup-jaw-unit'
    assert handler.validate({'operation': 'portable_cleanup', 'output_name': 'cleanup-portable-unit'}).name == 'cleanup-portable-unit'
    (tmp_path / 'cleanup-unit-unused').mkdir()
    with pytest.raises(ValueError, match='overwrite'):
        handler.validate({'operation': 'inspect', 'output_name': 'cleanup-unit-unused'})


def test_digest_reject(handler, monkeypatch, tmp_path):
    source = tmp_path / 'base.blend'
    source.write_bytes(b'test')
    monkeypatch.setattr(handler, 'SOURCE', source)
    monkeypatch.setattr(handler, 'DIGEST', '0' * 64)
    with pytest.raises(ValueError, match='source changed'):
        handler.validate({'operation': 'inspect', 'output_name': 'cleanup-unit-unused'})


@pytest.mark.parametrize('height,expected', [(0,1),(.21,1),(.255,.5),(.30,0),(.8,0)])
def test_face_protected(handler, height, expected):
    assert handler.neck_weight(height) == pytest.approx(expected)


def test_color_conversion(handler):
    assert handler.linear_channel(0) == 0
    assert handler.linear_channel(1) == 1
    assert handler.linear_channel(.5) == pytest.approx(.21404114)


def test_jaw_mask_is_local(handler):
    assert handler.jaw_mask(0, .4) == 0
    assert handler.jaw_mask(.7, .6) == 0
    assert handler.jaw_mask(.7, .2) == 0
    assert handler.jaw_mask(.7, .4) == pytest.approx(.85)
    assert handler.jaw_mask(-.7, .4) == handler.jaw_mask(.7, .4)


@pytest.mark.parametrize('rgb', [(0,0,0),(.1,.07,.03),(.1,.2,.5),(float('nan'),.2,.1)])
def test_projection_rejects_dark_or_blue(handler, rgb):
    assert handler.skin_projection_confidence(rgb) == 0


def test_projection_keeps_warm_lit_patch(handler):
    assert handler.skin_projection_confidence((.6,.4,.25)) == 1


def test_gap_fill_is_confined(handler):
    assert handler.gap_region(-.7,0,.4) == 0
    assert handler.gap_region(.7,0,.7) == 0
    assert handler.gap_region(.7,1,.4) == 0
    assert handler.gap_region(.7,0,.4) == 1
    assert handler.gap_region(.7,0,.53) == 1
    assert handler.gap_region(.7,0,.62) == 0


def test_ear_transfer_protects_face_and_opposite_side(handler):
    for point in [(-.9,0,.5), (0,-1,.5), (.9,0,.7), (.9,0,.2), (.9,-1.2,.5)]:
        assert handler.ear_region(*point) == 0
    assert handler.ear_region(.9,0,.5) == 1
