import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('sikh270',Path(__file__).parents[1]/'scripts/sikh270_guides.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{},dict(operation='exec',attempt=1),dict(operation='coarse',attempt=True),dict(operation='detail',attempt=31),dict(operation='coarse',attempt=1,code='bad')])
def test_closed_operations(job):
    with pytest.raises(ValueError):m.validate(job)

def test_ordered_guides():
    for j in range(1001):
        theta=-math.pi+math.tau*j/1000
        values=[m.interpolate(v,theta) for _,v in m.FOLDS]
        assert all(b>a for a,b in zip(values,values[1:]))
        for course in range(len(values)-1):
            for f in (0,.25,.5,.75,1):
                p=m.crown_point(theta,course,f)
                assert all(math.isfinite(c) for c in p)
                assert abs(p[0])<.14 and abs(p[1])<.17 and m.EYE-.07<p[2]<m.EYE+.20

def test_protected_source():
    assert m.sha(m.ROOT/m.SOURCE)==m.SOURCE_SHA
    assert m.validate(dict(operation='coarse',attempt=1)).name=='candidate-01'

def test_cloth_dispatch_closed():
    spec=importlib.util.spec_from_file_location('sikh270cloth',Path(__file__).parents[1]/'scripts/sikh270_cloth.py')
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    for job in (None,{},dict(operation='exec'),dict(operation='fit',path='/tmp/arbitrary')):
        with pytest.raises(ValueError):c.validate(job)
    assert c.validate(dict(operation='fit')).name=='candidate-12'
    assert c.validate(dict(operation='assemble')).name=='candidate-13'

def test_crown_lap_dispatch_and_bounds():
    spec=importlib.util.spec_from_file_location('sikh270crown',Path(__file__).parents[1]/'scripts/sikh270_crown.py')
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    for job in (None,{},dict(operation='exec'),dict(operation='build',code='bad')):
        with pytest.raises(ValueError):c.validate(job)
    c.validate(dict(operation='build'))
    for j in range(65):
        for k in range(9):
            for f in (-.025,0,.5,1,1.025):
                p=c.point(-math.pi+math.tau*j/64,k,f)
                assert all(math.isfinite(v) for v in p)
                assert abs(p[0])<.14 and abs(p[1])<.17 and m.EYE-.07<p[2]<m.EYE+.20
