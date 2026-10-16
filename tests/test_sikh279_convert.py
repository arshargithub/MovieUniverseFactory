import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('convert279',Path(__file__).resolve().parents[1]/'scripts/sikh279_convert.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{}, {'operation':'exec','attempt':1},{'operation':'build','attempt':True},{'operation':'build','attempt':0},{'operation':'build','attempt':31},{'operation':'build','attempt':1,'code':'bad'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

@pytest.mark.parametrize('op',['inventory','build','motion','reopen'])
def test_fixed(op):
    assert m.validate({'operation':op,'attempt':1}).name=='control-01'
