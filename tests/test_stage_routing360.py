"""Offline Director360 approval, bounded use, restart and expiration controls."""
import copy
import json
import pytest
from movie_factory import stage_routing as routing, staged_runner as sr, production_workflow as wf
from routing_fixtures360 import assignment as fixture_assignment, packet
from test_staged_runner import prepare, routed_adapter, simulation_runner
from test_production_workflow import setup, bind


def assignment(root,p,**kwargs):
    return fixture_assignment(root,p,runner_database='bounded.sqlite3',**kwargs)


def test_old_automatic_astra_policy_requires_explicit_reconciliation(tmp_path):
    old = {'version': 1, 'profile': 'specialist_3d', 'escalations': {}}
    with pytest.raises(wf.Blocked, match='LEGACY_ROUTING'):
        routing.resolve(old, 'builder', tmp_path)


@pytest.mark.parametrize('missing', ['director_approval', 'retrospective', 'assignment'])
def test_missing_approval_or_assignment_is_blocked(tmp_path, missing):
    record = assignment(tmp_path, packet());record.pop(missing)
    with pytest.raises(wf.Blocked, match='APPROVAL_REQUIRED'):
        routing.policy('general', {'planner': record})


def test_unbounded_call_grant_is_rejected(tmp_path):
    record = assignment(tmp_path, packet());record['assignment']['max_calls'] = 100
    with pytest.raises(wf.Blocked, match='ESCALATION_ASSIGNMENT'):
        routing.policy('general', {'planner': record})


@pytest.mark.parametrize('change', ['allowance', 'success_test', 'reason'])
def test_grant_cannot_expand_approved_assignment(tmp_path, change):
    p = packet();record = assignment(tmp_path, p)
    if change == 'allowance':record['assignment']['max_calls'] = 2
    elif change == 'success_test':record['assignment']['success_test'] = 'Approve the whole movie'
    else:record['reason'] = 'Take over the entire campaign'
    with pytest.raises(wf.Blocked, match='APPROVAL_SCOPE_MISMATCH'):
        routing.resolve(routing.policy('general', {'planner':record}), 'planner', tmp_path, p)


@pytest.mark.parametrize('source', ['director_approval', 'source', 'retrospective'])
def test_changed_authority_or_retro_blocks_before_dispatch(tmp_path, source):
    p = packet();record = assignment(tmp_path, p)
    binding = record[source] if source != 'source' else json.loads((tmp_path/record['director_approval']['path']).read_text())['source']
    (tmp_path/binding['path']).write_text('Changed evidence or authorization')
    with pytest.raises(wf.Blocked, match='STALE_|APPROVAL_SOURCE'):
        routing.resolve(routing.policy('general', {'planner':record}), 'planner', tmp_path, p)


@pytest.mark.parametrize('key,value', [('cycle',1), ('planning_step','STRATEGIZING'), ('task','another-task'), ('planning_input_digest','d'*64), ('candidate',{'version':'changed'})])
def test_assignment_expires_when_work_changes(tmp_path, key, value):
    p = packet();record = assignment(tmp_path,p);changed={**p,key:value}
    route = routing.resolve(routing.policy('general', {'planner':record}), 'planner', tmp_path, changed)
    assert route['model'] == routing.SOL and route['reason'] == 'assignment_scope_expired'


def test_active_escalation_requires_actual_scope_context(tmp_path):
    record = assignment(tmp_path, packet())
    with pytest.raises(wf.Blocked, match='SCOPE_CONTEXT_REQUIRED'):
        routing.resolve(routing.policy('general', {'planner':record}), 'planner', tmp_path)


def test_astra_model_override_without_approved_record_fails_before_runtime(tmp_path):
    proto = object.__new__(sr.CodexProtocol);proto.cwd = str(tmp_path)
    proto.preflight = lambda: pytest.fail('unauthorized route must not start runtime')
    route=routing.resolve(routing.policy('general'), 'planner', tmp_path);route['model']=routing.ASTRA
    with pytest.raises(wf.Blocked, match='APPROVAL_REQUIRED'):
        proto.infer({'actor':'planner','runtime_route':route})


def test_protocol_rechecks_assignment_scope_before_runtime(tmp_path):
    p=packet();record=assignment(tmp_path,p)
    route=routing.resolve(routing.policy('general',{'planner':record}),'planner',tmp_path,p)
    proto=object.__new__(sr.CodexProtocol);proto.cwd=str(tmp_path)
    proto.preflight=lambda:pytest.fail('wrong task must not start runtime')
    with pytest.raises(wf.Blocked,match='ESCALATION_SCOPE_MISMATCH'):
        proto.infer({**p,'task':'another-task','runtime_route':route})


def test_stage_grant_expires_and_returns_to_sol_after_restart(setup):
    root,c,brief,_,events=prepare(setup);seen=[]
    runner=sr.SerialRunner(c,'bounded.sqlite3',events.append,max_calls=7,routing=routing.policy('specialist_3d'))
    runner.step('t',routed_adapter(brief,seen),{})
    before=c.state('t');runner.escalate('t',assignment(root,c.packet('t')))
    assert c.state('t')==before
    restarted=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=runner.routing)
    for _ in range(3):restarted.step('t',routed_adapter(brief,seen),{})
    assert [x['runtime_route']['model'] for x in seen]==[routing.SOL,routing.ASTRA,routing.SOL,routing.SOL]
    assert seen[2]['runtime_route']['reason']=='assignment_scope_expired'


@pytest.mark.parametrize('allowed', [1,2])
def test_aborted_calls_consume_grant_and_restart_cannot_reset_it(setup, allowed):
    root,c,brief,_,_=prepare(setup);seen=[]
    runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=routing.policy('general'))
    runner.step('t',routed_adapter(brief,seen),{})
    record=assignment(root,c.packet('t'),max_calls=allowed);runner.escalate('t',record)
    for _ in range(allowed):
        def crash(req):seen.append(copy.deepcopy(req));raise RuntimeError('synthetic interrupted call')
        with pytest.raises(RuntimeError):runner.step('t',crash,{})
        with pytest.raises(wf.Blocked,match='CALL_ALREADY|UNRESOLVED'):
            runner.step('t',routed_adapter(brief,seen),{})
        call=runner.calls()[-1]
        runner.reconcile_aborted('t',call['id'],dict(runtime_terminated=True,no_result_admitted=True,tool_free=True,reason='Synthetic fixture process termination verified'))
        runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=runner.routing)
    with pytest.raises(wf.Blocked,match='ALREADY_USED'):runner.escalate('t',record)
    runner.step('t',routed_adapter(brief,seen),{})
    assert [x['runtime_route']['model'] for x in seen]==[routing.SOL]+[routing.ASTRA]*allowed+[routing.SOL]
    assert seen[-1]['runtime_route']['reason']=='assignment_call_limit_reached'
    assert len(runner.calls())==allowed+2


def test_wrong_task_or_stage_cannot_be_admitted_as_escalation(setup):
    root,c,brief,_,_=prepare(setup)
    runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=routing.policy('general'))
    runner.step('t',routed_adapter(brief,[]),{})
    p=c.packet('t');p['cycle']+=1
    with pytest.raises(wf.Blocked,match='ESCALATION_SCOPE_MISMATCH'):
        runner.escalate('t',assignment(root,p))


def test_another_runner_database_cannot_reset_approved_astra_allowance(setup):
    root,c,brief,_,_=prepare(setup)
    runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=routing.policy('general'))
    runner.step('t',routed_adapter(brief,[]),{})
    runner.escalate('t',assignment(root,c.packet('t')))
    other=sr.SerialRunner(c,'new-budget.sqlite3',max_calls=7,routing=runner.routing)
    with pytest.raises(wf.Blocked,match='RUNNER_DATABASE_MISMATCH'):
        other.step('t',lambda req:pytest.fail('must not reset assignment accounting'),{})
    assert not other.calls()


def test_explicit_sol_adoption_preserves_old_policy_calls_and_controller(setup):
    root,c,brief,_,_=prepare(setup)
    runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=routing.policy('specialist_3d'))
    runner.step('t',routed_adapter(brief,[]),{})
    old={'version':1,'profile':'specialist_3d','escalations':{}}
    with runner.connection() as con:con.execute('UPDATE routing SET policy=?',(json.dumps(old,sort_keys=True),))
    with pytest.raises(wf.Blocked,match='ROUTING_POLICY_CHANGED'):
        runner.step('t',routed_adapter(brief,[]),{})
    source=root/'sol-approval.txt';source.write_text('SYNTHETIC FIXTURE: use Sol for every stage')
    (root/'adopt.json').write_text(json.dumps(dict(decision='adopt_sol_default',task='t',source=bind(root,'sol-approval.txt'),director_reply='SYNTHETIC APPROVAL')))
    before=c.state('t');runner.adopt_sol_default('t',bind(root,'adopt.json'))
    assert c.state('t')==before and len(runner.calls())==1
    with runner.connection() as con:
        assert json.loads(con.execute('SELECT previous FROM route_events').fetchone()[0])==old
        assert con.execute('SELECT max_calls FROM policy').fetchone()[0]==7
        assert json.loads(con.execute('SELECT authority FROM route_adoptions').fetchone()[0])==bind(root,'adopt.json')
    assert routing.resolve(runner.routing,'builder',root)['model']==routing.SOL
    sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=runner.routing).step('t',routed_adapter(brief,[]),{})


def test_unidentified_legacy_escalation_history_does_not_break_new_grants(setup):
    root,c,brief,_,_=prepare(setup)
    runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=routing.policy('general'))
    runner.step('t',routed_adapter(brief,[]),{})
    legacy={'trigger':'unresolved_diagnosis','reason':'historical fixture','evidence':{}}
    old={'version':1,'profile':'general','escalations':{'planner':legacy}}
    with runner.connection() as con:
        serialized=json.dumps(runner.routing,sort_keys=True)
        con.execute('INSERT INTO route_events(task,previous,current) VALUES(?,?,?)',('t',json.dumps(old),serialized))
        row=con.execute('SELECT id,request FROM calls').fetchone();request=json.loads(row['request'])
        request['runtime_route']['escalation']=legacy
        con.execute('UPDATE calls SET request=?,request_hash=? WHERE id=?',(json.dumps(request),wf.pk.digest(request),row['id']))
    runner.escalate('t',assignment(root,c.packet('t')))
    seen=[];runner.step('t',routed_adapter(brief,seen),{})
    assert seen[0]['runtime_route']['model']==routing.ASTRA


def test_sol_adoption_cannot_clear_an_unresolved_call(setup):
    root,c,brief,_,_=prepare(setup)
    runner=sr.SerialRunner(c,'bounded.sqlite3',max_calls=7,routing=routing.policy('general'))
    def crash(req):raise RuntimeError('synthetic unreturned call')
    with pytest.raises(RuntimeError):runner.step('t',crash,{})
    (root/'adopt-source.txt').write_text('SYNTHETIC FIXTURE: adopt Sol defaults')
    (root/'adopt.json').write_text(json.dumps(dict(decision='adopt_sol_default',task='t',source=bind(root,'adopt-source.txt'),director_reply='SYNTHETIC APPROVAL')))
    before=c.state('t');calls=runner.calls()
    with pytest.raises(wf.Blocked,match='UNRESOLVED_CALL'):runner.adopt_sol_default('t',bind(root,'adopt.json'))
    assert c.state('t')==before and runner.calls()==calls
