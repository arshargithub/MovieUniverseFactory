import os
from pathlib import Path
import pytest

from movie_factory.settings import DEFAULTS, ALIASES, SettingsError, load_settings, safe_settings
from movie_factory.telemetry import Telemetry


@pytest.fixture(autouse=True)
def clear_known_env(monkeypatch):
    for name in set(DEFAULTS) | set(ALIASES):
        monkeypatch.delenv(name, raising=False)


def write_env(root, content, mode=0o600, name=".env"):
    path = root / name
    path.write_text(content)
    path.chmod(mode)
    return path


def test_lowercase_aliases_environment_precedence_and_redaction(tmp_path, monkeypatch, capsys):
    write_env(tmp_path, "openai_api_key='synthetic-secret-only'\ngithub_token=test-gh-secret\ngithub_repository=test/project\n")
    write_env(tmp_path, "openai_api_key=second-secret\n", name=".env.local")
    monkeypatch.setenv("openai_api_key", "lower-environment-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "upper-environment-secret")
    settings = load_settings(tmp_path)
    assert settings["OPENAI_API_KEY"] == "upper-environment-secret"
    assert settings["GH_TOKEN"] == "test-gh-secret"
    assert settings["GITHUB_REPOSITORY"] == "test/project"
    assert safe_settings(settings)["OPENAI_API_KEY"] == "<set>"
    assert "upper-environment-secret" not in repr(settings)
    assert capsys.readouterr().out == ""


def test_dotenv_never_executes_or_interpolates(tmp_path):
    write_env(tmp_path, "openai_api_key=$(touch NEVER_CREATED)\n")
    assert load_settings(tmp_path)["OPENAI_API_KEY"] == "$(touch NEVER_CREATED)"
    assert not (tmp_path / "NEVER_CREATED").exists()


@pytest.mark.parametrize("content", ["not_a_setting=private-value", "openai_api_key=one\nOPENAI_API_KEY=two", "MF_MAX_INITIAL_CALLS=not-an-integer"])
def test_invalid_settings_fail_without_values(tmp_path, content):
    write_env(tmp_path, content)
    with pytest.raises(SettingsError) as caught:
        load_settings(tmp_path)
    assert "private-value" not in str(caught.value)


def test_credential_file_must_be_private_and_not_symlink(tmp_path):
    path = write_env(tmp_path, "openai_api_key=synthetic\n", mode=0o644)
    with pytest.raises(SettingsError, match="owner-only"):
        load_settings(tmp_path)
    path.unlink()
    target = write_env(tmp_path, "openai_api_key=synthetic\n", name="different")
    path.symlink_to(target)
    with pytest.raises(SettingsError, match="regular file"):
        load_settings(tmp_path)


def test_telemetry_redacts_fields_values_keys_and_home_paths(tmp_path):
    path = tmp_path / "events.jsonl"
    events = Telemetry(path, secrets=("synthetic-value",))
    events.emit("test", note="synthetic-value /Users/alice/example", OPENAI_API_KEY="another-value",
                output_tokens=100, reasoning_tokens=80)
    content = path.read_text()
    assert "synthetic-value" not in content and "another-value" not in content
    assert "/Users/alice" not in content
    assert '"reasoning_tokens":80' in content
    assert path.stat().st_mode & 0o077 == 0
