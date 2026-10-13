import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('native_check',Path(__file__).resolve().parents[2]/'scripts/protection255_native_check.py')
n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)

@pytest.mark.parametrize('job',[{},None,{'operation':'eval'},{'operation':'inspect-restored-route','code':'x'},{'operation':'../../outside'}])
def test_closed_readonly_operation(job):
    with pytest.raises(ValueError):n.validate(job)

def test_targets_are_restored_not_production():
    for op in n.OPS:
        path=n.validate({'operation':op})
        assert path.is_relative_to(n.RESTORE) and path.name=='scene.blend'
