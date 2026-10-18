import ast
import importlib
import json
from pathlib import Path
import struct
import sys

import pytest

from movie_factory.trellis301_quality import split_exporter, glb_opacity_variant, array_digest
from movie_factory.trellis_adapter.patch import adapted_sources

ROOT = Path(__file__).resolve().parents[1]


def test_bake_split_preserves_exact_admitted_arithmetic():
    original = adapted_sources(ROOT / 'results/sikh288/upstream')['o-voxel/o_voxel/postprocess.py']
    result = split_exporter(original)
    compile(result, 'split-exporter', 'exec')
    before, after = original.split('    # --- Texture Baking (Attribute Sampling) ---')
    assert result.startswith(before.replace('def to_glb(', 'def prepare_surface(', 1))
    assert result.endswith(after)
    names = [n.name for n in ast.parse(result).body if isinstance(n, ast.FunctionDef)]
    assert names == ['prepare_surface', 'bake_surface']
    assert 'nvdiffrast' not in result


def test_bake_split_rejects_drift():
    with pytest.raises(ValueError):
        split_exporter('def to_glb(): pass')


def test_opacity_changes_only_json_mode():
    doc = {'asset': {'version': '2.0'}, 'materials': [{'alphaMode': 'OPAQUE',
        'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}}}], 'meshes': [{'unchanged': 1}]}
    blob = json.dumps(doc).encode()
    blob += b' ' * (-len(blob) % 4)
    binary = b'01234567'
    body = struct.pack('<I4s', len(blob), b'JSON') + blob + struct.pack('<I4s', len(binary), b'BIN\0') + binary
    raw = struct.pack('<4sII', b'glTF', 2, len(body) + 12) + body
    changed = glb_opacity_variant(raw)
    size = struct.unpack_from('<I', changed, 12)[0]
    changed_doc = json.loads(changed[20:20 + size])
    changed_doc['materials'][0]['alphaMode'] = 'OPAQUE'
    assert changed_doc == doc
    assert changed[20 + size:] == struct.pack('<I4s', len(binary), b'BIN\0') + binary
    assert len(changed) == struct.unpack_from('<I', changed, 8)[0]


def test_array_digest_detects_uv_changes():
    import numpy as np
    x = np.zeros((3, 2), dtype=np.float32)
    a = array_digest({'uv': x})
    x[1, 1] = 1
    assert array_digest({'uv': x}) != a
    assert array_digest({'position': x}) != array_digest({'uv': x})


def test_no_inference_in_export_worker():
    source = (ROOT / 'scripts/trellis301_export_worker.py').read_text()
    assert 'pipeline.run' not in source and 'hf_hub_download' not in source
    assert "remesh=True, remesh_band=1, remesh_project=0" in source
    assert "cumesh.remeshing.remesh_narrow_band_dc = preserved_shell" in source
    assert "geometry_uv_sha256'] == variants[2]['geometry_uv_sha256']" in source
    assert 'preserved_shell' in source and 'new_remesh=False' in source
    assert "HF_HUB_OFFLINE='1'" in source


@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    for name in ('trellis301_cloud', 'trellis298_cloud', 'trellis295_cloud', 'trellis294_cloud', 'trellis293_cloud'):
        sys.modules.pop(name, None)
    mod = importlib.import_module('trellis301_cloud')
    mod.configure()
    return mod


def test_mutations_require_root_review(controller):
    with pytest.raises(RuntimeError, match='Root'):
        controller.guards()
    with pytest.raises(RuntimeError, match='Root'):
        controller.launch()


def test_301_resources_and_offline_bootstrap(controller, monkeypatch):
    monkeypatch.setattr(controller.c, 'state', lambda: {'payload_sha256': 'a' * 64})
    bootstrap = controller.c.userdata()
    assert 'scripts/trellis301_export_worker.py' in bootstrap
    assert 'shutdown -h +115' in bootstrap and 'timeout 6500' in bootstrap
    assert 'HF_TOKEN' not in bootstrap and '.env' not in bootstrap
    assert controller.c.JOB == 'trellis301-export'
    assert controller.c.LOCAL == ROOT / '.runtime/trellis301/export'


def test_budget_preserves_aggregate_ceiling(controller, monkeypatch):
    class FakeLedger:
        def summary(self):
            return {'committed_usd': 4}
    monkeypatch.setattr(controller, 'ledger', FakeLedger)
    assert controller.aggregate()['admission_total_usd'] == 14
    with pytest.raises(RuntimeError, match='ceiling'):
        controller.aggregate(2)


def test_opacity_structured_job(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    mod = importlib.import_module('trellis301_inspect')
    mod.validate({'operation': 'opacity-control'})
    with pytest.raises(ValueError):
        mod.validate({'operation': 'opacity-control', 'code': 'untrusted'})


def test_frozen_payload_fails_before_cloud(controller, monkeypatch):
    monkeypatch.setattr(controller.c, 'state', lambda: {'controller_sha256': 'wrong'})
    with pytest.raises(RuntimeError, match='Controller'):
        controller.verify_frozen()


def test_closed_inventory_checks_every_resource_class(controller, monkeypatch, tmp_path):
    calls = []
    replies = {'describe-instances': {'Reservations': []}, 'describe-volumes': {'Volumes': []},
        'list-buckets': {'Buckets': []}, 'list-roles': {'Roles': []},
        'list-instance-profiles': {'InstanceProfiles': []}, 'list-functions': {'Functions': []},
        'describe-security-groups': {'SecurityGroups': []}, 'list-rules': {'Rules': []}}
    def fake_aws(service, operation, *args):
        calls.append(operation)
        return replies[operation]
    monkeypatch.setattr(controller.t, 'aws', fake_aws)
    monkeypatch.setattr(controller, 'OUT', tmp_path)
    assert not any(controller.closed_resource_inventory()['remaining'].values())
    assert set(calls) == set(replies)
    replies['list-buckets'] = {'Buckets': [{'Name': 'mf-trellis298c-281482331395'}]}
    with pytest.raises(RuntimeError, match='resources remain'):
        controller.closed_resource_inventory()
    receipt = json.loads((tmp_path / 'closed-resource-preflight.json').read_text())
    assert receipt['remaining']['buckets'] == ['mf-trellis298c-281482331395']


def test_latent_checkpoint_precedes_decode_failure(monkeypatch, tmp_path):
    from fractions import Fraction
    from types import SimpleNamespace
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    worker = importlib.import_module('trellis301_infer_worker')
    monkeypatch.setattr(worker, 'OUT', tmp_path)
    order = []
    class Tensor:
        dtype = 'float16'
        def detach(self): return self
        def cpu(self): return self
        def contiguous(self): return self
        def clone(self): return self
    latent = SimpleNamespace(feats=Tensor(), coords=Tensor(), shape=(1, 32),
        _scale=(Fraction(1), Fraction(1), Fraction(1)))
    def decode(shape, texture, resolution):
        order.append('decode')
        assert shape is latent and texture is latent and resolution == 1024
        raise RuntimeError('simulated decode OOM')
    pipeline = SimpleNamespace(decode_latent=decode)
    def save(tensors, path):
        assert set(tensors) == {'shape_feats', 'shape_coords', 'texture_feats', 'texture_coords'}
        Path(path).write_bytes(b'synthetic checkpoint')
        order.append('save')
    def upload(path, key):
        assert path.exists() and key.startswith('output/predecode/')
        order.append('upload')
    calls = worker.install_decode_checkpoint(pipeline, save, upload)
    with pytest.raises(RuntimeError, match='decode OOM'):
        pipeline.decode_latent(latent, latent, 1024)
    assert order == ['save', 'upload', 'upload', 'decode'] and calls == [1024]
    metadata = json.loads((tmp_path / 'predecode/latents.json').read_text())
    assert metadata['denormalized_for_decoder'] and metadata['decode_rescue_validation'] == 'NOT_RUN'
    with pytest.raises(RuntimeError, match='count/resolution'):
        pipeline.decode_latent(latent, latent, 1024)


def test_contingent_inference_retains_comparison_controls():
    source = (ROOT / 'scripts/trellis301_infer_worker.py').read_text()
    compile(source, 'contingent-worker', 'exec')
    assert "seed=298" in source and "pipeline_type='1024_cascade'" in source
    assert "return_latent=False" in source and 'pipeline.run' in source
    assert "sampler_overrides': {}" in source
    assert 'remesh=True, remesh_band=1, remesh_project=0' in source
    assert 'original.__file__ = str(Path(__file__).resolve())' in source
    assert "token=False" in source and 'HF_TOKEN' not in source
