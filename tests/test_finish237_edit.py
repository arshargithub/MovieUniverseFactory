import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def test_exact_quote_and_attribution():
    e=load('finish237_edit')
    assert 'Sir Winston Churchill' in e.PAGE and 'Sir Winston Churchill' in e.SRT
    assert 'a hardy and\\Nmartial people' in e.PAGE
    assert '0:00:08.18' in e.PAGE
    assert 'I trust' not in e.SRT

def test_audio_pan_and_boundaries():
    a=load('finish237_audio');target=np.zeros((a.RATE,2));sample=np.ones(100)
    a.put(target,sample,.999,pan=-1)
    assert np.max(target[:,0])==1 and np.max(target[:,1])==0
    with pytest.raises(ValueError):a.put(target,sample,-1)

def test_assembly_refuses_incomplete_sources(tmp_path,monkeypatch):
    e=load('finish237_edit');monkeypatch.setattr(e,'BASE',tmp_path)
    with pytest.raises(FileNotFoundError):e.inspect_sources()
