#!/usr/bin/env python3
"""Create a secret-screened, content-addressed manifest of active project state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_NAMES = {".DS_Store", ".env"}
EXCLUDED_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__", ".worker_runtime"}
EXCLUDED_PREFIXES = (
    ("results", "backup"),
    (".runtime", "archive-stage"),
    (".runtime", "active-backup-stage"),
    (".runtime", "python"),
)
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


def excluded(relative: Path) -> bool:
    parts = relative.parts
    if not parts:
        return False
    if relative.name in EXCLUDED_NAMES:
        return True
    if relative.name.startswith(".env") and relative.name != ".env.example":
        return True
    if EXCLUDED_PARTS.intersection(parts):
        return True
    if len(parts) >= 2 and parts[0] == ".runtime" and parts[1].startswith("closure-bundle-smoke-"):
        return True
    return any(parts[: len(prefix)] == prefix for prefix in EXCLUDED_PREFIXES)


def paths(root: Path) -> list[Path]:
    selected: list[Path] = []
    for directory, names, filenames in os.walk(root, followlinks=False):
        base = Path(directory)
        relative_base = base.relative_to(root)
        names[:] = sorted(
            name for name in names if not excluded(relative_base / name)
        )
        for name in sorted(filenames):
            path = base / name
            if not excluded(path.relative_to(root)):
                selected.append(path)
        for name in names:
            path = base / name
            if path.is_symlink():
                selected.append(path)
        names[:] = [name for name in names if not (base / name).is_symlink()]
    return sorted(set(selected))


def digest_stable(path: Path) -> tuple[str, os.stat_result]:
    before = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    after = path.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after:
        raise RuntimeError(f"File changed while being hashed: {path}")
    return digest.hexdigest(), after


def git_metadata(root: Path) -> dict:
    def run(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    return {
        "head": run("rev-parse", "HEAD"),
        "branch": run("branch", "--show-current"),
        "status_porcelain": run("status", "--porcelain=v1", "--untracked-files=all").splitlines(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--snapshot-id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    snapshot_id = args.snapshot_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or root / "results" / "backup" / f"active-{snapshot_id}-manifest.json"

    rows: list[dict] = []
    objects: dict[str, dict] = {}
    sensitive_paths: list[str] = []
    credential_like_paths: list[str] = []
    for path in paths(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows.append({"path": relative, "symlink": os.readlink(path)})
            continue
        if not path.is_file():
            continue
        sha256, current = digest_stable(path)
        row = {
            "path": relative,
            "bytes": current.st_size,
            "sha256": sha256,
            "mtime_ns": current.st_mtime_ns,
            "mode": stat.S_IMODE(current.st_mode),
        }
        rows.append(row)
        entry = objects.setdefault(sha256, {"sha256": sha256, "bytes": current.st_size, "paths": []})
        if entry["bytes"] != current.st_size:
            raise RuntimeError("SHA-256 size conflict")
        entry["paths"].append(relative)
        if current.st_size <= 2_000_000:
            content = path.read_bytes()
            if any(marker in content for marker in SENSITIVE_MARKERS):
                sensitive_paths.append(relative)
            if any(pattern.search(content) for pattern in CREDENTIAL_PATTERNS):
                credential_like_paths.append(relative)

    unique = sorted(objects.values(), key=lambda item: item["sha256"])
    physical_bytes = sum(row.get("bytes", 0) for row in rows)
    unique_bytes = sum(item["bytes"] for item in unique)
    manifest = {
        "schema_version": "1.0",
        "kind": "active-project-backup",
        "snapshot_id": snapshot_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(root),
        "scope": "Recoverable MovieUniverseFactory worktree state, active evidence/assets, replays, and operating ledgers.",
        "object_key_template": "movie-factory/backup/objects/sha256/<first-two>/<sha256>",
        "excluded": [
            ".env and private environment variants",
            ".git",
            ".venv and Python/test caches",
            ".runtime/python",
            "archive/backup staging trees",
            "closure smoke-test copies and disposable worker state",
            ".DS_Store",
            "results/backup (manifests and receipts are uploaded separately)",
        ],
        "git": git_metadata(root),
        "path_count": len(rows),
        "symlink_count": sum("symlink" in row for row in rows),
        "physical_bytes": physical_bytes,
        "unique_object_count": len(unique),
        "unique_bytes": unique_bytes,
        "deduplicated_bytes": physical_bytes - unique_bytes,
        "sensitive_marker_paths": sorted(set(sensitive_paths)),
        "credential_like_paths": sorted(set(credential_like_paths)),
        "paths": rows,
        "objects": unique,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n")
    temporary.replace(output)
    print(json.dumps({key: manifest[key] for key in (
        "snapshot_id", "path_count", "symlink_count", "physical_bytes",
        "unique_object_count", "unique_bytes", "deduplicated_bytes",
        "sensitive_marker_paths", "credential_like_paths",
    )}, indent=2))
    print(output)


if __name__ == "__main__":
    main()
