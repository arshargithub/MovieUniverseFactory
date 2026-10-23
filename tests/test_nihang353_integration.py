from movie_factory.adapters.blender.nihang_integrate353 import accelerating,attachment

def test_actual_landing_negative_control():
    assert not accelerating([-2.346,-2.105,-1.939,-1.901,-1.977,-2.235])
    assert accelerating([-2,-2.3,-2.6,-2.9])
    assert not accelerating([-2,-2,-2])

def test_head_assembly_includes_core_and_actual_face():
    for n in ['MF Nihang wrapped crown core','eyeball.L','MF347 integrated beard and moustache']:
        assert attachment(n)
    assert not attachment('MF coherent coat')
