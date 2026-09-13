"""Metered, stateless Responses calls; one physical request per invocation.

Verified sources (2026-09-09):
https://developers.openai.com/api/docs/models/gpt-5.4
https://developers.openai.com/api/docs/models/gpt-5.4-mini
https://developers.openai.com/api/docs/guides/structured-outputs
https://developers.openai.com/api/docs/guides/images-vision
https://developers.openai.com/api/docs/guides/reasoning
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import math
import time
from pathlib import Path

from jsonschema import Draft202012Validator
from PIL import Image

from ..budget import BudgetError, BudgetLedger
from ..settings import SECRET_NAMES
from ..telemetry import Telemetry, canonical_json, digest, sanitize


MODEL = "gpt-5.4-2026-03-05"
PRICEBOOK = {"model": MODEL, "currency": "USD", "input_per_million": 2.5,
             "cached_input_per_million": 0.25, "output_per_million": 15.0,
             "input_ceiling": 200_000, "service_tier": "default",
             "source": "https://developers.openai.com/api/docs/models/gpt-5.4",
             "verified_date": "2026-09-08"}
MINI_MODEL = "gpt-5.4-mini-2026-03-17"
MINI_PRICEBOOK = {"model": MINI_MODEL, "currency": "USD", "input_per_million": .75,
                  "cached_input_per_million": .075, "output_per_million": 4.5,
                  "input_ceiling": 200_000, "long_context_threshold": 272_000,
                  "service_tier": "default",
                  "source": "https://developers.openai.com/api/docs/models/gpt-5.4-mini",
                  "verified_date": "2026-09-09"}
PRICEBOOKS = {MODEL: PRICEBOOK, MINI_MODEL: MINI_PRICEBOOK}


def _dict(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return vars(value)


def normalize_usage(raw) -> dict:
    raw = _dict(raw)
    result = {"input_tokens": raw.get("input_tokens"),
              "cached_input_tokens": _dict(raw.get("input_tokens_details")).get("cached_tokens"),
              "output_tokens": raw.get("output_tokens"),
              "reasoning_tokens": _dict(raw.get("output_tokens_details")).get("reasoning_tokens"),
              "total_tokens": raw.get("total_tokens")}
    for value in result.values():
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("invalid_usage")
    i, c, o, r = (result[name] for name in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens"))
    if c is not None and i is not None and c > i or r is not None and o is not None and r > o:
        raise ValueError("invalid_usage")
    if result["total_tokens"] is not None and i is not None and o is not None and result["total_tokens"] != i + o:
        raise ValueError("invalid_usage")
    result["usage_certainty"] = "known" if all(result[name] is not None for name in
        ("input_tokens", "cached_input_tokens", "output_tokens")) else "unknown"
    return result


def usage_cost(usage: dict, pricebook: dict | None = None) -> dict:
    """Reasoning is attribution inside output cost, never an extra charge."""
    if usage.get("usage_certainty") != "known":
        return {"cost_usd": None, "input_cost_usd": None, "output_cost_usd": None,
                "reasoning_cost_usd": None, "other_output_cost_usd": None}
    pricebook = pricebook or PRICEBOOK
    i, c, o, r = (usage[name] for name in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens"))
    if i > pricebook.get("long_context_threshold", 272_000):
        raise ValueError("unsupported_long_context_pricing")
    input_cost = ((i - c) * pricebook["input_per_million"] + c * pricebook["cached_input_per_million"]) / 1_000_000
    output_cost = o * pricebook["output_per_million"] / 1_000_000
    reasoning_cost = None if r is None else r * pricebook["output_per_million"] / 1_000_000
    return {"cost_usd": input_cost + output_cost, "input_cost_usd": input_cost,
            "output_cost_usd": output_cost, "reasoning_cost_usd": reasoning_cost,
            "other_output_cost_usd": None if r is None else (o - r) * 15 / 1_000_000}


def _reject_remote_refs(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"$ref", "$dynamicRef"} and not str(item).startswith("#"):
                raise ValueError("remote_schema_reference_forbidden")
            _reject_remote_refs(item)
    elif isinstance(value, list):
        for item in value:
            _reject_remote_refs(item)


def provider_safe_schema(schema):
    """Translate valid Draft 2020-12 features absent from API strict schemas.

    The complete original schema remains the authoritative local validator.
    Tuple arrays become fixed-length arrays whose members use an anyOf union;
    local validation still enforces order and exact tuple semantics.
    """
    def convert(value):
        if isinstance(value, list):
            return [convert(item) for item in value]
        if not isinstance(value, dict):
            return value
        output = {}
        for key, item in value.items():
            if key in {"$schema", "$id"}:
                continue
            if key == "const":
                output["enum"] = [convert(item)]
            elif key not in {"prefixItems"} and not (key == "items" and item is False):
                output[key] = convert(item)
        if "prefixItems" in value:
            choices = [convert(item) for item in value["prefixItems"]]
            output["minItems"] = output.get("minItems", len(choices))
            output["maxItems"] = output.get("maxItems", len(choices))
            output["items"] = choices[0] if all(item == choices[0] for item in choices) else {"anyOf": choices}
        return output
    return convert(copy.deepcopy(schema))


def _load_json(text: str):
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result
    def no_constant(value):
        raise ValueError("nonfinite_json")
    return json.loads(text, object_pairs_hook=no_duplicates, parse_constant=no_constant)


class OpenAIProvider:
    def __init__(self, settings: dict, ledger: BudgetLedger, log_dir: Path, *, client=None, pricebooks=None):
        self.settings, self.ledger, self.log_dir = settings, ledger, Path(log_dir)
        self.secrets = tuple(settings.get(name, "") for name in SECRET_NAMES)
        self.telemetry = Telemetry(self.log_dir / "telemetry.jsonl", secrets=self.secrets)
        self.pricebooks = dict(pricebooks or PRICEBOOKS)
        for name in ("MF_PLANNER_MODEL", "MF_VISION_MODEL"):
            if settings.get(name, MODEL) not in self.pricebooks:
                raise ValueError("Requested model has no frozen pricebook")
        for effort in (settings.get("MF_REASONING_EFFORT", "medium"), settings.get("MF_PLANNER_REASONING_EFFORT", "medium"), settings.get("MF_VISION_REASONING_EFFORT", "medium")):
            if effort not in {"none", "low", "medium", "high", "xhigh"}:
                raise ValueError("Unsupported reasoning effort")
        if settings.get("MF_IMAGE_DETAIL", "high") not in {"low", "high"}:
            raise ValueError("Unsupported image detail")
        if client is None:
            if not settings.get("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY is required for live calls")
            from openai import OpenAI
            client = OpenAI(api_key=settings["OPENAI_API_KEY"], base_url="https://api.openai.com/v1",
                            max_retries=0, timeout=float(settings.get("MF_API_TIMEOUT_SECONDS", 180)))
        self.client = client

    def _prepare(self, prompt, schema, images, max_output_tokens, pricebook, image_detail):
        if type(max_output_tokens) is not int or not 1 <= max_output_tokens <= min(32768, int(self.settings.get("MF_LLM_MAX_OUTPUT_TOKENS", 8192))):
            raise ValueError("invalid_output_token_limit")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("empty_prompt")
        if len(images) > 8:
            raise ValueError("too_many_images")
        _reject_remote_refs(schema)
        Draft202012Validator.check_schema(schema)
        api_schema = provider_safe_schema(schema)
        Draft202012Validator.check_schema(api_schema)
        schema_text = canonical_json(api_schema)
        content = [{"type": "input_text", "text": prompt}]
        image_info = []
        for path in images:
            path = Path(path)
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 10_000_000:
                raise ValueError("invalid_local_image")
            raw = path.read_bytes()
            with Image.open(path) as im:
                width, height = im.size
                fmt = im.format
                if fmt not in {"PNG", "JPEG", "WEBP"} or getattr(im, "n_frames", 1) != 1 or width * height > 16_000_000:
                    raise ValueError("unsupported_image")
                im.verify()
            mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[fmt]
            content.append({"type": "input_image", "image_url": f"data:{mime};base64," + base64.b64encode(raw).decode("ascii"), "detail": image_detail})
            image_info.append({"sha256": hashlib.sha256(raw).hexdigest(), "width": width,
                               "height": height, "bytes": len(raw), "mime_type": mime, "detail": image_detail})
        # UTF-8 bytes bound text tokens conservatively; allow protocol overhead.
        # GPT-5.4 high: at most 2500 image patches * 1.2 = 3000 tokens.
        # Reserve 4096 per image, including additional per-item overhead.
        input_bound = len(prompt.encode("utf-8")) + len(schema_text.encode("utf-8")) + 4096 + 4096 * len(images)
        if input_bound > pricebook["input_ceiling"]:
            raise ValueError("input_exceeds_qualified_pricing_profile")
        reserve = (input_bound * pricebook["input_per_million"] + max_output_tokens * pricebook["output_per_million"]) / 1_000_000
        return content, image_info, input_bound, reserve, api_schema

    def generate_json(self, *, purpose: str, prompt: str, schema: dict,
                      images: list[Path] | None = None, run_id: str, stage: str,
                      max_output_tokens: int = 8192) -> dict:
        """No automatic retry. Caller may invoke again with a new accounted request."""
        result = {"data": None, "usage": normalize_usage(None), "cost_usd": None,
                  "response_id": None, "error": None, "reservation_id": None}
        image_inputs = images or []
        model = self.settings.get("MF_VISION_MODEL" if image_inputs else "MF_PLANNER_MODEL", MODEL)
        pricebook = self.pricebooks[model]
        image_detail = self.settings.get("MF_IMAGE_DETAIL", "high")
        effort = self.settings.get("MF_VISION_REASONING_EFFORT" if image_inputs else "MF_PLANNER_REASONING_EFFORT", self.settings.get("MF_REASONING_EFFORT", "medium"))
        try:
            content, image_info, input_bound, reserve, api_schema = self._prepare(prompt, schema, image_inputs, max_output_tokens, pricebook, image_detail)
        except Exception as exc:
            result["error"] = "request_validation:" + type(exc).__name__
            return result
        scope = self.settings.get("MF_COST_SCOPE", "development")
        try:
            request_id = self.ledger.reserve(run_id=run_id, stage=stage, amount_usd=reserve,
                        scope=scope, purpose=purpose, input_token_bound=input_bound,
                        max_output_tokens=max_output_tokens, model=model, prompt_hash=digest(prompt))
        except BudgetError as exc:
            result["error"] = "budget_denied:" + type(exc).__name__
            return result
        result["reservation_id"] = request_id
        common = {"run_id": run_id, "stage": stage, "cost_scope": scope, "purpose": purpose,
                  "reservation_id": request_id, "provider": "openai", "requested_model": model,
                  "prompt_hash": digest(prompt), "schema_hash": digest(schema)}
        # If durable audit logging fails, do not dispatch. Keep reservation conservative.
        self.telemetry.emit("provider_request", **common, prompt=prompt, schema=schema,
                            images=image_info, input_token_bound=input_bound,
                            max_output_tokens=max_output_tokens, reserved_usd=reserve,
                            reasoning_effort=effort, image_detail=image_detail,
                            pricebook=pricebook, status="reserved")
        started = time.monotonic()
        try:
            response = self.client.responses.create(
                model=model, input=[{"role": "user", "content": content}],
                text={"format": {"type": "json_schema", "name": "movie_factory_result", "strict": True, "schema": api_schema}},
                reasoning={"effort": effort},
                max_output_tokens=max_output_tokens, store=False, service_tier="default",
                tools=[], truncation="disabled")
        except Exception as exc:
            # Never log raw exceptions: SDK messages can contain request material.
            status = getattr(exc, "status_code", None)
            result["error"] = "provider_error:" + type(exc).__name__
            if type(status) is int:
                result["http_status"] = status
            self.ledger.settle(request_id, cost_usd=None, error=result["error"])
            self.telemetry.emit("provider_result", **common, **{key: value for key, value in result.items() if key != "reservation_id"},
                                latency_seconds=time.monotonic() - started, status="failed_unknown_charge")
            return result
        raw = _dict(response)
        result["response_id"] = raw.get("id")
        returned_model = raw.get("model")
        result["returned_model"] = returned_model
        result["provider_request_id"] = getattr(response, "_request_id", None)
        try:
            usage = normalize_usage(raw.get("usage"))
            costs = usage_cost(usage, pricebook)
            result.update(costs, usage=usage)
            if returned_model != model:
                result["cost_usd"] = None
                raise ValueError("unexpected_model")
            if raw.get("service_tier", "default") != "default":
                result["cost_usd"] = None
                raise ValueError("unexpected_service_tier")
            if usage.get("input_tokens") is not None and usage["input_tokens"] > input_bound:
                raise ValueError("input_reservation_bound_exceeded")
            if usage.get("output_tokens") is not None and usage["output_tokens"] > max_output_tokens:
                raise ValueError("output_token_bound_exceeded")
            if result["cost_usd"] is None:
                raise ValueError("usage_unavailable")
            if raw.get("status") != "completed":
                raise ValueError("response_not_completed")
            texts = []
            for output in raw.get("output", []):
                if output.get("type") == "reasoning":
                    continue
                if output.get("type") != "message":
                    raise ValueError("unexpected_output_item")
                for item in output.get("content", []):
                    if item.get("type") == "refusal":
                        raise ValueError("refusal")
                    if item.get("type") != "output_text":
                        raise ValueError("unexpected_output_content")
                    texts.append(item["text"])
            if not texts:
                raise ValueError("missing_json_output")
            data = _load_json("".join(texts))
            if not isinstance(data, dict):
                raise ValueError("nonobject_json_output")
            Draft202012Validator(schema).validate(data)
            result["data"] = data
        except Exception as exc:
            safe_codes = {"invalid_usage", "unsupported_long_context_pricing", "unexpected_model", "unexpected_service_tier",
                          "input_reservation_bound_exceeded", "output_token_bound_exceeded", "usage_unavailable",
                          "response_not_completed", "unexpected_output_item", "refusal", "unexpected_output_content",
                          "missing_json_output", "nonobject_json_output", "duplicate_json_key", "nonfinite_json"}
            message = str(exc) if type(exc) is ValueError and str(exc) in safe_codes else type(exc).__name__
            result["error"] = "response_invalid:" + message
        self.ledger.settle(request_id, cost_usd=result["cost_usd"], usage=result["usage"],
                           response_id=result["response_id"], error=result["error"])
        self.telemetry.emit("provider_result", **common,
                            **{key: value for key, value in result.items() if key != "reservation_id"},
                            latency_seconds=time.monotonic() - started,
                            status="completed" if not result["error"] else "failed")
        return result
