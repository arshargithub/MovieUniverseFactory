"""Known configuration only; dotenv files are data, never shell programs."""
from __future__ import annotations
import os
import re
import stat
from pathlib import Path


class SettingsError(ValueError):
    pass


DEFAULTS = {
    "OPENAI_API_KEY": "", "GH_TOKEN": "", "GITHUB_REPOSITORY": "",
    "MF_PROVIDER": "openai", "MF_PLANNER_MODEL": "gpt-5.4-2026-03-05",
    "MF_VISION_MODEL": "gpt-5.4-2026-03-05", "MF_REASONING_EFFORT": "medium",
    "MF_PLANNER_REASONING_EFFORT": "medium", "MF_VISION_REASONING_EFFORT": "medium",
    "MF_IMAGE_DETAIL": "high",
    "BLENDER_BIN": "/Applications/Blender.app/Contents/MacOS/Blender",
    "MF_COST_SCOPE": "development", "MF_MAX_CAMPAIGN_API_USD": 40.0,
    "MF_MAX_INITIAL_API_USD": 3.0, "MF_MAX_REVISION_API_USD": 2.0,
    "MF_MAX_INITIAL_CALLS": 8, "MF_MAX_REVISION_CALLS": 6,
    "MF_LLM_MAX_OUTPUT_TOKENS": 8192, "MF_API_TIMEOUT_SECONDS": 180.0,
    "MF_RUN_ROOT": "./runs", "MF_ARTIFACT_ROOT": "./artifacts",
    "MF_PRICEBOOK": "./config/prices.json", "MF_RENDER_PROFILE": "qualification_cpu",
    "MF_EXECUTION_MODE": "structured_ops", "MF_NETWORK_POLICY": "controller_only",
    "MF_MAX_REPAIRS_PER_STAGE": 2, "MF_WORKER_TIMEOUT_SECONDS": 300.0,
    "MF_RENDER_TIMEOUT_SECONDS": 600.0, "MF_INITIAL_TIMEOUT_SECONDS": 1800.0,
    "MF_REVISION_TIMEOUT_SECONDS": 900.0,
}
ALIASES = {name.lower(): name for name in DEFAULTS}
ALIASES.update({"github_token": "GH_TOKEN", "GITHUB_TOKEN": "GH_TOKEN",
                "github_repository": "GITHUB_REPOSITORY"})
SECRET_NAMES = frozenset({"OPENAI_API_KEY", "GH_TOKEN"})


def safe_settings(settings: dict) -> dict:
    return {key: ("<set>" if value else "<unset>") if key in SECRET_NAMES else value
            for key, value in settings.items()}


class Settings(dict):
    def __repr__(self):
        return repr(safe_settings(self))


def _read_dotenv(path: Path) -> dict:
    if not path.exists() and not path.is_symlink():
        return {}
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
        raise SettingsError("Local settings must be an owned regular file, not a symlink")
    if info.st_size > 65536:
        raise SettingsError("Local settings file is too large")
    result = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SettingsError(f"Invalid local setting at line {line_no}")
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        canonical = name if name in DEFAULTS else ALIASES.get(name)
        if canonical is None:
            raise SettingsError(f"Unsupported local setting at line {line_no}")
        if canonical in result:
            raise SettingsError(f"Duplicate local setting at line {line_no}")
        if value[:1] in {"'", '"'}:
            if len(value) < 2 or value[-1] != value[0]:
                raise SettingsError(f"Unclosed setting quote at line {line_no}")
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        if "\x00" in value or "\n" in value or "\r" in value:
            raise SettingsError(f"Invalid setting value at line {line_no}")
        result[canonical] = value
    if any(result.get(name) for name in SECRET_NAMES) and info.st_mode & 0o077:
        raise SettingsError("Credential settings file requires owner-only permissions (0600)")
    return result


def load_settings(repo_root: Path) -> dict:
    """Return canonical uppercase keys; env > .env.local > .env > defaults.

    Values are never printed. Call safe_settings() before serializing settings.
    Both lowercase user aliases and conventional environment names are accepted.
    """
    root = Path(repo_root).resolve()
    result = Settings(DEFAULTS)
    for filename in (".env", ".env.local"):
        result.update(_read_dotenv(root / filename))
    for alias, canonical in ALIASES.items():
        if alias in os.environ:
            result[canonical] = os.environ[alias]
    for name in DEFAULTS:
        if name in os.environ:
            result[name] = os.environ[name]
    for name, default in DEFAULTS.items():
        value = result[name]
        if isinstance(default, (int, float)):
            try:
                number = type(default)(value)
                if not 0 < number < float("inf"):
                    raise ValueError
                result[name] = number
            except (ValueError, TypeError, OverflowError):
                raise SettingsError(f"Invalid numeric configuration: {name}") from None
    if result["MF_COST_SCOPE"] not in {"development", "faults", "scored"}:
        raise SettingsError("Invalid MF_COST_SCOPE")
    if result["MF_PROVIDER"] not in {"openai", "mock"}:
        raise SettingsError("Invalid MF_PROVIDER")
    if result["MF_NETWORK_POLICY"] != "controller_only":
        raise SettingsError("Only controller_only network policy is supported")
    for name in ("MF_REASONING_EFFORT", "MF_PLANNER_REASONING_EFFORT", "MF_VISION_REASONING_EFFORT"):
        if result[name] not in {"none", "low", "medium", "high", "xhigh"}:
            raise SettingsError(f"Invalid reasoning effort: {name}")
    if result["MF_IMAGE_DETAIL"] not in {"low", "high"}:
        raise SettingsError("MF_IMAGE_DETAIL must be low or high")
    return result
