"""Inventory closed 3D evidence for private, content-addressed S3 archival.

This script reads files and writes only a compact manifest. It never reads .env,
contacts AWS, uploads data, or deletes local evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "archive" / "closed-3d-01-through-06a-manifest.json"
EXCLUDED_NAMES = {".DS_Store", ".env"}
EXCLUDED_PARTS = {".worker_runtime", "__pycache__", ".pytest_cache"}
SENSITIVE_MARKERS = (
    b"OPENAI_API_KEY=",
    b"openai_api_key=",
    b"GITHUB_TOKEN=",
    b"github_token=",
    b"AWS_SECRET_ACCESS_KEY=",
    b"aws_secret_access_key=",
)
CREDENTIAL_PATTERNS = (
    re.compile(rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def roots() -> list[Path]:
    selected = [ROOT / "exports", ROOT / "feasibility" / "3d"]
    selected += sorted(p for p in (ROOT / "runs").glob("3d*") if p.is_dir())
    selected += sorted(p for p in (ROOT / "results").glob("3d*") if p.is_dir())
    selected += [ROOT / ".runtime" / "assets" / "3d-02", ROOT / ".runtime" / "assets" / "3d-03"]
    return [p for p in selected if p.exists()]


def admitted(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path.name in EXCLUDED_NAMES or (path.name.startswith(".env") and path.name != ".env.example"):
        return False
    return not EXCLUDED_PARTS.intersection(relative.parts)


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main() -> None:
    paths: set[Path] = set()
    for base in roots():
        paths.update(p for p in base.rglob("*") if (p.is_file() or p.is_symlink()) and admitted(p))

    rows: list[dict] = []
    sensitive_paths: list[str] = []
    credential_like_paths: list[str] = []
    objects: dict[str, dict] = {}
    for path in sorted(paths):
        relative = str(path.relative_to(ROOT))
        if path.is_symlink():
            rows.append({"path": relative, "symlink": os.readlink(path)})
            continue
        size = path.stat().st_size
        sha256 = digest(path)
        rows.append({"path": relative, "bytes": size, "sha256": sha256})
        entry = objects.setdefault(sha256, {"sha256": sha256, "bytes": size, "paths": []})
        if entry["bytes"] != size:
            raise RuntimeError("SHA-256 size conflict")
        entry["paths"].append(relative)
        if size <= 2_000_000:
            content = path.read_bytes()
            if any(marker in content for marker in SENSITIVE_MARKERS):
                sensitive_paths.append(relative)
            if any(pattern.search(content) for pattern in CREDENTIAL_PATTERNS):
                credential_like_paths.append(relative)

    physical_bytes = sum(row.get("bytes", 0) for row in rows)
    unique = sorted(objects.values(), key=lambda item: item["sha256"])
    unique_bytes = sum(item["bytes"] for item in unique)
    manifest = {
        "schema_version": "1.0",
        "scope": "Closed 3D-01 through 3D-05 evidence, discontinued 3D-06A, authoritative exports, specs/results, and 3D-02/03 staged assets. Active Demonstrator assets/runs excluded.",
        "archive_model": "One S3 object per unique SHA-256; path table restores duplicate names without duplicate payload storage.",
        "excluded": [".env", ".DS_Store", "worker runtimes", "Python/test caches", "active runs/demonstrator-01", ".runtime/assets/demonstrator-01"],
        "roots": [str(path.relative_to(ROOT)) for path in roots()],
        "path_count": len(rows),
        "symlink_count": sum("symlink" in row for row in rows),
        "physical_bytes": physical_bytes,
        "unique_object_count": len(unique),
        "unique_bytes": unique_bytes,
        "deduplicated_bytes": physical_bytes - unique_bytes,
        "sensitive_marker_paths": sensitive_paths,
        "credential_like_paths": credential_like_paths,
        "paths": rows,
        "objects": unique,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({key: manifest[key] for key in (
        "path_count", "symlink_count", "physical_bytes", "unique_object_count",
        "unique_bytes", "deduplicated_bytes", "sensitive_marker_paths",
        "credential_like_paths")}, indent=2))


if __name__ == "__main__":
    main()
