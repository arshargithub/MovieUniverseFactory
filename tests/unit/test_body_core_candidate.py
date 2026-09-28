import pytest
from movie_factory.adapters.blender import body_core_candidate as b


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'}, {'operation':'inspect_core01','path':'x'}])
def test_strict_job(job):
    with pytest.raises(ValueError):b.validate(job)


def test_endpoint_strategies():
    points=[(0,0,0),(2,4,6)]
    assert b.endpoint({'strategy':'CUBE','cube_name':'joint'},points,{'joint':{0,1}})==(1,2,3)
    assert b.endpoint({'strategy':'VERTEX','vertex_index':1},points,{})==(2,4,6)
    assert b.endpoint({'strategy':'MEAN','vertex_indices':[0,1]},points,{})==(1,2,3)
    with pytest.raises(ValueError):b.endpoint({'strategy':'CODE'},points,{})


def test_bad_mesh_rejected():
    with pytest.raises(ValueError):b.parse_obj('v 0 0 0\ng body\nf 1 1 1')
