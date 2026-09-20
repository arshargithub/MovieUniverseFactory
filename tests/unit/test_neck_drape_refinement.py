import importlib.util
from pathlib import Path
import math
import sys

sys.path.insert(0,str(Path('src/movie_factory/adapters/blender').resolve()))

spec=importlib.util.spec_from_file_location('neck_drape',Path('src/movie_factory/adapters/blender/neck_drape_refinement.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_bridge_endpoints_and_no_overshoot():
    for a,b in ((.5,.65),(.7,.55),(.6,.6)):
        for da,db in ((-2,3),(.4,.4),(-.2,-.1),(0,0)):
            values=[m.monotone_hermite(a,b,da,db,i/100,.59) for i in range(101)]
            assert values[0]==a and abs(values[-1]-b)<1e-12
            assert all(min(a,b)-1e-12<=v<=max(a,b)+1e-12 and math.isfinite(v) for v in values)
            assert all((y-x)*(b-a)>=-1e-12 for x,y in zip(values,values[1:]))

def test_veil_continuity_and_finite_extent():
    for variant in (34,35):
        for i in range(101):
            angle=-2+4*i/100;origin=(1.1*math.sin(angle),.22+.9*math.cos(angle),-.3)
            points=[m.veil_target(angle,j/64,origin,variant) for j in range(65)]
            assert points[0]==origin
            assert all(all(math.isfinite(v) for v in p) and abs(p[0])<2.3 and abs(p[1])<1.6 for p in points)
            assert all(a[2]>b[2] and math.dist(a,b)<.15 for a,b in zip(points,points[1:]))

def test_neck_sections_no_radius_steps_at_knots():
    sections=[(-.86,.56,.64),(-1.2,.54,.61),(-1.5,.56,.62),(-1.72,.75,.66),(-1.94,1.2,.7),(-2.3,1.75,.77)]
    for z,x,y in sections:assert math.dist(m.neck_section(z,sections),(x,y))<1e-10
    for z,_,_ in sections[1:-1]:
        epsilon=1e-6
        left=m.neck_section(z-epsilon,sections);middle=m.neck_section(z,sections);right=m.neck_section(z+epsilon,sections)
        for i in (0,1):assert abs((middle[i]-left[i])-(right[i]-middle[i]))/epsilon<.001
