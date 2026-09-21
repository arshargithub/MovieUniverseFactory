import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('surface',Path('src/movie_factory/adapters/blender/face_surface_integration.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1},{'operation':'inspect','candidate':True}, {'operation':'inspect','candidate':2},{'operation':'inspect','candidate':1,'path':'anything'}])
def test_guards(job):
    with pytest.raises(ValueError):m.validate(job)

def test_pinned(tmp_path,monkeypatch):
    p=tmp_path/'source';p.write_bytes(b'ok');monkeypatch.setattr(m,'SOURCE',p)
    monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p));monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'inspect','candidate':1};m.validate(job).mkdir()
    with pytest.raises(ValueError):m.validate(job)
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Source'):m.validate(job)

def test_sphere_fit():
    import numpy as np
    t=np.linspace(0,6.2,40);p=np.array([[.3+.14*np.cos(a)*np.cos(b),-.79+.14*np.sin(a)*np.cos(b),.32+.14*np.sin(b)] for a,b in zip(t,np.sin(t))])
    center,radius,error=m.sphere_fit(p)
    assert np.allclose(center,[.3,-.79,.32]) and abs(radius-.14)<1e-6 and error<1e-6
    with pytest.raises(ValueError):m.sphere_fit(p[:5])
    with pytest.raises(ValueError):m.sphere_fit(p*5)

def test_acting_boundaries_and_controls():
    import math
    for t in (0,9.5,10):
        values,gaze=m.performance(t)
        assert all(v==0 for v in values.values()) and gaze==0
    assert m.performance(1.44)[0]['eyeBlinkLeft']==1
    for frame in range(240):
        values,gaze=m.performance(frame/24)
        assert all(0<=v<=1 for v in values.values()) and 0<=gaze<=math.radians(5)
