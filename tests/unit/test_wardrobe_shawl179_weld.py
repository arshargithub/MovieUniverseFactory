import importlib.util
from pathlib import Path
import numpy as np
import pytest
source=Path(__file__).resolve().parents[2]/'scripts/wardrobe_shawl179_weld.py'
spec=importlib.util.spec_from_file_location('weld179',source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_arc_sampling_preserves_outline_endpoints():
    points=np.array([[0,0,0],[.1,0,0],[.4,0,0],[1.,0,0]])
    sampled=module.regular_curve(points)
    assert np.allclose(sampled[:,0],np.linspace(0,1,4))
    assert np.allclose(sampled[[0,-1]],points[[0,-1]])

def test_collapsed_guide_rejected():
    with pytest.raises(ValueError):module.regular_curve(np.zeros((4,3)))

@pytest.mark.parametrize('job',[{},None,{'operation':'anything'},
    {'operation':'solve01','python':'anything'}, {'operation':'solve01','input':'/tmp/other'}])
def test_fixed_job_admission(job):
    with pytest.raises(ValueError):module.validate(job)
