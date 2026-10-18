import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    for n in ('trellis301_cascade','trellis301_cloud','trellis298_cloud','trellis295_cloud','trellis294_cloud','trellis293_cloud'):
        sys.modules.pop(n,None)
    m=importlib.import_module('trellis301_cascade');m.configure()
    return m


def test_budget_refuses_extension(controller,monkeypatch):
    class Ledger:
        def summary(self):return {'committed_usd':3.5}
    monkeypatch.setattr(controller,'ledger',Ledger)
    assert controller.aggregate()['admission_total_usd']==15
    assert not controller.aggregate()['extra10_activated']
    with pytest.raises(RuntimeError,match='ceiling'):
        controller.aggregate(.01)


def test_mutation_admission(controller):
    with pytest.raises(RuntimeError,match='Root'):
        controller.guards()
    with pytest.raises(RuntimeError,match='Root'):
        controller.launch()


def test_bootstrap_bounds_and_destinations(controller,monkeypatch):
    monkeypatch.setattr(controller.c,'state',lambda:{'payload_sha256':'a'*64,'encoder_sha256':'b'*64})
    text=controller.userdata()
    assert 'shutdown -h +55' in text and 'timeout 3000' in text
    assert 'scripts/trellis301_infer_worker.py' in text
    assert 'mf-trellis301-1024-281482331395' in text
    assert 'mf-trellis293-281482331395' not in text
    assert 'HF_TOKEN' not in text and '.env' not in text
    assert 'b'*64+'  encoder.tar' in text


def test_frozen_drift_before_cloud(controller,monkeypatch):
    monkeypatch.setattr(controller.c,'state',lambda:{'bindings':{'scripts/trellis301_cascade.py':'wrong'}})
    with pytest.raises(RuntimeError,match='changed'):
        controller.frozen()
