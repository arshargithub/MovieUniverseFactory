import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('matched', Path('src/movie_factory/adapters/blender/matched_face_review.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@pytest.mark.parametrize('angle', [-30, 30])
def test_camera_relative_light_positions(angle):
    camera = m.rotate_z((0, -6, 0), angle)
    for side in (-1, 1):
        light = m.rotate_z((side*3, -4, 3), angle)
        relative = tuple(a-b for a, b in zip(light, camera))
        assert m.rotate_z(relative, -angle) == pytest.approx((side*3, 2, 3))


@pytest.mark.parametrize('job', [None, {}, {'operation': 'repair', 'output_name': 'matched-light-01'}, {'operation': 'matched_lighting', 'output_name': '../elsewhere'}])
def test_reject_unrecognized_job(job):
    with pytest.raises(ValueError):
        m.validate(job)
