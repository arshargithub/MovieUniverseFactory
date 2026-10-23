import numpy as np
from movie_factory.adapters.blender.nihang_tack354 import blanket_probe
from movie_factory.adapters.blender.nihang_patch import validate
def test_drape_not_plane_and_corners_round():
    lo=(-.38,-.96,1.15);hi=(.38,-.32,1.51)
    middle=blanket_probe(.5,.5,lo,hi);edge=blanket_probe(0,.5,lo,hi)
    assert middle[2]-edge[2]>.3
    assert abs(blanket_probe(0,0,lo,hi)[1]+.64)<abs(blanket_probe(.5,0,lo,hi)[1]+.64)
    for u in np.linspace(0,1,25):assert np.isfinite(blanket_probe(u,.4,lo,hi)).all()
def test_fixed_tack_recipe():
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_tack354',target='mounted leader')]))
