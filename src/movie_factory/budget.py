"""Append-only, locked budget ledger; outstanding/unknown charges stay reserved."""
from __future__ import annotations
import fcntl
import json
import math
import os
import uuid
from contextlib import contextmanager
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from .telemetry import canonical_json, digest, utc_now


class BudgetError(RuntimeError):
    pass


class BudgetExceeded(BudgetError):
    pass


class LedgerCorrupt(BudgetError):
    pass


def _units(value) -> int:
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number < 0:
            raise ValueError
        return int((number * 1_000_000_000).to_integral_value(rounding=ROUND_CEILING))
    except (ValueError, TypeError, ArithmeticError):
        raise BudgetError("Cost must be a finite nonnegative USD amount") from None


class BudgetLedger:
    """The file owns policy after first creation; reopening cannot increase caps.

    reserve() counts a physical request before dispatch. settle(None) keeps its
    entire reservation. A later known settlement may reconcile an unknown one;
    conflicting known settlements fail. A torn/corrupted log fails closed.
    """

    def __init__(self, path: Path, campaign_limit: float = 40, *,
                 scope_limits=None, stage_limits=None, request_limit=None,
                 request_ceiling_usd=None, work_item_attempt_limit=None, additional_campaign_ceiling_usd=None):
        self.additional_campaign_ceiling_units = (_units(additional_campaign_ceiling_usd) if additional_campaign_ceiling_usd is not None else None)
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.policy = {
            "campaign_limit_units": _units(campaign_limit),
            "scope_limits_units": {key: _units(value) for key, value in
                                   (scope_limits or {"development": 10, "faults": 5, "scored": 25}).items()},
            "stage_limits": {key: {"amount_units": _units(value[0]), "calls": int(value[1])}
                             for key, value in (stage_limits or {
                                 "initial": (3, 8), "revision": (2, 6),
                                 "development": (10, 50), "faults": (5, 30)}).items()},
        }
        # Optional campaign-wide controls; omitted fields preserve historical policies.
        for key, value in (("request_limit", request_limit), ("work_item_attempt_limit", work_item_attempt_limit)):
            if value is not None:
                if type(value) is not int or value <= 0:
                    raise BudgetError("Request limits must be positive integers")
                self.policy[key] = value
        if request_ceiling_usd is not None:
            self.policy["request_ceiling_units"] = _units(request_ceiling_usd)
        if any(item["calls"] <= 0 for item in self.policy["stage_limits"].values()):
            raise BudgetError("Call limits must be positive")
        with self._locked() as handle:
            events = self._read(handle)
            if not events:
                self._append(handle, [], {"event_type": "policy", "policy": self.policy})
            elif events[0].get("policy") != self.policy:
                raise BudgetError("Existing ledger policy differs; caps cannot change on restart")

    @contextmanager
    def _locked(self):
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "r+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            os.fchmod(handle.fileno(), 0o600)
            yield handle

    def _read(self, handle) -> list:
        handle.seek(0)
        text = handle.read()
        if text and not text.endswith("\n"):
            raise LedgerCorrupt("Incomplete budget ledger record; reconcile before dispatch")
        events, previous = [], None
        try:
            for line in text.splitlines():
                event = json.loads(line)
                claimed = event.pop("event_hash")
                if event.get("previous_hash") != previous or digest(event) != claimed:
                    raise ValueError
                event["event_hash"] = claimed
                events.append(event)
                previous = claimed
        except (ValueError, TypeError, KeyError):
            raise LedgerCorrupt("Budget ledger integrity check failed") from None
        if events and (events[0].get("event_type") != "policy" or events[0].get("policy") != self.policy):
            raise LedgerCorrupt("Budget ledger policy mismatch")
        return events

    def _append(self, handle, events, event) -> dict:
        event = {"schema_version": "1.0", "event_id": str(uuid.uuid4()), "utc": utc_now(),
                 "previous_hash": events[-1]["event_hash"] if events else None, **event}
        event["event_hash"] = digest(event)
        handle.seek(0, os.SEEK_END)
        handle.write(canonical_json(event) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        # Persist the directory entry too, so a first reservation survives restart.
        directory_fd = os.open(self.path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return event

    @staticmethod
    def _reservations(events) -> dict:
        requests = {}
        for event in events[1:]:
            identity = event.get("reservation_id")
            if event["event_type"] == "reserved":
                if identity in requests:
                    raise LedgerCorrupt("Duplicate physical request reservation")
                requests[identity] = dict(event)
            elif event["event_type"] == "settled":
                if identity not in requests:
                    raise LedgerCorrupt("Settlement without reservation")
                requests[identity]["settlement"] = event
            else:
                raise LedgerCorrupt("Unknown budget ledger event")
        return requests

    @staticmethod
    def _charge(request) -> int:
        cost = request.get("settlement", {}).get("cost_units")
        return request["amount_units"] if cost is None else cost

    def reserve(self, *, run_id: str, stage: str, amount_usd: float,
                scope: str = "scored", purpose: str = "provider_call",
                reservation_id: str | None = None, **metadata) -> str:
        if stage not in self.policy["stage_limits"] or scope not in self.policy["scope_limits_units"]:
            raise BudgetError("Unknown budget stage or scope")
        if not isinstance(run_id, str) or not run_id or len(run_id) > 200:
            raise BudgetError("A bounded run_id is required")
        amount = _units(amount_usd)
        if amount <= 0:
            raise BudgetError("Live request requires a positive reservation")
        identity = reservation_id or str(uuid.uuid4())
        allowed_metadata = {key: value for key, value in metadata.items()
                            if key in {"input_token_bound", "max_output_tokens", "model", "prompt_hash"}}
        with self._locked() as handle:
            events = self._read(handle)
            requests = self._reservations(events)
            if any(item.get("settlement", {}).get("reservation_exceeded") for item in requests.values()):
                raise BudgetExceeded("Prior charge exceeded its reservation; reconcile bounding before dispatch")
            if len(requests) >= self.policy.get("request_limit", float("inf")):
                raise BudgetExceeded("Campaign physical request ceiling reached")
            if amount > self.policy.get("request_ceiling_units", float("inf")):
                raise BudgetExceeded("Per-request ceiling exceeded")
            attempts = [item for item in requests.values() if item["purpose"] == purpose]
            if len(attempts) >= self.policy.get("work_item_attempt_limit", float("inf")):
                raise BudgetExceeded("Work item attempt ceiling reached")
            if attempts and "work_item_attempt_limit" in self.policy and scope != "contingency":
                raise BudgetError("Work item retries must charge contingency")
            if identity in requests:
                raise BudgetError("Request identity already reserved; do not redispatch it")
            total = sum(self._charge(item) for item in requests.values())
            scope_total = sum(self._charge(item) for item in requests.values() if item["scope"] == scope)
            stage_requests = [item for item in requests.values() if item["run_id"] == run_id and item["stage"] == stage]
            stage_total = sum(self._charge(item) for item in stage_requests)
            stage_limit = self.policy["stage_limits"][stage]
            if total + amount > min(self.policy["campaign_limit_units"], self.additional_campaign_ceiling_units if self.additional_campaign_ceiling_units is not None else self.policy["campaign_limit_units"]):
                raise BudgetExceeded("Campaign spend ceiling would be exceeded")
            if scope_total + amount > self.policy["scope_limits_units"][scope]:
                raise BudgetExceeded("Scope spend ceiling would be exceeded")
            if stage_total + amount > stage_limit["amount_units"]:
                raise BudgetExceeded("Run stage spend ceiling would be exceeded")
            if len(stage_requests) >= stage_limit["calls"]:
                raise BudgetExceeded("Run stage call ceiling would be exceeded")
            self._append(handle, events, {"event_type": "reserved", "reservation_id": identity,
                         "run_id": run_id, "stage": stage, "scope": scope, "purpose": purpose,
                         "amount_units": amount, **allowed_metadata})
        return identity

    def settle(self, reservation_id: str, *, cost_usd: float | None,
               usage: dict | None = None, response_id: str | None = None,
               error: str | None = None) -> dict:
        cost = None if cost_usd is None else _units(cost_usd)
        with self._locked() as handle:
            events = self._read(handle)
            requests = self._reservations(events)
            if reservation_id not in requests:
                raise BudgetError("Cannot settle an unknown reservation")
            request = requests[reservation_id]
            existing = request.get("settlement")
            if existing:
                if existing["cost_units"] == cost and existing.get("response_id") == response_id:
                    return existing
                if existing["cost_units"] is not None:
                    raise BudgetError("Conflicting settlement; known charges are immutable")
                if cost is None:
                    raise BudgetError("Conflicting unknown settlement")
            numeric_usage = {key: value for key, value in (usage or {}).items()
                             if key in {"input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"}
                             and (value is None or type(value) is int)}
            return self._append(handle, events, {
                "event_type": "settled", "reservation_id": reservation_id, "cost_units": cost,
                "usage": numeric_usage, "response_id": response_id, "error": error,
                "usage_unknown": cost is None,
                "reservation_exceeded": cost is not None and cost > request["amount_units"],
            })

    def summary(self) -> dict:
        with self._locked() as handle:
            requests = self._reservations(self._read(handle))
        def totals(items):
            items = list(items)
            known = sum(item.get("settlement", {}).get("cost_units") or 0 for item in items)
            unknown = [item for item in items if item.get("settlement", {}).get("cost_units") is None]
            return {"calls": len(items), "known_cost_usd": known / 1e9,
                    "reserved_unknown_usd": sum(item["amount_units"] for item in unknown) / 1e9,
                    "committed_usd": sum(self._charge(item) for item in items) / 1e9,
                    "unresolved_calls": len(unknown),
                    "reservation_exceeded": any(item.get("settlement", {}).get("reservation_exceeded", False) for item in items)}
        return {**totals(requests.values()), "campaign_limit_usd": self.policy["campaign_limit_units"] / 1e9,
                "effective_campaign_limit_usd": min(self.policy["campaign_limit_units"], self.additional_campaign_ceiling_units if self.additional_campaign_ceiling_units is not None else self.policy["campaign_limit_units"]) / 1e9,
                "scopes": {scope: totals(item for item in requests.values() if item["scope"] == scope)
                           for scope in self.policy["scope_limits_units"]},
                "runs": {run: {stage: totals(item for item in requests.values() if item["run_id"] == run and item["stage"] == stage)
                                for stage in self.policy["stage_limits"]}
                         for run in sorted({item["run_id"] for item in requests.values()})}}
