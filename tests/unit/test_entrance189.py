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
    assert max(row['jawOpen'] for row in values)<.10
    assert max(row['browDownLeft'] for row in values)<.2
    assert values[312-217]['eyeBlinkLeft']==1.

def test_wake_widens():
    module()
    import entrance189_world as world
    assert world.plume_width(0)<world.plume_width(50)<world.plume_width(200)

def test_facial_shapes_are_independent_and_do_not_accumulate():
    module()
    import entrance189_face as face
    import numpy as np
    basis=np.ones((10,3),dtype=np.float32)
    original=basis.copy()
    for amount in (.01,.02,.04,.08):
        delta=np.full_like(basis,amount)
        result=face.independent_shape(basis,delta)
        np.testing.assert_allclose(result-basis,delta,atol=1e-7)
        np.testing.assert_array_equal(basis,original)
    for delta in (np.full_like(basis,float('nan')),np.ones_like(basis)):
        with pytest.raises(ValueError):face.independent_shape(basis,delta)

@pytest.mark.parametrize('job',[{}, {'operation':'decision-motion20','path':'other'}, {'operation':'exec'}])
def test_decision_camera_rejects_payload_expansion(job):
    module()
    import entrance189_decision as decision
    with pytest.raises(ValueError,match='Fixed'):decision.validate(job)


def test_edit_rejects_stale_review_and_changed_frames(tmp_path):
    module()
    import entrance189_edit as edit
    import hashlib
    import json
    video=tmp_path/'proof.mp4';video.write_bytes(b'fixture video')
    frame=tmp_path/'frame-0001.png';frame.write_bytes(b'fixture frame')
    source='a'*64
    (tmp_path/'result.json').write_text(json.dumps({'source_sha256':source}))
    (tmp_path/'media.json').write_text(json.dumps({'video_sha256':edit.digest(video),
        'frames':[{'name':frame.name,'sha256':hashlib.sha256(frame.read_bytes()).hexdigest()}]}))
    gate=tmp_path/'internal-review.json'
    gate.write_text(json.dumps({'status':'PROCEED_TO_EDIT','source_sha256':'b'*64}))
    with pytest.raises(ValueError,match='Source-bound'):edit.admit_review(tmp_path,video)
    gate.write_text(json.dumps({'status':'PROCEED_TO_EDIT','source_sha256':source}))
    edit.admit_review(tmp_path,video)
    frame.write_bytes(b'changed frame')
    with pytest.raises(ValueError,match='frame changed'):edit.admit_review(tmp_path,video)
