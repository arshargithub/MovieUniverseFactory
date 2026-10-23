from movie_factory.adapters.blender import nihang_fabric357 as m

def test_fold_bounds_and_binding_preservation():
    for a in (-.10,-.03,0,.04,.1):
        for f in (-1,0,1):
            assert 0<=m.fold_amount(a,.05,f,.10)<=.0055
            assert m.fold_amount(a,.05,f,0)==0
    assert m.fold_amount(0,.2,1,.1)==0

def test_fixed_fabric_recipe():
    from movie_factory.adapters.blender.nihang_patch import validate
    validate(dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_fabric357',target='mounted leader')]))
