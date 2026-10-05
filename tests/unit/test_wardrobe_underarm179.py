"""Inspection admission stays fixed and does not execute Blender."""
import importlib.util
from pathlib import Path
import pytest

source=Path(__file__).resolve().parents[2]/'scripts/wardrobe_underarm179.py'
spec=importlib.util.spec_from_file_location('underarm179',source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[{},None,{'operation':'arbitrary'},
    {'operation':'inspect01','code':'anything'},{'operation':'inspect01','path':'/tmp'}])
def test_only_fixed_inspection(job):
    with pytest.raises(ValueError):module.validate(job)
