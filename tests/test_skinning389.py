import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_skinning389 import validate,mask,blend

def test_closed_native_recipe():
    e=dict(kind='mounted_anatomy389_skinning',target='horse',mode=0)
    assert validate(e)==e
    assert validate(dict(e,mode=2))["mode"]==2
    for bad in [dict(e,mode=True),dict(e,mode=3),dict(e,script='x')]:
        with pytest.raises(ValueError):validate(bad)

def test_exact_exterior_and_shared_rigid_equivariance():
    a=np.array([[0.,0.,0.],[1.,2.,3.],[4.,5.,6.]],np.float32);b=a+np.array([.1,.2,.3]);m=np.array([0.,.5,1.]);v=blend(a,b,m)
    assert np.array_equal(v[0],a[0]);np.testing.assert_allclose(v[1],(a[1]+b[1])/2)
    np.testing.assert_allclose(blend(a+3,b+3,m),v+3,atol=1e-6)
    assert np.array_equal(blend(a,a,m),a)

def test_domain_excludes_head_and_distal():
    r=np.array([[0,-.8,.5],[0,-.8,1.25],[0,-.8,2.],[0,.2,1.25]])
    m=mask(r,np.ones(4,bool));assert m[1]==1 and np.array_equal(m[[0,2,3]],np.zeros(3))
    with pytest.raises(ValueError):blend(r,r,np.ones(4)*2)


def test_static_probe_cannot_be_reused_as_live_rig(tmp_path):
    from types import SimpleNamespace
    from movie_factory.adapters.blender.anatomy_skinning389 import run
    horse=SimpleNamespace(data=SimpleNamespace(vertices=[None]*22514),get=lambda k:k=='probe389')
    bpy=SimpleNamespace(data=SimpleNamespace(objects={'horse':horse,'horse.rig':object()}))
    helpers=lambda n:SimpleNamespace(select_production_scene=lambda b:object())
    with pytest.raises(ValueError,match='SKINNING389_SOURCE'):
        run(bpy,tmp_path,dict(kind='mounted_anatomy389_skinning',target='horse',mode=0),helpers)
