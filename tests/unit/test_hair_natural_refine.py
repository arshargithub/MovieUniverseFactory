import importlib.util
from pathlib import Path
import pytest
import json
import sys
import types
spec=importlib.util.spec_from_file_location('natural',Path('src/movie_factory/adapters/blender/hair_natural_refine.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1},{'operation':'preview','candidate':True},{'operation':'preview','candidate':-1},{'operation':'preview','candidate':9},{'operation':'preview','candidate':1,'code':'pass'}])
def test_rejects_unsupported_jobs(job):
    with pytest.raises(ValueError):m.validate(job)

def test_ear_relief_is_local_bounded_and_bilateral():
    for p in ((.3,-.8,.2),(.8,-.2,.2),(.8,0,.6),(.8,0,-.2),(0,0,0)):
        assert m.ear_delta(p)==(0.,0.,0.)
    for y in (-.1,-.05,0,.05,.1):
        for z in (0,.1,.2,.3):
            a=m.ear_delta((.83,y,z));b=m.ear_delta((-.83,y,z))
            assert abs(a[0])<.09 and a[0]==-b[0] and a[1:]==(0.,0.)

def test_inner_bowl_is_included_not_only_outer_rim():
    assert m.ear_delta((.71,-.025,.125))[0]<-.03

@pytest.fixture
def inputs(tmp_path,monkeypatch):
    source=tmp_path/'source.blend';source.write_bytes(b'source')
    donor=tmp_path/'donor.blend';donor.write_bytes(b'donor')
    for k,v in {'SOURCE':source,'SOURCE_SHA':m.digest(source),'DONOR':donor,'DONOR_SHA':m.digest(donor),'BASE':tmp_path}.items():monkeypatch.setattr(m,k,v)
    monkeypatch.setitem(sys.modules,'hair_uncovered_finish',types.SimpleNamespace(PINS={},ORIGINAL_PINS={},REF=tmp_path,ORIGINAL_REF=tmp_path))
    monkeypatch.setattr(m.shutil,'disk_usage',lambda p:types.SimpleNamespace(free=10_000_000_000))
    return tmp_path

def test_fresh_preview(inputs):
    assert m.validate({'operation':'preview','candidate':4})==inputs/'natural147-preview-04'

def test_forehead_output_is_fresh_namespace(inputs):
    assert m.validate({'operation':'preview','candidate':7})==inputs/'natural149-preview-07'

def test_forehead_lift_pins_roots_crown_rear_and_temples():
    assert m.forehead_delta((0,-.9,.85),0)==(0.,0.,0.)
    for p in ((0,-.9,1.3),(0,.4,.85),(.76,-.9,.85),(0,-.9,.48)):
        assert m.forehead_delta(p,.5)==(0.,0.,0.)
    assert m.forehead_delta((0,-.9,.85),.5)==(0.,0.,.075)
    for x in (-.7,-.5,0,.5,.7):
        for z in (.5,.7,.9,1.1,1.3):
            delta=m.forehead_delta((x,-.9,z),.1)
            assert delta[:2]==(0.,0.) and 0<=delta[2]<=.075

def test_gentler_forehead_variant():
    assert m.forehead_delta((0,-.9,.85),0,8)==(0.,0.,0.)
    assert m.forehead_delta((0,-.9,.85),.5,8)==(0.,0.,.050)
    assert m.forehead_delta((0,-.9,.85),.1,8)[2]<m.forehead_delta((0,-.9,.85),.1,7)[2]

@pytest.mark.parametrize('candidate',[5,6])
def test_accent_output_preserves_prior_namespace(inputs,candidate):
    assert m.validate({'operation':'preview','candidate':candidate})==inputs/f'natural148-preview-{candidate:02}'

def test_accent_seal_needs_current_handler(inputs):
    folder=inputs/'natural148-preview-06';folder.mkdir()
    (folder/'result.json').write_text(json.dumps({'protected_exact':True,'handler_sha256':'old'}))
    with pytest.raises(ValueError,match='Stale'):m.validate({'operation':'seal','candidate':6})

def test_source_tamper(inputs):
    m.SOURCE.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'):m.validate({'operation':'preview','candidate':4})

def test_existing_output_rejected(inputs):
    (inputs/'natural147-preview-04').mkdir()
    with pytest.raises(ValueError,match='Fresh'):m.validate({'operation':'preview','candidate':4})

def test_low_disk(inputs,monkeypatch):
    monkeypatch.setattr(m.shutil,'disk_usage',lambda p:types.SimpleNamespace(free=100))
    with pytest.raises(ValueError,match='Disk'):m.validate({'operation':'preview','candidate':4})

def test_stale_seal_prerequisite(inputs):
    folder=inputs/'natural147-preview-04';folder.mkdir()
    (folder/'result.json').write_text(json.dumps({'protected_exact':True,'handler_sha256':'old'}))
    with pytest.raises(ValueError,match='Stale'):m.validate({'operation':'seal','candidate':4})

def test_linked_output_rejected(inputs):
    (inputs/'natural147-preview-04').symlink_to(inputs/'missing')
    with pytest.raises(ValueError,match='Fresh'):m.validate({'operation':'preview','candidate':4})

def test_source_link_rejected(inputs):
    m.SOURCE.unlink();m.SOURCE.symlink_to(m.DONOR)
    with pytest.raises(ValueError,match='Pinned'):m.validate({'operation':'preview','candidate':4})
