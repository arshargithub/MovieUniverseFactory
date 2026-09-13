"""Load the bounded validator with fake bpy; malformed jobs cannot reach Blender."""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

@pytest.fixture
def module(monkeypatch):
 monkeypatch.setitem(sys.modules,'bpy',SimpleNamespace())
 monkeypatch.setitem(sys.modules,'mathutils',SimpleNamespace(Vector=None))
 path=Path('src/movie_factory/adapters/blender/demo_asset.py')
 spec=importlib.util.spec_from_file_location('test_demo_asset',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

@pytest.mark.parametrize('change',[{'mode':'execute_python'},{'python':'print(1)'},{'asset_path':'/tmp/other.blend'},{'asset_sha256':'0'*64},{'output_dir':'/tmp/out'},{'frame':9999}])
def test_reject_before_bpy(module,change,tmp_path):
 from movie_factory.packages import file_digest
 p=Path('.runtime/assets/demonstrator-01/Knight_0.blend').resolve()
 job={'mode':'demo_asset_inspect','asset_path':str(p),'asset_sha256':file_digest(p),'output_dir':str(Path('runs/demonstrator-01/test').resolve()),'profile':{}}
 job.update(change)
 with pytest.raises(ValueError):module.inspect_asset(None,tmp_path,job)
