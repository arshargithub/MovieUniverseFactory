import importlib.util
from pathlib import Path
import pytest


def module():
    path = Path(__file__).resolve().parents[1] / 'scripts/trellis301_export_inspect.py'
    spec = importlib.util.spec_from_file_location('inspect_export301', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_only_fixed_export_variants_and_operations():
    m = module()
    for variant in m.VARIANTS:
        for operation in ('render', 'reopen'):
            m.validate({'operation': operation, 'variant': variant})
    for bad in ({'operation':'render','variant':'../../other'},
                {'operation':'execute','variant':m.VARIANTS[0]},
                {'operation':'render','variant':m.VARIANTS[0],'code':'unexpected'}):
        with pytest.raises(ValueError):
            m.validate(bad)


def test_review_covers_both_profiles_quarters_front_and_back():
    m = module()
    assert dict(m.VIEWS) == {'front':0,'left-quarter':45,'left-profile':90,
                             'back':180,'right-profile':270,'right-quarter':315}


def test_blender_worker_admits_repository_import_before_helpers():
    path = Path(__file__).resolve().parents[1] / 'scripts/trellis301_export_inspect.py'
    source = path.read_text()
    worker = source.split('def worker(job):',1)[1].split('def main():',1)[0]
    assert worker.index("sys.path.insert(0, str(ROOT / 'src'))") < worker.index('from trellis301_prepare import')


def test_cascade_review_rejects_unstructured_jobs(monkeypatch):
    import importlib
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'scripts'))
    candidate = importlib.import_module('trellis301_cascade_inspect')
    for bad in ({'operation':'execute','variant':'1024-4096'},
                {'operation':'render','variant':'512'},
                {'operation':'render','variant':'1024-4096','code':'extra'}):
        with pytest.raises(ValueError):
            candidate.worker(bad)
