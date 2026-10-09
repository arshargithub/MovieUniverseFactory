"""Source-bound operations reject arbitrary caller code and paths."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import entrance196

@pytest.mark.parametrize('job',[{}, {'operation':'build'}, {'operation':'inspect01','code':'bad'}, {'operation':'inspect01','source':'other'}])
def test_closed_operation(job):
    with pytest.raises(ValueError):entrance196.validate(job)

def test_offsets_are_delayed_bounded_and_not_random():
    import numpy as np
    from entrance196_build import head_offsets
    p=np.sin(np.arange(144)*.57);o=head_offsets(p)
    assert o.shape==(144,2)
    assert abs(o).max()<=1.6
    assert np.allclose(o[1:,0],p[:-1]*1.6)
    assert np.allclose(o[2:,1],p[:-2]*1.4)
    with pytest.raises(ValueError):head_offsets([float('nan')]*144)

def test_ballistic_launch_fall_and_floor():
    import numpy as np
    from entrance196_build import ballistic
    o=np.array([0,0,-20.8]);v=np.array([4,8,12])
    assert np.allclose(ballistic(o,v,0,.1),o)
    assert ballistic(o,v,.12,.1)[2]>o[2]+.5
    assert ballistic(o,v,1,.1)[2]>=o[2]

def test_build_rejects_runtime_code():
    from entrance196_build import validate
    with pytest.raises(ValueError):validate({'operation':'build02','code':'print(1)'})

def test_render_rejects_runtime_paths():
    from entrance196_render import validate
    with pytest.raises(ValueError):validate({'operation':'controls03','source':'bad'})

def test_final_render_contract_has_exact_common_clock():
    from entrance196_render import OPERATIONS,FULL_CONTROLS
    source,frames,w,h,samples=OPERATIONS['motion38']
    assert source=='entrance196-integrate36'
    assert frames==tuple(range(217,361))
    assert (w,h,samples)==(432,768,12)
    assert FULL_CONTROLS['motion38']=='controls37'
    assert OPERATIONS['controls37'][0]==source
    assert OPERATIONS['verify39'][0]==source
    assert OPERATIONS['verify39'][1]==(265,295,360)

def test_ballistic_settles_and_remains_in_ground_coordinates():
    import numpy as np
    from entrance196_build import ballistic
    origin=np.array([1.,-25.,-20.7]);velocity=np.array([4.,12.,15.])
    q=np.array([ballistic(origin,velocity,t,.1) for t in np.linspace(0,1.5,91)])
    assert np.isfinite(q).all()
    assert q[:,2].min()>=origin[2]
    assert q[-1,2]==origin[2]
    assert np.all(np.diff(q[:,1])>0)
    # Translating world geography does not change the local ballistic arc.
    shift=np.array([0.,57.,0.])
    assert np.allclose(ballistic(origin+shift,velocity,.42,.1),ballistic(origin,velocity,.42,.1)+shift)
