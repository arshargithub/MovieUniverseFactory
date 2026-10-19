"""Scope guards only; not a visual or audiovisual judge."""
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('runner318',Path(__file__).resolve().parents[1]/'scripts/sikh318.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def test_fixed_worker_boundary():
    job=dict(operation='movie',version=2,start=1,end=6)
    assert runner.validate(job)==job
    for change in ({'operation':'eval'},{'version':False},{'version':5},{'start':False},{'start':0},{'end':7},{'end':697},{'code':'arbitrary()'}):
        with pytest.raises(ValueError):runner.validate(job|change)

def test_no_runtime_code_or_provider_inputs():
    assert set(runner.OPS)=={'inspect','build','look','movie','reopen','check'}
    assert runner.SOURCE.name=='sequence.blend'
    assert 'series01-sikh317' in str(runner.SOURCE)
