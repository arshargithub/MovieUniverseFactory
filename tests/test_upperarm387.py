from types import SimpleNamespace
import pytest
from movie_factory.adapters.blender.anatomy_upperarm387 import validate,segments,BONES
from movie_factory.adapters.blender.nihang_patch import validate as patch

class Bones(dict):
    def __iter__(self):return iter(self.values())

def test_actual_owner_closed_modes():
    e=dict(kind='mounted_upperarm387_rigid',target='horse',mode=0)
    for mode in (0,1):patch(dict(operation='nihang_patch',frame=339,width=640,height=640,samples=8,edits=[dict(e,mode=mode)]))
    for bad in (dict(e,mode=True),dict(e,mode=2),dict(e,mode=.5),dict(e,bones=[]),dict(e,target='human'),dict(e,code='x')):
        with pytest.raises(ValueError):validate(bad)

def test_fixed_segment_set_and_zero_control():
    for mode in (0,1):
        bones=Bones({n:SimpleNamespace(name=n,bbone_segments=10) for n in BONES+('other',)})
        old,new=segments(bones,mode)
        assert old==dict.fromkeys(bones.keys(),10)
        assert all(bones[n].bbone_segments==(1 if mode else 10) for n in BONES)
        assert bones['other'].bbone_segments==10
        assert new=={n:b.bbone_segments for n,b in bones.items()}
    bones[BONES[0]].bbone_segments=2
    with pytest.raises(ValueError):segments(bones,1)
