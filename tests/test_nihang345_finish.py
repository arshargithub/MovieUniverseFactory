import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_finish345 import frame_map,skirt_point,layer_weights,transported_frame,neutral_elbow

def test_neutral_elbow_preserves_lengths_and_prefers_palm_alignment():
    shoulder=np.array([0.,0.,0.]);wrist=np.array([.4,0.,.2]);direction=np.array([1.,0.,0.])
    elbow=neutral_elbow(shoulder,wrist,.3,.3,direction)
    assert np.linalg.norm(elbow-shoulder)==pytest.approx(.3)
    assert np.linalg.norm(wrist-elbow)==pytest.approx(.3)
    mirrored=elbow.copy();mirrored[2]*=-1
    # Compare all other points on the exact feasible elbow circle.
    axis=wrist/np.linalg.norm(wrist);center=wrist*.5;offset=elbow-center
    for theta in np.linspace(0,2*np.pi,64):
        other=center+offset*np.cos(theta)+np.cross(axis,offset)*np.sin(theta)
        assert (wrist-elbow)@direction >= (wrist-other)@direction-1e-9
    with pytest.raises(ValueError):neutral_elbow(shoulder,[2,0,0],.3,.3,direction)

def test_forearm_transport_retains_each_bones_rest_roll():
    # Two bones can share their length axis while having different local X/Z.
    a=.9;c,s=np.cos(a),np.sin(a)
    rest=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    assert np.allclose(transported_frame(rest,np.eye(3),[0,1,0]),rest)
    target=transported_frame(rest,np.eye(3),[1,1,0])
    assert np.allclose(target[:,1],np.array([1,1,0])/np.sqrt(2))
    assert np.allclose(target.T@target,np.eye(3))
    assert np.linalg.det(target)==pytest.approx(1)
    with pytest.raises(ValueError):transported_frame(rest,np.eye(3),[0,-1,0])
from movie_factory.adapters.blender.nihang_patch import validate

def test_palm_frame_is_proper_and_index_axis_follows_shaft():
    r=frame_map([1,0,0],[0,1,0],[0,0,1],[0,-1,0])
    assert np.allclose(r@r.T,np.eye(3)) and np.linalg.det(r)==pytest.approx(1)
    assert np.allclose(r@np.array([1,0,0]),[0,0,1])
    with pytest.raises(ValueError):frame_map([1,0,0],[2,0,0],[0,0,1],[0,-1,0])

def test_skirt_root_and_hem_are_supported_not_rigid_cylinder():
    root=[.17,-.04,1.145]
    assert np.allclose(skirt_point(root,0,.7),root)
    hem=skirt_point(root,1,.7)
    assert .59<hem[2]<.64 and hem[0]>.20

def test_fixed_handler_accepts_no_paths_or_code():
    r=dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,edits=[dict(kind='mounted_finish345',target='mounted leader')])
    assert validate(r)==r
    with pytest.raises(ValueError):validate(r|{'edits':[r['edits'][0]|{'code':'anything'}]})

def test_mask_groups_and_thighs_cannot_own_waist():
    bones={'spine05','spine04','upperleg01.L','upperarm01.L'}
    row={'body':1,'Left':1,'spine05':.55,'upperleg01.L':.4,'upperarm01.L':.05}
    assert layer_weights(row,bones,True)=={'spine05':1.0}
    result=layer_weights(row,bones)
    assert set(result)=={'spine05','upperleg01.L'} and sum(result.values())==pytest.approx(1)
