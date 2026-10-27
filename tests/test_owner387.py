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


def test_expanded_native_domain_keeps_distal_and_legacy_guards():
    from movie_factory.adapters.blender.anatomy_domain386 import preserve_owner387,preserve_forelegs
    from movie_factory.adapters.blender.nihang_patch import validate
    names=['DEF-forefoot.L','DEF-forefoot.R','DEF-f_hoof.L','DEF-f_hoof.R','DEF-forearm.L','DEF-forearm.R']
    r=np.array([[.2,-.8,1.2],[.2,-.8,.5],[.1,-.7,1.3],[.3,-.7,1.2]])
    edges=np.array([[0,1],[1,2],[2,3],[3,0]]);w=np.zeros((4,6));w[0,4]=1.;w[1,0]=1.;a=r[None].copy();b=a.copy();b[0,0,0]+=.01
    assert preserve_owner387(a,b,r,w,names,edges)['max_changed_delta']<.02
    with pytest.raises(ValueError,match='FROZEN_FORELEG'):preserve_forelegs(a,b,w,names)
    b[0,1,0]+=.01
    with pytest.raises(ValueError,match='DISTAL_OR_OUTSIDE'):preserve_owner387(a,b,r,w,names,edges)
    validate(dict(operation='nihang_patch',frame=339,width=640,height=640,samples=8,edits=[dict(kind='mounted_anatomy387_owner_target',target='horse',data=dict(path='.runtime/art-direction/anatomy386-targets/t.npz',sha256='a'*64))]))
