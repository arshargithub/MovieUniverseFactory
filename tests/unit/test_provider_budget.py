from concurrent.futures import ThreadPoolExecutor
import pytest

from movie_factory.budget import BudgetLedger, BudgetError, BudgetExceeded, LedgerCorrupt


def test_reservation_survives_restart_and_unknown_settlement(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = BudgetLedger(path)
    request = ledger.reserve(run_id="run1", stage="initial", amount_usd=1)
    ledger.settle(request, cost_usd=None, error="timeout")
    reopened = BudgetLedger(path)
    assert reopened.summary()["reserved_unknown_usd"] == 1
    assert reopened.summary()["unresolved_calls"] == 1
    reopened.settle(request, cost_usd=0.2, response_id="resp_test")
    assert reopened.summary()["known_cost_usd"] == 0.2
    assert reopened.summary()["reserved_unknown_usd"] == 0
    reopened.settle(request, cost_usd=0.2, response_id="resp_test")
    assert reopened.summary()["calls"] == 1
    with pytest.raises(BudgetError):
        reopened.settle(request, cost_usd=0.3, response_id="resp_test")


def test_per_run_stage_cost_and_call_limits(tmp_path):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl")
    ledger.reserve(run_id="r1", stage="revision", amount_usd=2)
    with pytest.raises(BudgetExceeded, match="stage spend"):
        ledger.reserve(run_id="r1", stage="revision", amount_usd=0.01)
    for _ in range(8):
        request = ledger.reserve(run_id="r2", stage="initial", amount_usd=0.1)
        ledger.settle(request, cost_usd=0)
    with pytest.raises(BudgetExceeded, match="call"):
        ledger.reserve(run_id="r2", stage="initial", amount_usd=0.1)


def test_scope_and_campaign_include_distinct_runs(tmp_path):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", campaign_limit=1.5,
                          scope_limits={"development": 1, "faults": 1, "scored": 1})
    ledger.reserve(run_id="a", stage="initial", scope="development", amount_usd=1)
    with pytest.raises(BudgetExceeded, match="Scope"):
        ledger.reserve(run_id="b", stage="initial", scope="development", amount_usd=0.1)
    ledger.reserve(run_id="c", stage="initial", scope="scored", amount_usd=0.5)
    with pytest.raises(BudgetExceeded, match="Campaign"):
        ledger.reserve(run_id="d", stage="initial", scope="faults", amount_usd=0.1)


def test_concurrent_reservations_are_atomic(tmp_path):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", campaign_limit=0.5)
    def reserve(index):
        try:
            ledger.reserve(run_id=f"run{index}", stage="initial", amount_usd=0.1)
            return True
        except BudgetExceeded:
            return False
    with ThreadPoolExecutor(max_workers=10) as pool:
        outcomes = list(pool.map(reserve, range(10)))
    assert sum(outcomes) == 5
    assert ledger.summary()["committed_usd"] == 0.5


def test_cannot_reuse_request_identity_or_broaden_policy(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = BudgetLedger(path)
    request = ledger.reserve(run_id="r1", stage="initial", amount_usd=1)
    with pytest.raises(BudgetError, match="already reserved"):
        ledger.reserve(run_id="r1", stage="initial", amount_usd=1, reservation_id=request)
    with pytest.raises(BudgetError):
        BudgetLedger(path, campaign_limit=100)


def test_torn_or_modified_ledger_fails_closed(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = BudgetLedger(path)
    with path.open("a") as handle:
        handle.write('{"incomplete":')
    with pytest.raises(LedgerCorrupt):
        ledger.reserve(run_id="x", stage="initial", amount_usd=1)


@pytest.mark.parametrize("amount", [-1, float("nan"), float("inf"), 0])
def test_invalid_reservations_denied(tmp_path, amount):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl")
    with pytest.raises(BudgetError):
        ledger.reserve(run_id="x", stage="initial", amount_usd=amount)
