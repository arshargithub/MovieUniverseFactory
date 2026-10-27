import pytest
from movie_factory.adapters.blender.anatomy_graft390 import validate,boundary_vertices

def test_closed_bound_geometry_recipe():
    e=dict(kind='mounted_forequarter390_graft',target='horse',mode=0,data=dict(path='.runtime/art-direction/anatomy390-targets/graft254.npz',sha256='a'*64))
    assert validate(e)==e
    for v in [dict(e,mode=True),dict(e,mode=2),dict(e,code='x'),dict(e,data=dict(path='.runtime/art-direction/anatomy390-targets/../evil.npz',sha256='a'*64))]:
        with pytest.raises(ValueError):validate(v)

def test_boundary_ownership_excludes_internal_vertices():
    p=[[0,1,4,3],[1,2,5,4],[3,4,7,6],[4,5,8,7]]
    assert boundary_vertices(p)=={0,1,2,3,5,6,7,8}
    with pytest.raises(ValueError):boundary_vertices([[0,1,1,-1]])
    with pytest.raises(ValueError):boundary_vertices([[0,1,2,-1],[1,0,3,-1],[0,1,4,-1]])
