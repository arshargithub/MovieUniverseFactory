import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('recovery_exit',Path(__file__).resolve().parents[2]/'scripts/calibration255_gate.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

def test_missing_remote_evidence_blocks(tmp_path):
    assert not gate.recovery_ready(tmp_path)

def test_remote_inventory_alone_is_not_scene_restore(tmp_path):
    out=tmp_path/'results/backup/protect255';out.mkdir(parents=True)
    (out/'final-verification.json').write_text(json.dumps({'recovery_copy_verified':True,
        'snapshot_id':'protect255-20261013-final','inventory':{'all_expected_keys_and_sizes_match':True}}))
    (out/'remote-capsule-restore.json').write_text('{}')
    assert not gate.recovery_ready(tmp_path)

def test_exact_restore_identity_required(tmp_path):
    out=tmp_path/'results/backup/protect255';out.mkdir(parents=True)
    (out/'final-verification.json').write_text(json.dumps({'recovery_copy_verified':True,
        'snapshot_id':'protect255-20261013-final','inventory':{'all_expected_keys_and_sizes_match':True}}))
    restore={'all_hashes_match':True,'native_dependency_checks_pass':True,'files':61,'native_reopens':2,
        'clean_sha256':'1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'}
    target=out/'remote-capsule-restore.json';target.write_text(json.dumps(restore))
    assert gate.recovery_ready(tmp_path)
    restore['clean_sha256']='0'*64;target.write_text(json.dumps(restore))
    assert not gate.recovery_ready(tmp_path)
