import importlib.util
from pathlib import Path
import pytest

FILE = Path(__file__).resolve().parents[2] / 'src/movie_factory/adapters/blender/body_studio_fit.py'
spec = importlib.util.spec_from_file_location('body_studio_fit', FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('job', [{}, {'operation':'inspect01','path':'/tmp/other'}, {'operation':'exec'}, None])
def test_reject_nonfixed_jobs(job):
    with pytest.raises(ValueError):
        module.validate(job)


def test_reject_changed_source(monkeypatch):
    monkeypatch.setattr(module, 'digest', lambda p: '0'*64)
    with pytest.raises(ValueError, match='Pinned'):
        module.validate({'operation':'inspect01'})


def test_chest_blend_is_continuous_and_bounded():
    assert module.chest_blend(-4)==0
    assert module.chest_blend(-1)==1
    values=[module.chest_blend(-3.1+i*.01) for i in range(131)]
    assert all(0<=v<=1 for v in values)
    assert values==sorted(values)
    assert max(b-a for a,b in zip(values,values[1:]))<.014


def test_fixed_fit_job_and_no_overwrite(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    out=module.validate({'operation':'fit04'})
    out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):
        module.validate({'operation':'fit04'})


def test_weight_sharpening_preserves_sum_support_and_dominance():
    result=module.sharpen_weights({'upper':.8,'lower':.2,'hand':0})
    assert sum(result.values())==pytest.approx(1)
    assert result['upper']>.8 and result['hand']==0
    assert module.sharpen_weights({})=={}
    assert module.sharpen_weights({'a':.5,'b':.5})=={'a':.5,'b':.5}


@pytest.mark.parametrize('operation', ['fit17','fit18','fit19','fit20','fit21','fit22','fit23','fit24','fit25','fit26','fit27'])
def test_correction_operations_are_fixed_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    job={'operation':operation}
    path=module.validate(job)
    assert path.name=='body158-'+operation
    with pytest.raises(ValueError):module.validate({**job,'code':'anything'})
    path.mkdir()
    with pytest.raises(ValueError):module.validate(job)


@pytest.mark.parametrize('job', [{'operation':'fit40'}, {'operation':'fit27','path':'other'}, {'operation':'fit27','python':'pass'}])
def test_correction_rejects_unreviewed_variants_and_payload(job):
    with pytest.raises(ValueError):module.validate(job)


@pytest.mark.parametrize('operation',['fit28','fit29','fit30','fit31','fit32','fit33'])
def test_restored_bust_outputs_are_separate(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    path=module.validate({'operation':operation})
    assert path.name=='body159-'+operation
    path.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':operation})


def test_lateral_shoulder_weight_is_continuous_at_source_boundary():
    values=[module.shoulder_chest_weight(1.5,-2.5+i*.01) for i in range(121)]
    assert all(0<=v<=1 for v in values)
    assert values==sorted(values)
    assert max(b-a for a,b in zip(values,values[1:]))<.012
    assert module.shoulder_chest_weight(1.5,-1.9)<.6
    assert module.shoulder_chest_weight(.5,-1.8)==1.


@pytest.mark.parametrize('operation',['fit34','fit35','fit36','fit37','fit38','fit39'])
def test_continuous_donor_operations_are_fixed(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    path=module.validate({'operation':operation})
    assert path.name=='body160-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'path':'other'})
    path.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':operation})


def test_anatomical_support_fades_with_flat_endpoints():
    assert module.smooth_transition(-.1)==0
    assert module.smooth_transition(1.1)==1
    assert module.smooth_transition(.001)<1e-7
    assert 1-module.smooth_transition(.999)<1e-7
