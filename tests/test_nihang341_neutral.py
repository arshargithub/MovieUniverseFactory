import math
import numpy as np
import pytest
from types import SimpleNamespace
from movie_factory.adapters.blender import nihang_neutral as n, nihang_patch as p, nihang_control as c


def recipe(phase='neutral'):
    return dict(operation='nihang_patch',frame=283,width=640,height=640,samples=16,
                edits=[dict(kind='neutral_garment_proof',target='mounted leader',phase=phase)])


@pytest.mark.parametrize('phase',['neutral','bend'])
def test_typed_recipe(phase):
    assert p.validate(recipe(phase))['edits'][0]['phase']==phase


@pytest.mark.parametrize('field,value',[('phase','eval'),('path','/tmp/x'),('code','print(1)'),('target','other')])
def test_no_dynamic_operation(field,value):
    r=recipe();r['edits'][0][field]=value
    with pytest.raises(ValueError):p.validate(r)


def test_zero_bend_identity():
    pts=np.array([[.3,-.02,1.1],[.18,0,1.36],[-.3,0,1.0]])
    np.testing.assert_allclose(n.bend_points(pts,0),pts,atol=1e-15)


def test_neutral_ease_leaves_arm_back_and_neck_alone():
    pts=np.array([[.30,-.05,1.2],[0,.10,1.2],[0,-.05,1.42],[0,-.12,1.18]])
    result=n.neutral_ease(pts)
    np.testing.assert_array_equal(result[:3],pts[:3])
    assert -.18<result[3,1]<-.16
    np.testing.assert_array_equal(result[:,[0,2]],pts[:,[0,2]])


def test_bend_preserves_shoulder_opposite_and_forearm_radius():
    pts=np.array([[.31,-.005,.91],[.18,0,1.36],[-.30,0,1.02]])
    result=n.bend_points(pts,math.radians(-75))
    np.testing.assert_array_equal(result[1:],pts[1:])
    elbow=np.array([.285,-.005,1.13])
    assert np.linalg.norm(result[0]-elbow)==pytest.approx(np.linalg.norm(pts[0]-elbow))
    assert result[0,1]<pts[0,1] # forward is -Y, never an outward elbow flip


def test_elbow_field_never_grabs_outer_thigh():
    pts=np.array([[.20,0,.96],[.24,.02,.91],[.18,-.07,.83],[.31,-.005,.91]])
    result=n.bend_points(pts,math.radians(-75),np.array([False,False,False,True]))
    np.testing.assert_array_equal(result[:3],pts[:3])
    assert np.linalg.norm(result[3]-pts[3])>.1


def test_connected_arm_keeps_medial_fingers_and_excludes_nearby_body():
    pts=np.array([[.20,0,.85],[.44,0,.85],[.30,0,1.16],
                  [.20,.1,.85],[.24,.1,.85],[.24,.1,1.16]])
    mask=n.connected_arm(pts,[(0,1,2),(3,4,5)])
    np.testing.assert_array_equal(mask,[True,True,True,False,False,False])
    weights=n.bend_weights(pts,mask)
    assert weights[0]==weights[1]==1
    assert (weights[3:]==0).all()


@pytest.mark.parametrize('view',['neutral_front','neutral_back','neutral_side'])
def test_fixed_neutral_views(view):
    r=dict(operation='nihang_frames',frame=283,frames=[283],width=640,height=640,samples=16,view=view)
    assert c.validate(r)==r


@pytest.mark.parametrize('collection,users,fake,expected',[
    ('libraries',0,False,False),('libraries',1,False,True),
    ('libraries',0,True,True),('images',0,False,True),('cache_files',0,False,True)])
def test_only_orphan_appended_libraries_are_not_runtime_dependencies(collection,users,fake,expected):
    assert c.dependency_relevant(collection,SimpleNamespace(users=users,use_fake_user=fake))==expected

def test_weak_append_provenance_is_not_a_live_link():
    lib=SimpleNamespace(users=2,use_fake_user=False)
    assert not c.dependency_relevant('libraries',lib,[SimpleNamespace(library=None)])
    assert c.dependency_relevant('libraries',lib,[SimpleNamespace(library=lib)])
    assert c.dependency_relevant('images',lib,[])
