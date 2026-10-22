import pytest
import numpy as np
from movie_factory.adapters.blender.nihang_anatomy351 import plane_rotation,reachable_elbow,spear_elbow_hint
from movie_factory.adapters.blender.nihang_patch import validate as patch_validate
from movie_factory.adapters.blender.nihang_control import validate, ANATOMY_VIEWS

@pytest.mark.parametrize('view',sorted(ANATOMY_VIEWS))
def test_anatomy_has_fixed_temporary_controls(view):
    r=dict(operation='nihang_frames',frame=327,frames=[327],view=view,width=640,height=640,samples=8)
    assert validate(r)==r

@pytest.mark.parametrize('view',['anatomy_delete','anatomy_rest_side','anatomy_custom_back;execute'])
def test_unreviewed_diagnostic_view_rejected(view):
    with pytest.raises(ValueError,match='NIHANG_DIAGNOSTIC_VIEW'):
        validate(dict(operation='nihang_frames',frame=327,frames=[327],view=view,width=640,height=640,samples=8))

def test_plane_transport_is_proper_and_maps_hinge():
    a=np.array([1.,0,0]);b=np.array([0.,1,0]);u=np.array([0.,0,1]);v=np.array([1.,0,0])
    r=plane_rotation(a,b,u,v)
    assert np.allclose(r@a,u) and np.allclose(r@b,v)
    assert np.allclose(r.T@r,np.eye(3)) and np.isclose(np.linalg.det(r),1)
    assert np.allclose(plane_rotation(a,b,a,b),np.eye(3))

def test_reachable_elbow_preserves_lengths_and_pole():
    s=np.array([0.,0,0]);w=np.array([.3,0,0]);e=reachable_elbow(s,w,.25,.2,[0,1,0])
    assert np.isclose(np.linalg.norm(e-s),.25) and np.isclose(np.linalg.norm(w-e),.2)
    assert e[1]>0

def test_degenerate_controls_fail_closed():
    with pytest.raises(ValueError):plane_rotation([1,0,0],[2,0,0],[1,0,0],[0,1,0])
    with pytest.raises(ValueError):reachable_elbow([0,0,0],[1,0,0],.25,.2,[0,1,0])

def test_fixed_anatomy_operation_has_no_free_code_or_parameters():
    r=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_anatomy351',target='mounted leader')])
    assert patch_validate(r)==r
    r['edits'][0]['code']='anything'
    with pytest.raises(ValueError):patch_validate(r)

def test_spear_elbow_is_below_and_forward_for_measured_pose():
    s=np.array([.197,-.063,1.511]);w=np.array([.291,-.048,1.493])
    e=reachable_elbow(s,w,.283,.279,spear_elbow_hint(s))
    assert e[2]<s[2]-.15 and e[1]<s[1]
    assert np.isclose(np.linalg.norm(e-s),.283)
