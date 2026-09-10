"""Safe, reproducible staging for externally acquired 3D assets."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from .packages import atomic_json, file_digest, manifest_for, safe_relative


MAX_ARCHIVE_BYTES = 500_000_000
MAX_MEMBER_BYTES = 300_000_000
MAX_SELECTED_BYTES = 500_000_000


def _safe_member(info: zipfile.ZipInfo) -> tuple[str, ...]:
    path = PurePosixPath(info.filename)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError("unsafe archive member path")
    if stat.S_ISLNK(info.external_attr >> 16) or info.is_dir():
        raise ValueError("selected archive member must be a regular file")
    if info.file_size < 0 or info.file_size > MAX_MEMBER_BYTES:
        raise ValueError("selected archive member exceeds size limit")
    return path.parts


def prepare_assets(source_root: Path, manifest: dict[str, Any], output: Path) -> dict[str, Any]:
    source_root, output = source_root.resolve(), output.resolve()
    if output.exists():
        raise FileExistsError(output)
    experiment_id = manifest.get("experiment_id")
    if manifest.get("schema_version") != "1.0" or experiment_id not in {"3D-02", "3D-03"}:
        raise ValueError("unsupported asset manifest")
    assets = manifest.get("assets")
    required_count = {"3D-02": 3, "3D-03": 1}[experiment_id]
    if not isinstance(assets, list) or len(assets) != required_count:
        raise ValueError(f"{experiment_id} requires exactly {required_count} asset source(s)")
    output.mkdir(parents=True, mode=0o700)
    staged: list[Path] = []
    records = []
    seen_ids = set()
    selected_total = 0
    try:
        for asset in assets:
            asset_id = asset.get("asset_id")
            if not isinstance(asset_id, str) or not asset_id or asset_id in seen_ids:
                raise ValueError("asset IDs must be unique non-empty strings")
            seen_ids.add(asset_id)
            archive_candidate = source_root / asset["archive_filename"]
            if archive_candidate.is_symlink():
                raise ValueError("asset archive may not be a symbolic link")
            archive = safe_relative(source_root, archive_candidate)
            if not archive.is_file() or archive.stat().st_size > MAX_ARCHIVE_BYTES:
                raise ValueError("asset archive is missing or invalid")
            if file_digest(archive) != asset["archive_sha256"]:
                raise ValueError("asset archive digest mismatch")
            members = asset.get("members")
            if not isinstance(members, list) or not members:
                raise ValueError("asset requires selected members")
            names = [member.get("archive_path") for member in members]
            if len(names) != len(set(names)):
                raise ValueError("duplicate selected archive member")
            member_records = []
            with zipfile.ZipFile(archive) as package:
                for member in members:
                    info = package.getinfo(member["archive_path"])
                    parts = _safe_member(info)
                    selected_total += info.file_size
                    if selected_total > MAX_SELECTED_BYTES:
                        raise ValueError("selected asset payload exceeds total size limit")
                    data = package.read(info)
                    digest = hashlib.sha256(data).hexdigest()
                    if digest != member["sha256"] or len(data) != info.file_size:
                        raise ValueError("selected asset member digest mismatch")
                    target = output / asset_id / Path(*parts)
                    safe_relative(output, target)
                    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, "wb") as handle:
                        handle.write(data)
                        handle.flush()
                        os.fsync(handle.fileno())
                    staged.append(target)
                    member_records.append({
                        "archive_path": member["archive_path"],
                        "staged_path": str(target.relative_to(output)),
                        "bytes": len(data), "sha256": digest,
                    })
            records.append({
                "asset_id": asset_id, "archive_filename": archive.name,
                "archive_sha256": asset["archive_sha256"], "members": member_records,
            })
        payload = {
            "schema_version": "1.0", "experiment_id": experiment_id,
            "source_manifest_sha256": hashlib.sha256(
                json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "assets": records, "selected_bytes": selected_total,
            "artifacts": manifest_for(output, staged),
        }
        atomic_json(output / "staged-manifest.json", payload)
        return payload
    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise
