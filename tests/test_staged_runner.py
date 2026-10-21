"""Offline runner controls; these fixtures are not a live runtime qualification."""
import copy
import json
from pathlib import Path

import pytest

from movie_factory import production_workflow as wf
from movie_factory import staged_runner as sr
from movie_factory import stage_routing as routing
from test_production_workflow import setup, bind, direction, review, make_brief
import expert_fixtures as ef


def prepare(setup, cap=4):
    root, controller, brief, fresh = setup
    brief.update(offline_only=False, frozen_evidence_only=True)
    controller.create('t', 'production', bind(root, 'authority.md'), 'create', 2,
                      direction(brief), mode='frozen_evidence')
    events = []
    return root, controller, brief, sr.SerialRunner(controller, 'runner.sqlite3', events.append, cap), events


def plan(runner, brief):
    return runner.step('t', lambda req: {'result': brief}, {})


def build(root, controller):
    p = controller.packet('t')
    return {'fingerprint': p['fingerprint'], 'candidate': {'version': 'frozen', 'artifacts': {'clip': bind(root, 'candidate.bin')}},
            'requirement_uses': ef.uses(p['brief']),
            'reference_uses': {r['id']: {'reference_digest': wf.pk.digest(r), 'application': 'Existing frozen evidence only'} for r in p['brief']['references']}}


def test_fresh_context_and_successful_presentation(setup):
    root, c, brief, runner, events = prepare(setup)
    seen = []
    def adapter(result):
        def call(request):
            seen.append(copy.deepcopy(request)); return {'result': result}
        return call
    runner.step('t', adapter(brief), {})
    runner.step('t', adapter(build(root, c)), {})
    runner.step('t', adapter(review(root, c)), {})
    receipt = runner.present('t')
    assert receipt['frozen_evidence_only'] and not receipt['offline_replay_only']
    assert not receipt['production_approved']
    assert [r['actor'] for r in seen] == ['planner', 'builder', 'reviewer']
    assert all('ticket' not in r for r in seen)
    assert 'builder_record' not in seen[-1]
    assert seen[0]['direction']['references'] == seen[-1]['brief']['references']
    assert [e['event'] for e in events].count('stage_admitted') == 3


def test_uncertain_call_no_duplicate_after_restart(setup):
    _, c, brief, runner, _ = prepare(setup)
    count = []
    def crash(req):
        count.append(1); raise RuntimeError('process crashed after dispatch')
    with pytest.raises(RuntimeError): runner.step('t', crash, {})
    restart = sr.SerialRunner(c, 'runner.sqlite3')
    with pytest.raises(wf.Blocked, match='CALL_ALREADY'): restart.step('t', crash, {})
    with pytest.raises(wf.Blocked, match='UNCERTAIN'): restart.recover('t')
    assert count == [1] and c.state('t')['stage'] == 'BRIEFING'


def test_returned_result_recovered_without_inference(setup, monkeypatch):
    _, c, brief, runner, _ = prepare(setup)
    original = runner._admit_returned
    monkeypatch.setattr(runner, '_admit_returned', lambda row: (_ for _ in ()).throw(RuntimeError('crash')))
    with pytest.raises(RuntimeError): plan(runner, brief)
    monkeypatch.setattr(runner, '_admit_returned', original)
    assert sr.SerialRunner(c, 'runner.sqlite3').recover('t')['stage'] == 'EXECUTING'
    assert len(runner.calls()) == 1


def test_crash_after_controller_transition_is_idempotent(setup, monkeypatch):
    _, c, brief, runner, _ = prepare(setup)
    original = c.submit
    def crash(*args, **kwargs):
        original(*args, **kwargs); raise RuntimeError('after submit')
    monkeypatch.setattr(c, 'submit', crash)
    with pytest.raises(RuntimeError): plan(runner, brief)
    monkeypatch.setattr(c, 'submit', original)
    assert runner.recover('t')['stage'] == 'EXECUTING'
    assert len([e for e in c.events('t') if e['action'] == 'submit:planner']) == 1


def test_single_runner_lock_even_with_second_database(setup):
    _, c, _, runner, _ = prepare(setup)
    other = sr.SerialRunner(c, 'other.sqlite3')
    with runner.exclusive():
        with pytest.raises(wf.Blocked, match='BUSY'):
            with other.exclusive(): pass


def test_call_cap_cannot_reset_or_grow(setup):
    root, c, brief, runner, _ = prepare(setup, cap=1)
    plan(runner, brief)
    with pytest.raises(wf.Blocked, match='CAP_CHANGE'): sr.SerialRunner(c, 'runner.sqlite3', max_calls=4)
    with pytest.raises(wf.Blocked, match='CAP_EXHAUSTED'): runner.step('t', lambda req: {'result': build(root, c)}, {})


@pytest.mark.parametrize('supplement', [{'actor': 'reviewer'}, {'builder_record': 'trust me'}, {'ticket': 'x'}])
def test_no_contract_override_or_builder_advocacy(setup, supplement):
    _, _, brief, runner, _ = prepare(setup)
    with pytest.raises(wf.Blocked, match='UNSCOPED|OVERRIDE'): runner.step('t', lambda req: {'result': brief}, supplement)
    assert runner.calls() == []


def test_no_unreviewed_presentation(setup):
    _, _, brief, runner, _ = prepare(setup)
    plan(runner, brief)
    with pytest.raises(wf.Blocked, match='REVIEW_REQUIRED'): runner.present('t')


def test_failed_visible_review_stays_internal(setup):
    root, c, brief, runner, _ = prepare(setup)
    plan(runner, brief)
    runner.step('t', lambda req: {'result': build(root, c)}, {})
    runner.step('t', lambda req: {'result': review(root, c, status='FAIL')}, {})
    assert c.state('t')['stage'] == 'EXECUTING' and c.state('t')['cycle'] == 1
    with pytest.raises(wf.Blocked, match='NOT_READY'): runner.present('t')


def test_stale_candidate_blocked_on_presentation(setup):
    root, c, brief, runner, _ = prepare(setup)
    plan(runner, brief)
    runner.step('t', lambda req: {'result': build(root, c)}, {})
    runner.step('t', lambda req: {'result': review(root, c)}, {})
    (root / 'candidate.bin').write_text('changed')
    with pytest.raises(ValueError): runner.present('t')


def test_denies_tools_and_never_logs_reasoning():
    proto = object.__new__(sr.CodexProtocol)
    events, replies = [], []
    proto.progress, proto.send, proto.history = events.append, replies.append, []
    proto.event({'method': 'item/reasoning/textDelta', 'params': {'delta': 'private reasoning'}})
    assert events == [] and proto.history == []
    with pytest.raises(wf.Blocked, match='UNEXPECTED_RUNTIME_REQUEST'):
        proto.event({'method': 'item/tool/call', 'id': 3, 'params': {'name': 'write_file'}})
    assert replies[0]['error']['code'] == -32601
    with pytest.raises(wf.Blocked, match='UNEXPECTED_TOOL_ITEM'):
        proto.event({'method': 'item/started', 'params': {'item': {'type': 'commandExecution'}}})


def test_no_api_credentials_forwarded(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'not-a-real-key')
    monkeypatch.setenv('CODEX_API_KEY', 'also-fake')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'also-fake')
    monkeypatch.setenv('GEMINI_API_KEY', 'also-fake')
    monkeypatch.setenv('CUSTOM_SECRET', 'also-fake')
    assert not set(sr.clean_environment()) & {'OPENAI_API_KEY', 'CODEX_API_KEY', 'AWS_SESSION_TOKEN', 'GEMINI_API_KEY', 'CUSTOM_SECRET'}


def test_image_scope_and_hash(setup):
    root, _, brief, runner, _ = prepare(setup)
    path = str(root / 'evidence.jpg')
    with pytest.raises(wf.Blocked, match='STALE_IMAGE'):
        runner.step('t', lambda req: {'result': brief}, {'image_paths': [path], 'image_hashes': {path: 'bad'}})
    assert not runner.calls()


def test_rejects_old_offline_mode_for_live_runner(setup):
    root, c, brief, _ = setup
    c.create('t', 'production', bind(root, 'authority.md'), 'create', 2, direction(brief))
    runner = sr.SerialRunner(c, 'runner.sqlite3')
    with pytest.raises(wf.Blocked, match='FROZEN_EVIDENCE_MODE'): plan(runner, brief)


def test_scoped_knowledge_survives_stage_dispatch(setup):
    _, _, brief, runner, _ = prepare(setup)
    seen = []
    context = {'packet_digest': 'fixture', 'obligations': ['reference_roles', 'audience_read']}
    def adapter(request):
        seen.append(request); return {'result': brief}
    runner.step('t', adapter, {'knowledge_context': context})
    assert seen[0]['knowledge_context'] == context


@pytest.mark.parametrize('selected', [routing.SOL, routing.ASTRA])
def test_protocol_fresh_thread_no_environment_and_structured_result(selected):
    proto = object.__new__(sr.CodexProtocol)
    proto.cwd, proto.mcp_off, proto.history = '/private/tmp/fixture', {'mcp_servers.fixture.enabled': False}, []
    proto.preflight = lambda: {'auth_type': 'chatgpt'}
    proto.progress = lambda event: None
    calls = []
    def rpc(method, params):
        calls.append((method, params))
        if method == 'model/list': return {'data': [{'model': selected, 'supportedReasoningEfforts': [{'reasoningEffort': 'high'}]}]}
        if method == 'thread/start':
            return {'thread': {'id': 'fresh'}, 'approvalPolicy': 'never', 'model': selected, 'reasoningEffort': 'high'}
        return {'turn': {'id': 'turn'}}
    proto.rpc = rpc
    events = iter([
        {'method': 'item/completed', 'params': {'item': {'type': 'agentMessage',
         'text': json.dumps({'result_json': json.dumps({'verdict': 'NOT_RUN'})})}}},
        {'method': 'turn/completed', 'params': {'turn': {'id': 'turn', 'status': 'completed'}}}])
    proto.read = lambda **kw: next(events)
    route = routing.resolve(routing.policy('general'), 'reviewer', Path('/private/tmp'))
    route['model'] = selected
    result = proto.infer({'actor': 'reviewer', 'runtime_route': route, 'image_paths': ['/private/tmp/fixture.png']})
    start, turn = calls[1][1], calls[2][1]
    assert start['ephemeral'] and start['environments'] == turn['environments'] == []
    assert start['dynamicTools'] == start['selectedCapabilityRoots'] == []
    assert start['config']['mcp_servers.fixture.enabled'] is False
    assert all(start['config']['features.' + feature] is False for feature in sr.DISABLED)
    assert turn['outputSchema'] == sr.OUTPUT_SCHEMA
    assert result['result'] == {'verdict': 'NOT_RUN'}
    assert result['runtime']['reasoning_effort'] == 'high'
    assert start['model'] == turn['model'] == selected
    assert start['config']['model_reasoning_effort'] == turn['effort'] == 'high'
    assert result['runtime']['requested_route'] == route


def test_preflight_rejects_api_auth():
    proto = object.__new__(sr.CodexProtocol)
    proto.send = lambda message: None
    proto.rpc = lambda method, params: {'account': {'type': 'apiKey'}} if method == 'account/read' else {}
    with pytest.raises(wf.Blocked, match='CHATGPT_AUTH_REQUIRED'): proto.preflight()


def test_context_overflow_blocks_before_reservation(setup):
    _, _, brief, runner, _ = prepare(setup)
    with pytest.raises(wf.Blocked, match='CONTEXT_BUDGET'):
        runner.step('t', lambda req: {'result': brief}, {'knowledge_context': 'x' * 120_001})
    assert not runner.calls()


def test_user_message_echo_is_not_a_tool():
    proto = object.__new__(sr.CodexProtocol)
    proto.history, proto.progress = [], lambda event: None
    proto.event({'method': 'item/started', 'params': {'item': {'type': 'userMessage'}}})
    assert not proto.history


def test_explicit_abort_retains_reservation_and_cap(setup):
    _, c, brief, runner, _ = prepare(setup, cap=2)
    def crash(req): raise RuntimeError('owned runtime terminated')
    with pytest.raises(RuntimeError): runner.step('t', crash, {})
    cid = runner.calls()[0]['id']
    with pytest.raises(wf.Blocked, match='ABORT_EVIDENCE'):
        runner.reconcile_aborted('t', cid, {})
    runner.reconcile_aborted('t', cid, {'runtime_terminated': True, 'no_result_admitted': True,
                                      'tool_free': True, 'reason': 'Protocol input echo was misclassified'})
    assert runner.recover('t')['stage'] == 'BRIEFING'
    plan(runner, brief)
    assert [r['status'] for r in runner.calls()] == ['ABORTED', 'SUBMITTED']
    with pytest.raises(wf.Blocked, match='CAP_EXHAUSTED'):
        runner.step('t', lambda req: {'result': {}}, {})


def test_runtime_setting_mismatch_blocks_before_inference():
    proto = object.__new__(sr.CodexProtocol)
    proto.cwd, proto.mcp_off = '/private/tmp/fixture', {}
    proto.expected_model, proto.expected_effort = 'expected-model', 'high'
    proto.preflight = lambda: {}
    calls = []
    def rpc(method, params):
        calls.append(method)
        if method == 'model/list': return {'data': [{'model': routing.SOL, 'supportedReasoningEfforts': [{'reasoningEffort': 'high'}]}]}
        return {'thread': {'id': 'fresh'}, 'approvalPolicy': 'never',
                'model': 'different-model', 'reasoningEffort': 'low'}
    proto.rpc = rpc
    with pytest.raises(wf.Blocked, match='RUNTIME_SETTING_MISMATCH'):
        proto.infer({'actor': 'reviewer', 'runtime_route': routing.resolve(routing.policy('general'), 'reviewer', Path('/private/tmp'))})
    assert calls == ['model/list', 'thread/start']


@pytest.mark.parametrize('profile,expected', [('general', [routing.SOL]*3),
                                          ('specialist_3d', [routing.SOL, routing.ASTRA, routing.SOL])])
def test_routing_defaults(tmp_path, profile, expected):
    assert [routing.resolve(routing.policy(profile), a, tmp_path)['model'] for a in routing.ACTORS] == expected


def test_escalation_requires_reason_current_evidence_and_valid_actor(tmp_path):
    (tmp_path / 'diagnosis.txt').write_text('Structural assumption unresolved')
    escalation = {'trigger': 'foundational_strategy', 'reason': 'Must select representation before building',
                  'evidence': {'diagnosis.txt': wf.pk.file_hash(tmp_path / 'diagnosis.txt')}}
    p = routing.policy('specialist_3d', {'planner': escalation})
    assert routing.resolve(p, 'planner', tmp_path)['model'] == routing.ASTRA
    assert routing.resolve(p, 'reviewer', tmp_path)['model'] == routing.SOL
    (tmp_path / 'diagnosis.txt').write_text('changed')
    with pytest.raises(wf.Blocked, match='STALE_ESCALATION'): routing.resolve(p, 'planner', tmp_path)
    with pytest.raises(wf.Blocked, match='ROUTING_ACTOR'): routing.policy('general', {'director': escalation})
    escalation['trigger'] = 'want_a_pass'
    with pytest.raises(wf.Blocked, match='ESCALATION_REASON'): routing.policy('general', {'reviewer': escalation})


def routed_adapter(result, seen):
    def call(request):
        seen.append(copy.deepcopy(request))
        route = request['runtime_route']
        return {'result': result, 'runtime': {'model': route['model'], 'reasoning_effort': route['effort'],
                                            'requested_route': route}}
    return call


def test_routed_three_stage_chain_and_policy_restart(setup):
    root, c, brief, _, events = prepare(setup)
    p = routing.policy('specialist_3d')
    runner = sr.SerialRunner(c, 'routed.sqlite3', events.append, routing=p)
    seen = []
    runner.step('t', routed_adapter(brief, seen), {})
    # Caller mutation cannot change a constructed runner's policy.
    p['profile'] = 'general'
    with pytest.raises(wf.Blocked, match='ROUTING_POLICY_CHANGED'):
        sr.SerialRunner(c, 'routed.sqlite3', routing=p).step('t', routed_adapter({}, seen), {})
    with pytest.raises(wf.Blocked, match='ROUTING_POLICY_CHANGED'):
        sr.SerialRunner(c, 'routed.sqlite3').step('t', routed_adapter({}, seen), {})
    runner = sr.SerialRunner(c, 'routed.sqlite3', routing=routing.policy('specialist_3d'))
    runner.step('t', routed_adapter(build(root, c), seen), {})
    runner.step('t', routed_adapter(review(root, c, status='FAIL'), seen), {})
    assert [r['runtime_route']['model'] for r in seen] == [routing.SOL, routing.ASTRA, routing.SOL]
    assert all('ticket' not in r for r in seen) and 'builder_record' not in seen[-1]
    with pytest.raises(wf.Blocked, match='NOT_READY'): runner.present('t')


def test_runtime_mismatch_never_admitted_or_retried(setup):
    _, c, brief, _, _ = prepare(setup)
    runner = sr.SerialRunner(c, 'routed.sqlite3', routing=routing.policy('general'))
    with pytest.raises(wf.Blocked, match='RETURNED_ROUTING_MISMATCH'):
        runner.step('t', lambda req: {'result': brief, 'runtime': {'model': routing.ASTRA}}, {})
    assert c.state('t')['stage'] == 'BRIEFING'
    with pytest.raises(wf.Blocked, match='RETURNED_ROUTING_MISMATCH'): runner.recover('t')
    assert len(runner.calls()) == 1


def test_no_live_inference_without_route():
    proto = object.__new__(sr.CodexProtocol)
    proto.preflight = lambda: pytest.fail('must not start runtime')
    with pytest.raises(wf.Blocked, match='EXPLICIT_RUNTIME_ROUTE_REQUIRED'): proto.infer({'actor': 'planner'})


def test_explicit_escalation_preserves_state_and_cap(setup):
    root, c, brief, _, _ = prepare(setup)
    runner = sr.SerialRunner(c, 'routed.sqlite3', max_calls=1, routing=routing.policy('general'))
    runner.step('t', routed_adapter(brief, []), {})
    before = c.state('t')
    record = {'trigger': 'unresolved_diagnosis', 'reason': 'Fixture method ambiguity',
              'evidence': {'authority.md': wf.pk.file_hash(root / 'authority.md')}}
    runner.escalate('t', record)
    assert c.state('t') == before
    with runner.connection() as con:
        assert con.execute('SELECT count(*) FROM route_events').fetchone()[0] == 1
        updated = json.loads(con.execute('SELECT policy FROM routing').fetchone()[0])
    assert routing.resolve(updated, 'builder', root)['model'] == routing.ASTRA
    assert routing.resolve(updated, 'reviewer', root)['model'] == routing.SOL
    with pytest.raises(wf.Blocked, match='ALREADY_TOP'): runner.escalate('t', record)
    resumed = sr.SerialRunner(c, 'routed.sqlite3', max_calls=1, routing=updated)
    with pytest.raises(wf.Blocked, match='CAP_EXHAUSTED'):
        resumed.step('t', routed_adapter(build(root, c), []), {})


@pytest.mark.parametrize('models,error', [([], 'MODEL_UNAVAILABLE'),
    ([{'model': routing.ASTRA, 'supportedReasoningEfforts': [{'reasoningEffort': 'high'}]}], 'MODEL_UNAVAILABLE'),
    ([{'model': routing.SOL, 'supportedReasoningEfforts': [{'reasoningEffort': 'low'}]}], 'EFFORT_UNAVAILABLE')])
def test_unavailable_routes_do_not_fallback(tmp_path, models, error):
    proto = object.__new__(sr.CodexProtocol)
    proto.preflight = lambda: {}
    calls = []
    def rpc(method, params):
        calls.append(method); return {'data': models}
    proto.rpc = rpc
    with pytest.raises(wf.Blocked, match=error):
        proto.infer({'actor': 'planner', 'runtime_route': routing.resolve(routing.policy('general'), 'planner', tmp_path)})
    assert calls == ['model/list']
