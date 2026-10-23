import pytest
from movie_factory.adapters.blender.nihang_coat357 import coat_slot
from movie_factory.adapters.blender.nihang_control import validate as frames
from movie_factory.adapters.blender.nihang_patch import validate

def test_dominant_surface_not_polygon_count():
    assert coat_slot([(0,8),(1,.5),(1,.5),(2,1)])==0
    with pytest.raises(ValueError):coat_slot([(0,4),(1,3),(2,3)])

def test_fixed_coat_and_head_control():
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_coat357',target='mounted leader')]))
    frames(dict(operation='nihang_frames',frame=327,frames=[283,327],view='horse_head',width=640,height=640,samples=24))
