import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe186',Path(__file__).parents[2]/'scripts/wardrobe186.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[{},None,{'operation':'bad'},{'operation':'inspect01','code':'bad'}])
def test_reject_unstructured(job):
    with pytest.raises(ValueError): module.validate(job)

def test_validate_bound_new_output(tmp_path,monkeypatch):
    source=tmp_path/'source.blend';source.write_bytes(b'fixture')
    monkeypatch.setattr(module,'SOURCE',source)
    monkeypatch.setattr(module,'SOURCE_SHA',module.base.digest(source))
    monkeypatch.setattr(module.base,'BASE',tmp_path)
    output=module.validate({'operation':'inspect01'})
    output.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':'inspect01'})

def test_shoulder_support_bounds_and_locality():
    assert module.arm_support(0)==0
    assert module.arm_support(1)==1
    values=[module.arm_support(i/100) for i in range(101)]
    assert values==sorted(values)
    assert module.arm_support(.65)==1
    assert module.arm_support(.3)>.3
