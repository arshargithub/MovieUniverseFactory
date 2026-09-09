from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_schema(repo_root: Path, name: str) -> dict[str, Any]:
    return json.loads((repo_root / "schemas" / name).read_text())


def validate(repo_root: Path, name: str, value: Any) -> list[str]:
    validator = Draft202012Validator(load_schema(repo_root, name))
    return [f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in sorted(validator.iter_errors(value), key=lambda e: list(e.absolute_path))]
