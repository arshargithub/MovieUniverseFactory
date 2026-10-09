"""Closed dispatch and correction math; never an aesthetic acceptance test."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import entrance200_inspect as inspect

@pytest.mark.parametrize('job',[{}, {'operation':'other'}, {'operation':'inspect01','code':'bad'}, {'operation':'inspect01','source':'bad'}])
def test_closed_inspection(job):
    with pytest.raises(ValueError):inspect.validate(job)

def test_source_pin():
    assert len(inspect.SOURCE_SHA)==64
    assert inspect.SOURCE.name=='scene.blend'

def test_closed_controls():
    from entrance200_controls import validate
    with pytest.raises(ValueError):validate({'operation':'controls02','source':'bad'})

def test_response_finite_and_lagged():
    import numpy as np
    from entrance200_build import response_plan,validate
    names=['chest','MF185_neck','MF185_head'];e=np.zeros((144,3,3));e[:,:,0]=np.sin(np.arange(144)[:,None]*.6)*.06
    out=response_plan(e,names)
    assert out.shape==(144,2) and np.isfinite(out).all()
    assert abs(out).max()<.25 and np.ptp(out[:,0])>.01
    with pytest.raises(ValueError):response_plan(e[:10],names)
    with pytest.raises(ValueError):validate({'operation':'candidate03','code':'bad'})

def test_render_clock_and_closed_schema():
    from entrance200_render import OPS,validate
    assert OPS['motion07']==tuple(range(217,361))
    assert OPS['motion18']==tuple(range(217,361))
    assert {343,350}.issubset(OPS['verify19'])
    assert OPS['fixed05']==OPS['before06']
    with pytest.raises(ValueError):validate({'operation':'controls04','source':'bad'})
