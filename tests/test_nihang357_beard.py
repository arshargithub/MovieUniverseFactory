import numpy as np
from movie_factory.adapters.blender.nihang_beard357 import zone,guide
from movie_factory.adapters.blender.nihang_patch import validate
def test_no_neck_or_ear_domain():
    for x in np.linspace(-.1,.1,51):
        for d in [.114,.13,.16,.22]:assert zone(x,d) is None
    assert zone(.09,.06) is None
    assert zone(0,.075) is None
    assert zone(.05,.055)=='cheek'
    assert zone(0,.10)=='chin'
def test_roots_preserved_and_free_end():
    for kind,root in [('cheek',(.05,-.08,1.70)),('chin',(0,-.10,1.66)),('lip',(.02,-.12,1.71))]:
        p=guide(root,1.776,7,kind);assert np.isfinite(p).all();assert np.array_equal(p[0],root)
        assert p[-1,2]<p[0,2]
        if kind!='lip':assert p[-1,2]<1.60
def test_fixed_recipe():
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_beard357',target='mounted leader')]))

def test_dense_paths_have_volume_and_root_pin():
    from movie_factory.adapters.blender.nihang_groom357 import path
    p=path((.05,-.1,1.72),1.776,4,'cheek')
    assert np.array_equal(p[0],[.05,-.1,1.72])
    assert p[:,1].min()<-.13 and np.ptp(p[:,0])>.01
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_groom357',target='mounted leader')]))
