#!/usr/bin/env python3
"""Create a no-copy hardlink view of active-backup content objects."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    if manifest.get("credential_like_paths"):
        raise RuntimeError("Credential-like content detected; upload refused")
    root = Path(manifest["source_root"])
    stage = args.stage / "objects" / "sha256"
    stage.mkdir(parents=True, exist_ok=True)
    rows_by_path = {row["path"]: row for row in manifest["paths"]}
    created = 0
    for item in manifest["objects"]:
        sha256 = item["sha256"]
        source_relative = item["paths"][0]
        source = root / source_relative
        source_row = rows_by_path[source_relative]
        current = source.stat()
        if current.st_size != item["bytes"] or current.st_mtime_ns != source_row["mtime_ns"]:
            raise RuntimeError(f"Source changed after manifest creation: {source}")
        target = stage / sha256[:2] / sha256
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.stat().st_ino != current.st_ino or target.stat().st_size != item["bytes"]:
                raise RuntimeError(f"Unexpected staged object: {target}")
            continue
        os.link(source, target)
        created += 1

    staged = [path for path in stage.glob("*/*") if path.is_file()]
    if len(staged) != manifest["unique_object_count"]:
        raise RuntimeError("Incomplete staged object set")
    if sum(path.stat().st_size for path in staged) != manifest["unique_bytes"]:
        raise RuntimeError("Staged byte count mismatch")
    print(json.dumps({
        "created_hardlinks": created,
        "staged_objects": len(staged),
        "logical_bytes": manifest["unique_bytes"],
        "additional_payload_blocks": "none; hardlinks share source inodes",
    }, indent=2))


if __name__ == "__main__":
    main()
