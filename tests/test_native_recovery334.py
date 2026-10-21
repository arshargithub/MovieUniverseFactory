"""Recovery does not reset artistic limits or hide failed native attempts."""
import copy
import pytest
from movie_factory import native_admission as na, production_workflow as wf
from movie_factory.adapters.blender import runner
from test_production_workflow import setup
from test_native_handler333 import prepare, run


def failed(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch)
    monkeypatch.setattr(runner, 'run_blender', lambda *a, **kw: {'ok': False})
    result = run(root, bridge)
    assert result['status'] == 'FAILED'
    request = dict(c.state('t')['routing']['request'], continuation=True)
    c.route_request('recovery', request, 't')
    return root, c, bridge


def test_recovery_retains_task_counter_history_and_requires_new_plan(setup, monkeypatch):
    root, c, bridge = failed(setup, monkeypatch)
    old = c.state('t')
    result = c.recover_native_control('t', 'recovery', old['direction'], 'preflight diagnosis', 'recover')
    assert result['stage'] == 'BRIEFING' and result['planning_step'] == 'GROUNDING'
    assert result['cycle'] == old['cycle'] and result['max_corrections'] == old['max_corrections']
    assert result['technical_recoveries'] == 1 and not result['planning_artifacts']
    assert c.packet('t')['planning_step'] == 'GROUNDING'
    assert bridge.runs(old)['proof']['status'] == 'FAILED'
    with pytest.raises(wf.Blocked): run(root, bridge)
    assert c.recover_native_control('t', 'recovery', old['direction'], 'preflight diagnosis', 'recover') == result


@pytest.mark.parametrize('fault', ['scope', 'lease', 'no_continuation', 'no_failure', 'failed_review', 'limit'])
def test_recovery_guards(setup, monkeypatch, fault):
    root, c, bridge = failed(setup, monkeypatch)
    old = c.state('t'); direction = copy.deepcopy(old['direction'])
    admission = 'recovery'
    if fault == 'scope': direction['intent'] = 'New artistic work'
    if fault == 'no_continuation': admission = 'request'
    if fault == 'lease': c.job('t', 'held', 'acquire', 'held')
    if fault in {'no_failure', 'failed_review', 'limit'}:
        def mutate(con):
            state = c._state(con, 't')
            if fault == 'limit': state['technical_recoveries'] = 3
            if fault == 'failed_review': state['review'] = {'verdict': 'FAIL'}
            if fault == 'no_failure': state['fingerprint'] = 'no such run'
            return state
        c._change('t', 'synthetic-only', 'synthetic-test', {}, mutate)
    with pytest.raises(wf.Blocked):
        c.recover_native_control('t', admission, direction, 'diagnosis', 'recover')
