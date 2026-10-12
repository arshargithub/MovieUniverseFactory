import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('grip217',Path(__file__).resolve().parents[2]/'scripts/entrance217_grip.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def test_scope_is_closed():
    assert mod.validate({'operation':'control21'})=='opening'
    assert mod.validate({'operation':'opening24'})=='opening'
    assert mod.validate({'operation':'route25'})=='route'
    for job in ({'operation':'other'},{'operation':'control21','code':'x'},[]):
        with pytest.raises(ValueError):mod.validate(job)
