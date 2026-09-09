import json
from pathlib import Path

import pytest

from movie_factory.cli import resolve_replay_seed
from movie_factory.packages import atomic_json, content_id, safe_relative


def test_content_id_is_order_independent():
    assert content_id({"b": 2, "a": 1}) == content_id({"a": 1, "b": 2})


def test_atomic_json_roundtrip(tmp_path):
    path = tmp_path / "result.json"
    atomic_json(path, {"ok": True})
    assert json.loads(path.read_text()) == {"ok": True}
    assert not list(tmp_path.glob(".result.json.*"))


def test_safe_relative_rejects_escape(tmp_path):
    with pytest.raises(ValueError):
        safe_relative(tmp_path, Path("../secret"))


def test_legacy_revision_replay_seed_comes_from_authenticated_intent(tmp_path):
    stage = tmp_path / "revision"
    stage.mkdir()
    intent = {"package_kind":"intent","stage":"revision","seed":303}
    intent["package_id"] = content_id(intent)
    atomic_json(stage / "intent-package.json", intent)
    executable = {"intent_package_hash": intent["package_id"]}
    assert resolve_replay_seed(stage / "executable-package.json", executable, "revision") == 303


def test_legacy_revision_replay_rejects_unbound_intent(tmp_path):
    stage = tmp_path / "revision"
    stage.mkdir()
    intent = {"package_kind":"intent","stage":"revision","seed":505}
    intent["package_id"] = content_id(intent)
    atomic_json(stage / "intent-package.json", intent)
    with pytest.raises(ValueError, match="does not match"):
        resolve_replay_seed(stage / "executable-package.json", {"intent_package_hash":"wrong"}, "revision")
