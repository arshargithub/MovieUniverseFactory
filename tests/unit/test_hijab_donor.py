import importlib.util
import json
from pathlib import Path
import struct
import math
import pytest

spec = importlib.util.spec_from_file_location('hijab', Path('src/movie_factory/adapters/blender/hijab_donor.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


@pytest.mark.parametrize('job', [None, {}, {'operation':'exec','stage':'audit'},
    {'operation':'hijab_donor','stage':'../audit'},
    {'operation':'hijab_donor','stage':'audit','code':'anything'}])
def test_deny_job(job):
    with pytest.raises(ValueError): m.validate(job)


def glb(doc):
    data = json.dumps(doc).encode()
    return struct.pack('<4sIIII', b'glTF', 2, 20+len(data), len(data), 0x4E4F534A)+data


def test_glb_limits():
    assert m.inspect_glb(glb({'meshes':[{}]}))['meshes'] == [{}]
    for doc in ({'meshes':[{}], 'images':[{'uri':'file:///etc/passwd'}]},
                {'meshes':[{}], 'buffers':[{'uri':'https://example.com'}]},
                {'meshes':[{}], 'extensionsUsed':['unknown']},
                {'meshes':[{}], 'accessors':[{'count':200001}]}, {'meshes':[]}):
        with pytest.raises(ValueError): m.inspect_glb(glb(doc))
    with pytest.raises(ValueError): m.inspect_glb(b'invalid')


def test_changed_source(tmp_path, monkeypatch):
    source = tmp_path/'donor.glb'; source.write_bytes(b'changed')
    monkeypatch.setattr(m, 'DONOR', source)
    with pytest.raises(ValueError, match='Source changed'):
        m.validate({'operation':'hijab_donor','stage':'audit'})


def test_fit_mapping():
    assert m.fit_point((0, 0, 2.491938))[2] == pytest.approx(1.5427442)
    for x in (-2., 0., 2.):
        for y in (-1.7, 0., 1.9):
            for z in (-3.6, 0., 2.5):
                assert all(math.isfinite(v) for v in m.fit_point((x,y,z)))
    assert m.fit_point((-1, 0, 1))[0] == -m.fit_point((1,0,1))[0]


def test_second_fit_preserves_crown_height_and_lowers_wrap():
    assert m.fit_point((0,0,2.49),2)[2] == m.fit_point((0,0,2.49),1)[2]
    assert m.fit_point((0,-1,0),2)[2] < m.fit_point((0,-1,0),1)[2]
    assert m.fit_point((1,0,1),2)[0] < m.fit_point((1,0,1),1)[0]
