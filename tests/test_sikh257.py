"""Offline admission tests, not visual qualification."""
import pytest
from movie_factory.sikh257_contract import validate
from movie_factory.sikh257_geometry import cloth_strip,end_translation,joint_between
import math

@pytest.mark.parametrize('job', [None,{}, {'operation':'exec','attempt':1}, {'operation':'layout','attempt':True}, {'operation':'layout','attempt':0}, {'operation':'layout','attempt':100}, {'operation':'layout','attempt':1,'code':'bad'}, {'operation':'../escape','attempt':1}])
def test_reject_unstructured_jobs(job,tmp_path):
    with pytest.raises(ValueError):validate(job,tmp_path)

def test_real_sources_and_bounded_destination():
    out=validate({'operation':'inspect','attempt':99})
    assert out.name=='inspect-99'
    assert out.parent.name=='series01-sikh257'

def test_strip_is_one_connected_material_grid():
    d=cloth_strip()
    assert len(d['verts'])==d['rows']*d['cols']
    assert len(d['faces'])==(d['rows']-1)*(d['cols']-1)
    assert all(math.isfinite(c) for v in d['verts'] for c in v)
    # The first free row shares edges with crown; not separate cloth objects.
    boundary=(d['crown_rows']-1)*d['cols']
    assert any(min(f)<=boundary<max(f) for f in d['faces'])
    assert all(a[0]<=b[0] for a,b in zip(d['rest'],d['rest'][1:]))

def test_uncover_has_continuous_staged_endpoint():
    p=[end_translation(f) for f in range(145)]
    assert p[0]==(0.,0.,0.)
    assert p[54][2]==0 and p[54][1]<0
    assert p[96][2]==-.24
    assert max(math.dist(a,b) for a,b in zip(p,p[1:]))<.01

def test_face_cover_front_has_outward_winding():
    d=cloth_strip();row=d['crown_rows']+30;f=d['faces'][row*(d['cols']-1)+5]
    a,b,c=[d['verts'][i] for i in f[:3]]
    u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
    normal_y=u[2]*v[0]-u[0]*v[2]
    assert normal_y<0

@pytest.mark.parametrize('target',[(.35,-.38,1.09),(.026,-.18,1.40),(.117,.07,1.70)])
def test_arm_control_preserves_lengths(target):
    a=(.215,.09,1.395);j=joint_between(a,target,.31,.30,(1,.1,-.5))
    assert math.dist(a,j)==pytest.approx(.31)
    assert math.dist(j,target)==pytest.approx(.30)

def test_unreachable_control_does_not_stretch():
    with pytest.raises(ValueError):joint_between((0,0,0),(0,0,2),.3,.3,(1,0,0))
