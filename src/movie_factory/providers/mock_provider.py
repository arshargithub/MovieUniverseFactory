"""Explicit zero-charge fake; output must be supplied by the test/controller."""
from __future__ import annotations
from copy import deepcopy
from jsonschema import Draft202012Validator

class MockProvider:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    def generate_json(self, *, purpose, prompt, schema, images=None, run_id, stage, max_output_tokens=8192):
        self.calls.append({"purpose": purpose, "run_id": run_id, "stage": stage})
        result = {"data": None, "usage": {"input_tokens": 0, "cached_input_tokens": 0,
                  "output_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0,
                  "usage_certainty": "mock"}, "cost_usd": 0.0,
                  "response_id": None, "error": None, "provider": "mock"}
        if not self.responses:
            result["error"] = "mock_response_not_configured"
            return result
        value = deepcopy(self.responses.pop(0))
        try:
            Draft202012Validator(schema).validate(value)
            result["data"] = value
        except Exception:
            result["error"] = "mock_schema_invalid"
        return result
