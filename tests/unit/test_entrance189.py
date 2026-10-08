"""Admission tests for fixed, source-bound production diagnostics."""
import importlib.util
from pathlib import Path
import pytest

def module():
    path=Path(__file__).resolve().parents[2]/'scripts/entrance189.py'
    spec=importlib.util.spec_from_file_location('entrance189',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

@pytest.mark.parametrize('job',[{}, {'operation':'unknown'},
    {'operation':'diagnose01','code':'print(1)'}, {'operation':'diagnose01','path':'/tmp/other'}])
def test_reject_unreviewed_operations(job):
    with pytest.raises(ValueError,match='Fixed189'):module().validate(job)

def test_mdd_roundtrip_and_preservation(tmp_path):
    module()
    import entrance189_groom as groom
    import numpy as np
    a=np.arange(90,dtype=np.float32).reshape(5,6,3)/13
    p=tmp_path/'test.mdd'
    groom.write_mdd(p,5,6,iter(a))
    np.testing.assert_array_equal(groom.read_mdd(p),a)
    with pytest.raises(ValueError,match='Preserve'):groom.write_mdd(p,5,6,iter(a))

def test_scoped_face_controls():
    module()
    import entrance189_performance as performance
    import math
    values=[performance.facial_values(f) for f in range(217,361)]
    assert all(math.isfinite(v) and 0<=v<=1 for row in values for v in row.values())
    assert max(row['jawOpen'] for row in values)<.05
    assert max(row['browDownLeft'] for row in values)<.1

def test_wake_widens():
    module()
    import entrance189_world as world
    assert world.plume_width(0)<world.plume_width(50)<world.plume_width(200)
