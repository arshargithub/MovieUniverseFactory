import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_studio_package',Path(__file__).resolve().parents[2]/'scripts/package_wardrobe_studio.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def ready(root):
    (root/'view.png').touch()
    return {'candidate':'wardrobe173-seal01','known_structural_blockers':[],
            'criteria':[{'id':key,'status':'PASS','images':['view.png'],'observation':'Manually inspected actual selected static region'} for key in module.CRITERIA]}

def test_all_studio_scope_criteria_required(tmp_path):
    review=ready(tmp_path)
    module.check_review(review,tmp_path,'wardrobe173-seal01',module.CRITERIA)
    review['criteria'].pop()
    with pytest.raises(ValueError):module.check_review(review,tmp_path,'wardrobe173-seal01',module.CRITERIA)

@pytest.mark.parametrize('defect',['blocker','ambiguous','old_candidate','missing_evidence'])
def test_relative_improvement_is_not_readiness(tmp_path,defect):
    review=ready(tmp_path)
    if defect=='blocker':review['known_structural_blockers']=['broken upper leather']
    elif defect=='ambiguous':review['criteria'][0]['status']='NOT_RUN'
    elif defect=='old_candidate':review['candidate']='wardrobe172-seal01'
    else:review['criteria'][0]['images']=['absent.png']
    with pytest.raises(ValueError):module.check_review(review,tmp_path,'wardrobe173-seal01',module.CRITERIA)
