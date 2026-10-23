from movie_factory.adapters.blender.nihang_tack358 import smooth_path
import pytest

def test_path_retains_endpoints_and_finite_neighborhood():
    p=[(0,0,0),(1,.2,0),(2,.3,.1)]
    out=smooth_path(p,12)
    assert len(out)==25 and out[0]==p[0] and out[-1]==p[-1]
    assert all(-.1<=x<=2.1 and -.1<=y<=.4 and -.1<=z<=.2 for x,y,z in out)

def test_typed_route():
    from movie_factory.adapters.blender.nihang_patch import validate
    v=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,edits=[dict(kind='mounted_tack358',target='mounted leader')])
    assert validate(v)['edits'][0]['kind']=='mounted_tack358'
    v['edits'][0]['code']='not allowed'
    with pytest.raises(ValueError):validate(v)

def test_rein_blend_keeps_whole_grip_segment():
    from movie_factory.adapters.blender.nihang_rein358 import influence
    assert influence(0)==1
    assert all(influence(u)==0 for u in (.75,.8,1))
    values=[influence(i/80) for i in range(81)]
    assert all(0<=v<=1 for v in values)
    assert all(a>=b for a,b in zip(values,values[1:]))
    assert abs(influence(.7499))<1e-7

def test_exterior_route_seed_pins_both_ends():
    from movie_factory.adapters.blender.nihang_rein358 import seed_weights
    assert seed_weights(0)==(0,0)
    assert all(abs(x)<1e-15 for x in seed_weights(1))
    assert seed_weights(.25)[0]>seed_weights(.75)[0]>0
