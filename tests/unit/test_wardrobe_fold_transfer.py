import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_fold_transfer',Path(__file__).resolve().parents[2]/'src/movie_factory/adapters/blender/wardrobe_fold_transfer.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_donor_missing_is_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'SOURCE',tmp_path/'absent.glb')
    with pytest.raises(ValueError,match='changed'):module.validate_source()

def test_donor_symlink_is_rejected(monkeypatch,tmp_path):
    source=tmp_path/'original.glb';source.write_bytes(b'not authorized')
    alias=tmp_path/'alias.glb';alias.symlink_to(source);monkeypatch.setattr(module,'SOURCE',alias)
    with pytest.raises(ValueError,match='changed'):module.validate_source()

@pytest.mark.parametrize('amount,expected',[(1,.16),(-1,-.075),(.02,.044)])
def test_relief_is_bounded(monkeypatch,amount,expected):
    class Value:
        def __init__(self,x):self.x=x
        def __sub__(self,other):return Value(self.x-other.x)
        def dot(self,other):return self.x
    class Tree:
        def __init__(self,x):self.x=x
        def find_nearest(self,point):return Value(self.x),None,0,.2
    monkeypatch.setattr(module,'trees',lambda:(Tree(amount),Tree(0)))
    assert module.relief(None)==pytest.approx(expected)

def test_distant_donor_has_no_effect(monkeypatch):
    class Tree:
        def find_nearest(self,point):return object(),None,0,1.0
    monkeypatch.setattr(module,'trees',lambda:(None,Tree()))
    assert module.relief(None)==0
