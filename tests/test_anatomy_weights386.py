import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_weights386 import validate,remap

def test_reject_unbounded_and_code_fields():
    good=dict(kind='mounted_anatomy386_weights',target='horse',strength=.6)
    assert validate(good)==good
    for e in [dict(good,strength=.71),dict(good,strength=float('nan')),dict(good,code='x')]:
        with pytest.raises(ValueError):validate(e)

def test_local_mass_transfer_preserves_other_groups_and_outside():
    names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L']
    r=np.tile([.12,-.9,1.25],(10,1));r[-1,2]=.8
    w=np.tile([.4,.4,.05,.05,.1],(10,1));edges=np.array([[i,i+1] for i in range(9)])
    skin=np.ones(10,bool);skin[-2]=False
    target,mask=remap(r,w,names,edges,.6,skin)
    assert np.allclose(target.sum(1),w.sum(1))
    assert np.array_equal(target[:,4],w[:,4])
    assert np.array_equal(target[-2:],w[-2:])
    assert target[0,0]<w[0,0] and target[0,2]>w[0,2]
    assert np.all(target>=0)

def test_core_policy_freezes_forearm_even_next_to_active_chest():
    names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L']
    r=np.tile([.12,-.9,1.25],(8,1));w=np.tile([.4,.4,.05,.05,.1],(8,1))
    w[3]=[.02,.02,.03,.03,.9];w[4]=[.11,.11,.34,.34,.1]
    edges=np.array([[i,i+1] for i in range(7)])
    result,mask=remap(r,w,names,edges,.6,np.ones(8,bool),core=True)
    assert np.array_equal(result[[3,4]],w[[3,4]])
    assert mask[3]==mask[4]==0 and mask[0]>0
    assert np.allclose(result.sum(1),w.sum(1))
