import pytest
from movie_factory.adapters.blender import nihang_padcontact369 as p, nihang_patch


def test_exact_scope_and_safe_recipe():
    e = dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='inspect')
    recipe = dict(operation='nihang_patch', frame=306, width=432, height=768, samples=8, edits=[e])
    nihang_patch.validate(recipe)
    e.update(mode='fit', offset=.024)
    nihang_patch.validate(recipe)
    p.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='bind'))
    p.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='follow'))
    p.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='diagnose'))
    p.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='refine', level=3))
    for field, value in [('code', 'arbitrary'), ('target', 'horse'), ('offset', .5), ('mode', 'sculpt')]:
        bad = dict(e); bad[field] = value
        with pytest.raises(ValueError): p.validate(bad)


@pytest.mark.parametrize('offset', [float('nan'), float('inf'), True, -.01, .036])
def test_finite_contact_bounds(offset):
    with pytest.raises(ValueError):
        p.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='fit', offset=offset))


def test_inside_and_outside_are_distinct_controls():
    assert p.classify([.008, .003, .002])['penetrating_samples'] == 0
    assert p.classify([.008, -.006, -.002])['penetrating_samples'] == 2
    for values in ([], [float('nan')]):
        with pytest.raises(ValueError): p.classify(values)


@pytest.mark.parametrize('level', [True, 1, 4, 2.5, '3'])
def test_refinement_is_bounded(level):
    with pytest.raises(ValueError):
        p.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='refine', level=level))
