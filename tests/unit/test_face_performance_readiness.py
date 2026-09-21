import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('readiness', Path('src/movie_factory/adapters/blender/face_performance_readiness.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@pytest.mark.parametrize('job', [None, {}, {'operation':'exec','candidate':1},
    {'operation':'diagnose','candidate':True}, {'operation':'diagnose','candidate':2},
    {'operation':'diagnose','candidate':1,'code':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError): m.validate(job)


def test_source_output_guards(tmp_path, monkeypatch):
    source=tmp_path/'source.blend'; source.write_bytes(b'accepted')
    monkeypatch.setattr(m,'SOURCE',source); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source))
    monkeypatch.setattr(m,'BASE',tmp_path)
    job={'operation':'diagnose','candidate':1}
    out=m.validate(job); out.mkdir()
    with pytest.raises(ValueError,match='Existing'): m.validate(job)
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='source'): m.validate(job)


def test_binding_rejects_ambiguous_and_absent():
    a=((.1,.2),);b=((.2,.3),)
    assert m.binding([a,b,b],[a,b,(),((.9,.9),)])==[0,None,None,None]
