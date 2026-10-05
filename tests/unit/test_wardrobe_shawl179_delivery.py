import importlib.util
from pathlib import Path
import pytest
source=Path(__file__).resolve().parents[2]/'scripts/wardrobe_shawl179_delivery.py'
spec=importlib.util.spec_from_file_location('delivery179',source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'unknown'},
    {'operation':'screen02','path':'/tmp'}, {'operation':'screen02','code':'pass'}])
def test_fixed_delivery_only(job):
    with pytest.raises(ValueError):module.validate(job)

def test_unbound_cache_never_dispatches(monkeypatch):
    monkeypatch.setattr(module,'CACHE_SHA',None)
    with pytest.raises(ValueError,match='Unbound'):module.validate({'operation':'screen02'})
