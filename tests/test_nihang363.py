"""Fixed diagnostic transport tests, not anatomical or simulation qualification."""
import pytest
from movie_factory.adapters.blender.nihang_patch import validate
from movie_factory.adapters.blender.nihang_control import validate as control
@pytest.mark.parametrize('kind',['mounted_flagcontrol363','mounted_audit363','mounted_hand363','mounted_grip363','mounted_repair363','mounted_chest363','mounted_flag363'])
def test_fixed_readonly_audit(kind):
 r=dict(operation='nihang_patch',frame=283,width=432,height=768,samples=8,edits=[dict(kind=kind,target='mounted leader')]);validate(r)
 r['edits'][0]['path']='arbitrary'
 with pytest.raises(ValueError):validate(r)

def test_chest_field_is_local_finite_and_preserves_unweighted_forelegs():
 import numpy as np
 from movie_factory.adapters.blender.nihang_repair363 import chest_delta
 p=np.array([[0,-1.01,1.20],[0,-.80,.80],[.3,-.8,1.25],[0,0,1.2]])
 d=chest_delta(p,np.array([1,1,0,1]))
 assert np.isfinite(d).all() and 0<d[0,1]<.18
 assert np.all(d[1:]==0) and np.all(d[:,[0,2]]==0)

def test_chest_fairing_removes_local_bump_without_moving_anchors():
 import numpy as np
 from movie_factory.adapters.blender.nihang_chest363 import fair_delta
 p=np.array([[0,-.6,1.2],[.1,-.7,1.2],[-.1,-.7,1.2],[0,-.7,1.1],[0,-.7,1.3]])
 e=[(0,i) for i in range(1,5)];b=np.ones(5);l=np.array([0,1,1,1,1]);d=fair_delta(p,e,b,l)
 assert d[0,1]<0 and np.linalg.norm(d[0])<.11 and np.all(d[1:]==0)
 p[0,1]=-.7;assert np.max(np.abs(fair_delta(p,e,b,l)))<1e-10
@pytest.mark.parametrize('view',['flag363','flag363_reverse','horse_chest','horse_chest_side','leader_right_contact','leader_left_contact'])
def test_bounded_diagnostic_view(view):
 control(dict(operation='nihang_frames',frame=283,frames=[283,327],view=view,width=640,height=640,samples=8))

from movie_factory.native_admission import review_observations
from movie_factory.production_workflow import Blocked
def test_av_availability_is_not_human_pass():
 req=[dict(id='motion',director_av=True)]
 assert review_observations(['motion'],req,dict(verdict='PASS',observation='File exists'),'PASS')[0]['status']=='NOT_TESTED'
 with pytest.raises(Blocked,match='AV_CANNOT'):
  review_observations(['motion'],req,dict(verdict='PASS',observation='x',requirement_outcomes={'motion':dict(status='PASS',observation='Not human')}),'PASS')
def test_component_not_tested_preserves_failure_boundary():
 req=[dict(id='form',director_av=False)]
 v=dict(verdict='PASS',observation='Diagnostic rendered',requirement_outcomes={'form':dict(status='NOT_TESTED',observation='Known art failure remains')})
 assert review_observations(['form'],req,v,'PASS')[0]['status']=='NOT_TESTED'
 with pytest.raises(Blocked,match='HIDES_FAILURE'):review_observations(['form'],req,v,'FAIL')
 v['requirement_outcomes']={}
 with pytest.raises(Blocked,match='COVERAGE'):review_observations(['form'],req,v,'PASS')
