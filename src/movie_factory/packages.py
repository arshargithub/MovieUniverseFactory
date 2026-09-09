from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def content_id(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_relative(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if resolved_root != resolved and resolved_root not in resolved.parents:
        raise ValueError(f"path escapes root: {candidate}")
    return resolved


def manifest_for(root: Path, paths: list[Path]) -> list[dict[str, Any]]:
    out = []
    for path in sorted((p.resolve() for p in paths), key=str):
        safe_relative(root, path)
        out.append({"path": str(path.relative_to(root.resolve())), "bytes": path.stat().st_size, "sha256": file_digest(path)})
    return out
