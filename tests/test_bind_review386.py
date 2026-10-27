import importlib.util
from pathlib import Path
import pytest
from movie_factory.native_admission import review_observations

def client():
    p=Path(__file__).resolve().parents[1]/'scripts/sikh386_bind_source_review.py'
    spec=importlib.util.spec_from_file_location('review_client386_test',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def report(crossing):
    return dict(neutral_error=0.,relative_corrective_error=0.,max_original_rest_delta=.07,geometry_actions_other_objects_preserved=True,pose_preservation=dict(outside_surface_max_error=0.,skeleton_and_world_max_error=0.),original_armature_live=[['Armature',True,True]],strength=.6,surface_diagnostics=[dict(frame=339,after_crossings=crossing)])

REQ=[dict(id=n,director_av=False) for n in ['preservation','evidence']]

def test_failed_source_client_cannot_hide_failure_with_passed_invariants():
    v=client().build_review(dict(artifacts={}),report(2))
    assert v['verdict']=='FAIL' and v['open_defects']
    rows=review_observations(['preservation','evidence'],REQ,v,'FAIL')
    assert [x['status'] for x in rows]==['FAIL','FAIL']
    bad=dict(v,requirement_outcomes=dict(preservation=dict(status='PASS',observation='Would repeat218clientbug.'),evidence=dict(status='NOT_TESTED',observation='Not anatomical approval.')))
    with pytest.raises(Exception,match='NATIVE_OUTCOME_HIDES_FAILURE'):review_observations(['preservation','evidence'],REQ,bad,'FAIL')

def test_clean_source_control_keeps_artistic_evidence_untested():
    v=client().build_review(dict(artifacts={}),report(0));rows=review_observations(['preservation','evidence'],REQ,v,'PASS')
    assert [x['status'] for x in rows]==['PASS','NOT_TESTED']
    assert v['cycle_disposition']['category']=='causal_control_only'
