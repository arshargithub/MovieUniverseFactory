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

@pytest.mark.parametrize('candidate', list(range(1,13)))
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
