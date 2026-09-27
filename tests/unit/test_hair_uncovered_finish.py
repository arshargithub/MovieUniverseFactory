import importlib.util
import math
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('uncovered_finish', Path('src/movie_factory/adapters/blender/hair_uncovered_finish.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

@pytest.mark.parametrize('job', [None, {}, {'operation':'exec','candidate':1}, {'operation':'preview','candidate':True}, {'operation':'preview','candidate':0}, {'operation':'preview','candidate':99}, {'operation':'preview','candidate':1,'code':'pass'}])
def test_rejects_arbitrary_jobs(job):
    with pytest.raises(ValueError):
        m.validate(job)

@pytest.mark.parametrize('candidate', list(range(1,21)))
def test_shape_is_continuous_bounded_and_finite(candidate):
    for x in (-1.2, -.5, 0, .5, 1.2):
        for y in (-.8, 0, .8):
            for z in (-2., -.5, .5, 1.5):
                p = (x,y,z)
                q = m.shape(p,candidate)
                assert all(math.isfinite(v) for v in q)
                # Variants5+ add .14 units of approved lower-hair breadth.
                assert max(abs(a-b) for a,b in zip(p,q)) < (.45 if candidate >= 5 else .30)
                near = m.shape((x+.00001,y,z),candidate)
                assert max(abs(a-b) for a,b in zip(q,near)) < .001

def test_root_center_stays_on_approved_forehead():
    p=(0.,-.7,1.)
    assert m.shape(p,1)==p

def test_crown_keeps_roots_and_lower_lengths_fixed():
    for candidate in (13,14,15,16,17,18):
        for p in ((0,-.85,1),(.8,-.3,1.2),(.9,.3,.4)):
            if candidate==13 or p[1]<=-.82:
                assert all(abs(v)<1e-9 for v in m.crown_offset(p,p,0,candidate))
            assert m.crown_offset(p,p,.5,candidate)==(0.,0.,0.)
        assert m.crown_offset((.8,0,.4),(0,-.6,1.3),.15,candidate)==(0.,0.,0.)

def test_crown_lift_is_finite_bounded_and_unequal():
    a=m.crown_offset((-.4,-.4,1.3),(0,-.57,1.3),.16,13)
    b=m.crown_offset((.4,-.4,1.3),(0,-.57,1.3),.16,13)
    assert .1<a[2]<.4 and .1<b[2]<.4 and abs(a[2]-b[2])>.03
    assert all(math.isfinite(v) and abs(v)<.4 for v in a+b)

@pytest.mark.parametrize('candidate',[16,17,18])
def test_connected_crest_continuity_and_bound(candidate):
    for x in (-1.,-.5,0.,.5,1.):
        for y in (-1.,-.6,0.,.5):
            for t in (0.,.1,.3,.449,.45):
                p=(x,y,1.3);root=(x,y,1.2)
                a=m.crown_offset(p,root,t,candidate)
                b=m.crown_offset((x+.00001,y,1.3),root,t,candidate)
                assert all(math.isfinite(v) and abs(v)<.23 for v in a)
                assert max(abs(v-w) for v,w in zip(a,b))<.001

def test_complete_trajectory_groups_deterministic():
    import numpy as np
    rng=np.random.default_rng(7)
    rows=rng.normal(size=(18,64,3))
    original=rows.copy()
    a=m.lock_groups(rows,5);b=m.lock_groups(rows,5)
    assert np.array_equal(a,b) and np.array_equal(rows,original)
    assert len(set(a))==5 and len(a)==len(rows)

@pytest.mark.parametrize('candidate',[19,20])
@pytest.mark.parametrize('operation',['seal','verify'])
def test_rejected_diagnostics_cannot_be_promoted(candidate,operation):
    with pytest.raises(ValueError,match='cannot be promoted'):
        m.validate({'operation':operation,'candidate':candidate})

@pytest.fixture
def pinned(tmp_path,monkeypatch):
    from types import SimpleNamespace
    source=tmp_path/'source.blend';source.write_bytes(b'known native')
    ref=tmp_path/'front.png';ref.write_bytes(b'approved reference')
    monkeypatch.setattr(m,'SOURCE',source);monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source))
    monkeypatch.setattr(m,'BASE',tmp_path);monkeypatch.setattr(m,'REF',tmp_path)
    monkeypatch.setattr(m,'PINS',{ref.name:m.digest(ref)})
    monkeypatch.setattr(m,'ORIGINAL_PINS',{})
    monkeypatch.setattr(m.shutil,'disk_usage',lambda p:SimpleNamespace(free=10_000_000_000))
    return tmp_path

def test_fresh_output_validated(pinned):
    assert m.validate({'operation':'preview','candidate':7})==pinned/'finalhair142-preview-07'

@pytest.mark.parametrize('name',['source.blend','front.png'])
def test_changed_inputs_rejected(pinned,name):
    (pinned/name).write_bytes(b'changed')
    with pytest.raises(ValueError):m.validate({'operation':'preview','candidate':7})

@pytest.mark.parametrize('symlink',[False,True])
def test_existing_outputs_preserved(pinned,symlink):
    out=pinned/'finalhair142-preview-07'
    if symlink:out.symlink_to(pinned/'missing')
    else:out.mkdir()
    with pytest.raises(ValueError):m.validate({'operation':'preview','candidate':7})

def test_requires_preview_before_seal(pinned):
    with pytest.raises(ValueError):m.validate({'operation':'seal','candidate':7})

def test_low_disk_rejected(pinned,monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(m.shutil,'disk_usage',lambda p:SimpleNamespace(free=1))
    with pytest.raises(ValueError):m.validate({'operation':'preview','candidate':7})

@pytest.mark.parametrize('bad',['handler','candidate','protection','symlink'])
def test_seal_prerequisites_bound(pinned,bad):
    import json
    folder=pinned/'finalhair142-preview-07'
    target=pinned/'actual';target.mkdir()
    if bad=='symlink':folder.symlink_to(target,target_is_directory=True)
    else:folder.mkdir()
    record={'candidate':8 if bad=='candidate' else 7,'protected_exact':bad!='protection',
            'handler_sha256':'bad' if bad=='handler' else m.digest(Path(m.__file__))}
    (folder/'result.json').write_text(json.dumps(record))
    with pytest.raises(ValueError):m.validate({'operation':'seal','candidate':7})

def test_seal_correct_binding(pinned):
    import json
    folder=pinned/'finalhair142-preview-07';folder.mkdir()
    (folder/'result.json').write_text(json.dumps({'candidate':7,'protected_exact':True,'handler_sha256':m.digest(Path(m.__file__))}))
    assert m.validate({'operation':'seal','candidate':7})==pinned/'finalhair142-seal-07'
