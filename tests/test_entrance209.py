import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from entrance209_sword import validate
from entrance209_prop import centerline,sheath_mesh
import numpy as np
from entrance209_review import validate as review_validate

def test_closed_operation():
    validate({'operation':'inspect01'})
    for job in (None,{}, {'operation':'exec'}, {'operation':'inspect01','code':'x'},
                {'operation':'inspect01','source':'/tmp/other.blend'}):
        with pytest.raises(ValueError):
            validate(job)

def test_closed_review():
    review_validate({'operation':'proof05'})
    for j in ({'operation':'eval'}, {'operation':'proof05','source':'x'},None):
        with pytest.raises(ValueError):review_validate(j)

def test_right_rearward_continuous_sheath():
    p=centerline(np.linspace(0,1,100));v,f=sheath_mesh()
    assert np.all(p[:,0]<0)
    assert np.all(np.diff(p[:,1])>0)
    assert np.all(np.diff(p[:,2])<0)
    assert np.isfinite(v).all()
    assert max(max(x) for x in f)<len(v)
    assert 6<np.linalg.norm(np.diff(p,axis=0),axis=1).sum()<8
    edges={}
    for face in f:
        for a,b in zip(face,face[1:]+face[:1]):
            k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
    assert set(edges.values())=={2}
