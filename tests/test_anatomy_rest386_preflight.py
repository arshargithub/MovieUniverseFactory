import pytest
import importlib.util
from importlib.machinery import ModuleSpec
from types import SimpleNamespace
from movie_factory.adapters.blender import nihang_patch as p

@pytest.mark.parametrize('kind',['mounted_anatomy386_rest','mounted_anatomy386_form','mounted_anatomy386_pectoral'])
def test_rest_apply_uses_existing_horse_owner(monkeypatch,tmp_path,kind):
 class Loader:
  def create_module(self,spec):return None
  def exec_module(self,module):module.run=lambda bpy,out,edit:{'rest':True}
 monkeypatch.setattr(importlib.util,'spec_from_file_location',lambda name,path:ModuleSpec(name,Loader()))
 bpy=SimpleNamespace(data=SimpleNamespace(objects={'horse':object()}),context=SimpleNamespace(scene=SimpleNamespace(frame_set=lambda f:None),view_layer=SimpleNamespace(update=lambda:None)))
 e=dict(kind=kind,target='horse',data=dict(path='.runtime/art-direction/anatomy386-targets/a.npz',sha256='a'*64))
 assert p.apply(bpy,dict(frame=283,edits=[e]),tmp_path)==[{'anatomy386':{'rest':True}}]
