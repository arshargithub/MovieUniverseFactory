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
