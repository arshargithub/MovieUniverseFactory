"""Offline tests. Synthetic review evidence never qualifies a production asset."""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]

def historical_voice_fixture(root):
    """Synthetic pending-selection state; do not pretend current253 is pending."""
    catalog=json.loads((root/pk.CATALOG).read_text())
    record=next(r for r in catalog['records'] if r['id']=='narrative')
    record.pop('accepted_artifact',None)
    record['unresolved_decision']='select_performed_voice'
    record['decision_exceptions']=[{'task_id':'audio223-preview','operation':'audio','authority_source':'docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md'}]
    (root/pk.CATALOG).write_text(json.dumps(catalog))
    (root/pk.PINS).write_text(json.dumps(pk.freeze(root)))


@pytest.fixture
def root(tmp_path):
    catalog = json.loads((ROOT / pk.CATALOG).read_text())
    paths = [pk.CATALOG, "docs/knowledge/pilot/expectations.json"] + [s["path"] for s in catalog["sources"].values()]
    for path in paths:
        dest = tmp_path / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, dest)
    (tmp_path / pk.PINS).write_text(json.dumps(pk.freeze(tmp_path)))
    return tmp_path


def task(root, operation="contact", entities=None):
    return {"id": "test-only", "operation": operation, "entities": entities or ["hand"],
            "query": "correct grasp", "intent": "credible control without deforming sleeves",
            "phase": "planning", "inputs": {pk.CATALOG: pk.file_hash(root / pk.CATALOG)}, "open_decisions": []}


def test_only_catalog_authorized_audition_bypasses_final_voice_choice(root):
    historical_voice_fixture(root)
    t = task(root, 'audio', ['officer'])
    source = 'docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md'
    t.update(id='audio223-preview', phase='execution',
             execution_authority={'source': source, 'scope': 'authorized audition only'})
    t['inputs'][source] = pk.file_hash(root / source)
    assert pk.task_packet(root, t)['dispatch_ready']
    for change in ({'id': 'unapproved-audition'}, {'operation': 'delivery'}):
        candidate = {**t, **change}
        assert 'DIRECTOR_DECISION:select_performed_voice' in pk.task_packet(root, candidate)['blockers']


def test_reference_analysis_keeps_rights_without_selecting_voice(root):
    historical_voice_fixture(root)
    t = task(root, 'audio_analysis', ['music_reference'])
    p = pk.task_packet(root, t)
    ids = {r['id'] for r in p['obligations']}
    assert {'music_reference', 'sound', 'rights', 'authority'} <= ids
    assert not {'narrative', 'narration_a'} & ids
    # The same operation cannot hide an explicitly affected officer/voice.
    t.update(entities=['officer'], phase='execution')
    assert 'DIRECTOR_DECISION:select_performed_voice' in pk.task_packet(root, t)['blockers']


def review(root, packet):
    evidence = {"path": pk.CATALOG, "sha256": pk.file_hash(root / pk.CATALOG)}
    return {"packet_digest": packet["packet_digest"],
            "checks": [{"id": r["id"], "kind": r["check_kind"], "status": "PASS",
                        "observation": "SYNTHETIC gate test, not actual scene inspection",
                        "action_taken": "Exercised evidence contract", "evidence": [evidence]} for r in packet["obligations"]],
            "hypotheses": [{"prediction": "synthetic defect", "observation": "synthetic inspected evidence",
                            "response": "no issue in synthetic fixture", "result": "not_observed"}],
            "adjacent_regressions": "synthetic neighboring checks", "stopping_reason": "test fixture only"}


def test_coverage_partitions_all_lines(root):
    report = pk.coverage(root)
    assert report["sources"] == len(pk.load(root)[0]['sources'])
    for source in pk.load(root)[1]["sources"].values():
        sections = source["sections"]
        assert sections[0]["start_line"] == 1
        assert sections[-1]["end_line"] == len((root / source["path"]).read_text().splitlines())
        assert all(a["end_line"] + 1 == b["start_line"] for a, b in zip(sections, sections[1:]))
    assert all(r["record_ids"] and r["reason"] for r in report["sections"])


def test_deterministic_graph_closure_and_cycles(root):
    packet = pk.task_packet(root, task(root))
    assert set(packet["entity_versions"]) == {"hand", "arm", "rein", "horse", "shawl", "pashtun"}
    assert {"identity", "contact", "garment", "motion", "secondary"} <= {r["id"] for r in packet["obligations"]}
    assert packet == pk.task_packet(root, task(root))


def test_query_paraphrase_cannot_drop_mandatory_rules(root):
    first = task(root)
    second = {**first, "query": "odd finger silhouette, not a grasp"}
    assert pk.task_packet(root, first)["obligations"] == pk.task_packet(root, second)["obligations"]


def test_248_director_style_and_quality_survive_task_routing(root):
    for operation,entities in [('contact',['hand']),('camera',['shot']),('audio',['officer']),('modeling',['pashtun'])]:
        packet=pk.task_packet(root,task(root,operation,entities))
        actions={r['id']:r['action'] for r in packet['obligations']}
        assert 'larger-than-life' in actions['anticipation']
        assert 'shot/beat performance and believability brief' in actions['anticipation']
        assert 'early proof and observable failure conditions' in actions['anticipation']
        assert 'not lowering' in actions['stopping']
    # A new lead is not silently covered by a Pashtun-only entity graph.
    for character in ('sikh','gurkha'):
        with pytest.raises(pk.KnowledgeError,match='UNRESOLVED'):
            pk.task_packet(root,task(root,'modeling',[character]))


def test_fts_handles_punctuation_and_does_not_promote(root):
    catalog, _ = pk.load(root)
    conn = pk.build_index(root, catalog)
    try:
        for query in ['" OR * NOT (', "single-wrap GPU ban narration", ""]:
            assert isinstance(pk.search(conn, query), list)
    finally:
        conn.close()
    packet = pk.task_packet(root, task(root, "audio", ["officer"]))
    assert next(r for r in packet["obligations"] if r["id"] == "narration_a")["status"] == "adopted"
    #239 adopts Director-led discovery/local finishing, not every delivery
    # proposal. Retrieval must preserve both states rather than promote all.
    assert next(r for r in packet["obligations"] if r["id"] == "sound")["status"] == "adopted"
    assert next(r for r in packet["obligations"] if r["id"] == "captions")["status"] == "proposed"


@pytest.mark.parametrize("mutation", ["source", "catalog", "pins"])
def test_stale_corpus_fails_closed(root, mutation):
    path = {"source": "docs/planning/MOTION_DESIGN_TEMPLATE.md", "catalog": pk.CATALOG, "pins": pk.PINS}[mutation]
    p = root / path
    if mutation == "source":
        p.write_text(p.read_text() + "\nChanged authoritative requirement\n")
    else:
        data = json.loads(p.read_text())
        data["catalog_sha256" if mutation == "pins" else "version"] = "tampered"
        p.write_text(json.dumps(data))
    with pytest.raises(pk.KnowledgeError, match="STALE_CORPUS"):
        pk.task_packet(root, task(root))


@pytest.mark.parametrize("field,value", [("operation", "unknown"), ("entities", ["unmapped-character"])])
def test_unmapped_tasks_block(root, field, value):
    t = task(root)
    t[field] = value
    with pytest.raises(pk.KnowledgeError, match="UNRESOLVED"):
        pk.task_packet(root, t)


def test_missing_and_wrong_input_bindings(root):
    t = task(root)
    t["inputs"] = {}
    assert not pk.task_packet(root, t)["dispatch_ready"]
    t["inputs"] = {pk.CATALOG: "0" * 64}
    assert not pk.task_packet(root, t)["dispatch_ready"]


def test_execution_needs_authority_and_decisions(root):
    historical_voice_fixture(root)
    t = task(root, "audio", ["officer"])
    t.update(phase="execution", open_decisions=["script and voice"])
    result = pk.task_packet(root, t)
    assert "MISSING_EXECUTION_AUTHORITY" in result["blockers"]
    assert "DIRECTOR_DECISION:script and voice" in result["blockers"]
    t["execution_authority"] = {"source": "unbound.md", "scope": "claimed"}
    assert "UNBOUND_EXECUTION_AUTHORITY" in pk.task_packet(root, t)["blockers"]
    t["open_decisions"] = []
    t["execution_authority"] = {"source": pk.CATALOG, "scope": "synthetic claimed authority"}
    assert "DIRECTOR_DECISION:select_performed_voice" in pk.task_packet(root, t)["blockers"]


def test_proposed_creative_option_is_not_promoted_by_search(root):
    catalog=json.loads((root/pk.CATALOG).read_text())
    record=next(r for r in catalog['records'] if r['id']=='narration_a')
    record.update(status='proposed',kind='creative_option')
    (root/pk.CATALOG).write_text(json.dumps(catalog))
    (root/pk.PINS).write_text(json.dumps(pk.freeze(root)))
    t=task(root,'audio',['officer']);t['query']='Use narration A'
    assert 'narration_a' not in {r['id'] for r in pk.task_packet(root,t)['obligations']}


def test_context_limit_blocks_without_dropping_obligations(root):
    t = task(root)
    t["max_context_characters"] = 1
    packet = pk.task_packet(root, t)
    assert "CONTEXT_TOO_LARGE_SPLIT_TASK_DO_NOT_TRUNCATE" in packet["blockers"]
    assert "contact" in {r["id"] for r in packet["obligations"]}


def test_independent_oracle_regressions(root):
    assert pk.evaluate(root)["passed"]


def test_missing_contact_edge_reproduces_held_out_miss(root):
    catalog = json.loads((root / pk.CATALOG).read_text())
    catalog["edges"].remove(["arm", "depends_on", "hand"])
    (root / pk.CATALOG).write_text(json.dumps(catalog))
    (root / pk.PINS).write_text(json.dumps(pk.freeze(root)))
    report = pk.evaluate(root)
    assert not report["passed"]
    assert [r["id"] for r in report["cases"] if "contact" in r["missing_critical"]] == ["neck", "shawl"]


def test_gate_accepts_only_complete_current_synthetic_evidence(root):
    packet = pk.task_packet(root, task(root))
    assert pk.check_review(root, packet, review(root, packet))["ready_for_review"]


@pytest.mark.parametrize("failure", ["missing_check", "fail", "not_run", "no_evidence", "no_action", "no_observation", "wrong_kind", "stale_evidence", "duplicate", "unknown", "hypothesis", "regressions", "stop", "review_digest"])
def test_negative_gate_cases(root, failure):
    packet = pk.task_packet(root, task(root))
    r = review(root, packet)
    c = r["checks"][0]
    if failure == "missing_check":
        r["checks"].pop()
    elif failure in {"fail", "not_run"}:
        c["status"] = failure.upper()
    elif failure == "no_evidence":
        c["evidence"] = []
    elif failure == "no_action":
        c["action_taken"] = ""
    elif failure == "no_observation":
        c["observation"] = ""
    elif failure == "wrong_kind":
        c["kind"] = "numeric-test-is-visual-pass"
    elif failure == "stale_evidence":
        c["evidence"][0]["sha256"] = "0" * 64
    elif failure == "duplicate":
        r["checks"].append(copy.deepcopy(c))
    elif failure == "unknown":
        r["checks"].append({**c, "id": "unknown"})
    elif failure == "hypothesis":
        r["hypotheses"][0]["result"] = "unresolved"
    elif failure == "regressions":
        r["adjacent_regressions"] = ""
    elif failure == "stop":
        r["stopping_reason"] = ""
    else:
        r["packet_digest"] = "0" * 64
    assert not pk.check_review(root, packet, r)["ready_for_review"]


def test_modified_packet_and_changed_task_cannot_reuse_review(root):
    packet = pk.task_packet(root, task(root))
    r = review(root, packet)
    packet["obligations"].pop()
    assert not pk.check_review(root, packet, r)["ready_for_review"]
    packet = pk.task_packet(root, task(root))
    packet["task"]["query"] = "camera now closer"
    assert not pk.check_review(root, packet, r)["ready_for_review"]


@pytest.mark.parametrize("path", ["../outside", ".env", ".env.local", ".git/config", ".aws/config", "/etc/passwd"])
def test_private_and_traversal_paths_block(root, path):
    with pytest.raises(pk.KnowledgeError):
        pk.safe_path(root, path)


def test_symlink_escape_blocks(root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "private"
    outside.write_text("not for indexing")
    (root / "linked").symlink_to(outside)
    with pytest.raises(pk.KnowledgeError):
        pk.safe_path(root, "linked")


def test_invalid_catalog_edges_and_duplicate_records(root):
    catalog, _ = pk.load(root)
    catalog["edges"].append(["hand", "invented", "arm"])
    with pytest.raises(pk.KnowledgeError):
        pk.validate_catalog(catalog)
    catalog["edges"].pop()
    catalog["records"].append(catalog["records"][0])
    with pytest.raises(pk.KnowledgeError):
        pk.validate_catalog(catalog)


def test_fresh_process_rebuild_produces_identical_packet(root):
    t = task(root)
    taskfile = root / "task.json"
    taskfile.write_text(json.dumps(t))
    target = ".runtime/knowledge-pilot213/fresh.json"
    result = subprocess.run([sys.executable, "-m", "movie_factory.production_knowledge", "--root", str(root), "packet", "--task", "task.json", "--output", target], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads((root / target).read_text()) == pk.task_packet(root, t)


def test_cli_refuses_source_overwrite_and_refreeze(root):
    assert pk.main(["--root", str(root), "coverage", "--output", pk.CATALOG]) == 2
    assert pk.main(["--root", str(root), "freeze", "--output", pk.PINS]) == 2


def test_cli_error_replaces_old_success_output(root):
    target = ".runtime/knowledge-pilot213/coverage.json"
    args = ["--root", str(root), "coverage", "--output", target]
    assert pk.main(args) == 0
    path = root / "docs/planning/MOTION_DESIGN_TEMPLATE.md"
    path.write_text(path.read_text() + "\nUnreviewed change\n")
    assert pk.main(args) == 2
    assert json.loads((root / target).read_text())["passed"] is False
