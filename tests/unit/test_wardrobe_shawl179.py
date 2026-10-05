"""Pure construction/operation admission; no native or paid calls."""
import importlib.util
import math
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[2]/'scripts/wardrobe_shawl179.py'
spec=importlib.util.spec_from_file_location('shawl179',SCRIPT)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

@pytest.mark.parametrize('u,v',[(0,0),(.22,.5),(.45,1),(.65,.5),(1,0)])
def test_head_cut_is_finite(u,v):
    assert all(math.isfinite(x) for x in module.head_point(u,v))

def test_single_course_not_double():
    assert module.wrap_description(1,.5)[0]==pytest.approx(2*math.pi)

def test_fixed_periodic_topology():
    assert module.COUNT==3287
    assert module.WRAP_ROWS==96

def test_lateral_cloth_reaches_shoulder_instead_of_rear_plane():
    middle=module.head_point(.7,.5)
    side=module.head_point(.7,0)
    assert middle[1]>1.2 and side[1]<.3

@pytest.mark.parametrize('job',[{}, {'operation':'arbitrary'}, {'operation':'initial01','code':'x'},'x'])
def test_rejects_unstructured_payload(job):
    with pytest.raises(ValueError): module.validate(job)

def test_wrap_coordinates_bounded():
    with pytest.raises(ValueError): module.wrap_description(1.1,.5)
