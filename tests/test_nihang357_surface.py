import numpy as np
from movie_factory.adapters.blender.nihang_surface357 import brow_path

def test_brow_flow_is_outward_taperable_and_root_pinned():
    for side in (-1,1):
        root=np.array([side*.033,-.11,1.80]);p=brow_path(root,side,31)
        assert np.allclose(p[0],root)
        assert side*(p[-1,0]-root[0])>0
        assert np.max(np.linalg.norm(p-root,axis=1))<.008

def test_surface_recipe_is_bounded_and_fixed():
    from movie_factory.adapters.blender.nihang_patch import validate
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_surface357',target='mounted leader')]))
