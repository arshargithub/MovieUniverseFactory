"""Create a no-copy hardlink view of unique objects for AWS CLI upload."""
from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "archive" / "closed-3d-01-through-06a-manifest.json"
STAGE = ROOT / ".runtime" / "archive-stage" / "closed-3d-v1" / "objects"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("credential_like_paths"):
        raise RuntimeError("Credential-like content detected; upload refused")
    STAGE.mkdir(parents=True, exist_ok=True)
    created = 0
    for item in manifest["objects"]:
        sha256 = item["sha256"]
        source = ROOT / item["paths"][0]
        target = STAGE / sha256[:2] / sha256
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.stat().st_ino != source.stat().st_ino or target.stat().st_size != item["bytes"]:
                raise RuntimeError(f"Unexpected staged object: {target}")
            continue
        os.link(source, target)
        created += 1
    staged = [path for path in STAGE.glob("*/*") if path.is_file()]
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
