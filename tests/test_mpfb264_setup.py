"""Offline admission checks; no Blender/extension execution."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('mpfb264_setup', Path(__file__).parents[1] / 'scripts/mpfb264_setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec', 'attempt': 1},
    {'operation': 'prove', 'attempt': True}, {'operation': 'prove', 'attempt': 0},
    {'operation': 'prove', 'attempt': 11}, {'operation': 'prove', 'attempt': 1, 'path': '/tmp/x'},
    {'operation': '../escape', 'attempt': 1}])
def test_reject_unbounded_jobs(job):
    with pytest.raises(ValueError):
        setup.validate(job)


@pytest.mark.parametrize('operation', ['configure', 'prove', 'reopen'])
def test_scoped_outputs(operation):
    result = setup.validate({'operation': operation, 'attempt': 1})
    assert result.name == 'proof-01'
    assert result.parent.name == 'series01-sikh264'


def test_installed_and_donor_integrity():
    assert setup.verify_sources() > 2000
