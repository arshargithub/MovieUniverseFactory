import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from entrance201_dust import cloud_centers,AGES

def test_wake_straight_registration_and_extent():
    a=cloud_centers(0);b=cloud_centers(7)
    assert np.array_equal(a,b)
    assert np.all(np.diff(a[:,1])>0)
    assert a[-1,1]>280 and a[-1,2]>-6

def test_wake_history_follows_curve_not_current_heading():
    t=np.linspace(0,8,1537);route={'time':t,'position':np.column_stack((-t*t,-12*t,.2*t*t))}
    p=cloud_centers(4,route)
    expected=np.interp(4-AGES,t,-t*t)*8.3+2.5*AGES
    assert np.allclose(p[:,0],expected)
    assert np.isfinite(p).all()

def test_history_join_is_continuous():
    t=np.linspace(0,8,1537);route={'time':t,'position':np.column_stack((t*0,-12*t,t*0))}
    assert np.allclose(cloud_centers(0,route),cloud_centers(0))

def test_cover_only_advances_supported_headfall():
    from entrance201_fit import cover_points
    p=np.zeros((7205,3));p[:2501,1]=1.85;p[:2501,2]=.17
    q=cover_points(p,np.eye(4))
    assert .15<q[30,2]-p[30,2]<.20
    assert np.array_equal(q[2501:],p[2501:])
    assert np.allclose(q[15*61:2501],p[15*61:2501])
    assert np.linalg.norm(q-p,axis=1).max()<.2

def test_crown_envelope_is_bounded_and_not_chest_projection():
    from entrance201_clearance import clearance_delta
    x,z=np.meshgrid(np.linspace(-.9,.9,100),np.linspace(-.3,.8,100));hair=np.column_stack((x.ravel(),np.full(x.size,1.8),z.ravel()))
    cloth=np.zeros((2501,3));cloth[30]=[0,1.7,.4]
    d=clearance_delta(hair,cloth)
    assert .14<d[30]<.15 and d.max()<.15
    assert d.reshape(41,61)[10:].max()==0
