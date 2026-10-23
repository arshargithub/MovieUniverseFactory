import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_arm352 import solve,unit,turn,supported_pose
from movie_factory.adapters.blender.nihang_patch import validate

REST=tuple(map(np.array,([.197,-.019,1.520],[.383,-.020,1.307],[.527,-.227,1.169],
                       [0,0,.06],[.04,-.09,0],[.028,-.063,0])))

def test_coordinated_solution_preserves_lengths_and_proper_frames():
    s=REST[0];p=solve(s,[.35,-.2,1.5],[0,0,1],REST,np.array([.25,-.08,-.18]),.12,0.)
    assert np.isclose(np.linalg.norm(p['elbow']-s),np.linalg.norm(REST[1]-s))
    assert np.isclose(np.linalg.norm(p['wrist']-p['elbow']),np.linalg.norm(REST[2]-REST[1]))
    for key in ('hand','upper','lower'):
        assert np.allclose(p[key].T@p[key],np.eye(3))
        assert np.isclose(np.linalg.det(p[key]),1.)
    assert np.allclose(p['hand']@unit(REST[3]),[0,0,1])
    assert np.isfinite(p['score'])

def test_rodriques_keeps_axis_component_and_length():
    v=np.array([1.,2,3]);r=turn(v,[0,0,1],.7)
    assert np.isclose(r[2],3) and np.isclose(np.linalg.norm(v),np.linalg.norm(r))

def test_unreachable_and_degenerate_fail_before_mutation():
    with pytest.raises(ValueError,match='UNREACHABLE'):
        solve(REST[0],[5,0,2],[0,0,1],REST,np.array([.25,-.08,-.18]),.12,0)
    with pytest.raises(ValueError,match='DEGENERATE'):unit([0,0,0])

def test_fixed_recipe_rejects_extra_parameters():
    r=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,
           edits=[dict(kind='mounted_arm352',target='mounted leader')])
    assert validate(r)==r
    r['edits'][0]['yaw']=90
    with pytest.raises(ValueError):validate(r)

def test_supported_pose_keeps_elbow_out_and_wrist_aligned():
    p=supported_pose(REST[0],[.4,-.2,-1],np.eye(3),REST)
    assert p['elbow'][0]>REST[0][0]+.05 and p['elbow'][2]<REST[0][2]-.2
    assert p['bend']<35
    assert np.allclose(unit(p['center']-[.4,-.2,-1]),p['up'])
    assert np.isclose(np.linalg.norm(p['elbow']-REST[0]),np.linalg.norm(REST[1]-REST[0]))
    assert np.isclose(np.linalg.norm(p['wrist']-p['elbow']),np.linalg.norm(REST[2]-REST[1]))
