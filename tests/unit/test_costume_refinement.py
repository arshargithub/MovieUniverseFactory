import importlib.util
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path('src/movie_factory/adapters/blender').resolve()))

spec=importlib.util.spec_from_file_location('costume',Path('src/movie_factory/adapters/blender/costume_refinement.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_face_exactly_untouched():
    for x in (-1,-.3,0,.5,1):
        for y in (-1,-.5,0,.8):
            for z in (-.86,-.8,0,1.5):
                for variant in range(16,37):assert m.neck_point(x,y,z,variant)==(x,y,z)

def test_neck_finite_and_bounded():
    for i in range(100):
        a=i*math.pi*2/100
        for z in (-.9,-1,-1.3,-1.7,-1.9,-2.3):
            for variant in range(16,37):
                p=m.neck_point(.8*math.sin(a),.22+.7*math.cos(a),z,variant)
                assert all(math.isfinite(v) for v in p)
                assert abs(p[0])<1.8 and abs(p[1])<1.1 and p[2]==z

def test_shawl_modest_bounded_continuous():
    for i in range(81):
        a=-1.9+3.8*i/80
        points=[m.shawl_point(a,j/56) for j in range(57)]
        assert all(-5.6<p[2]<-1.2 and abs(p[0])<2.2 and abs(p[1])<1.2 for p in points)
        assert all(math.dist(x,y)<.15 for x,y in zip(points,points[1:]))

def test_body_proportion_leaves_face_and_is_monotone():
    for z in (-.86,0,1):assert m.body_z(z)==z
    values=[m.body_z(-3+i*.01) for i in range(301)]
    assert all(a<b for a,b in zip(values,values[1:]))
    assert abs(m.body_z(-3)+2.77)<1e-8

def test_reference_neck_taper_is_not_face_slimming():
    # Only authorized neck section narrows; the protected face plane is exact.
    assert m.neck_point(.7,.22,-1.3,23)[0]<m.neck_point(.7,.22,-1.3,16)[0]
    assert m.neck_point(.7,.22,-.86,23)==(.7,.22,-.86)

def test_strap_envelope_does_not_propagate_fold_forever():
    values=[0,0,-1,0,0,0,0,0]
    assert m.support_envelope(values,radius=1)==[0,-1,-1,-1,0,0,0,0]
    assert values==[0,0,-1,0,0,0,0,0]

def test_shorter_neck_preserves_face_and_order():
    for variant in (29,30,31,32,33,34,35,36):
        for z in (-.86,-.5,0,1.5):assert m.body_z(z,variant)==z
        values=[m.body_z(-6+i*.002,variant) for i in range(3751)]
        assert all(a<b for a,b in zip(values,values[1:]))
        assert abs(m.body_z(-2,variant)-m.body_z(-2,28)-.17)<1e-8
        assert m.body_z(-1,variant)<-.86

def test_tension_profile_never_sinks_or_changes_endpoints():
    values=[0,0,-.3,0,.1,0,-.1,0,0]
    result=m.tension_profile(values)
    assert result[0]==values[0] and result[-1]==values[-1]
    assert all(a<=b for a,b in zip(result,values))
    assert all(min(values)<=x<=max(values) for x in result)
    assert values==[0,0,-.3,0,.1,0,-.1,0,0]
    assert m.tension_profile([1,1,1])==[1,1,1]
