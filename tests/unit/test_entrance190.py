"""New shot controls preserve strict operations and a bounded blink clock."""
import importlib.util
from pathlib import Path
import pytest

def load(name):
    path=Path(__file__).resolve().parents[2]/'scripts'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def test_quick_blink_complete_and_asymmetric():
    b=load('entrance190_blink').blink
    assert b(312)==1 and b(311.5)==0 and b(313.5)==0
    assert b(311)==b(314)==0
    assert 0<b(313)<.3
    assert b(311.75)==pytest.approx(.5)
    assert b(312.75)==pytest.approx(.5)
    assert all(0<=b(i/16)<=1 for i in range(217*16,361*16))

@pytest.mark.parametrize('name',['entrance190_blink','entrance190_route'])
@pytest.mark.parametrize('job',[{}, {'operation':'exec'}, {'operation':'blink01','code':'bad'}])
def test_closed_operations(name,job):
    with pytest.raises(ValueError,match='Fixed'):load(name).validate(job)

def test_route_single_clock_continuity():
    import numpy as np
    m=load('entrance190_route_math');r=m.trajectory()
    assert np.isfinite(np.concatenate([a.ravel() for a in r.values()])).all()
    assert r['speed'][0]==12 and r['speed'].min()==6.5
    assert r['source_frame'][0]==144 and np.all(np.diff(r['source_frame'])>0)
    assert np.all(np.diff(r['heading'])<=0) and r['heading'][-1]==pytest.approx(-np.deg2rad(55))
    assert np.max(abs(r['bank']))<np.deg2rad(15)
    assert r['position'][-1,0]<0  # right branch relative to -Y travel
    assert np.max(r['grade'])==.12
    measured=np.linalg.norm(np.diff(r['position'],axis=0),axis=1)*24*8
    np.testing.assert_allclose(measured,(r['speed'][:-1]+r['speed'][1:])/2,atol=.0001)
    assert m.sample(0)['position'].tolist()==[0,0,0]

def test_rider_uses_source_phase_not_cache_length():
    import numpy as np
    m=load('entrance190_rider');period=24/2.2
    for sf in np.linspace(144,310,333):
        f=m.source_pose_frame(sf)
        assert 360-period<f<=360
        assert abs(((f-217-sf)/period)-round((f-217-sf)/period))<1e-10
    assert m.gathered(0)==0
    assert m.gathered(2)==1
    assert m.gathered(8)==pytest.approx(.35)

def test_cloth_support_rigid_transform_preserves_distances():
    import numpy as np
    m=load('entrance190_shawl')
    points=np.array([[0.,1,2],[3,4,5],[-1,0,2]])
    matrices=np.repeat(np.eye(4)[None],2,axis=0)
    matrices[1,:3,:3]=[[0,-1,0],[1,0,0],[0,0,1]]
    matrices[1,:3,3]=[10,20,30]
    q=m.transformed(points,matrices)
    np.testing.assert_allclose(q[0],points)
    np.testing.assert_allclose(q[1],points@matrices[1,:3,:3].T+matrices[1,:3,3])
    np.testing.assert_allclose(np.linalg.norm(q[:,1]-q[:,0],axis=1),np.linalg.norm(points[1]-points[0]))

def test_shared_geography_matches_contact_route():
    import numpy as np
    r=load('entrance190_route_math').trajectory();m=load('entrance190_geography')
    points=r['position'][::8]
    height,distance=m.fields(points[:,:2],r)
    np.testing.assert_allclose(height,points[:,2],atol=1e-9)
    np.testing.assert_allclose(distance,0,atol=1e-9)
    height,_=m.fields(np.array([[0.,-40],[0,-60],[0,5]]),r)
    np.testing.assert_allclose(height,0,atol=1e-9)

def test_wake_history_continues_preceding_straight_motion():
    import numpy as np
    m=load('entrance190_scene');r=load('entrance190_route_math').trajectory()
    np.testing.assert_allclose(m.path_sample(r,-2),[0,24,0])
    np.testing.assert_allclose(m.path_sample(r,0),[0,0,0])
    np.testing.assert_allclose(m.path_sample(r,8),r['position'][-1])
    assert m.path_sample(r,6)[0]<m.path_sample(r,4)[0]

def test_perspective_exit_recedes_and_camera_path_is_continuous():
    import numpy as np
    m=load('entrance190_perspective');r=load('entrance190_route_math').trajectory()
    a,ta=m.camera(r,6);b,tb=m.camera(r,8)
    assert np.linalg.norm(b-tb)>np.linalg.norm(a-ta)*1.5
    before,_=m.camera(r,6-1e-5);after,_=m.camera(r,6+1e-5)
    assert np.linalg.norm(after-before)<.01
    assert np.isfinite(m.project(np.array([[0,0,0]]),np.array([0.,2,2]),np.array([0.,0,0]))).all()

def test_reopen_parity_rejects_known_differences():
    import numpy as np
    compare=load('entrance190_verify').compare
    a=np.zeros((2,2,3),dtype=np.uint8)
    assert compare(a,a)['status']=='PASS'
    assert compare(a,a+1)['status']=='PASS'
    assert compare(a,a+2)['status']=='FAIL'
    with pytest.raises(ValueError,match='dimensions'):compare(a,a[:1])

def test_blink_replacement_covers_every_changed_integer_frame():
    old=load('entrance189_performance').facial_values
    new=load('entrance190_blink').blink
    changed={f for f in range(217,361) if abs(old(f)['eyeBlinkLeft']-new(f))>1e-6}
    assert changed=={310,311,313,314}
    assert changed.issubset(set(range(310,315)))
    assert old(309)['eyeBlinkLeft']==new(309)==0
    assert old(315)['eyeBlinkLeft']==new(315)==0
