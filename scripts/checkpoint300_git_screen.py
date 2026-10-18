"""Read-only outgoing Git screening; never emits matched credential bytes."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from protect255 import scan


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    base = git("rev-parse", "origin/main").decode().strip()
    head = git("rev-parse", "HEAD").decode().strip()
    span = base + ".." + head
    refs = git("rev-list", "--objects", span).decode().splitlines()
    findings, binary, forbidden = [], [], []
    count = total = 0
    inventory = []
    for line in refs:
        oid, _, name = line.partition(" ")
        if git("cat-file", "-t", oid).strip() != b"blob":
            continue
        data = git("cat-file", "blob", oid)
        count += 1
        total += len(data)
        categories = scan(data)
        if re.search(rb"hf_[A-Za-z0-9]{25,}", data):
            categories.append("huggingface_token")
        if categories:
            findings.append({"oid": oid, "path": name, "categories": categories})
        if b"\0" in data:
            binary.append({"oid": oid, "path": name})
        parts = Path(name).parts
        if any(p in {".env", ".aws", ".ssh", "credentials", ".runtime"} for p in parts):
            forbidden.append(name)
        inventory.append({"oid": oid, "path": name, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    report = {
        "base": base, "head": head, "range": span,
        "commits": int(git("rev-list", "--count", span)),
        "blobs_scanned": count, "bytes_scanned": total,
        "findings": findings, "binary_blobs": binary,
        "forbidden_paths": forbidden,
        "passed": not (findings or binary or forbidden),
        "limits": "Pattern screening of all outgoing Git blobs, including intermediate versions; not proof that every possible secret is absent. No native/media or credential stores are included.",
        "inventory": inventory,
    }
    destination = ROOT / ".runtime/protection300/git-screen.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "inventory"}, indent=2))
    if not report["passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
