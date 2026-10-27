import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_articulation387 import validate,insertion_solution
from movie_factory.adapters.blender.nihang_patch import validate as patch

def matrix(q):
    w,x,y,z=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def test_endpoint_control_zero_and_rigid_orientation():
    h=np.array([.126,-.581,1.403]);t=np.array([.126,-.948,1.209]);p=np.array([.21,-.732,1.43])
    q,s,g=insertion_solution(h,t,p,0);assert np.allclose(q,[1,0,0,0]) and s==pytest.approx(1) and np.allclose(g,t)
    q,s,g=insertion_solution(h,t,p,1);assert np.allclose(h+matrix(q)@(t-h)*s,p) and .2<s<1
    for f in np.linspace(0,1,11):
        q,s,g=insertion_solution(h,t,p,float(f));assert np.allclose(h+matrix(q)@(t-h)*s,g) and np.linalg.det(matrix(q))==pytest.approx(1)

def test_schema_allows_only_fixed_leaf_articulation():
    e=dict(kind='mounted_articulation387',target='horse',strength=1.)
    patch(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
    for bad in [dict(e,strength=True),dict(e,strength=float('nan')),dict(e,strength=1.01),dict(e,bone='head'),dict(e,code='x'),dict(e,target='horse.rig')]:
        with pytest.raises(ValueError):validate(bad)

def test_bad_endpoint_scale_is_not_clamped_into_apparent_safety():
    for h,t,p in [([0,0,0],[0,0,0],[0,1,0]),([0,0,0],[0,.4,0],[0,-.4,0]),([0,0,0],[0,.4,0],[0,2,0])]:
        with pytest.raises(ValueError):insertion_solution(h,t,p,1)


def test_calibrated_handle_retains_bind_offset_instead_of_snapping_to_joint():
    from movie_factory.adapters.blender.anatomy_articulation387 import calibrated_point
    A=np.eye(4);A[:3,3]=[.2,-.8,1.4];P=np.array([.12,-.95,1.2])
    assert np.allclose(calibrated_point(A,A,P),P)
    B=A.copy();theta=.6;B[:3,:3]=[[1,0,0],[0,np.cos(theta),-np.sin(theta)],[0,np.sin(theta),np.cos(theta)]]
    expected=B[:3,3]+B[:3,:3]@(P-A[:3,3]);assert np.allclose(calibrated_point(A,B,P),expected)
    assert not np.allclose(expected,B[:3,3])
    with pytest.raises(ValueError):calibrated_point(np.zeros((4,4)),B,P)
    patch(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[dict(kind='mounted_articulation387_calibrated',target='horse',strength=.8)]))
