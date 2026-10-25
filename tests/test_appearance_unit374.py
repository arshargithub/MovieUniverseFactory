from copy import deepcopy
import pytest
from test_work_units367 import prepared,reviewed
from test_production_workflow import setup
from movie_factory import work_units as u,expert_planning as ep,production_workflow as wf

def appearance(setup):
 b=prepared(setup);unit=b['work_unit'];unit['discipline']='appearance';b['references'][0]['role']='directional_design'
 unit['appearance_proof']=dict(poses=[283,333,346],views=['front','side','reverse'],motion_source=next(iter(b['source_bindings'].values())),interfaces=['neckbase','forelegroots','tack'])
 b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);return b

def test_appearance_uses_form_role_without_mislabeling_motion(setup):
 b=appearance(setup);ep.validate(b)
 b['references'][0]['role']='faithful_motion'
 with pytest.raises(wf.Blocked,match='UNIT_REFERENCE'):u.validate(b)
 assert u.validate(prepared(setup))['reference']

@pytest.mark.parametrize('field,value',[('poses',[283,333]),('poses',[283,333,True]),('views',['front','side']),('views',['front','front','side']),('interfaces',['neck']),('motion_source',{'path':'missing','sha256':'0'*64})])
def test_incomplete_appearance_proof_blocks(setup,field,value):
 b=appearance(setup);b['work_unit']['appearance_proof'][field]=value
 with pytest.raises(wf.Blocked):u.validate(b)

def test_every_pose_view_cell_required_in_execution_and_review(setup):
 b=appearance(setup);unit=b['work_unit'];rid=unit['positive_criteria'][0]['id'];use=dict(id=unit['id'],criteria={rid:'Reference/source compared'},changed_domains=[],boundaries={'first_lift':'Frozen accepted pose velocity contacts'},pose_views={k:'Actual source image comparison' for k in u.appearance_cells(unit)})
 u.execution(b,{'unit_application':use});use['pose_views'].popitem()
 with pytest.raises(wf.Blocked):u.execution(b,{'unit_application':use})
 r=reviewed(b);r['unit_review']['pose_views']={k:deepcopy(r['unit_review']['criteria'][rid]) for k in u.appearance_cells(unit)}
 assert u.review(b,r,{'frame':{}})==([],[])
 key=next(iter(r['unit_review']['pose_views']));r['unit_review']['pose_views'][key]['status']='FAIL';assert u.review(b,r,{'frame':{}})[0]
 r['unit_review']['pose_views'].pop(key)
 with pytest.raises(wf.Blocked):u.review(b,r,{'frame':{}})

def test_unknown_discipline_and_outside_kind_still_block(setup):
 b=appearance(setup);b['work_unit']['discipline']='anything'
 with pytest.raises(wf.Blocked):u.validate(b)
 b=appearance(setup)
 with pytest.raises(wf.Blocked):u.native(dict(task='t',cycle=1,brief=b),dict(operation='nihang_patch',edits=[dict(kind='unplanned')]))
