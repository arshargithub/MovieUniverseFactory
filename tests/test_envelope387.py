import importlib.util
from pathlib import Path
import numpy as np
s=importlib.util.spec_from_file_location('envelope387',Path(__file__).resolve().parents[1]/'scripts/anatomy386_envelope387.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_volume_fields_and_smooth_union_have_declared_signs():
    p=np.array([[0.,0,0],[1,0,0],[2,0,0]])
    assert np.allclose(m.ellipsoid(p,np.zeros(3),np.ones(3)),[-1,0,1])
    assert np.allclose(m.capsule(p,[0,0,0],[1,0,0],.1,.1),[-.1,-.1,.9])
    a=np.array([-.2,.2,1]);b=np.array([.3,.25,2])
    assert np.all(m.union(a,b)<=np.minimum(a,b)+1e-12)
    assert np.allclose(m.union(a,b),m.union(b,a))
