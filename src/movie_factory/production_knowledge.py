"""Local, source-bound production context pilot. No providers or Blender execution.

Catalog records are curated interpretations, not new approvals. Search is advisory;
the deterministic route carries obligations. CLI exit codes are enforceable by a
caller, but do not intercept unrelated shell/Blender jobs or judge image quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

CATALOG = "docs/knowledge/pilot/catalog.json"
PINS = "docs/knowledge/pilot/source-pins.json"
SCHEMA = 1
ACTIVE = {"adopted", "supported"}
STATUSES = ACTIVE | {"proposed", "superseded", "contradicted", "rejected"}
EDGE_TYPES = {"contacts", "depends_on", "adjacent_to", "part_of", "connects_to", "supported_by", "shows"}


class KnowledgeError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_path(root, value):
    """Only explicit project paths. Never follow symlinks outside or admit secrets."""
    p = Path(value)
    if p.is_absolute() or ".." in p.parts or any(
        part in {".git", ".aws", ".env", ".venv"} or part.startswith(".env.") for part in p.parts
    ):
        raise KnowledgeError(f"disallowed project path: {value}")
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise KnowledgeError(f"missing/outside project: {value}")
    return resolved


def read_json(root, value):
    return json.loads(safe_path(root, value).read_text())


def sections(text):
    """Partition all lines, including introduction, into stable heading occurrences."""
    lines = text.splitlines(keepends=True)
    starts = [(i, line.strip()) for i, line in enumerate(lines) if re.match(r"^#{1,6} ", line)]
    if not starts or starts[0][0]:
        starts.insert(0, (0, "preamble"))
    result = []
    for n, (start, heading) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        body = "".join(lines[start:end])
        result.append({"heading": heading, "start_line": start + 1, "end_line": end,
                       "sha256": hashlib.sha256(body.encode()).hexdigest()})
    return result


def validate_catalog(catalog):
    if catalog.get("schema_version") != SCHEMA:
        raise KnowledgeError("unsupported catalog schema")
    records = catalog["records"]
    ids = [r["id"] for r in records]
    if len(set(ids)) != len(ids):
        raise KnowledgeError("duplicate record ID")
    for r in records:
        if r["status"] not in STATUSES or not r["action"].strip() or not r["sources"] or not r["tags"]:
            raise KnowledgeError(f"invalid record: {r['id']}")
        if any(s not in catalog["sources"] for s in r["sources"]):
            raise KnowledgeError(f"unknown source: {r['id']}")
        if r.get("superseded_by") and r["superseded_by"] not in ids:
            raise KnowledgeError("unknown replacement")
    for source in catalog["sources"].values():
        if not source["reason"].strip() or not source["records"] or set(source["records"]) - set(ids):
            raise KnowledgeError("unmapped source")
    for start, relation, end in catalog["edges"]:
        if start not in catalog["entities"] or end not in catalog["entities"] or relation not in EDGE_TYPES:
            raise KnowledgeError("invalid graph edge")


def source_snapshot(root, catalog):
    result = {}
    for key, s in catalog["sources"].items():
        if not s["path"].startswith("docs/"):
            raise KnowledgeError("corpus sources must be explicit docs paths")
        p = safe_path(root, s["path"])
        result[key] = {"path": s["path"], "sha256": file_hash(p), "sections": sections(p.read_text())}
    return result


def freeze(root):
    catalog = read_json(root, CATALOG)
    validate_catalog(catalog)
    return {"schema_version": SCHEMA, "catalog_sha256": digest(catalog),
            "sources": source_snapshot(root, catalog),
            "method": "Reviewed nine-document corpus frozen explicitly; re-freezing is not an audit or automatic acceptance of source changes."}


def load(root):
    catalog = read_json(root, CATALOG)
    validate_catalog(catalog)
    pins = read_json(root, PINS)
    if pins.get("catalog_sha256") != digest(catalog) or pins.get("sources") != source_snapshot(root, catalog):
        raise KnowledgeError("STALE_CORPUS: inspect changed sources/catalog, amend records and tests, then explicitly re-freeze")
    return catalog, pins


def build_index(root, catalog, db=":memory:"):
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge USING fts5(id UNINDEXED, status UNINDEXED, body);
        DELETE FROM knowledge;
        CREATE TABLE IF NOT EXISTS edges (source TEXT, relation TEXT, target TEXT);
        DELETE FROM edges;
    """)
    for r in catalog["records"]:
        # Include actual source text for discovery; it never determines current authority.
        body = r["action"] + "\n" + "\n".join(safe_path(root, catalog["sources"][s]["path"]).read_text() for s in r["sources"])
        conn.execute("INSERT INTO knowledge VALUES (?,?,?)", (r["id"], r["status"], body))
    conn.executemany("INSERT INTO edges VALUES (?,?,?)", catalog["edges"])
    conn.commit()
    return conn


def search(conn, query, limit=5):
    # Quote tokens to prevent user FTS operators/syntax from becoming query logic.
    words = re.findall(r"\w+", query, flags=re.UNICODE)[:32]
    if not words:
        return []
    expression = " OR ".join('"' + w + '"' for w in words)
    return [{"id": row[0], "status": row[1], "role": "supporting_only"} for row in conn.execute(
        "SELECT id,status FROM knowledge WHERE knowledge MATCH ? ORDER BY bm25(knowledge),id LIMIT ?", (expression, limit))]


def coverage(root):
    catalog, pins = load(root)
    rows = []
    for key, source in pins["sources"].items():
        for sec in source["sections"]:
            rows.append({"source": key, **sec, "disposition": "reviewed_source_context",
                         "record_ids": catalog["sources"][key]["records"],
                         "reason": catalog["sources"][key]["reason"]})
    return {"schema_version": SCHEMA, "corpus_digest": digest(pins), "sources": len(pins["sources"]),
            "section_count": len(rows), "sections": rows, "gaps": catalog["gaps"],
            "limit": "Every section inventoried after full-source reading; source-to-record mapping is broad. Not independent semantic proof that every sentence became a rule. Deep linked sources remain outside this audit."}


def task_packet(root, task):
    catalog, pins = load(root)
    required = {"id", "operation", "entities", "query", "intent", "phase", "inputs", "open_decisions"}
    if required - task.keys() or task["phase"] not in {"planning", "execution"}:
        raise KnowledgeError("incomplete task or invalid phase")
    if not task["intent"].strip() or not task["entities"] or not isinstance(task["inputs"], dict):
        raise KnowledgeError("task needs explicit intent/entities/input bindings")
    if task["operation"] not in catalog["operations"]:
        raise KnowledgeError("UNRESOLVED_OPERATION: audit and map before dispatch")
    if any(e not in catalog["entities"] for e in task["entities"]):
        raise KnowledgeError("UNRESOLVED_ENTITY: audit missing dependencies before dispatch")
    reached = {e: "explicit task entity" for e in task["entities"]}
    queue = list(reached)
    traversed = []
    while queue:
        start = queue.pop(0)
        for a, relation, b in catalog["edges"]:
            if a == start:
                traversed.append([a, relation, b])
                if b not in reached:
                    reached[b] = f"{a} {relation} {b}"
                    queue.append(b)
    tags = set(catalog["operations"][task["operation"]])
    for e in reached:
        tags.update(catalog["entities"][e]["tags"])
    obligations, excluded = [], []
    for r in catalog["records"]:
        applicable = "*" in r["tags"] or bool(tags.intersection(r["tags"]))
        eligible = r["status"] in ACTIVE or (r["status"] == "proposed" and r["kind"] == "workflow")
        if applicable and eligible:
            obligations.append({**r, "reason": "global binding rule" if "*" in r["tags"] else "matched facets: " + ", ".join(sorted(tags.intersection(r["tags"]))),
                                "citations": [catalog["sources"][s]["path"] for s in r["sources"]],
                                "authority": "recommended check, not creative approval" if r["status"] == "proposed" else r["status"]})
        else:
            excluded.append({"id": r["id"], "reason": "not current authority/workflow" if not eligible else "outside declared impact facets"})
    blockers = []
    for path, expected in task["inputs"].items():
        if file_hash(safe_path(root, path)) != expected:
            blockers.append("STALE_INPUT:" + path)
    if not task["inputs"]:
        blockers.append("MISSING_INPUT_BINDINGS")
    if task["phase"] == "execution":
        blockers += ["DIRECTOR_DECISION:" + d for d in task["open_decisions"]]
        # Current canonical state cannot be overridden by omitting the task's decision list.
        for r in obligations:
            if r.get("unresolved_decision"):
                # Reuse of a reviewed artifact is narrower than a new creative call.
                # Both the exact artifact and current authority source must be bound.
                accepted = r.get("accepted_artifact", {})
                if (accepted and task.get("preserve_accepted_artifact") == accepted.get("sha256")
                    and task["inputs"].get(accepted.get("path")) == accepted.get("sha256")
                    and accepted.get("authority_source") in task["inputs"]):
                    continue
                # Only a catalog-reviewed audition can precede final selection.
                authority = task.get("execution_authority")
                exception = any(
                    e.get("task_id") == task["id"] and e.get("operation") == task["operation"]
                    and isinstance(authority, dict)
                    and e.get("authority_source") == authority.get("source")
                    for e in r.get("decision_exceptions", [])
                )
                if not exception:
                    blockers.append("DIRECTOR_DECISION:" + r["unresolved_decision"])
        if not task.get("execution_authority"):
            blockers.append("MISSING_EXECUTION_AUTHORITY")
        else:
            authority = task["execution_authority"]
            if not isinstance(authority, dict) or not authority.get("scope") or not authority.get("source"):
                blockers.append("INVALID_EXECUTION_AUTHORITY")
            elif authority["source"] not in task["inputs"]:
                blockers.append("UNBOUND_EXECUTION_AUTHORITY")
    max_context = task.get("max_context_characters", 24000)
    if type(max_context) is not int or max_context < 1:
        raise KnowledgeError("invalid context budget")
    if len(json.dumps(obligations)) > max_context:
        blockers.append("CONTEXT_TOO_LARGE_SPLIT_TASK_DO_NOT_TRUNCATE")
    conn = build_index(root, catalog)
    try:
        supporting = search(conn, task["query"])
    finally:
        conn.close()
    packet = {"schema_version": SCHEMA, "task": task, "corpus_digest": digest(pins),
              "engine_sha256": file_hash(Path(__file__)),
              "entity_versions": {e: catalog["entities"][e]["version"] for e in sorted(reached)},
              "entity_reasons": reached, "traversed_edges": traversed, "facets": sorted(tags),
              "obligations": obligations, "excluded": excluded, "supporting_search": supporting,
              "blockers": blockers, "dispatch_ready": not blockers,
              "gaps": catalog["gaps"], "open_decisions": task["open_decisions"],
              "limits": "Planning readiness is not execution authorization. Manually curated scope and authority records require agent verification. CLI enforces evidence structure/freshness, not honesty or perceptual quality."}
    packet["packet_digest"] = digest(packet)
    return packet


def packet_markdown(packet):
    t = packet["task"]
    lines = [f"# Context for {t['id']}", "", t["intent"], "",
             f"Phase: {t['phase']}. Packet: `{packet['packet_digest']}`.", "",
             "## Required actions and checks", ""]
    for r in packet["obligations"]:
        lines.extend([f"### {r['id']} — {r['status']}", "", r["action"], "",
                      f"Selection: {r['reason']}. Evidence kind: {r['check_kind']}.", "",
                      "Sources: " + ", ".join(r["citations"]), ""])
    lines += ["## Open decisions and blockers", ""]
    lines += ["- " + x for x in packet["open_decisions"] + packet["blockers"]] or ["None for this scoped planning operation."]
    lines += ["", "## Limits", "", packet["limits"], ""] + ["- " + x for x in packet["gaps"]]
    return "\n".join(lines) + "\n"


def check_review(root, packet, review):
    """Fail closed on stale/modified packets or unsupported evidence. No visual oracle."""
    fresh = task_packet(root, packet["task"])
    failures = list(fresh["blockers"])
    if fresh != packet:
        failures.append("STALE_OR_MODIFIED_PACKET")
    if review.get("packet_digest") != fresh["packet_digest"]:
        failures.append("REVIEW_PACKET_MISMATCH")
    checks = review.get("checks", [])
    if not isinstance(checks, list) or any(not isinstance(c, dict) for c in checks):
        return {"ready_for_review": False, "failures": failures + ["INVALID_CHECKS"]}
    by_id = {c.get("id"): c for c in checks}
    if len(by_id) != len(checks):
        failures.append("DUPLICATE_CHECK")
    wanted = {r["id"] for r in fresh["obligations"]}
    if set(by_id) - wanted:
        failures.append("UNKNOWN_CHECK")
    for r in fresh["obligations"]:
        c = by_id.get(r["id"], {})
        prefix = r["id"] + ":"
        if c.get("status") != "PASS":
            failures.append(prefix + "FAIL_OR_NOT_RUN")
        if c.get("kind") != r["check_kind"] or not c.get("observation", "").strip() or not c.get("action_taken", "").strip():
            failures.append(prefix + "MISSING_APPLICATION_OR_WRONG_EVIDENCE_KIND")
        if not c.get("evidence"):
            failures.append(prefix + "MISSING_EVIDENCE")
        for item in c.get("evidence", []):
            try:
                if file_hash(safe_path(root, item["path"])) != item["sha256"]:
                    failures.append(prefix + "STALE_EVIDENCE")
            except (KnowledgeError, KeyError, TypeError):
                failures.append(prefix + "INVALID_EVIDENCE")
    hypotheses = review.get("hypotheses", [])
    if not hypotheses:
        failures.append("MISSING_ANTICIPATORY_REVIEW")
    for h in hypotheses:
        if not h.get("prediction") or not h.get("observation") or not h.get("response") or h.get("result") not in {"not_observed", "resolved"}:
            failures.append("UNRESOLVED_HYPOTHESIS")
    if not review.get("adjacent_regressions") or not review.get("stopping_reason"):
        failures.append("MISSING_REGRESSION_OR_STOPPING_REVIEW")
    return {"ready_for_review": not failures, "failures": sorted(set(failures)),
            "scope": packet["task"]["phase"], "limits": "Evidence checked for presence and hashes, not artistic truth or Director acceptance. Planning evidence cannot qualify a production result."}


def evaluate(root, oracle_path="docs/knowledge/pilot/expectations.json"):
    oracle = read_json(root, oracle_path)
    catalog, _ = load(root)
    ids = {r["id"] for r in catalog["records"]}
    common = set(oracle["global_required"])
    results = []
    for case in oracle["cases"]:
        task = {k: case[k] for k in ["id", "operation", "entities", "query"]}
        task.update(intent=case["reason"], phase="planning", inputs={oracle_path: file_hash(safe_path(root, oracle_path))}, open_decisions=[])
        packet = task_packet(root, task)
        actual = {r["id"] for r in packet["obligations"]}
        expected = common | set(case["required"])
        useful = set(case["useful"])
        results.append({"id": case["id"], "split": case["split"], "expected": sorted(expected),
                        "selected": sorted(actual), "missing_critical": sorted(expected - actual),
                        "unrecognized_expected": sorted((expected | useful) - ids),
                        "forbidden_selected": sorted(actual & set(case["forbidden"])),
                        "extra_context": sorted(actual - expected - useful),
                        "useful_recall": len(actual & useful) / len(useful) if useful else None,
                        "critical_recall": len(actual & expected) / len(expected),
                        "context_characters": len(json.dumps(packet["obligations"])),
                        "packet_digest": packet["packet_digest"]})
    return {"schema_version": SCHEMA, "oracle_sha256": file_hash(safe_path(root, oracle_path)),
            "passed": all(not r["missing_critical"] and not r["forbidden_selected"] and not r["unrecognized_expected"] for r in results),
            "cases": results,
            "limit": "Finite agent-authored applicability oracle, authored before routing. Structured descriptors supplied by agent; no independent-model or audience validation. Useful recall and irrelevant burden are separate from critical recall."}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="command", required=True)
    for name in ["freeze", "coverage", "evaluate"]:
        command = sub.add_parser(name)
        command.add_argument("--output", type=Path, required=True)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, required=True)
    packet = sub.add_parser("packet")
    packet.add_argument("--task", required=True)
    packet.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("check")
    check.add_argument("--packet", required=True)
    check.add_argument("--review", required=True)
    check.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    root = args.root.resolve()
    safe_output = False
    try:
        # Writes confined to pilot-specific derived outputs; no source/native overwrite.
        output = args.output if args.output.is_absolute() else root / args.output
        output = output.resolve()
        allowed = [root / ".runtime/knowledge-pilot213", root / "docs/knowledge/pilot/generated"]
        if args.command == "freeze":
            if output != root / PINS or output.exists():
                raise KnowledgeError("freeze requires a new source-pins.json; archive/audit an old pin before explicitly replacing it")
        elif not any(output.is_relative_to(d) for d in allowed):
            raise KnowledgeError("output must be inside a pilot derived-output directory")
        safe_output = True
        output.parent.mkdir(parents=True, exist_ok=True)
        if args.command == "build":
            catalog, _ = load(root)
            build_index(root, catalog, str(output)).close()
            print(json.dumps({"built": str(output), "records": len(catalog["records"])}))
            return 0
        if args.command == "freeze":
            result = freeze(root)
        elif args.command == "coverage":
            result = coverage(root)
        elif args.command == "evaluate":
            result = evaluate(root)
        elif args.command == "packet":
            result = task_packet(root, read_json(root, args.task))
        else:
            result = check_review(root, read_json(root, args.packet), read_json(root, args.review))
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        if args.command == "packet":
            output.with_suffix(".md").write_text(packet_markdown(result))
        passed = result.get("passed", result.get("ready_for_review", result.get("dispatch_ready", True)))
        print(json.dumps({"output": str(output), "passed": passed}))
        return 0 if passed else 2
    except (KnowledgeError, OSError, ValueError, KeyError, TypeError) as exc:
        error = {"error": str(exc), "passed": False}
        if safe_output:
            output.write_text(json.dumps(error, indent=2) + "\n")
            if args.command == "packet":
                output.with_suffix(".md").write_text("# Context blocked\n\n" + str(exc) + "\n")
        print(json.dumps(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
