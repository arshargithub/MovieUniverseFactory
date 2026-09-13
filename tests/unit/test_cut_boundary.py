"""Reject out-of-contract jobs before touching native assets."""
import importlib.util
from pathlib import Path
import sys,types
import pytest

@pytest.fixture
def module(monkeypatch):
 monkeypatch.setitem(sys.modules,'bpy',types.ModuleType('bpy'))
 mathutils=types.ModuleType('mathutils');mathutils.Vector=object;mathutils.Quaternion=object
 monkeypatch.setitem(sys.modules,'mathutils',mathutils)
 p=Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/demo_cut_world.py'
 spec=importlib.util.spec_from_file_location('cut_boundary_test',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m

@pytest.mark.parametrize('profile',[
 {'shot':'shot1','start':False,'end':1},
 {'shot':'shot1','start':0,'end':145},
 {'shot':'shot2','start':143,'end':145},
 {'shot':'shot4','start':575,'end':577},
 {'shot':'shot3','start':432,'end':432},
 {'shot':'shot1','start':0,'end':1,'python':'anything'},
 {'shot':'unbounded','start':0,'end':1},
])
def test_invalid_render_profile_rejected_before_native_read(module,profile):
 with pytest.raises(ValueError):module._render(None,'unused',profile,None)

def test_output_must_remain_in_run_root(module):
 with pytest.raises(ValueError):module._bounded('/tmp/unapproved-cut-output')
