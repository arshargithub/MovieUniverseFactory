import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_drape import torso_weight,checked_delta

def test_torso_interfaces_pinned():
    p=np.array([[0,0,.055],[0,0,.455],[.3,0,.25],[0,.1,.25]])
    assert np.allclose(torso_weight(p,True),[0,0,0,1])
    p[:,2]+=.83
    assert np.allclose(torso_weight(p,False),[0,0,0,1])

def test_delta_bounded_and_pinned():
    p=np.zeros((2,3));q=np.full((2,3),.02)
    assert np.allclose(checked_delta(p,q,[0,1]),[[0,0,0],[.02,.02,.02]])
    with pytest.raises(ValueError):checked_delta(p,q*10,[1,1])
    with pytest.raises(ValueError):checked_delta(p,q*np.nan,[1,1])

def test_bad_points_rejected():
    with pytest.raises(ValueError):torso_weight([[0,np.nan,0]],True)

def test_standalone_worker_import_contract():
    import importlib.util
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/'src/movie_factory/adapters/blender/nihang_look.py'
    spec=importlib.util.spec_from_file_location('standalone_look',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert callable(module.drape_module().settle)
