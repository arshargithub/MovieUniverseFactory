import importlib.util
from pathlib import Path
import pytest
import json
spec=importlib.util.spec_from_file_location('s331',Path(__file__).resolve().parents[1]/'scripts/sikh331.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def test_contract():
    assert m.validate({'operation':'inspect','version':1,'frames':[283]})
@pytest.mark.parametrize('change',[{'operation':'eval'},{'version':True},{'version':21},{'frames':[1]},{'frames':[283.0]},{'frames':[]},{'code':'pass'}])
def test_reject(change):
    with pytest.raises(ValueError):m.validate({'operation':'inspect','version':1,'frames':[283],**change})
def test_pose_contract():
    from movie_factory.sikh331_motion import pose,POSES
    assert all(b[0]>a[0] for a,b in zip(POSES,POSES[1:]))
    assert pose(327)['drop']<.1  # lower than inherited near-straight-support crest
    assert pose(353)['drop']<pose(348)['drop']
    assert pose(441)==pose(252)
def test_closed_package_cannot_launch_or_prepare(tmp_path):
    p=tmp_path/'results/sikh331/STATUS.json';p.parent.mkdir(parents=True)
    p.write_text(json.dumps({'native_dispatch_closed':True}))
    with pytest.raises(ValueError,match='SIKH331_REPLAN_REQUIRED'):m.require_open(tmp_path)
def test_incomplete_closure_fails_closed(tmp_path):
    p=tmp_path/'results/sikh331/STATUS.json';p.parent.mkdir(parents=True)
    p.write_text('{}')
    with pytest.raises(ValueError):m.require_open(tmp_path)
def test_actual_closeout_never_claims_prospective_success():
    root=Path(__file__).resolve().parents[1]
    status=json.loads((root/'results/sikh331/STATUS.json').read_text())
    report=json.loads((root/status['controller_record']).read_text())
    assert status['remaining_corrections']==report['remaining_corrections']==0
    assert report['stage']=='REPLAN_REQUIRED'
    assert report['chronology']=='RETROSPECTIVE_NOT_PROSPECTIVE'
    assert not status['review_ready'] and not report['production_ready']
    assert {'P1','P2','P4','P7'} <= set(report['findings']['failures'])
