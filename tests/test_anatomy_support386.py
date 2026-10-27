import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_support386 import validate,calibrated_rest,transfer,qualify_roundtrip
from movie_factory.adapters.blender.anatomy_weights386 import remap
from movie_factory.adapters.blender.nihang_patch import validate as patch_validate

def test_closed_secondary_support_operation():
    e=dict(kind='mounted_anatomy386_rigid_support',target='horse',strength=.6)
    patch_validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
    for bad in [dict(e,strength=.8),dict(e,strength=float('nan')),dict(e,code='x')]:
        with pytest.raises(ValueError):validate(bad)

def test_rest_calibration_preserves_nonidentity_neutral_deformation():
    b=np.eye(4);b[:3,3]=[.1,-.6,1.4];a=b.copy();a[:3,3]+=[.04,-.01,.03]
    theta=.4;c=np.array([[np.cos(theta),-np.sin(theta),0,.2],[np.sin(theta),np.cos(theta),0,-.8],[0,0,1,1.1],[0,0,0,1.]])
    rest=calibrated_rest(a,b,c)
    assert np.allclose(c@np.linalg.inv(rest),a@np.linalg.inv(b))
    p=np.array([.1,-.9,1.3,1.]);assert np.allclose(c@np.linalg.inv(rest)@p,a@np.linalg.inv(b)@p)

def test_transfer_adds_only_secondary_groups_not_bbone_upperarm():
    names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L']
    r=np.tile([.12,-.9,1.25],(6,1));w=np.tile([.4,.4,.05,.05,.1],(6,1));w[3]=[.02,.02,.03,.03,.9]
    edges=np.array([[i,i+1] for i in range(5)]);v,m=transfer(r,w,names,edges,np.ones(6,bool),.6,remap)
    assert np.array_equal(v[:,2:5],w[:,2:5]) and np.array_equal(v[3,:5],w[3])
    assert np.allclose(v.sum(1),w.sum(1)) and v[0,-2]>0

def test_zero_roundtrip_must_explain_actual_original_rig_drift():
    a=np.zeros((3,4,4));delta=np.ones_like(a)*.000049
    assert qualify_roundtrip(a,a+delta,a,a+delta)==0
    wrong=delta.copy();wrong[0,0,0]+=.00001
    with pytest.raises(ValueError,match='NOT_EXPLANATORY'):qualify_roundtrip(a,a+wrong,a,a+delta)

def test_dominant_chest_connector_moves_but_forearm_dominant_neighbor_frozen():
    names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L']
    r=np.tile([.12,-.9,1.25],(8,1));w=np.tile([.65,0,.03,.02,.3],(8,1));w[4]=[.02,.02,.03,.03,.9]
    edges=np.array([[i,i+1] for i in range(7)]);skin=np.ones(8,bool)
    old,_=transfer(r,w,names,edges,skin,.6,remap);new,mask=transfer(r,w,names,edges,skin,.6,remap,dominant=True)
    assert old[0,-2]==0 and new[0,-2]>.25
    assert np.array_equal(new[4,:5],w[4]) and np.array_equal(new[:,2:5],w[:,2:5])
    assert np.allclose(new.sum(1),w.sum(1))
    patch_validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[dict(kind='mounted_anatomy386_dominant_support',target='horse',strength=.6)]))
