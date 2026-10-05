import importlib.util
from pathlib import Path
import numpy as np
import pytest

path=Path(__file__).resolve().parents[2]/'scripts/wardrobe_shawl180.py'
spec=importlib.util.spec_from_file_location('shawl180',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[{}, {'operation':'code'}, {'operation':'masscontrol01','path':'/tmp'}, 'masscontrol01'])
def test_no_untrusted_operation_payload(job):
    with pytest.raises(ValueError): module.validate(job)

def test_stretch_metric_detects_undeformed_and_doubled_sheet():
    p=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0]],dtype=float)
    r=module.measures(p,[[0,1,2,3]],{1:p,2:p*2},.5)
    assert r['dressed_area_m2']==pytest.approx(.25)
    assert r['edge_stretch']['1']['max']==pytest.approx(1)
    assert r['edge_stretch']['2']['min']==pytest.approx(2)
