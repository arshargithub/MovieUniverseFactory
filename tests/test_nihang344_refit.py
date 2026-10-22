import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_refit import cuff_fit,coat_region
from movie_factory.adapters.blender.nihang_patch import validate

def test_cuff_preserves_axis_and_unaffected_torso():
    p=np.array([[.5,.1,1],[.5,.02,1],[0,.1,1]])
    q,m=cuff_fit(p,[.5,0,1],[.3,0,1],1)
    assert q[0,1]==pytest.approx(.044)
    assert q[1].tolist()==p[1].tolist() and q[2].tolist()==p[2].tolist()
    assert np.all(q[:,0]==p[:,0]) and m.tolist()==[True,True,False]

def test_fixed_refit_scope_only():
    r=dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,edits=[dict(kind='coherent_refit',target='mounted leader')])
    assert validate(r)==r
    r['edits'][0]['path']='anything'
    with pytest.raises(ValueError):validate(r)

def test_body_shell_keeps_shoulders_but_not_hands_head_or_legs():
    points=[[0,0,1.75],[.2,0,1.55],[0,0,1.4],[0,0,.9],[.54,-.28,1.15],[.45,-.12,1.24]]
    w={s:np.array([s*.527,-.227,1.169]) for s in (-1,1)}
    e={s:np.array([s*.383,-.020,1.307]) for s in (-1,1)}
    assert coat_region(points,w,e).tolist()==[False,True,True,False,False,True]
