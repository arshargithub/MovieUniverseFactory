import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_review_package',Path(__file__).resolve().parents[2]/'scripts/package_wardrobe_fit_review.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def ready(root):
    (root/'frame.png').touch()
    return {'candidate':'wardrobe169-seal01','known_structural_blockers':[],
            'criteria':[{'id':name,'status':'PASS','images':['frame.png'],'observation':'Inspected static scope'} for name in module.CRITERIA]}


def test_ready_gate(tmp_path):module.check_review(ready(tmp_path),tmp_path)


def test_refinement_requires_its_own_candidate_and_criteria(tmp_path):
    review=ready(tmp_path)
    criteria={'protected_foundation','tailored_silhouette','costume_character','open_scarf_fit','single_tail_assembly','mounted_and_partial_regressions'}
    with pytest.raises(ValueError):
        module.check_review(review,tmp_path,'wardrobe170-seal02',criteria)
    review['candidate']='wardrobe170-seal02'
    review['criteria']=[{'id':name,'status':'PASS','images':['frame.png'],'observation':'Manually inspected scoped refinement'} for name in criteria]
    module.check_review(review,tmp_path,'wardrobe170-seal02',criteria)


def test_correction_requires_all_five_and_adjacent_review(tmp_path):
    review=ready(tmp_path)
    criteria={'protected_foundation','full_scarf','sleeves','flared_hem','rugged_fabric','skin_continuity','posed_interfaces','adjacent_regressions','whole_static_candidate'}
    with pytest.raises(ValueError):module.check_review(review,tmp_path,'wardrobe171-seal01',criteria)
    review['candidate']='wardrobe171-seal01'
    review['criteria']=[{'id':name,'status':'PASS','images':['frame.png'],'observation':'Actual selected evidence inspected'} for name in criteria]
    module.check_review(review,tmp_path,'wardrobe171-seal01',criteria)
    review['known_structural_blockers']=['rear scarf spike']
    with pytest.raises(ValueError):module.check_review(review,tmp_path,'wardrobe171-seal01',criteria)


@pytest.mark.parametrize('defect',['blocker','failed','missing','escape'])
def test_failed_review_stays_internal(tmp_path,defect):
    review=ready(tmp_path)
    if defect=='blocker':review['known_structural_blockers']=['floating belt']
    elif defect=='failed':review['criteria'][0]['status']='FAIL'
    elif defect=='missing':review['criteria'].pop()
    else:review['criteria'][0]['images']=['../elsewhere.png']
    with pytest.raises(ValueError):module.check_review(review,tmp_path)
