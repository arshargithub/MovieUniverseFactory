import pytest
from movie_factory.adapters.blender.nihang_patch import validate

@pytest.mark.parametrize('kind',['mounted_waist353','mounted_waist353_attach','mounted_finish353','mounted_motion353','mounted_integrate353','mounted_gesture353'])
def test_fixed_owned_operations_no_code_or_paths(kind):
    recipe=dict(operation='nihang_patch',frame=327,width=432,height=768,samples=8,edits=[dict(kind=kind,target='mounted leader')])
    assert validate(recipe)==recipe
    for key,value in [('code','print(1)'),('path','/tmp/other.blend'),('target','accepted principal')]:
        bad=recipe|{'edits':[recipe['edits'][0]|{key:value}]}
        with pytest.raises(ValueError):validate(bad)
