import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_actor import garment_mask,supported_waist_height
from movie_factory.adapters.blender.nihang_patch import validate

def test_fixed_actor_scope():
    recipe=dict(operation='nihang_patch',frame=283,width=540,height=960,samples=16,
                edits=[dict(kind='coherent_actor',target='mounted leader')])
    assert validate(recipe)==recipe
    for edit in [dict(kind='coherent_actor',target='principal Sikh'),
                 dict(kind='coherent_actor',target='mounted leader',code='x')]:
        with pytest.raises(ValueError):validate(recipe|{'edits':[edit]})

def test_cuff_plane_excludes_hand_not_torso():
    wrists={1:np.array([.53,-.23,1.17]),-1:np.array([-.53,-.23,1.17])}
    elbows={1:np.array([.38,-.02,1.31]),-1:np.array([-.38,-.02,1.31])}
    p=np.array([[0,-.12,1.2],[.38,-.02,1.31],[.56,-.35,1.11],[0,0,1.75]])
    assert garment_mask(p,'coat',wrists,elbows).tolist()==[True,True,False,False]
    assert garment_mask(p,'pants',wrists,elbows).tolist()==[False]*4

def test_belt_above_highest_nonplanar_hem_not_global_minimum():
    p=np.array([[-.18,-.1,1.025],[.18,-.1,1.058],[.18,.1,1.041],[-.18,.1,1.05],
                [-.18,-.1,1.5],[.18,-.1,1.5],[.18,.1,1.5],[-.18,.1,1.5]])
    faces=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    assert supported_waist_height(p,faces)==pytest.approx(1.083)
