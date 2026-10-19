"""Guard the fixed local diagnostic boundary, not its artistic result."""
import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('finish317',Path(__file__).resolve().parents[1]/'scripts/finish317.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def test_fixed_operations_only():
    assert module.validate({'operation':'finish'})=='finish'
    for job in ({'operation':'eval'},{'operation':'finish','code':'x'},{'operation':True}):
        with pytest.raises(ValueError):module.validate(job)
