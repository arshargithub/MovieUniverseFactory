import pytest
import numpy as np
from movie_factory.adapters.blender.nihang_cloth352 import blend_weights,elbow_ease
from movie_factory.adapters.blender.nihang_patch import validate

def test_weight_transfer_normalizes_and_prefers_nearby():
    w=blend_weights([[('spine04',1.)],[('upperarm01.L',1.)]],[.01,.1])
    assert abs(sum(w.values())-1)<1e-6 and w['spine04']>.98

def test_no_empty_weights():
    with pytest.raises(ValueError):blend_weights([[]],[.01])

def test_cloth_fixed_parameters_only():
    r=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_cloth352',target='mounted leader')])
    assert validate(r)==r
    r['edits'][0]['source']='arbitrary'
    with pytest.raises(ValueError):validate(r)

def test_elbow_ease_is_bounded_local_and_radial():
    s=np.array([0,0,1]);e=np.array([0,0,.7]);w=np.array([0,0,.4]);p=np.array([.06,0,.7])
    v=elbow_ease(p,s,e,w)
    assert 0<v[0]-p[0]<=.022 and np.allclose(v[1:],p[1:])
    q=np.array([.06,0,1.3]);assert np.linalg.norm(elbow_ease(q,s,e,w)-q)<1e-6
