import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('sikh281_eye',Path(__file__).parents[1]/'scripts/sikh281_eye.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('op',['build','reopen','motion','verify'])
def test_operations(op):assert m.validate({'operation':op,'attempt':1}).name=='control-01'

@pytest.mark.parametrize('j',[{},None,{'operation':'exec','attempt':1},{'operation':'build','attempt':0},{'operation':'build','attempt':True},{'operation':'build','attempt':1,'path':'/tmp/other'}])
def test_invalid(j):
    with pytest.raises(ValueError):m.validate(j)

def test_source():assert m.sha(m.SOURCE)==m.SOURCE_SHA
