import pytest
from movie_factory.adapters.blender.anatomy_muscle386 import validate,contraction_keys,BONES,FRAMES
from movie_factory.adapters.blender.nihang_patch import validate as patch

def test_fixed_secondary_tissue_contract_no_bone_selection_or_code():
    e=dict(kind='mounted_anatomy386_muscle_contract',target='horse',amount=.3)
    patch(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
    for bad in [dict(e,amount=.41),dict(e,amount=float('nan')),dict(e,bones=['head']),dict(e,code='x')]:
        with pytest.raises(ValueError):validate(bad)
    assert BONES==['DEF-breast.L','DEF-breast.R']

def test_fixed_profile_preserves_boundary_and_neutral_before_loading():
    v=dict(contraction_keys(.3));assert v[276]==v[293]==v[358]==v[367]==1
    assert v[333]==v[339]==.7 and all(.7<=x<=1 for x in v.values())
    assert set([272,283,315,333,339,346,370])<=set(FRAMES)
    assert all(x==1 for _,x in contraction_keys(0))
