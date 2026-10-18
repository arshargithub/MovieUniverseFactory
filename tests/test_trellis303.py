import ast
import importlib
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def worker(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    return importlib.import_module('trellis303_worker')


@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    for n in ('trellis303_cloud','trellis301_cascade','trellis301_cloud','trellis298_cloud','trellis295_cloud','trellis294_cloud','trellis293_cloud'):
        sys.modules.pop(n,None)
    m=importlib.import_module('trellis303_cloud'); m.configure(); return m


def metadata():
    return json.loads((ROOT/'.runtime/trellis301/cascade/retrieved/evidence/predecode/latents.json').read_text())


def test_metadata_binding(worker):
    worker.validate_metadata(metadata())


@pytest.mark.parametrize('key,value',[('denormalized_for_decoder',False),('resolution',512),('seed',303),('latents_sha256','wrong'),('pipeline_config_sha256','wrong')])
def test_bad_binding(worker,key,value):
    m=metadata(); m[key]=value
    with pytest.raises(ValueError): worker.validate_metadata(m)


def test_sparse_shape_rejection(worker):
    m=metadata();m['shape']['shape']=[2,32]
    with pytest.raises(ValueError):worker.validate_metadata(m)


def test_upload_allowlist(worker):
    with pytest.raises(ValueError):worker.upload(Path('/tmp/credential'))


def test_process_isolation(worker,monkeypatch):
    calls=[];monkeypatch.setattr(worker,'run',lambda command:calls.append(command))
    worker.infer()
    assert [x[-1] for x in calls]==['--decode','--export']
    assert all(x[0]==sys.executable for x in calls)


def test_raw_save_precedes_repair():
    tree=ast.parse((ROOT/'scripts/trellis303_worker.py').read_text())
    funcs={n.name:ast.get_source_segment((ROOT/'scripts/trellis303_worker.py').read_text(),n) for n in tree.body if isinstance(n,ast.FunctionDef)}
    assert 'fill_holes' not in funcs['decode']
    assert funcs['decode'].index("save_tensors('raw-shape")<funcs['decode'].index('decode_tex_slat')
    assert "save_tensors('source.safetensors'" in funcs['decode']
    assert 'with torch.no_grad()' in funcs['decode']
    assert 'pipeline.run(' not in funcs['decode']
    assert funcs['export'].index('fill_holes')<funcs['export'].index('to_glb')


def test_budget_ceiling(controller,monkeypatch):
    class Ledger:
        def summary(self): return {'committed_usd':3.5}
    monkeypatch.setattr(controller,'ledger',Ledger)
    assert controller.aggregate()['admission_total_usd']==18.5
    with pytest.raises(RuntimeError):controller.aggregate(.01)


def test_guard_admission(controller):
    with pytest.raises(RuntimeError):controller.guards(False)
    with pytest.raises(RuntimeError):controller.launch(False)


def test_bootstrap(controller,monkeypatch):
    monkeypatch.setattr(controller.c,'state',lambda:{'payload_sha256':'a'*64})
    text=controller.userdata()
    assert 'encoder.tar' not in text and 'input/head.png' not in text
    assert 'mf-trellis303-recovery-281482331395' in text
    assert 'timeout 3000' in text and 'shutdown -h +55' in text
    assert '.env' not in text and 'HF_TOKEN' not in text
