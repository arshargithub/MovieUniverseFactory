import importlib.util
import math
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('sikh272',Path(__file__).parents[1]/'scripts/sikh272_construct.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('j',[None,{},dict(operation='exec',attempt=1),dict(operation='construct',attempt=True),dict(operation='construct',attempt=31),dict(operation='construct',attempt=1,path='/tmp/x')])
def test_closed_dispatch(j):
    with pytest.raises(ValueError):m.validate(j)

def test_source():
    assert m.sha(m.ROOT/m.SOURCE)==m.SOURCE_SHA
    assert m.validate(dict(operation='construct',attempt=1)).name=='candidate-01'

def test_surface_bounds():
    for family,count in ((0,6),(1,3)):
        for layer in range(count):
            for i in range(100):
                for u in (0,.5,1):
                    p=m.wrap_surface(-math.pi+math.tau*i/100,u,layer,family)
                    assert all(math.isfinite(v) for v in p)
                    assert abs(p[0])<.13 and abs(p[1])<.16 and m.EYE-.10<p[2]<m.EYE+.20

def test_continuous_fold_surface():
    for j in range(101):
        v=j/100
        a=m.folded_surface(-math.pi,v);b=m.folded_surface(math.pi,v)
        assert max(abs(x-y) for x,y in zip(a,b))<1e-12
        for i in range(100):
            p=m.folded_surface(-math.pi+math.tau*i/100,v)
            assert all(math.isfinite(c) for c in p)
            assert abs(p[0])<.12 and abs(p[1])<.14 and m.EYE-.05<p[2]<m.EYE+.17
