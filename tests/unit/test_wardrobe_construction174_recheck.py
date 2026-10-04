import importlib.util
from pathlib import Path
import inspect
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('recheck174',ROOT/'scripts/wardrobe_construction174_recheck.py')
module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


@pytest.mark.parametrize('job',[{},None,{'operation':'verify01'},{'operation':'verify02','code':'x'}])
def test_fixed_recheck_only(job):
    with pytest.raises(ValueError,match='Fixed'):module.validate(job)


def test_selected_artifact_is_not_rebuilt_or_saved():
    text = inspect.getsource(module.main)
    assert 'verify(' in text and 'seal(' not in text and 'save_as' not in text
    text = (ROOT/'scripts/wardrobe_construction174_verify.py').read_text()
    assert 'mats = studio.make_materials()' in text
    assert "bpy.data.materials['MF_173_'" not in text


def test_native_recheck_does_not_import_outer_packaging_runtime():
    text = inspect.getsource(module.validate)
    assert 'import package_wardrobe' not in text
    assert "verification-binding03.json" in text


def test_neutral_replay_restores_initial_belt_shell_before_construction():
    text = (ROOT/'scripts/wardrobe_construction174_verify.py').read_text()
    assert 'initial_shell = (original_shell.thickness,original_shell.offset)' in text
    assert 'thickness.thickness,thickness.offset = initial_shell' in text
