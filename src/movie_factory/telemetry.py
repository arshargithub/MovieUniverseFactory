"""Small durable, sanitized JSONL event writer. Never persist reasoning content."""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def digest(data) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def sanitize(value, secrets=()):
    """Redact known secret values, credential-like fields, and home path identity."""
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if re.search(r"authorization|api[_-]?key|password|secret|^(?:gh|github)[_-]?token$|cookie", str(key), re.I):
                result[key] = "<redacted>"
            else:
                result[key] = sanitize(item, secrets)
        return result
    if isinstance(value, (list, tuple)):
        return [sanitize(item, secrets) for item in value]
    if isinstance(value, Path):
        value = str(value)
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(str(secret), "<redacted>")
        value = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]{8,})", "<redacted>", value)
        return re.sub(r"/(?:Users|home)/[^/\s]+", "/home/<user>", value)
    return value


def append_event(path: Path, event: dict, *, secrets=()) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"schema_version": "1.0", "event_id": str(uuid.uuid4()), "utc": utc_now(), **event}
    record = sanitize(record, secrets)
    payload = (canonical_json(record) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.fchmod(fd, 0o600)
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    return record


class Telemetry:
    def __init__(self, path: Path, *, secrets=(), context=None):
        self.path, self.secrets, self.context = Path(path), tuple(secrets), context or {}

    def emit(self, event_type: str, **fields) -> dict:
        return append_event(self.path, {**self.context, **fields, "event_type": event_type}, secrets=self.secrets)
