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
    assert OPS['repeat20']==(360,)
    assert OPS['fixed05']==OPS['before06']
    with pytest.raises(ValueError):validate({'operation':'controls04','source':'bad'})

def test_pixel_exception_is_exact_and_stays_a_strict_failure(tmp_path,monkeypatch):
    import json,numpy as np
    from PIL import Image
    import entrance200_media as media
    monkeypatch.setattr(media,'BASE',tmp_path)
    full=tmp_path/'full';verify=tmp_path/'verify';repeat=tmp_path/'entrance200-repeat20'
    for p in (full,verify,repeat):p.mkdir()
    a=np.zeros((768,432,4),dtype=np.uint8);a[:,:,3]=255
    Image.fromarray(a).save(full/'frame-0360.png')
    a[116,97,:2]=2
    for p in (verify,repeat):Image.fromarray(a).save(p/'frame-0360.png')
    (repeat/'result.json').write_text(json.dumps({'source_sha256':'source'}))
    (repeat/'structural-parity.json').write_text(json.dumps({'status':'PASS'}))
    record={'status':'SCOPED_BACKGROUND_ROUNDING_EXCEPTION','source_sha256':'source',
            'full_frame_sha256':media.sha(full/'frame-0360.png'),
            'verify_frame_sha256':media.sha(verify/'frame-0360.png'),
            'repeat_sha256':media.sha(repeat/'frame-0360.png')}
    (verify/'pixel-review.json').write_text(json.dumps(record))
    assert media.reviewed_final_parity(full,verify,'source')['status'].startswith('STRICT_FAIL')
    a[117,97,:2]=2
    for p in (verify,repeat):Image.fromarray(a).save(p/'frame-0360.png')
    record.update(verify_frame_sha256=media.sha(verify/'frame-0360.png'),repeat_sha256=media.sha(repeat/'frame-0360.png'))
    (verify/'pixel-review.json').write_text(json.dumps(record))
    with pytest.raises(ValueError,match='specifically inspected'):media.reviewed_final_parity(full,verify,'source')
