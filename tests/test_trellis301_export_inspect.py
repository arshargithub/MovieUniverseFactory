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
