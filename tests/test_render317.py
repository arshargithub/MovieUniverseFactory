import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('render317',Path(__file__).resolve().parents[1]/'scripts/render317.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def test_bounded_frames():
    j={'operation':'movie','version':3,'start':1,'end':24};assert module.validate(j)==j
    for change in ({'end':25},{'start':False},{'operation':'eval'},{'version':0},{'code':'print(1)'}):
        with pytest.raises(ValueError):module.validate(j|change)
