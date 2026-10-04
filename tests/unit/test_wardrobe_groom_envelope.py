import importlib.util
import sys
from pathlib import Path
import math
import pytest

directory=Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender'
sys.path.insert(0,str(directory))
spec=importlib.util.spec_from_file_location('wardrobe_groom_envelope',directory/'wardrobe_groom_envelope.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_local_contour_does_not_bridge_remote_rear_locks():
    points=[]
    for j in range(101):
        z=j/100;rear=1 if z<.25 else .3
        for i in range(32):
            a=math.tau*i/32;points.append((.5*math.cos(a),rear*math.sin(a),z))
    vertices,faces=module.envelope(points,levels=20,segments=32)
    assert len(vertices)==642 and len(faces)==672
    upper=[p for p in vertices if .55<p[2]<.85]
    assert max(p[1] for p in upper)<.35
    assert max(p[1] for p in vertices)>.9

@pytest.mark.parametrize('points',[[],[(0,0,0)]*10,[(float('nan'),0,1)]*10])
def test_invalid_groom_support_rejected(points):
    with pytest.raises(ValueError):module.envelope(points)
