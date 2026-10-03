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


@pytest.mark.parametrize('defect',['blocker','failed','missing','escape'])
def test_failed_review_stays_internal(tmp_path,defect):
    review=ready(tmp_path)
    if defect=='blocker':review['known_structural_blockers']=['floating belt']
    elif defect=='failed':review['criteria'][0]['status']='FAIL'
    elif defect=='missing':review['criteria'].pop()
    else:review['criteria'][0]['images']=['../elsewhere.png']
    with pytest.raises(ValueError):module.check_review(review,tmp_path)
