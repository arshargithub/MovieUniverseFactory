"""Offline safety tests; no claim of native or perceptual qualification."""
import pytest
from movie_factory.adapters.blender.nihang_control import validate


def test_read_only_rig_inspection_recipe():
    r = {'operation': 'nihang_rig_inspect', 'frame': 327,
         'width': 64, 'height': 64, 'samples': 1}
    assert validate(r) == r
    for extra in ({'repair': True}, {'script': 'anything'}, {'target': 'unrelated'}):
        with pytest.raises(ValueError): validate(r | extra)


def test_fixed_length_support_solver():
    from movie_factory.adapters.blender.nihang_support import bend_joint
    import math
    a=[0,0,1]; b=[0,0,0]
    k=bend_joint(a,b,.7,.7,[0,-1,0])
    assert k[1]<0
    assert math.dist(a,k)==pytest.approx(.7)
    assert math.dist(b,k)==pytest.approx(.7)
    with pytest.raises(ValueError,match='NO_STRETCH'): bend_joint(a,b,.4,.4,[0,-1,0])


def test_support_recipe_is_bounded():
    from movie_factory.adapters.blender.nihang_patch import validate as patch
    pose={'kind':'supported_pose','target':'horse.rig','frame':327,'pitch':-.8,
          'hip_back':.12,'hip_drop':.18,'neck_pitch':.2,'poll_pitch':.55}
    r={'operation':'nihang_patch','frame':327,'width':540,'height':960,'samples':8,
       'edits':[{'kind':'repair_bbone_targets','target':'horse.rig'},pose]}
    assert patch(r)==r
    for key,value in [('pitch',-9),('frame',True),('hip_drop',float('nan'))]:
        with pytest.raises(ValueError): patch(r|{'edits':[pose|{key:value}]})


def test_inspected_driver_names_include_hyphens():
    from types import SimpleNamespace as S
    from movie_factory.adapters.blender.nihang_support import repair_bbone_targets
    target=S(id=None,id_type='OBJECT',data_path='pose.bones["thigh_tweak.L.001"]["rubber_tweak"]')
    driver=S(is_valid=False,type='SUM',variables=[S(type='SINGLE_PROP',targets=[target])])
    curves=[S(driver=driver,data_path='bones["DEF-thigh.L"].bbone_easeout') for _ in range(64)]
    data=S(animation_data=S(drivers=curves),path_resolve=lambda p:1.0,update_tag=lambda:None)
    rig=S(data=data,path_resolve=lambda p:0.0,update_tag=lambda:None)
    bpy=S(data=S(objects={'horse.rig':rig}),context=S(view_layer=S(update=lambda:None)))
    assert repair_bbone_targets(bpy)==64
    assert target.id is rig
