from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def _run(argv: list[str], timeout: int = 30) -> dict[str, Any]:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
        return {"ok": result.returncode == 0, "exit_code": result.returncode, "output": (result.stdout + result.stderr)[:12000]}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(repo_root: Path, blender_bin: str, settings: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = settings or {}
    binary = Path(blender_bin)
    disk = shutil.disk_usage(repo_root)
    blender = _run([str(binary), "--version"]) if binary.exists() else {"ok": False, "error": "Blender executable missing"}
    git = _run(["git", "status", "--porcelain=v1"], timeout=10)
    return {
        "schema_version": "1.0",
        "ok": bool(binary.exists() and blender.get("ok") and sys.prefix == str((repo_root / ".venv").resolve())),
        "platform": {"macos": platform.mac_ver()[0], "architecture": platform.machine(), "python": platform.python_version()},
        "virtual_environment": {"expected": str((repo_root / ".venv").resolve()), "actual": sys.prefix, "isolated": sys.prefix == str((repo_root / ".venv").resolve())},
        "disk": {"free_gib": round(disk.free / 1024**3, 2), "recommended_gib": 20, "minimum_gib": 5, "meets_minimum": disk.free >= 5 * 1024**3},
        "blender": {"path": str(binary), "sha256": _sha256(binary) if binary.exists() else None, **blender},
        "git": git,
        "configuration": {name: bool(settings.get(name)) for name in ("OPENAI_API_KEY", "GH_TOKEN", "GITHUB_REPOSITORY")},
        "security": {"env_mode": oct((repo_root / ".env").stat().st_mode & 0o777) if (repo_root / ".env").exists() else None, "secrets_reported": False},
    }
