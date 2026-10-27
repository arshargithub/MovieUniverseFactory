import importlib.util
from pathlib import Path
import numpy as np
import pytest
s=importlib.util.spec_from_file_location('owner387',Path(__file__).resolve().parents[1]/'scripts/anatomy386_owner387.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_zero_and_constant_field_are_fixed_points():
    p=np.ones((4,3));e=np.array([[0,1],[1,2],[2,3],[3,0]])
    assert np.array_equal(m.fair(p,e,np.ones(4)),p)
    p=np.arange(12).reshape(4,3).astype(float)
    assert np.array_equal(m.fair(p,e,np.zeros(4)),p)
    mask=np.array([0,1,1,0]);result=m.fair(p,e,mask,steps=3)
    assert np.array_equal(result[[0,3]],p[[0,3]]) and np.isfinite(result).all()
    with pytest.raises(ValueError):m.fair(p,e,np.array([0,2,0,0]))
