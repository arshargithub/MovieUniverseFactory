import importlib.util
from pathlib import Path
import math
import pytest
s=importlib.util.spec_from_file_location('renew',Path('src/movie_factory/adapters/blender/dressing_renewal.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','variant':1},{'operation':'dressing_renewal','variant':True},{'operation':'dressing_renewal','variant':4}])
def test_reject(job):
    with pytest.raises(ValueError):m.validate(job)

def test_hood_clearance_and_finite():
    assert m.hood_point(0,0)[2]>1.5
    assert m.hood_point(math.pi/2,0)[0]>1.1
    for i in range(101):
        for j in range(31):assert all(math.isfinite(v) for v in m.hood_point(-2.47+4.94*i/100,j/30))

def test_wrap_periodic_and_below_face():
    for v in (0,.5,1):assert m.wrap_point(0,v)==pytest.approx(m.wrap_point(2*math.pi,v))
    assert max(m.wrap_point(i*.1,j*.1)[2] for i in range(63) for j in range(11))<-.9

def test_shoulder_variant_periodic():
    for v in (0,.5,1):assert m.wrap_point(0,v,2)==pytest.approx(m.wrap_point(2*math.pi,v,2))
    assert m.wrap_point(math.pi/2,1,2)[2]>m.wrap_point(0,1,2)[2]
