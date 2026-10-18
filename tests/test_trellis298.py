import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    for name in ('trellis298_cloud', 'trellis295_cloud', 'trellis294_cloud', 'trellis293_cloud'):
        sys.modules.pop(name, None)
    m = importlib.import_module('trellis298_cloud')
    m.configure()
    return m


def test_private_payload_bootstrap(controller, monkeypatch):
    m = controller
    monkeypatch.setattr(m.c, 'state', lambda: {'payload_sha256': 'a'*64, 'encoder_sha256': 'b'*64})
    text = m.userdata()
    assert 'scripts/trellis298_worker.py' in text
    assert 'shutdown -h +115' in text and 'timeout 6500' in text
    assert 'HF_TOKEN' not in text and '.env' not in text
    assert 'b'*64 in text and 'sha256sum --check' in text
    assert m.c.BUCKET == 'mf-trellis298-281482331395'


def test_launch_requires_encoder(controller, monkeypatch):
    monkeypatch.setattr(controller, 'no_active', lambda: None)
    monkeypatch.setattr(controller.c, 'state', lambda: {})
    with pytest.raises(AssertionError):
        controller.launch()


def test_no_overlapping_worker(controller, monkeypatch):
    monkeypatch.setattr(controller.prior, 'no_prior_active', lambda: None)
    monkeypatch.setattr(controller.t, 'aws', lambda *a, **k: {'Reservations': [{'Instances': [{}]}]})
    with pytest.raises(AssertionError):
        controller.no_active()


def test_inference_safety_contract():
    source = (ROOT / 'scripts/trellis298_worker.py').read_text()
    assert 'token=False' in source
    assert 'low_vram' in source
    assert 'RestrictedImports()' in source
    assert 'production_ready\': False' in source
    assert 'torch.load(' not in source and 'trust_remote_code=True' not in source


def test_inference_import_preflight_precedes_compilation():
    source = (ROOT / 'scripts/trellis298_worker.py').read_text()
    assert 'regex==2025.9.18' in source
    assert source.index('INFERENCE_IMPORT_PREFLIGHT_PASS') < source.index('for directory in')


def test_attempt_b_has_distinct_resources(controller):
    controller.configure('b')
    assert controller.c.BUCKET == 'mf-trellis298b-281482331395'
    assert controller.c.LOCAL.name == 'trellis298b'
    assert controller.OUT == ROOT / 'results/trellis298/cloud-b'


def test_attempt_c_preserves_earlier_ledger(controller):
    controller.configure('c')
    assert controller.c.BUCKET == 'mf-trellis298c-281482331395'
    assert controller.c.ledger is controller.continuation_ledger
    assert controller.OUT == ROOT / 'results/trellis298/cloud-c'


def test_full_preflight_before_weight_downloads():
    source = (ROOT / 'scripts/trellis298_worker.py').read_text()
    assert source.index("'--preflight'") < source.index("'--infer'")
    assert 'for name in models.__all__' in source
    assert 'SparseConv3d(16, 16, 3)' in source
    assert 'memory_efficient_attention(q, q, q)' in source


def test_optional_io_exclusion_is_pinned():
    source = (ROOT / 'scripts/trellis298_cloud.py').read_text()
    assert 'ca30e1545d11f3e862b7d11b31af6200427c91482f11d8b543982d692cd8588b' in source
    assert "patches['inference/o-voxel/o_voxel/__init__.py']" in source


def test_inspection_operation_allowlist(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    m = importlib.import_module('trellis298_inspect')
    m.validate({'operation': 'inspect', 'candidate': 'head512'})
    for job in ({'operation': 'exec', 'candidate': 'head512'},
                {'operation': 'inspect', 'candidate': '../../elsewhere'},
                {'operation': 'inspect', 'candidate': 'head512', 'code': 'anything'}):
        with pytest.raises(ValueError):
            m.validate(job)


def test_representation_controls_are_fixed_and_offline(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    m = importlib.import_module('trellis298_repair')
    for op in ('smooth', 'remesh'):
        m.validate({'operation': op})
    for job in (None, {}, {'operation': 'exec'},
                {'operation': 'smooth', 'code': 'anything'}):
        with pytest.raises(ValueError):
            m.validate(job)
    source = (ROOT / 'scripts/trellis298_repair.py').read_text()
    assert 'use_scripts=False' in source
    assert "'--offline-mode'" in source
    assert "'production_ready':False" in source
    assert 'mod.voxel_size = .003' in source


def test_dense_control_deduplicates_without_changing_winding(monkeypatch):
    import numpy as np
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    m = importlib.import_module('trellis298_dense_control')
    vertices = np.array([[0,0,0], [.1,0,0], [0,.1,0], [.00001,0,0]], dtype=np.float32)
    faces = np.array([[0,1,2], [3,1,2], [0,3,1]], dtype=np.int32)
    points, out = m.cluster(vertices, faces)
    assert len(points) == 3 and len(out) == 1
    tri = points[out[0]]
    assert np.cross(tri[1]-tri[0],tri[2]-tri[0])[2] > 0
    with pytest.raises(AssertionError):
        m.cluster(vertices, faces, 999)


def test_export_only_has_no_generation_or_encoder_staging(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    module = importlib.import_module('trellis298_export')
    module.configure()
    assert module.c.BUCKET == 'mf-trellis298d-281482331395'
    assert module.c.ledger is module.previous.continuation_ledger
    source = (ROOT / 'scripts/trellis298_export_worker.py').read_text()
    assert 'remesh=True, remesh_band=1, remesh_project=0' in source
    assert 'open-sheet.safetensors' in source and 'remeshed-source.safetensors' in source
    assert 'pipeline.run(' not in source and 'hf_hub_download' not in source
    controller_source = (ROOT / 'scripts/trellis298_export.py').read_text()
    assert "'encoder_upload':False" in controller_source
    assert 'previous.continuation_aggregate(4)' in controller_source
    assert 'assert len(f) > 8' in source
    assert 'counts == 2' in source and 'orientation == 0' in source
    assert 'expected_thickness' in source
    assert "'total_gpu_peak_bytes':None" in source
    assert "c.state()['staged_payload_sha256'] == c.state()['payload_sha256']" in controller_source


def test_export_freeze_rejects_controller_drift(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    m = importlib.import_module('trellis298_export')
    m.configure()
    monkeypatch.setattr(m.c, 'state', lambda: {'controller_sha256':'wrong'})
    with pytest.raises(AssertionError):
        m.verify_frozen()
