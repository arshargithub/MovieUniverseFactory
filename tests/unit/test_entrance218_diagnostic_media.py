"""Diagnostic evidence is not allowed to masquerade as a complete movie."""
import importlib.util
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('diagnostic218',ROOT/'scripts/entrance218_diagnostic_media.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def test_missing_diagnostic_is_incomplete(monkeypatch,tmp_path):
    monkeypatch.setattr(mod,'BASE',tmp_path)
    assert mod.collect()==({},False)


def test_changed_contact_image_is_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(mod,'BASE',tmp_path)
    source=tmp_path/'entrance218-opening12';source.mkdir()
    (source/'scene.blend').write_bytes(b'native')
    digest=mod.sha(source/'scene.blend')
    (source/'result.json').write_text(json.dumps({'native_sha256':digest}))
    folder=tmp_path/'entrance214-diagnostic42';folder.mkdir()
    (folder/'frame-0000.png').write_bytes(b'frame')
    (folder/'L-0000.png').write_bytes(b'changed')
    (folder/'R-0000.png').write_bytes(b'right')
    (folder/'progress.json').write_text(json.dumps({'source_sha256':digest,'frames':[
        {'index':0,'native_frame':217,'sha256':mod.sha(folder/'frame-0000.png'),
         'contacts':{'L':'old','R':mod.sha(folder/'R-0000.png')}}]}))
    with pytest.raises(ValueError,match='Changed or unacknowledged'):
        mod.collect()
