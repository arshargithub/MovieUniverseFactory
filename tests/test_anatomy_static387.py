from types import SimpleNamespace
import pytest
from movie_factory.adapters.blender.anatomy_static387 import freeze,validate
from movie_factory.adapters.blender.nihang_patch import validate as patch

def test_freeze_observes_then_disables_only_blur():
    for before in [True,False]:
        render=SimpleNamespace(use_motion_blur=before,resolution_x=640);s=SimpleNamespace(render=render);v=freeze(s)
        assert v['source_use_motion_blur'] is before and render.use_motion_blur is False and render.resolution_x==640
    for render in [SimpleNamespace(),SimpleNamespace(use_motion_blur=1)]:
        with pytest.raises(ValueError):freeze(SimpleNamespace(render=render))

def test_closed_control_and_bound_target_vocabulary():
    e=dict(kind='mounted_anatomy387_static_control',target='horse')
    for edit in [e,dict(kind='mounted_anatomy387_static_target',target='horse',data=dict(path='.runtime/art-direction/anatomy386-targets/example.npz',sha256='a'*64))]:
        patch(dict(operation='nihang_patch',frame=339,width=640,height=640,samples=8,edits=[edit]))
    for bad in [dict(e,code='x'),dict(e,target='scene'),dict(e,blur=True)]:
        with pytest.raises(ValueError):validate(bad)
