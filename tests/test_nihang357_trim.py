import pytest
from movie_factory.adapters.blender.nihang_trim357 import loops

def test_closed_boundary_loops_keep_shared_vertices():
    assert len(loops([(0,1,2,3),(3,2,4,5)]))==1
    assert set(loops([(0,1,2,3),(3,2,4,5)])[0])==set(range(6))

def test_branch_rejected():
    with pytest.raises(ValueError):loops([(0,1,2),(0,3,4)])

def test_fixed_trim_recipe():
    from movie_factory.adapters.blender.nihang_patch import validate
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_trim357',target='mounted leader')]))
