"""Reject incomplete or changed evidence before encoding a delivery."""
import importlib.util
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('media214',ROOT/'scripts/entrance214_media.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def setup(monkeypatch,tmp_path,args):
    base=tmp_path/'native';base.mkdir()
    out=tmp_path/'review';out.mkdir()
    monkeypatch.setattr(mod,'BASE',base);monkeypatch.setattr(mod,'OUT',out)
    monkeypatch.setattr(sys,'argv',['media214',*args])
    return base,out


def test_incomplete_sequence_is_not_encoded(monkeypatch,tmp_path):
    _,out=setup(monkeypatch,tmp_path,['--encode'])
    with pytest.raises(ValueError,match='Incomplete chronology'):mod.main()
    assert not (out/'director-preview').exists()


def test_modified_frame_is_not_used(monkeypatch,tmp_path):
    base,out=setup(monkeypatch,tmp_path,[])
    folder=base/'entrance214-motion18';folder.mkdir()
    (folder/'frame-0000.png').write_bytes(b'changed')
    (folder/'progress.json').write_text(json.dumps({'source_sha256':'source','frames':[
        {'index':0,'native_frame':217,'sha256':'original'}]}))
    with pytest.raises(ValueError,match='Bad acknowledged frame'):mod.main()
    assert not (out/'director-preview').exists()
