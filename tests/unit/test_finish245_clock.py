import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from finish245_clock import clocks
from finish237_clock import clocks as prior,PERIOD

def test_full_rate_gait_and_world():
    a=np.array([clocks('opening',i) for i in range(234)])
    assert np.allclose(np.diff(a[:,2]),1)
    assert np.allclose(np.mod(np.diff(a[:,0])-1,PERIOD),0,atol=1e-10) or np.allclose(np.mod(np.diff(a[:,0])-1+1e-8,PERIOD),1e-8,atol=1e-7)
    assert a[-1,0]==360
    assert np.all(np.diff(a[:,1])>=0)

def test_route_exact_and_hard_cut():
    assert all(clocks('route',i)==prior('route',i) for i in range(306))
    assert clocks('route',47)[1]==390
    assert clocks('route',48)[1]==391
