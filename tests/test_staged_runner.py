"""Offline runner controls; these fixtures are not a live runtime qualification."""
import copy
import json

import pytest

from movie_factory import production_workflow as wf
from movie_factory import staged_runner as sr
from test_production_workflow import setup, bind, direction, review, make_brief


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


def test_protocol_fresh_thread_no_environment_and_structured_result():
    proto = object.__new__(sr.CodexProtocol)
    proto.cwd, proto.mcp_off, proto.history = '/private/tmp/fixture', {'mcp_servers.fixture.enabled': False}, []
    proto.preflight = lambda: {'auth_type': 'chatgpt'}
    proto.progress = lambda event: None
    calls = []
    def rpc(method, params):
        calls.append((method, params))
        if method == 'thread/start':
            return {'thread': {'id': 'fresh'}, 'approvalPolicy': 'never', 'model': 'observed'}
        return {'turn': {'id': 'turn'}}
    proto.rpc = rpc
    events = iter([
        {'method': 'item/completed', 'params': {'item': {'type': 'agentMessage',
         'text': json.dumps({'result_json': json.dumps({'verdict': 'NOT_RUN'})})}}},
        {'method': 'turn/completed', 'params': {'turn': {'id': 'turn', 'status': 'completed'}}}])
    proto.read = lambda **kw: next(events)
    result = proto.infer({'actor': 'reviewer', 'image_paths': ['/private/tmp/fixture.png']})
    start, turn = calls[0][1], calls[1][1]
    assert start['ephemeral'] and start['environments'] == turn['environments'] == []
    assert start['dynamicTools'] == start['selectedCapabilityRoots'] == []
    assert start['config']['mcp_servers.fixture.enabled'] is False
    assert all(start['config']['features.' + feature] is False for feature in sr.DISABLED)
    assert turn['outputSchema'] == sr.OUTPUT_SCHEMA
    assert result['result'] == {'verdict': 'NOT_RUN'}
    assert result['runtime']['reasoning_effort'] is None


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
