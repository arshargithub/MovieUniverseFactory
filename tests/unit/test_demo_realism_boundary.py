import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

@pytest.mark.parametrize('change',[{'mode':'python'},{'profile':{'code':'print(1)'}},{'python':'print(1)'},{'output_dir':'/tmp/out'}])
def test_realism_rejects_outside_fixed_boundary(monkeypatch,change):
    monkeypatch.setitem(sys.modules,'bpy',SimpleNamespace())
    monkeypatch.setitem(sys.modules,'mathutils',SimpleNamespace(Vector=None))
    spec=importlib.util.spec_from_file_location('test_realism',Path('src/movie_factory/adapters/blender/demo_realism.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    job={'mode':'demo_realism_probe','output_dir':'runs/demonstrator-01/not-created','profile':{}};job.update(change)
    with pytest.raises(ValueError):m.build(None,job['output_dir'],job,None)
