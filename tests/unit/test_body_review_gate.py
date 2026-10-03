import importlib.util
from pathlib import Path
import pytest

FILE=Path(__file__).resolve().parents[2]/'scripts/package_body_correction_review.py'
spec=importlib.util.spec_from_file_location('body_review_gate',FILE)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def review(status='PASS'):
    return {'candidate':'body161-fit46','criteria':[{'id':key,'status':status,'images':['checked.png'],'observation':'Explicit scoped visual inspection'} for key in ('neck_clavicles','chest_shoulders','arms_elbows','knees','abdomen','whole_result')]}


@pytest.mark.parametrize('status',['FAIL','NOT_RUN','YELLOW','NOT_APPLICABLE'])
def test_failed_or_unreviewed_candidate_cannot_be_packaged(tmp_path,status):
    with pytest.raises(ValueError,match='must stay internal'):
        module.check_review_gate(review(status),'body161-fit46',tmp_path)


def test_pass_still_requires_candidate_and_present_image_evidence(tmp_path):
    with pytest.raises(ValueError):module.check_review_gate(review(),'body160-fit39',tmp_path)
    with pytest.raises(ValueError):module.check_review_gate(review(),'body161-fit46',tmp_path)
    (tmp_path/'checked.png').touch()
    assert module.check_review_gate(review(),'body161-fit46',tmp_path)
    changed=review();changed['criteria'].pop()
    with pytest.raises(ValueError):module.check_review_gate(changed,'body161-fit46',tmp_path)


def test_reference_path_cannot_replace_uninspected_candidate_evidence(tmp_path):
    data=review();data['criteria'][0]['images']=['../old.png']
    with pytest.raises(ValueError):module.check_review_gate(data,'body161-fit46',tmp_path)


def test_hip_handoff_requires_landmark_gate_and_no_unresolved_blockers(tmp_path):
    data=review();data['candidate']='body168-hip66'
    data.update(known_blockers_remaining=[],failure_seeking_review=True)
    (tmp_path/'checked.png').touch()
    with pytest.raises(ValueError,match='integrated'):module.check_review_gate(data,'body168-hip66',tmp_path)
    for key in ('hip_fold','pelvic_volume_and_cleft'):
        data['criteria'].append({'id':key,'status':'PASS','images':['checked.png'],'observation':'Full and partial bend inspected; structural landmarks retained'})
    assert module.check_review_gate(data,'body168-hip66',tmp_path)
    data['known_blockers_remaining']=['Cleft lost at partial bend']
    with pytest.raises(ValueError,match='stay internal'):module.check_review_gate(data,'body168-hip66',tmp_path)
    data['known_blockers_remaining']=[];data['criteria'][-1]['status']='NOT_RUN'
    with pytest.raises(ValueError,match='stay internal'):module.check_review_gate(data,'body168-hip66',tmp_path)
