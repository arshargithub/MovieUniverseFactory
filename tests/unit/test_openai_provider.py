from copy import deepcopy
from types import SimpleNamespace

import pytest
from PIL import Image

from movie_factory.budget import BudgetLedger
from movie_factory.providers.openai_provider import MODEL, OpenAIProvider, normalize_usage, provider_safe_schema, usage_cost


SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}},
          "required": ["ok"], "additionalProperties": False}


def response(**updates):
    data = {"id": "resp_fake", "model": MODEL, "status": "completed", "service_tier": "default",
            "usage": {"input_tokens": 300, "input_tokens_details": {"cached_tokens": 100},
                      "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 25}, "total_tokens": 350},
            "output": [{"type": "reasoning", "summary": [{"text": "Do not persist this reasoning"}]},
                       {"type": "message", "content": [{"type": "output_text", "text": '{"ok":true}'}]}]}
    data.update(updates)
    return data


class FakeClient:
    def __init__(self, result=None, error=None):
        self.result, self.error, self.calls = result or response(), error, []
        self.responses = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return deepcopy(self.result)


def provider(tmp_path, result=None, error=None, cap=40):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", campaign_limit=cap)
    client = FakeClient(result, error)
    settings = {"MF_PLANNER_MODEL": MODEL, "MF_VISION_MODEL": MODEL,
                "MF_COST_SCOPE": "development", "OPENAI_API_KEY": "synthetic-private-value"}
    instance = OpenAIProvider(settings, ledger, tmp_path / "logs", client=client)
    return instance, ledger, client


def call(instance, **kwargs):
    return instance.generate_json(purpose="test", prompt="Return valid JSON.", schema=SCHEMA,
                                  run_id="run1", stage="initial", **kwargs)


def test_valid_response_request_contract_and_reasoning_cost(tmp_path):
    instance, ledger, client = provider(tmp_path)
    result = call(instance)
    assert result["data"] == {"ok": True} and result["error"] is None
    assert result["cost_usd"] == pytest.approx(0.001275)
    assert result["reasoning_cost_usd"] == pytest.approx(0.000375)
    assert ledger.summary()["known_cost_usd"] == pytest.approx(result["cost_usd"])
    request = client.calls[0]
    assert request["model"] == MODEL and request["store"] is False
    assert request["tools"] == [] and request["service_tier"] == "default"
    assert request["text"]["format"]["strict"] is True
    assert request["reasoning"] == {"effort": "medium"}
    assert "Do not persist this reasoning" not in (tmp_path / "logs/telemetry.jsonl").read_text()


@pytest.mark.parametrize("raw, error", [
    (response(status="incomplete", incomplete_details={"reason": "max_output_tokens"}), "response_not_completed"),
    (response(output=[{"type": "message", "content": [{"type": "refusal", "refusal": "no"}]}]), "refusal"),
    (response(output=[{"type": "message", "content": [{"type": "output_text", "text": '{"ok":"wrong type"}'}]}]), "ValidationError"),
    (response(output=[{"type": "message", "content": [{"type": "output_text", "text": '{"ok":true,"ok":false}'}]}]), "duplicate_json_key"),
    (response(output=[{"type": "function_call", "name": "unexpected"}]), "unexpected_output_item"),
    (response(output=[]), "missing_json_output"),
])
def test_bad_outputs_are_never_executable_but_cost_is_charged(tmp_path, raw, error):
    instance, ledger, client = provider(tmp_path, raw)
    result = call(instance)
    assert result["data"] is None and error in result["error"]
    assert ledger.summary()["known_cost_usd"] > 0
    assert len(client.calls) == 1


def test_missing_usage_retains_entire_reservation(tmp_path):
    instance, ledger, _ = provider(tmp_path, response(usage=None))
    result = call(instance)
    assert result["data"] is None and result["cost_usd"] is None
    assert ledger.summary()["unresolved_calls"] == 1
    assert ledger.summary()["reserved_unknown_usd"] > 0


def test_missing_reasoning_count_is_unknown_attribution_not_zero(tmp_path):
    raw = response()
    raw["usage"].pop("output_tokens_details")
    instance, ledger, _ = provider(tmp_path, raw)
    result = call(instance)
    assert result["error"] is None
    assert result["usage"]["reasoning_tokens"] is None
    assert result["reasoning_cost_usd"] is None
    assert result["cost_usd"] > 0


def test_invalid_usage_and_unpriced_models_fail_closed(tmp_path):
    raw = response()
    raw["usage"]["output_tokens_details"]["reasoning_tokens"] = 100
    instance, ledger, _ = provider(tmp_path, raw)
    result = call(instance)
    assert result["data"] is None and "invalid_usage" in result["error"]
    assert ledger.summary()["unresolved_calls"] == 1


def test_timeout_no_automatic_retry_and_no_exception_secret(tmp_path):
    instance, ledger, client = provider(tmp_path, error=TimeoutError("synthetic-private-value in HTTP request"))
    result = call(instance)
    assert result["error"] == "provider_error:TimeoutError"
    assert len(client.calls) == 1 and ledger.summary()["unresolved_calls"] == 1
    assert "synthetic-private-value" not in (tmp_path / "logs/telemetry.jsonl").read_text()


def test_budget_denied_before_provider_dispatch(tmp_path):
    instance, ledger, client = provider(tmp_path, cap=0.001)
    result = call(instance)
    assert "budget_denied" in result["error"]
    assert not client.calls and ledger.summary()["calls"] == 0


def test_image_payload_and_conservative_reservation(tmp_path):
    path = tmp_path / "test.png"
    Image.new("RGB", (1280, 720), "red").save(path)
    instance, ledger, client = provider(tmp_path)
    result = call(instance, images=[path])
    assert result["error"] is None
    image = client.calls[0]["input"][0]["content"][1]
    assert image["detail"] == "high" and image["image_url"].startswith("data:image/png;base64,")
    text = (tmp_path / "logs/telemetry.jsonl").read_text()
    assert '"width":1280' in text
    assert "base64" not in text


def test_remote_schema_ref_denied_before_dispatch(tmp_path):
    instance, ledger, client = provider(tmp_path)
    result = instance.generate_json(purpose="test", prompt="x", schema={"$ref": "https://example.com/schema"}, run_id="r", stage="initial")
    assert "request_validation" in result["error"]
    assert not client.calls


def test_sdk_configuration_disables_implicit_retries(tmp_path, monkeypatch):
    import openai
    captured = {}
    def fake_constructor(**kwargs):
        captured.update(kwargs)
        return FakeClient()
    monkeypatch.setattr(openai, "OpenAI", fake_constructor)
    OpenAIProvider({"OPENAI_API_KEY": "synthetic"}, BudgetLedger(tmp_path / "ledger.jsonl"), tmp_path / "logs")
    assert captured["max_retries"] == 0
    assert captured["timeout"] == 180
    assert captured["base_url"] == "https://api.openai.com/v1"


def test_provider_schema_translates_const_and_tuple_but_local_schema_stays_strict():
    local = {"type":"array", "prefixItems":[{"const":1},{"const":2}], "items":False}
    api = provider_safe_schema(local)
    assert local["prefixItems"][0] == {"const":1}
    assert api == {"type":"array","minItems":2,"maxItems":2,
                   "items":{"anyOf":[{"enum":[1]},{"enum":[2]}]}}
