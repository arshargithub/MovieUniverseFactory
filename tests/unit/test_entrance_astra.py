import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[2]
spec=importlib.util.spec_from_file_location('entrance_astra',ROOT/'scripts/entrance_astra.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[None,{}, {'operation':'execute'}, {'operation':'proof01','code':'no'}, {'operation':'audit01','path':'/tmp/no'}])
def test_fixed_operation_rejects_payloads(job):
    with pytest.raises(ValueError):module.validate(job)

def test_existing_evidence_preserved(tmp_path,monkeypatch):
    source=tmp_path/'source.blend';source.write_bytes(b'fixture')
    monkeypatch.setattr(module.prior,'SOURCE',source)
    monkeypatch.setattr(module.prior,'SOURCE_SHA',module.prior.actor.base.digest(source))
    monkeypatch.setattr(module,'BASE',tmp_path)
    (tmp_path/'entrance-astra-audit01').mkdir()
    with pytest.raises(ValueError,match='Preserve evidence'):
        module.validate({'operation':'audit01'})
