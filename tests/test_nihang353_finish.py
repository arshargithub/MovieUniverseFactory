from movie_factory.adapters.blender.nihang_finish353 import crown_part

def test_complete_crown_not_just_visible_courses():
    for name in ['MF Nihang wrapped crown core','MF Nihang gathered crown cloth','MF Nihang overlapped cloth course.005']:
        assert crown_part(name)
    assert not crown_part('MF coherent coat')
