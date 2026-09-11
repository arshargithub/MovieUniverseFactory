#!/usr/bin/env python3
"""Verify the compact 3D-05 closure supplement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
for artifact in manifest["artifacts"]:
    path = root / artifact["path"]
    payload = path.read_bytes()
    assert len(payload) == artifact["bytes"], artifact["path"]
    assert hashlib.sha256(payload).hexdigest() == artifact["sha256"], artifact["path"]
print(f"Verified {len(manifest['artifacts'])} 3D-05 closure supplement artifacts.")
