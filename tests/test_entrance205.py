import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from entrance205_motion import trajectory, profile, sample
from entrance205_camera import route_camera,glance
from entrance205_geography import fields


def test_real_time_coordinated_trajectory():
    d=trajectory()
    assert len(d['time'])==2305
    assert np.all(np.diff(d['source_frame'])>0)
    assert np.max(d['grade'])==.48
    assert d['position'][-1,2]>25
    assert np.rad2deg(d['heading'][-1])==-68
    assert np.min(d['speed'])>=5.2-1e-9
    assert np.max(abs(d['bank']))<=np.deg2rad(27)+1e-9
    assert np.allclose(sample(0)['position'],0)


def test_fast_redirection_and_supported_launch():
    d=trajectory()
    turning=d['time'][(d['heading']<np.deg2rad(-5))&(d['heading']>np.deg2rad(-63))]
    assert np.ptp(turning)<1.5
    assert profile(4.25)[2]==.48
    assert profile(0)[0]==12
    assert profile(12)[0]>8


def test_clear_editorial_coverage_and_forward_finish():
    assert [route_camera(t)[3] for t in (0,1.2,1.25,4.5,4.6,8,12)]==[
        'ots','ots','front_maneuver','front_maneuver',
        'close_climb_glance_forward','close_climb_glance_forward','close_climb_glance_forward']
    assert glance(6)==1
    assert glance(8)==0
    assert all(glance(t)==0 for t in np.linspace(8,12,50))


def test_route_support_and_exposed_edge():
    d=trajectory();p=d['position'][::8];z,dist=fields(p[:,:2],d)
    assert np.max(abs(z-p[:,2]))<.001
    t=8;r=sample(t);right=np.array([np.cos(r['heading']),np.sin(r['heading'])])
    edge,_=fields(np.array([r['position'][:2]+right*x for x in (0,1,2,4,6)]),d)
    assert abs(edge[1]-edge[0])<.1
    assert edge[-1]<edge[0]-10
    # Frontal coverage must not run through the newly steeper ground.
    for t in np.linspace(1.25,4.59,30):
        camera=route_camera(t)[0];ground,_=fields(camera[None,:2],d)
        assert camera[2]>ground[0]+.5


def test_front_camera_is_on_downhill_outboard_side():
    for t in np.linspace(1.25,4.59,30):
        d=sample(t);right=np.array([np.cos(d['heading']),np.sin(d['heading']),0.])
        assert np.dot(route_camera(t)[0]-d['position'],right)>2


def test_rough_bank_does_not_intrude_into_hoof_support():
    d=trajectory()
    for t in np.linspace(3.3,12,40):
        p=sample(t);right=np.array([np.cos(p['heading']),np.sin(p['heading'])])
        xy=np.array([p['position'][:2]+right*x for x in (-.75,0,.75)])
        z,_=fields(xy,d)
        assert np.max(abs(z-p['position'][2]))<.01


def test_fixed_matte_seams_outside_camera_horizontal_coverage():
    # Numerical guard only; the actual rendered corners still need review.
    for t in np.linspace(0,12,145):
        camera,target,lens,shot=route_camera(t)
        forward=target-camera;forward/=np.linalg.norm(forward)
        right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right)
        up=np.cross(right,forward)
        for side in (-1,1):
            for vertical in (-1,1):
                ray=forward+right*side*(20.25/(2*lens))+up*vertical*(36/(2*lens))
                a=ray[:2]@ray[:2];b=2*(camera[:2]@ray[:2]);c=camera[:2]@camera[:2]-(8000/8.3)**2
                distance=(-b+np.sqrt(b*b-4*a*c))/(2*a)
                hit=camera[:2]+distance*ray[:2]
                angle=np.rad2deg(np.arctan2(hit[1],hit[0]))
                if shot=='ots':assert -224<angle<-76
                else:assert -76<angle<136
