import json
from pathlib import Path
import httpx
import pytest
from movie_factory.providers.runway_provider import RunwayProvider, RunwayError, load_runway_key
from movie_factory.settings import load_settings, safe_settings
from movie_factory.budget import BudgetExceeded


def provider(tmp_path, handler):
    return RunwayProvider(tmp_path, tmp_path / "run", client=httpx.Client(
        base_url="https://api.dev.runwayml.com", transport=httpx.MockTransport(handler)))


def test_key_alias_and_redaction(tmp_path):
    env = tmp_path / ".env"
    env.write_text("runway_api_key=not-a-real-secret\n")
    env.chmod(0o600)
    s = load_settings(tmp_path)
    assert s["RUNWAY_API_KEY"] == "not-a-real-secret"
    assert "not-a-real-secret" not in repr(s)
    assert safe_settings(s)["RUNWAY_API_KEY"] == "<set>"


def test_reserve_before_dispatch_and_no_duplicate(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    calls = []
    def handler(request):
        calls.append(request)
        assert p.ledger.summary()["committed_usd"] == .6
        payload = json.loads(request.content)
        assert payload["model"] == "gen4.5" and payload["duration"] == 5
        return httpx.Response(200, json={"id": "11111111-1111-4111-8111-111111111111"})
    p = provider(tmp_path, handler)
    p.submit("cinematic", image, "Gallop")
    with pytest.raises(RunwayError, match="already exists"):
        p.submit("cinematic", image, "Gallop")
    assert len(calls) == 1


def test_unknown_charge_retained_and_error_redacted(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    p = provider(tmp_path, lambda r: httpx.Response(503, text="SECRET response"))
    with pytest.raises(RunwayError, match="HTTP 503") as exc:
        p.submit("cinematic", image, "Gallop")
    assert "SECRET" not in str(exc.value)
    assert p.ledger.summary()["reserved_unknown_usd"] == .6


def test_validation_no_calls(tmp_path):
    p = provider(tmp_path, lambda r: pytest.fail("network called"))
    with pytest.raises(RunwayError): p.submit("../bad", Path("none"), "x")
    with pytest.raises(RunwayError): p.submit("good", Path("none"), "x" * 1001)
    assert p.ledger.summary()["calls"] == 0


def test_poll_does_not_generate_or_settle_guess(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    def handler(r):
        if r.method == "POST": return httpx.Response(200, json={"id":"11111111-1111-4111-8111-111111111111"})
        return httpx.Response(200, json={"status":"SUCCEEDED", "output":["https://example.com/private.mp4?token=secret"]})
    p = provider(tmp_path, handler)
    p.submit("cinematic", image, "Gallop")
    summary = p.poll("cinematic")
    assert summary["status"] == "SUCCEEDED" and "secret" not in str(summary)
    assert p.ledger.summary()["calls"] == 1
    assert p.ledger.summary()["reserved_unknown_usd"] == .6


def test_only_approved_migration_link(tmp_path, monkeypatch):
    home = tmp_path / "home"
    target = home / ".config/movie-factory/.env"
    target.parent.mkdir(parents=True)
    target.write_text("runway_api_key=fixture\n")
    target.chmod(0o600)
    monkeypatch.setattr(Path, "home", lambda: home)
    (tmp_path / ".env").symlink_to(target)
    assert load_runway_key(tmp_path) == "fixture"
    target.chmod(0o644)
    with pytest.raises(ValueError, match="owner-only"): load_runway_key(tmp_path)


def test_request_ceiling_and_attempt_bound(tmp_path):
    p = provider(tmp_path, lambda r: pytest.fail("network called"))
    with pytest.raises(BudgetExceeded):
        p.ledger.reserve(run_id="x", stage="preview", amount_usd=.61, purpose="x")
    for scope in ["scored", "contingency"]:
        p.ledger.reserve(run_id="x", stage="preview", amount_usd=.6, scope=scope, purpose="x")
    with pytest.raises(BudgetExceeded):
        p.ledger.reserve(run_id="x", stage="preview", amount_usd=.6, scope="contingency", purpose="x")
