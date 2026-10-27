"""Closed handler/data boundary; actual native source preservation is separate."""
import hashlib
import importlib.util
from importlib.machinery import ModuleSpec
from types import SimpleNamespace
import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_anatomy386 as a, nihang_patch as p, nihang_control as c


def test_closed_export_and_no_recipe_code():
    e=dict(kind='mounted_anatomy386_export',target='horse');a.validate(e)
    p.validate(dict(operation='nihang_patch',frame=283,width=576,height=576,samples=8,edits=[e]))
    for bad in [{**e,'code':'run'}, {**e,'target':'another'}, {**e,'path':'input'}]:
        with pytest.raises(ValueError):a.validate(bad)


@pytest.mark.parametrize('path',['/tmp/a.npz','.runtime/art-direction/anatomy386-targets/../secret.npz',
    '.runtime/art-direction/other/a.npz','.runtime/art-direction/anatomy386-targets/a.py'])
def test_target_file_scope(path):
    with pytest.raises(ValueError):a.validate(dict(kind='mounted_anatomy386_target',target='horse',data={'path':path,'sha256':'a'*64}))


def test_wrong_array_shape_cannot_reach_bpy(tmp_path):
    path=tmp_path/'.runtime/art-direction/anatomy386-targets/a.npz';path.parent.mkdir(parents=True)
    np.savez_compressed(path,source=np.zeros((1,1,3)),target=np.zeros((1,1,3)),rest=np.zeros((1,3)),mask=np.zeros(1),times=np.zeros(1))
    b={'path':str(path.relative_to(tmp_path)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    with pytest.raises(ValueError,match='ARRAY_SHAPE'):a.load(tmp_path,b)
    b['sha256']='0'*64
    with pytest.raises(ValueError,match='DATA_STALE'):a.load(tmp_path,b)


def test_dispatch_uses_fixed_export(monkeypatch,tmp_path):
    marker=object();monkeypatch.setattr(a,'export',lambda bpy,out:marker)
    assert a.run(None,tmp_path,dict(kind='mounted_anatomy386_export',target='horse')) is marker


def test_closed_anatomical_camera_views():
    for v in a.VIEWS:
        c.validate(dict(operation='nihang_frames',frame=283,frames=[283,333,339],view=v,width=640,height=640,samples=8))
    with pytest.raises(ValueError):
        c.validate(dict(operation='nihang_frames',frame=283,frames=[283],view='anatomy_arbitrary386',width=640,height=640,samples=8))


@pytest.mark.parametrize('kind',['mounted_anatomy386_export','mounted_anatomy386_target'])
def test_actual_apply_preflight_accepts_existing_horse(monkeypatch,tmp_path,kind):
    class Loader:
        def create_module(self,spec):return None
        def exec_module(self,module):module.run=lambda bpy,out,edit:{'fixed386':edit['kind']}
    monkeypatch.setattr(importlib.util,'spec_from_file_location',lambda name,path:ModuleSpec(name,Loader()))
    calls=[];bpy=SimpleNamespace(data=SimpleNamespace(objects={'horse':object()}),
        context=SimpleNamespace(scene=SimpleNamespace(frame_set=calls.append),view_layer=SimpleNamespace(update=lambda:None)))
    edit=dict(kind=kind,target='horse')
    if kind.endswith('target'):edit['data']=dict(path='.runtime/art-direction/anatomy386-targets/test.npz',sha256='a'*64)
    result=p.apply(bpy,dict(frame=283,edits=[edit]),tmp_path)
    assert result==[{'anatomy386':{'fixed386':kind}}] and calls==[283]
