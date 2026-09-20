import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('anatomy',Path('src/movie_factory/adapters/blender/neck_anatomy_review.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[{},None,{'operation':'exec','candidate':1},{'operation':'build','candidate':True},{'operation':'build','candidate':8},{'operation':'build','candidate':1,'path':'x'}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_quintic_endpoint_values_slopes():
    for a,b,da,db in ((.6,1.7,0.,1.5),(.6,.8,-.1,.2)):
        h=1.03;e=1e-6
        assert m.bridge(a,b,da,db,0,h)==a
        assert abs(m.bridge(a,b,da,db,1,h)-b)<1e-12
        assert abs((m.bridge(a,b,da,db,e,h)-a)/(h*e)-da)<1e-4
        assert abs((b-m.bridge(a,b,da,db,1-e,h))/(h*e)-db)<1e-4

def test_cubic_extension_endpoint_values_slopes():
    h=.9;e=1e-6
    for a,b,da,db in ((.64,.94,.55,.3),(.59,1.75,.16,1.6),(.593,.74,-.5,.16)):
        assert m.cubic_bridge(a,b,da,db,0,h)==a
        assert abs(m.cubic_bridge(a,b,da,db,1,h)-b)<1e-12
        assert abs((m.cubic_bridge(a,b,da,db,e,h)-a)/(h*e)-da)<1e-4
        assert abs((b-m.cubic_bridge(a,b,da,db,1-e,h))/(h*e)-db)<1e-4

def test_relief_bounded_protected_and_no_back_ridge():
    for c in (1,2,3,4):
        for x in (-1,-.3,0,.3,1):
            for z in (-2,m.BOTTOM,-1.6,-1.3,-1.,m.TOP,0):
                assert m.relief(x,z,0,c)==0
                assert abs(m.relief(x,z,math.pi,c))<.13
                if z>=m.TOP or z<=m.BOTTOM:assert m.relief(x,z,math.pi,c)==0

def test_source_and_output_guards(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_bytes(b'pinned');monkeypatch.setattr(m,'SOURCE',source)
    monkeypatch.setattr(m,'SOURCE_SHA',m.hashlib.sha256(b'pinned').hexdigest());monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'build','candidate':1};out=m.validate(job);out.mkdir()
    with pytest.raises(ValueError,match='Existing'):m.validate(job)
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate(job)

@pytest.mark.parametrize('candidate',[2,3,4])
def test_anatomical_points_bounded_face_and_height_unchanged(candidate):
    for z in (0,m.TOP,m.BOTTOM,-2):assert m.anatomical_point(.3,.4,z,candidate)==(.3,.4,z)
    for i in range(101):
        a=i*2*math.pi/100
        for j in range(101):
            z=m.BOTTOM+(m.TOP-m.BOTTOM)*j/100
            p=m.anatomical_point(.7*math.sin(a),.1+.7*math.cos(a),z,candidate)
            assert p[2]==z and all(math.isfinite(v) for v in p)
            assert abs(p[0])<1.8 and abs(p[1])<1.

def test_posterior_exception_keeps_face_jaw_ears_locked():
    for x in (-1,-.7,0,.7,1):
        for y in (-1,-.5,0,.12,.5,.8):
            for z in (-1.5,-.85,-.6,-.45,0,1):
                if y<=.12 or z>=-.45 or abs(x)>=.7 or z<=-1.48:
                    assert m.posterior_weight(x,y,z)==0
    assert m.posterior_weight(0,.65,-.85)>0

def test_taper_guard_and_finite_points():
    for x in (-1,-.75,0,.75,1):
        for y in (-1,-.7,0,.1,.6):
            for z in (-2,-.85,-.5,-.3,0,1):
                if z>=-.3 or z<=m.BOTTOM or (z>=m.TOP and math.hypot(x,y-.1)>=.7):
                    assert m.taper_point(x,y,z,5)==(x,y,z)
    for z in (-.3,-.6,-.8,-1,-1.3,-1.6,-1.89):
        for i in range(100):
            a=2*math.pi*i/100
            p=m.taper_point(.6*math.sin(a),.1+.6*math.cos(a),z,5)
            assert p[2]==z and all(math.isfinite(v) for v in p)
            assert abs(p[0])<1.8 and abs(p[1])<1.

def test_spline_continuous_curvature():
    knots=(.3,.5,.75,1.,1.2,1.45,1.7,1.89);values=(.495,.475,.479,.509,.55,.61,.69,.768)
    for x,y in zip(knots,values):assert abs(m.spline_value(x,knots,values)-y)<1e-10
    h=1e-4
    for x in knots[1:-1]:
        f=lambda z:m.spline_value(z,knots,values)
        left=(f(x)-2*f(x-h)+f(x-2*h))/h**2
        right=(f(x+2*h)-2*f(x+h)+f(x))/h**2
        assert abs(left-right)<.01

def test_template_extension_restores_full_face_plane_guard():
    for candidate in (6,7):
        for x in (-1,0,1):
            for y in (-1,0,1):
                for z in (-.86,-.6,0,1):assert m.protected_vertex(x,y,z,candidate)
