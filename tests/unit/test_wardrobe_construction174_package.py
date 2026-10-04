import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
spec = importlib.util.spec_from_file_location('package_construction174',ROOT/'scripts/package_wardrobe_construction174.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def test_source_paths_are_unique_scoped_python_files():
    paths = module.source_paths()
    assert len(paths)==len(set(paths))
    assert all(p.suffix=='.py' and ROOT in p.parents for p in paths)
    assert ROOT/'scripts/wardrobe_construction174.py' in paths
    assert all('.runtime' not in str(p.relative_to(ROOT)) and '.env' not in p.name for p in paths)


def test_no_binding_overwrite_or_after_selected_dispatch(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'OUT',tmp_path)
    (tmp_path/'source-binding.json').write_text('{}')
    with pytest.raises(ValueError,match='Bind once'): module.bind()


def test_known_blocker_cannot_be_packaged(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'OUT',tmp_path)
    (tmp_path/'visual-review.json').write_text(json.dumps({'candidate':'wardrobe174-seal01',
        'criteria':[],'known_structural_blockers':['shoulder tabs']}))
    with pytest.raises(ValueError,match='Known blockers'): module.package()
