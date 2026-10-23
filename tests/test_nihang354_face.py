from movie_factory.adapters.blender.nihang_face354 import free_length
from movie_factory.adapters.blender.nihang_patch import validate
def test_cheek_is_not_long_curtain():
    assert free_length(1.70,1.75,0)<.025
    assert free_length(1.62,1.75,0)>.07
    for i in range(500):assert .01<=free_length(1.68,1.75,i)<.09
def test_fixed_face_recipe():
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_face354',target='mounted leader')]))
