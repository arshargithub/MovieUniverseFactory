import numpy as np
from movie_factory.adapters.blender.nihang_form354 import beard_path,moustache_path
from movie_factory.adapters.blender.nihang_patch import validate
import pytest

def test_roots_and_rounded_envelope():
    ends=[]
    for i,x in enumerate(np.linspace(-.07,.07,29)):
        r=(x,-.1,1.65);p=beard_path(r,1.75,i)
        assert np.allclose(p[0],r) and np.isfinite(p).all()
        assert np.max(np.linalg.norm(np.diff(p,axis=0),axis=1))<.025
        ends.append(p[-1,2])
    assert min(ends[11:18])<min(ends[:3])
    assert np.ptp(ends)>.015  # old straight curtain negative

def test_moustache_not_outward_wing():
    for x in (-.04,-.01,.01,.04):
        p=moustache_path((x,-.1,1.7),0)
        assert np.linalg.norm(p[-1]-p[0])<.02
        assert p[-1,2]<p[0,2]

def test_fixed_recipe_only():
    v=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_form354',target='mounted leader')])
    assert validate(v)==v
    v['edits'][0]['code']='print(1)'
    with pytest.raises(ValueError):validate(v)
