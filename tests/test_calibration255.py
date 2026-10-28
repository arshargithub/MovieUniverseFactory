"""New current-authority tests plus synthetic application/invalidations."""
import copy
import json
import re
import subprocess
import sys
from pathlib import Path
import pytest
from movie_factory import production_knowledge as pk
from test_production_knowledge import root, task, review

def test_new_source_lessons_route(root):
    source=Path(__file__).resolve().parents[1]/'docs/knowledge/pilot/calibration255-cases.json'
    dest=root/'docs/knowledge/pilot/calibration255-cases.json';dest.write_bytes(source.read_bytes())
    assert pk.evaluate(root,str(dest.relative_to(root)))['passed']

def test_provisional_does_not_approve_new_voice_or_release(root):
    t=task(root,'audio',['officer']);t.update(phase='execution')
    source='docs/knowledge/CURRENT_PRODUCTION_STATE.md'
    t['inputs'][source]=pk.file_hash(root/source)
    t['execution_authority']={'source':source,'scope':'synthetic new take'}
    assert 'DIRECTOR_DECISION:approve_new_narration_or_bind_accepted_unit' in pk.task_packet(root,t)['blockers']
    # Exact content, not a caller-supplied claim of acceptance, must be bound.
    t['preserve_accepted_artifact']='wrong'
    assert not pk.task_packet(root,t)['dispatch_ready']

def test_bound_reuse_requires_real_content_and_authority(root):
    # Small synthetic accepted artifact exercises the same binding mechanism.
    p=root/'accepted.txt';p.write_text('synthetic accepted picture')
    c=json.loads((root/pk.CATALOG).read_text());n=next(x for x in c['records'] if x['id']=='narrative')
    n['accepted_artifact'].update(path='accepted.txt',sha256=pk.file_hash(p))
    (root/pk.CATALOG).write_text(json.dumps(c));(root/pk.PINS).write_text(json.dumps(pk.freeze(root)))
    t=task(root,'audio',['officer']);source='docs/knowledge/CURRENT_PRODUCTION_STATE.md'
    t.update(phase='execution',preserve_accepted_artifact=pk.file_hash(p),execution_authority={'source':source,'scope':'synthetic exact reuse'})
    t['inputs'].update({'accepted.txt':pk.file_hash(p),source:pk.file_hash(root/source)})
    # Refresh catalog input after constructing this synthetic fixture.
    t['inputs'][pk.CATALOG]=pk.file_hash(root/pk.CATALOG)
    packet=pk.task_packet(root,t);assert packet['dispatch_ready']
    p.write_text('changed content')
    assert not pk.task_packet(root,t)['dispatch_ready']
    assert not pk.check_review(root,packet,review(root,packet))['ready_for_review']

def test_current_authority_excludes_old_pending_claim(root):
    packet=pk.task_packet(root,task(root,'knowledge',['knowledge']))
    current=next(r for r in packet['obligations'] if r['id']=='current_state')['action']
    #257 added Sikh onboarding and revised wording; test current authority,
    #not obsolete literal phrases or a deliberately superseded unknown entity.
    # Meaning-bearing anchors, not one obsolete full sentence. The exact asset
    # hash and execution/release negative controls below remain independently bound.
    assert all(x in current for x in ['253', 'Pashtun20s', 'provisional', 'Preserve accepted'])
    assert re.search(r'strict replay\s*FAIL', current)
    assert all(x in current for x in ['rights', 'final release', 'separate'])
    record=next(x for x in json.loads((root/pk.CATALOG).read_text())['records'] if x['id']=='narrative')
    assert record['accepted_artifact']['sha256']=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    assert record['unresolved_decision']=='approve_new_narration_or_bind_accepted_unit'
    source=(root/'docs/knowledge/CURRENT_PRODUCTION_STATE.md').read_text()
    assert 'Final pass occurs only when the full trailer is approved for release' in source
    assert pk.task_packet(root,task(root,'modeling',['sikh']))['obligations']
    for name in ['gurkha','unmapped_new_asset']:
        with pytest.raises(pk.KnowledgeError,match='UNRESOLVED_ENTITY'):
            pk.task_packet(root,task(root,'modeling',[name]))

def test_application_gate_cannot_validate_semantic_truth(root):
    packet=pk.task_packet(root,task(root));r=review(root,packet)
    assert pk.check_review(root,packet,r)['ready_for_review']
    # This is the disclosed boundary: fabricated-but-well-formed assertions pass.
    # Never call this a visual quality proof. Manual evidence review is mandatory.
    r['checks'][0]['observation']='SYNTHETIC unsupported positive claim'
    assert pk.check_review(root,packet,r)['ready_for_review']
    r['checks'][0]['status']='NOT_RUN'
    assert not pk.check_review(root,packet,r)['ready_for_review']

def test_fresh_process_reconstructs_same_packet(root,tmp_path):
    t=task(root,'knowledge',['knowledge']);f=root/'task.json';f.write_text(json.dumps(t))
    direct=pk.task_packet(root,t)
    code='import json;from pathlib import Path;from movie_factory import production_knowledge as p;r=Path(__import__("sys").argv[1]);print(json.dumps(p.task_packet(r,json.loads((r/"task.json").read_text()))))'
    child=subprocess.check_output([sys.executable,'-c',code,str(root)])
    assert json.loads(child)==direct

def test_review_issue_metadata_survives_ledger_roundtrip(tmp_path):
    from movie_factory.experiment_ledger import Ledger
    ledger=Ledger(tmp_path/'isolated.sqlite3')
    event={'event_id':'synthetic-review-1','experiment_id':'SIMULATED-CAL255','episode_id':'one',
           'utc':'2026-10-13T00:00:00+00:00','event_type':'human_review','phase':'rough',
           'review_id':'R1','artifact_sha256':'synthetic-only','issue_id':'I1','detected_by':'director',
           'discovery_phase':'integrated_review','repeated_from':None,'classification':'escaped_defect',
           'cause':'judgment','disposition':'reopen_same_issue','revision_radius':['hand','rein','sleeve']}
    assert ledger.append(event)
    assert not ledger.append(event)
    row=ledger.events()[0]
    for key in ('issue_id','review_id','discovery_phase','repeated_from','cause','revision_radius'):
        assert row[key]==event[key]
