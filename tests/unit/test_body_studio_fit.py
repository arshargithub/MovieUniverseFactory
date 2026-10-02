import importlib.util
from pathlib import Path
import pytest

FILE = Path(__file__).resolve().parents[2] / 'src/movie_factory/adapters/blender/body_studio_fit.py'
spec = importlib.util.spec_from_file_location('body_studio_fit', FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('job', [{}, {'operation':'inspect01','path':'/tmp/other'}, {'operation':'exec'}, None])
def test_reject_nonfixed_jobs(job):
    with pytest.raises(ValueError):
        module.validate(job)


def test_reject_changed_source(monkeypatch):
    monkeypatch.setattr(module, 'digest', lambda p: '0'*64)
    with pytest.raises(ValueError, match='Pinned'):
        module.validate({'operation':'inspect01'})


def test_chest_blend_is_continuous_and_bounded():
    assert module.chest_blend(-4)==0
    assert module.chest_blend(-1)==1
    values=[module.chest_blend(-3.1+i*.01) for i in range(131)]
    assert all(0<=v<=1 for v in values)
    assert values==sorted(values)
    assert max(b-a for a,b in zip(values,values[1:]))<.014


def test_fixed_fit_job_and_no_overwrite(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    out=module.validate({'operation':'fit04'})
    out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):
        module.validate({'operation':'fit04'})
