import importlib.util
from pathlib import Path
import math
import pytest

spec=importlib.util.spec_from_file_location('wardrobe_outer175',Path(__file__).resolve().parents[2]/'scripts/wardrobe_outer175.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'}, {'operation':'preview01','code':'x'}, {'operation':'preview01','path':'/tmp'}])
def test_enum_only(job):
    with pytest.raises(ValueError):m.validate(job)

def test_pinned_no_overwrite(monkeypatch,tmp_path):
    monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m.prior,'digest',lambda p:m.SOURCE_SHA)
    out=m.validate({'operation':'preview01'});out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):m.validate({'operation':'preview01'})
    monkeypatch.setattr(m.prior,'digest',lambda p:'bad')
    with pytest.raises(ValueError,match='Pinned'):m.validate({'operation':'preview02'})

def test_two_broad_offset_exterior_courses():
    for i in range(181):
        points=[m.route_point(i,j/40) for j in range(41)]
        assert all(math.isfinite(c) and abs(c)<5 for p in points for c in p)
        # Narrow shoulder crossing, broader chest/rear courses by design.
        assert math.dist(points[-1],points[0])>.60
    assert m.route_point(90,.5)[1]>m.route_point(0,.5)[1]
    assert m.route_point(135,.5)[2]<m.route_point(45,.5)[2]
    # Cloth lies across the shoulder, not a standing vertical collar.
    a,b=m.route_point(22.5,0),m.route_point(22.5,1)
    assert abs(a[0]-b[0])>.5 and abs(a[2]-b[2])<.2

def test_outer_layer_does_not_call_legacy_pressure():
    import inspect
    assert 'ORIGINAL_PRESS' not in inspect.getsource(m.outer_clearance)
    assert 'press_visible_scarf=outer_clearance' in inspect.getsource(m.install)

def test_construction_solve_uses_current_pose_harness_and_outer_start():
    import inspect
    text=inspect.getsource(m.construct)
    assert text.index('prior.leather(frame,mats)')<text.index('outer_clearance(False)')<text.index('loft_shoulders(ob)')
    assert "ob['MF_175_construction_settled']=False" in text
    assert 'settle_shoulders(ob)' not in text
    assert 'assembled overlapping static surfaces' in text

def test_local_solve_protects_chest_rear_head_and_broad_ends():
    assert all(m.shoulder_freedom(i)==0 for i in (0,45,90,135,180,190,210,242))
    assert m.shoulder_freedom(22.5)==1 and m.shoulder_freedom(112.5)==1

def test_outer_layer_excludes_obsolete_hidden_wrap_from_leather_support():
    import inspect
    assert 'MF_173_diagonal_scarf_fall' not in inspect.getsource(m.tunic_support_cloud)
    assert 'support_cloud=tunic_support_cloud' in inspect.getsource(m.install)

def test_common_rear_drape_does_not_change_crown_front_or_neutral():
    assert m.rear_drop(0,1.8,-2)==0
    assert m.rear_drop(.6,-1.5,-2)==0
    assert m.rear_drop(.6,1.8,.5)==0
    assert 0<m.rear_drop(.6,1.8,-2)<=1.1

def test_binding_has_fixed_sources_and_no_credentials():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
    import wardrobe_outer175_evidence as evidence
    assert Path(m.__file__) in evidence.source_paths()
    assert Path(evidence.__file__) in evidence.source_paths()
    assert len(set(evidence.source_paths()))==len(evidence.source_paths())
    assert all('.env' not in str(p) for p in evidence.source_paths()+evidence.input_paths())

def test_manifest_rejects_extra_paths(monkeypatch,tmp_path):
    import wardrobe_outer175_evidence as evidence
    monkeypatch.setattr(evidence,'OUT',tmp_path)
    evidence.write(tmp_path/'source-binding.json',{'source_files':[{'path':'.env'}]})
    with pytest.raises(ValueError,match='Unexpected'):evidence.binding()

def test_gallery_binds_real_png_names_and_approved_pair():
    import wardrobe_outer175_evidence as evidence
    frames=evidence.gallery_frames()
    assert len(frames)==19
    assert frames[0][0].name=='frontal-v02-individualized.png'
    assert frames[1][0].name=='portrait-v07-individualized.png'
    assert all(p.suffix=='.png' and label and short for p,short,label in frames)
    assert any(p.name=='mounted-upper-rear.png' for p,_,_ in frames)
    assert evidence.BASE/'wardrobe174-seal01/result.json' in evidence.input_paths()


def test_failure_receipt_cannot_present_ready_candidate(monkeypatch,tmp_path):
    import wardrobe_outer175_evidence as evidence
    monkeypatch.setattr(evidence,'OUT',tmp_path)
    evidence.write(tmp_path/'method-disposition.json',{'status':'PASS'})
    with pytest.raises(AssertionError):evidence.failure()


def test_failure_receipt_cannot_hide_existing_selected_bundle(monkeypatch,tmp_path):
    import wardrobe_outer175_evidence as evidence
    monkeypatch.setattr(evidence,'OUT',tmp_path)
    monkeypatch.setattr(evidence,'BASE',tmp_path)
    evidence.write(tmp_path/'method-disposition.json',{
        'status':'FAILED_INTERNAL_REVIEW_DIRECTOR_DECISION_REQUIRED',
        'known_blockers':['broken rear route'],
        'Director_acceptance':'NOT_REQUESTED_FOR_FAILED_CANDIDATE'})
    (tmp_path/'wardrobe175-seal01').mkdir()
    with pytest.raises(AssertionError):evidence.failure()
