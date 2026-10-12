import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('fist218',Path(__file__).resolve().parents[2]/'scripts/entrance218_fist.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def test_closed_diagnostic_scope():
    assert mod.validate({'operation':'shape01'})==0
    assert mod.validate({'operation':'shape02'})==1
    for job in ({'operation':'build'},{'operation':'shape01','code':'x'},[]):
        with pytest.raises(ValueError):mod.validate(job)
