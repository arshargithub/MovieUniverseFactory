"""Offline control tests. No Blender/provider calls or artistic pass fixtures."""
import copy
import json
from pathlib import Path
import pytest
from movie_factory import task_router as tr, native_admission as na
from movie_factory import production_workflow as wf
from movie_factory.adapters.blender import runner
REAL_RUNNER = runner.run_blender
from test_production_workflow import setup, bind, direction, submit, build, review
import planning_fixtures as pf


def request(root, ops):
    return {'text': 'Synthetic requested work', 'operations': ops,
            'rationale': 'Synthetic scope interpretation', 'authority': bind(root, 'authority.md')}


@pytest.mark.parametrize('ops,route', [(['display'], 'show'), (['explain'], 'show'),
    (['research'], 'research'), (['plan'], 'plan'), (['code', 'test'], 'engineering'),
    (['upload'], 'operations'), (['research', 'asset'], 'production'),
    (['display', 'motion'], 'production'), (['native_inspect'], 'production')])
def test_route_selection(ops, route):
    d = tr.decide({'text': 'Request', 'operations': ops, 'rationale': 'Reason'})
    assert d['route'] == route and not d['authority_granted']


@pytest.mark.parametrize('ops', [[], ['unknown'], ['render', 'render'], 'render'])
def test_unknown_not_lightweight(ops):
    with pytest.raises(ValueError): tr.decide({'text': 'Work', 'operations': ops, 'rationale': 'Reason'})


def test_native_runner_without_controller_refuses_before_side_effect(tmp_path):
    out = tmp_path / 'out'
    with pytest.raises(wf.Blocked, match='ROUTE_FIRST'):
        runner.run_blender({'output_dir': str(out)}, blender_bin='/never/launched')
    assert not out.exists()


def test_routing_persisted_before_task_and_idempotent(setup):
    root, c, b, _ = setup
    req = request(root, ['display'])
    d = c.route_request('request', req)
    assert c.route_request('request', req) == d
    with pytest.raises(wf.Blocked, match='CONFLICT'):
        c.route_request('request', request(root, ['render']))
    c.create('show', 'show', req['authority'], 'create', admission='request')
    assert c.state('show')['routing'] == d
    assert c.state('show')['stage'] == 'LIGHTWEIGHT'
    c.complete_lightweight('show', {'offline_only': True, 'verification': 'Synthetic file present',
        'artifacts': {'display': bind(root, 'evidence.jpg')}}, 'done')
    assert c.deliver('show', 'delivery')['receipt']['stage'] == 'COMPLETE'


def test_direct_native_create_and_misrouting_block(setup):
    root, c, b, _ = setup
    with pytest.raises(wf.Blocked, match='ROUTE_FIRST'):
        c.create('t', 'production', bind(root, 'authority.md'), 'c', direction=direction(b), mode='local_native')
    c.route_request('r', request(root, ['render']))
    with pytest.raises(wf.Blocked, match='ROUTE_MISMATCH'):
        c.create('t', 'show', bind(root, 'authority.md'), 'c', admission='r')


def test_continuation_preserves_identity_not_new_budget(setup):
    root, c, b, _ = setup
    c.create('t', 'production', bind(root, 'authority.md'), 'c', direction=direction(b))
    req = request(root, ['render']) | {'continuation': True}
    d = c.route_request('continue', req, 't')
    assert d['route'] == 'production'
    with pytest.raises(wf.Blocked, match='NO_NEW_LIMIT'):
        c.create('other', 'production', req['authority'], 'c2', direction=direction(b, 'other'), admission='continue')
    with pytest.raises(ValueError, match='SCOPE_EXPANSION'):
        c.route_request('expansion', req | {'operations': ['upload']}, 't')


def native(setup, monkeypatch, plan=True):
    root, _, b, _ = setup
    c = wf.Controller(root, tr.DATABASE)
    (root / 'parent.blend').write_bytes(b'SYNTHETIC NATIVE')
    b['source_bindings']['parent'] = bind(root, 'parent.blend')
    b['offline_only'] = False
    req = request(root, ['native_inspect'])
    c.route_request('request', req)
    c.create('t', 'production', req['authority'], 'create', direction=direction(b), mode='local_native', admission='request')
    if plan:
        pf.complete(c, 't', b, 'plan')
    calls = []
    def worker(job, *, _admission, **kwargs):
        na.check_capability(_admission, job)
        calls.append(copy.deepcopy(job))
        output = Path(job['output_dir']); output.mkdir(parents=True)
        (output / 'snapshot.json').write_text('{"synthetic":true}')
        return {'ok': True}
    monkeypatch.setattr(runner, 'run_blender', worker)
    return root, c, b, na.Bridge(c), calls


def dispatch(root, bridge, step='proof', ident='proof-run'):
    return bridge.dispatch('t', step, ident, parent=bind(root, 'parent.blend'), blender_bin=na.BLENDER_BIN)


def step_review(bridge, run, verdict='PASS'):
    return bridge.record_review('t', run['step'], {'verdict': verdict,
        'observation': 'Synthetic fixture inspected', 'comparison': 'Synthetic expected snapshot',
        'open_defects': [], 'evidence': run['artifacts'], 'run_digest': wf.pk.digest(run)})


def test_plan_must_precede_native(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch, plan=False)
    with pytest.raises(wf.Blocked, match='BEFORE_PLANNING'):
        dispatch(root, bridge)
    assert calls == []


def test_dependency_actual_output_review_precedes_build(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    with pytest.raises(wf.Blocked, match='DEPENDENCY_NOT_RUN'):
        dispatch(root, bridge, 'build', 'build-run')
    run = dispatch(root, bridge)
    with pytest.raises(wf.Blocked, match='REVIEW_NOT_RUN'):
        dispatch(root, bridge, 'build', 'build-run')
    step_review(bridge, run, 'FAIL')
    with pytest.raises(wf.Blocked, match='REVIEW_FAILED'):
        dispatch(root, bridge, 'build', 'build-run')
    assert len(calls) == 1


def test_job_replay_and_foreign_candidate_blocked(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    run = dispatch(root, bridge); step_review(bridge, run)
    with pytest.raises(wf.Blocked, match='ALREADY_ATTEMPTED'):
        dispatch(root, bridge, ident='new-name-same-step')
    run2 = dispatch(root, bridge, 'build', 'build-run'); step_review(bridge, run2)
    with pytest.raises(wf.Blocked, match='NOT_DISPATCH_OUTPUTS'):
        build(root, c)
    assert c.state('t')['stage'] == 'EXECUTING'
    assert len(calls) == 2


def test_native_outputs_must_enter_final_review(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    for step in ['proof', 'build']:
        run = dispatch(root, bridge, step, step + '-run'); step_review(bridge, run)
    state = c.state('t')
    artifacts = {step + ':' + key: val for step, run in bridge.runs(state).items() for key, val in run['artifacts'].items()}
    import expert_fixtures as ef
    result = {'fingerprint': state['fingerprint'], 'requirement_uses': ef.uses(b),
        'reference_uses': {r['id']: {'reference_digest': wf.pk.digest(r), 'application': 'Synthetic'} for r in b['references']},
        'candidate': {'version': 'native-fixture', 'artifacts': artifacts}}
    submit(c, 't', result, 'builder')
    with pytest.raises(wf.Blocked, match='NOT_READY'): c.deliver('t', 'deliver')
    assert c.state('t')['stage'] == 'REVIEWING'
    submit(c, 't', review(root, c, status='FAIL'), 'review')
    assert c.state('t')['cycle'] == 1
    assert c.state('t')['stage'] == 'EXECUTING'


def test_source_change_and_dependency_change_block(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    run = dispatch(root, bridge); step_review(bridge, run)
    (root / run['artifacts']['snapshot']['path']).write_text('{}')
    with pytest.raises(ValueError): dispatch(root, bridge, 'build', 'build-run')
    (root / 'parent.blend').write_text('CHANGED')
    with pytest.raises(ValueError): dispatch(root, bridge, 'build', 'build-run')
    assert len(calls) == 1


def test_offline_and_frozen_cannot_native(setup):
    root, _, b, _ = setup
    (root / 'parent.blend').write_text('SYNTHETIC')
    c = wf.Controller(root, tr.DATABASE)
    c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=direction(b))
    pf.complete(c, 't', b, 'plan')
    with pytest.raises(wf.Blocked, match='OFFLINE_OR_FROZEN'):
        dispatch(root, na.Bridge(c))


def test_failed_worker_never_dependency_and_no_retry_rename(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    monkeypatch.setattr(runner, 'run_blender', lambda *a, **k: {'ok': False})
    run = dispatch(root, bridge)
    assert run['status'] == 'FAILED'
    with pytest.raises(wf.Blocked): bridge.record_review('t', 'proof', {})
    with pytest.raises(wf.Blocked, match='ALREADY_ATTEMPTED'): dispatch(root, bridge, ident='rename')


def test_interrupt_retains_lease_not_automatic_replay(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    def interrupt(*args, **kwargs): raise KeyboardInterrupt()
    monkeypatch.setattr(runner, 'run_blender', interrupt)
    with pytest.raises(KeyboardInterrupt): dispatch(root, bridge)
    assert bridge.runs(c.state('t'))['proof']['status'] == 'RESERVED'
    with pytest.raises(wf.Blocked): dispatch(root, bridge, ident='again')
    with pytest.raises(wf.Blocked, match='JOB_STILL_ACTIVE'):
        c.replan('t', 'STRATEGIZING', 'Cannot replan until process state reconciled', 'rp')


def test_semantic_negative_control_declared_show_is_not_prose_understanding():
    d = tr.decide({'text': 'Render a new film', 'operations': ['display'],
                   'rationale': 'Deliberately dishonest declaration'})
    assert d['route'] == 'show'  # Preserved limitation, not semantic success.
    assert not d['authority_granted']


def test_real_runner_path_with_mock_process_and_clean_environment(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    monkeypatch.setattr(runner, 'run_blender', REAL_RUNNER)
    binary = root / 'Blender'; binary.write_text('not executed'); binary.chmod(0o700)
    monkeypatch.setattr(na, 'BLENDER_BIN', str(binary))
    seen = []
    class Process:
        returncode = 0
        def __init__(self, command, **kwargs):
            seen.append((command, kwargs['env']))
            j = json.loads(Path(command[-1]).read_text())
            out = Path(j['output_dir'])
            (out / 'snapshot.json').write_text('{"synthetic":true}')
            (out / 'worker-status.json').write_text('{"ok":true}')
        def wait(self, **kwargs): return 0
    monkeypatch.setattr(runner.subprocess, 'Popen', Process)
    monkeypatch.setenv('FAKE_PRIVATE_TOKEN', 'synthetic-must-not-propagate')
    run = dispatch(root, bridge)
    assert run['status'] == 'RETURNED' and len(seen) == 1
    command, env = seen[0]
    assert '--disable-autoexec' in command and '--factory-startup' in command
    assert Path(command[command.index('--python') + 1]).name == 'worker.py'
    assert 'FAKE_PRIVATE_TOKEN' not in env
    assert Path(env['HOME']).is_relative_to(root / '.runtime/factory-native')


def test_unregistered_binary_and_unbound_input_refused(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    with pytest.raises(wf.Blocked, match='EXECUTABLE'):
        bridge.dispatch('t', 'proof', 'p', parent=bind(root, 'parent.blend'), blender_bin='/bin/sh')
    (root / 'other.blend').write_text('not admitted')
    with pytest.raises(wf.Blocked, match='UNBOUND'):
        bridge.dispatch('t', 'proof', 'p', parent=bind(root, 'other.blend'), blender_bin=na.BLENDER_BIN)
    assert calls == []


def test_replan_preserves_limit_and_invalidates_proof(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    run = dispatch(root, bridge); step_review(bridge, run)
    c.replan('t', 'STRATEGIZING', 'Synthetic method reassessment', 'replan')
    assert c.state('t')['cycle'] == 1
    pf.complete(c, 't', b, 'new-plan')
    assert bridge.runs(c.state('t')) == {}
    with pytest.raises(wf.Blocked, match='DEPENDENCY_NOT_RUN'):
        dispatch(root, bridge, 'build', 'later-build')


def test_native_task_cannot_reset_deliverable_or_change_database(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    with pytest.raises(wf.Blocked, match='DELIVERABLE_ALREADY_TRACKED'):
        c.create('renamed', 'production', bind(root, 'authority.md'), 'rename',
                 direction=direction(b), mode='local_native', admission='request')
    other = wf.Controller(root, 'other.sqlite3')
    other.route_request('r', request(root, ['native_inspect']))
    with pytest.raises(wf.Blocked, match='CANONICAL'):
        other.create('t', 'production', bind(root, 'authority.md'), 'create',
                     direction=direction(b), mode='local_native', admission='r')


def test_capability_substitution_and_replay_refused(setup, monkeypatch):
    root, c, b, bridge, calls = native(setup, monkeypatch)
    def worker(job, *, _admission, **kwargs):
        with pytest.raises(wf.Blocked, match='SUBSTITUTION'):
            na.check_capability(_admission, job | {'mode': 'render'})
        na.check_capability(_admission, job)
        with pytest.raises(wf.Blocked, match='REPLAY'):
            na.check_capability(_admission, job)
        return {'ok': False}
    monkeypatch.setattr(runner, 'run_blender', worker)
    assert dispatch(root, bridge)['status'] == 'FAILED'


def test_legacy_cli_never_reaches_action_before_routing(monkeypatch, capsys):
    from movie_factory import cli
    from types import SimpleNamespace
    calls = []
    monkeypatch.setattr(cli, 'parser', lambda: SimpleNamespace(parse_args=lambda argv:
        SimpleNamespace(func=lambda args: calls.append('side effect'))))
    assert cli.main([]) == 2
    assert calls == [] and 'ROUTE_FIRST' in capsys.readouterr().err
