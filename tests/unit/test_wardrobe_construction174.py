import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('wardrobe_construction174', Path(__file__).resolve().parents[2] / 'scripts/wardrobe_construction174.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec'}, {'operation': 'probe01', 'code': 'x'}, {'operation': 'probe01', 'path': '/tmp'}])
def test_enum_only(job):
    with pytest.raises(ValueError): module.validate(job)


def test_pin_no_overwrite(monkeypatch, tmp_path):
    source = tmp_path / 'input.blend'; source.touch()
    monkeypatch.setattr(module, 'SOURCE', source)
    monkeypatch.setattr(module, 'BASE', tmp_path)
    monkeypatch.setattr(module, 'digest', lambda p: module.SOURCE_SHA)
    out = module.validate({'operation': 'probe01'}); out.mkdir()
    with pytest.raises(ValueError, match='overwrite'): module.validate({'operation': 'probe01'})
    monkeypatch.setattr(module, 'digest', lambda p: 'bad')
    with pytest.raises(ValueError, match='Pinned'): module.validate({'operation': 'preview01'})


def test_hem_folds_release_only_below_belt():
    assert module.hem_fold(1, -.5, -4.5) == 0
    assert module.hem_fold(1, -.5, -5.42) == 0
    assert 0 <= module.hem_fold(1, -.5, -6.7) < .15


def test_fixed_function_replacements_and_no_paid_dispatch():
    import inspect
    text = inspect.getsource(module.install)
    assert 'sculpt_fabric = sculpt' in text and 'construct_scarf = construct' in text
    assert 'leather_paths = leather' in text
    text = inspect.getsource(module.leather)
    assert 'skin' in text and 'cloth' in text and 'end_weight' in text


def test_connected_sheet_has_shared_column_edges_and_no_duplicate_faces():
    faces = module.sheet_faces(223)
    assert len(faces) == 222*40
    assert len(set(faces)) == len(faces)
    assert min(min(f) for f in faces) == 0
    assert max(max(f) for f in faces) == 223*41-1
    edges = {}
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            key = tuple(sorted((a,b))); edges[key] = edges.get(key,0)+1
    assert set(edges.values()) == {1,2}
    assert sum(n==1 for n in edges.values()) == 2*222+2*40


def test_whole_sheet_settle_is_frozen_and_restores_scene_state():
    import inspect
    text = inspect.getsource(module.settle_connected)
    assert 'no shoulder clips' in text and 'j<=23' in text
    assert 'evaluated.to_mesh' in text and 'ob.modifiers.remove(cloth)' in text
    assert 'scene.gravity = gravity' in text and 'scene.frame_set(original_frame)' in text
    assert 'MF_studio_adult_body' in text and 'MF_173_static_groom_clearance' in text


def test_legacy_end_mapping_is_not_applied_to_connected_sheet():
    import inspect
    text = inspect.getsource(module.install)
    assert 'compress_cloth = no_legacy_mapping' in text
    assert 'tuck_scarf_ends = no_legacy_mapping' in text


def test_shoulder_cleanup_does_not_select_crown_chest_center_or_hem():
    assert module.shoulder_cleanup_weight(0,-2)==0
    assert module.shoulder_cleanup_weight(1.5,.5)==0
    assert module.shoulder_cleanup_weight(1.5,-5)==0
    assert module.shoulder_cleanup_weight(1.5,-2)>0.9


def test_layering_separates_free_head_fall_from_loaded_wrap():
    import inspect
    assert 'MF_174_wrap_under_harness' in inspect.getsource(module.construct)
    assert 'layer[index].value' in inspect.getsource(module.layered_pressure)
    text = inspect.getsource(module.leather)
    assert 'original_centers' in text and 'clearance' in text
    assert 'studio.torso_matrix(q.z)' in text


def test_selected_dispatch_requires_binding(monkeypatch,tmp_path):
    source = tmp_path/'input.blend';source.touch()
    monkeypatch.setattr(module,'SOURCE',source)
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA)
    with pytest.raises(ValueError,match='Freeze selected'):
        module.validate({'operation':'seal01'})


def test_binding_rejects_extra_or_traversal_paths(monkeypatch,tmp_path):
    import json
    monkeypatch.setattr(module,'BASE',tmp_path)
    folder = tmp_path/'wardrobe174-operating';folder.mkdir()
    (folder/'source-binding.json').write_text(json.dumps({'source_files':[{'path':'../wrong.py','sha256':'bad'}]}))
    with pytest.raises(ValueError,match='Unexpected source'):
        module.source_binding()


def test_selected_save_and_reopen_are_separate_from_appearance():
    import inspect
    assert 'full=True' in inspect.getsource(module.seal)
    assert 'use_module = False' in inspect.getsource(module.seal)
    assert "'visual_gate':'NOT_RUN'" in inspect.getsource(module.seal)
    spec = importlib.util.spec_from_file_location('verify174',Path(module.__file__).with_name('wardrobe_construction174_verify.py'))
    verifier = importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    text = inspect.getsource(verifier.verify)
    assert 'use_scripts=False' in text and 'allow_pickle=False' in text
    assert 'rollback' in text and 'protected_signatures_exact' in text


def test_belt_entry_target_cannot_dip_below_then_return_up():
    values = [module.end_approach_z(i) for i in range(25)]
    assert values==sorted(values)
    assert values[0]==pytest.approx(-5.12)
    assert values[-1]==pytest.approx(-4.67)
    assert module.end_approach_z(-10)==values[0]
