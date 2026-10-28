"""Synthetic evidence and mocked workers; not production/artistic qualification."""
import copy
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from movie_factory import retrospective as rt, production_workflow as wf
from movie_factory import production_knowledge as pk
from test_production_workflow import setup, start, build, review, submit, bind
from test_task_router332 import native, dispatch, step_review


def observed(root, c, ident, *, req='appearance', status='FAIL', attempt=None, role='production', **flags):
    data=dict(attempt=attempt or ident,role=role,origin='test',
              observations=[dict(requirement=req,status=status,observation='Synthetic evidence',**flags)],
              evidence={'image':bind(root,'evidence.jpg')})
    c.retrospective('t','outcome',data,ident)
    return data


def response(root,c,key='appearance'):
    packet=c.retrospective_packet('t')
    data=dict(cause='Hypothesis, not proven',uncertainty='Weights versus joint frame',
              change_or_retain_rationale='Separate bare pose from cloth fit',preserve='Prior neutral cloth volume',
              test='Matched bare neutral and bent pose',expected='No elbow wedge',failure_response='Reassess frame and weights',
              target_stage='STRATEGIZING',plan=pk.digest(c.state('t').get('brief')),
              gate_digest=pk.digest(packet['gates'][key]),evidence={'image':bind(root,'evidence.jpg')})
    c.retrospective('t','response',dict(key=key,response=data),'response:'+key)
    return data


def admit(root,c,key='appearance'):
    data=dict(response_event='response:'+key,counterexample='Could retain the wrong joint frame',
              checks={x:dict(status='PASS',observation='Synthetic challenge') for x in ('causal_test','actual_method','preservation','authority')},
              evidence={'image':bind(root,'evidence.jpg')})
    c.retrospective('t','admit',dict(key=key,challenge=data),'admit:'+key)
    return data


def evaluate(root,c,key,ident,result='effective'):
    data=dict(result=result,outcome_event=ident,observation='Synthetic measured outcome',evidence={'image':bind(root,'evidence.jpg')})
    return c.retrospective('t','evaluate',dict(key=key,evaluation=data),'effect:'+key)


def test_three_real_reviews_trigger_and_preserve_counter(setup):
    root,c,_,_=setup;start(setup,limit=5)
    for i in range(3):
        build(root,c,event='build'+str(i))
        submit(c,'t',review(root,c,status='FAIL'),'review'+str(i))
        if i==1: assert c.retrospective_packet('t')['warnings']['appearance']==2
    c=wf.Controller(root,'state.sqlite3')
    assert c.state('t')['cycle']==3
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'
    with pytest.raises(wf.Blocked,match='RETRO_REQUIRED'):c.packet('t')
    with pytest.raises(wf.Blocked,match='RETRO_REQUIRED'):c.job('t','job','acquire','acquire')


@pytest.mark.parametrize('flag', ['falsified','foundation','regressed','dependency_changed'])
def test_immediate_triggers(setup,flag):
    root,c,_,_=setup;start(setup)
    observed(root,c,'one',**{flag:True})
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'


def test_negative_controls_and_duplicate_views_do_not_spend_variants(setup):
    root,c,_,_=setup;start(setup)
    for i in range(4):observed(root,c,'negative'+str(i),role='negative_control')
    for i in range(4):observed(root,c,'view'+str(i),attempt='one-attempt')
    assert c.retrospective_packet('t')['gates']=={}
    assert c.state('t')['cycle']==0


def test_unexpected_falsifier_in_negative_control_is_not_ignored(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'bad-control',role='negative_control',falsified=True)
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'


def test_negative_control_or_worker_pass_cannot_close_creative_finding(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'bad',regressed=True);response(root,c);admit(root,c)
    for role in ('negative_control','technical'):
        observed(root,c,'test-'+role,status='PASS',role=role)
        with pytest.raises(wf.Blocked,match='WRONG_EFFECT_SCOPE'):evaluate(root,c,'appearance','test-'+role)


def test_response_allows_test_not_closure_and_effect_needs_new_evidence(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'regression',regressed=True)
    response(root,c);admit(root,c)
    assert c.packet('t')['retrospective']['gates']['appearance']['status']=='TESTING'
    with pytest.raises(wf.Blocked,match='NO_POST_TEST'):evaluate(root,c,'appearance','regression')
    observed(root,c,'new-test',status='PASS')
    evaluate(root,c,'appearance','new-test')
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='CLOSED'


def test_failed_or_inconclusive_intervention_reopens(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'first',falsified=True);response(root,c);admit(root,c)
    observed(root,c,'test',status='FAIL')
    assert c.retrospective_packet('t')['gates']['appearance']['reason']=='intervention_failed'
    with pytest.raises(wf.Blocked):c.packet('t')


def test_exhaustion_and_replanning_do_not_reset_retro(setup):
    root,c,b,_=setup;start(setup,limit=0)
    build(root,c);submit(c,'t',review(root,c,status='FAIL'),'review')
    assert '__allowance__' in c.retrospective_packet('t')['gates']
    c.revise('t',b,bind(root,'authority.md'),'Existing authority retains failed work','revise')
    assert c.state('t')['max_corrections']==0
    assert '__allowance__' in c.retrospective_packet('t')['gates']


def test_manual_replanning_exhaustion_and_extension_retain_synthesis(setup):
    from test_production_allowance import blocked,route
    from movie_factory import production_allowance as pa
    root,c,data=blocked(setup)
    before=c.retrospective_packet('t')['gates']['__allowance__']
    binding=route(root,c,data)
    pa.extend(c,'t','extension',binding,'extension-approved')
    assert c.retrospective_packet('t')['gates']['__allowance__']==before
    assert c.state('t')['cycle']==3 and c.state('t')['max_corrections']==6


def test_admission_plan_change_requires_new_reconciliation(setup):
    root,c,b,_=setup;start(setup)
    observed(root,c,'bad',regressed=True);response(root,c);admit(root,c)
    with c.transaction() as con:
        state=c._state(con,'t');state['brief']=dict(b,scope='Changed execution scope')
        with pytest.raises(wf.Blocked,match='TEST_PLAN_CHANGED'):rt.guard(con,state)


def test_incomplete_or_failed_response_challenge_cannot_admit(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'bad',regressed=True);response(root,c)
    with pytest.raises(wf.Blocked,match='CHALLENGE_COVERAGE'):
        c.retrospective('t','admit',dict(key='appearance',challenge=dict(response_event='response:appearance',checks={})), 'bad-admission')


def test_corrected_history_does_not_leave_old_admission_valid(setup):
    root,c,_,_=setup;start(setup)
    data=observed(root,c,'bad',falsified=True)
    response(root,c);admit(root,c)
    data=copy.deepcopy(data);data['supersedes']='bad';data['observations'][0].update(status='PASS',falsified=False)
    c.retrospective('t','outcome',data,'corrected')
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'


def test_evidence_and_response_staleness(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'one',regressed=True);response(root,c)
    observed(root,c,'two',regressed=True)
    with pytest.raises(wf.Blocked):admit(root,c)


def test_retro_invalidates_old_builder_ticket(setup):
    root,c,_,_=setup;start(setup);ticket=c.packet('t')
    observed(root,c,'note',status='PASS')
    with pytest.raises(wf.Blocked,match='WRONG_STAGE_OR_TICKET'):
        c.submit('t','builder',ticket['ticket'],{},'old')


def test_duplicate_events_concurrent_are_once_only(setup):
    root,c,_,_=setup;start(setup)
    def call(_):return observed(root,c,'same',regressed=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(call,range(2)))
    assert c.retrospective_packet('t')['gates']['appearance']['triggers']==['same']
    with c.transaction() as con:
        with pytest.raises(sqlite3.IntegrityError,match='immutable'):
            con.execute('DELETE FROM retrospective_events')


def test_native_review_is_a_trigger_before_final_candidate(setup,monkeypatch):
    root,c,b,bridge,calls=native(setup,monkeypatch)
    run=dispatch(root,bridge)
    verdict=dict(verdict='FAIL',observation='Prior form lost',comparison='Compared scoped control',
        open_defects=['bad cloth'],evidence=run['artifacts'],run_digest=pk.digest(run),
        retrospective_observations=[dict(requirement='appearance',status='FAIL',observation='Useful volume lost',regressed=True)])
    bridge.record_review('t','proof',verdict)
    bridge.record_review('t','proof',verdict)
    assert c.state('t').get('candidate') is None
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'
    assert len(calls)==1


def test_worker_failure_is_recorded_without_candidate(setup,monkeypatch):
    from movie_factory.adapters.blender import runner
    root,c,b,bridge,calls=native(setup,monkeypatch)
    monkeypatch.setattr(runner,'run_blender',lambda *a,**k:{'ok':False})
    run=dispatch(root,bridge)
    assert run['status']=='FAILED'
    with c.connect() as con:
        value=rt.snapshot(con,'t')
    assert value['outcomes'][-1]['origin']=='worker'
    assert value['outcomes'][-1]['role']=='technical'
    assert c.state('t').get('candidate') is None


def test_finding_after_reservation_invalidates_native_capability(setup,monkeypatch):
    from movie_factory.adapters.blender import runner
    from movie_factory import native_admission as na
    root,c,b,bridge,calls=native(setup,monkeypatch)
    def intercepted(job,*,_admission,**kwargs):
        observed(root,c,'concurrent-finding',regressed=True)
        na.check_capability(_admission,job)
        pytest.fail('Must not reach process launch')
    monkeypatch.setattr(runner,'run_blender',intercepted)
    run=dispatch(root,bridge)
    assert run['status']=='FAILED' and calls==[]
    assert not (root/'.runtime/factory-native/proof-run').exists()


def test_packet_overflow_blocks_instead_of_truncating_required_response(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'bad',regressed=True)
    data=response(root,c)
    data['cause']='x'*60001
    c.retrospective('t','response',dict(key='appearance',response=data),'long-response')
    with pytest.raises(wf.Blocked,match='PACKET_TOO_LARGE'):c.retrospective_packet('t')


def test_unrelated_task_can_continue(setup):
    root,c,_,_=setup;start(setup);start(setup,task='independent')
    observed(root,c,'bad',foundation=True)
    assert c.packet('independent')['stage']=='EXECUTING'


def test_known_false_semantic_pass_remains_negative_control(setup):
    root,c,_,_=setup;start(setup)
    # These are knowingly false declarations, not inspected production evidence.
    for i in range(4):observed(root,c,'false'+str(i),status='PASS')
    assert c.retrospective_packet('t')['gates']=={}
    assert c.packet('t')['stage']=='EXECUTING'


def test_failed_supplement_cannot_be_overridden_by_pass(setup):
    root,c,_,_=setup;start(setup)
    data=observed(root,c,'first')
    data['attempt']='second';data['observations'] += [dict(requirement='appearance',status='PASS',observation='Conflicting declaration')]
    c.retrospective('t','outcome',data,'second')
    assert c.retrospective_packet('t')['warnings']['appearance']==2


def test_id_rename_invalidates_contract_without_discarding_history(setup):
    root,c,b,_=setup;start(setup)
    observed(root,c,'old',regressed=True)
    changed=copy.deepcopy(b);changed['requirements'][0]['id']='renamed'
    with c.transaction() as con:rt.plan(con,c._state(con,'t'),'new-plan',changed)
    gates=c.retrospective_packet('t')['gates']
    assert 'appearance' in gates and '__requirements__' in gates


def test_fresh_requirement_pass_does_not_close_open_finding(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'fail',regressed=True);observed(root,c,'pass',status='PASS')
    with pytest.raises(wf.Blocked,match='RETRO_REQUIRED'):c.packet('t')


def test_admitted_evidence_changes_block_continuation(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'fail',regressed=True);response(root,c);admit(root,c)
    (root/'evidence.jpg').write_text('changed after admission')
    with pytest.raises(ValueError):c.packet('t')


def test_delivery_retry_cannot_use_old_receipt_after_new_finding(setup):
    root,c,_,_=setup;start(setup);build(root,c)
    submit(c,'t',review(root,c),'review');c.deliver('t','receipt')
    observed(root,c,'new-regression',regressed=True)
    for eid in ('receipt','new-receipt'):
        with pytest.raises(wf.Blocked,match='RETRO_REQUIRED'):c.deliver('t',eid)


def test_testing_cannot_deliver_until_effect_review(setup):
    root,c,_,_=setup;start(setup);build(root,c)
    submit(c,'t',review(root,c),'review')
    observed(root,c,'new-regression',regressed=True);response(root,c);admit(root,c)
    with pytest.raises(wf.Blocked,match='EFFECT_NOT_EVALUATED'):c.deliver('t','receipt')


def test_inconclusive_reopens_but_does_not_consume_an_extra_correction(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'bad',regressed=True);response(root,c);admit(root,c)
    observed(root,c,'measurement',status='NOT_TESTED')
    evaluate(root,c,'appearance','measurement','inconclusive')
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'
    assert c.state('t')['cycle']==0


def test_unknown_evidence_uses_reconciliation_hold(setup):
    root,c,_,_=setup;start(setup)
    observed(root,c,'uncertain',status='UNKNOWN')
    assert c.retrospective_packet('t')['gates']['appearance']['reason']=='evidence_reconciliation'


def test_failed_review_transaction_rolls_back_native_record(setup,monkeypatch):
    root,c,b,bridge,calls=native(setup,monkeypatch);run=dispatch(root,bridge)
    original=rt.auto_outcome
    monkeypatch.setattr(rt,'auto_outcome',lambda *a,**k:(_ for _ in ()).throw(RuntimeError('synthetic crash')))
    with pytest.raises(RuntimeError):step_review(bridge,run)
    with c.connect() as con:assert not con.execute('SELECT 1 FROM native_reviews').fetchone()
    monkeypatch.setattr(rt,'auto_outcome',original)
    step_review(bridge,run)


def proof_fixture(root,c):
    b=bind(root,'evidence.jpg')
    record=dict(schema_version=1,id='cloth23',state='qualified',reuse_mode='exact',source=[b],provenance=[b],
        dependencies=[b],evidence=[b],failures=[],tested_conditions={'rig':'old'},
        rights=dict(status='verified_for_use',scope='Synthetic',evidence_paths=['evidence.jpg']),
        effort=dict(active_seconds=None))
    (root/'resource.json').write_text(json.dumps(record))
    c.retrospective('t','proof',dict(id='cloth23',manifest=bind(root,'resource.json'),conditions={'rig':'old'},
        requirements=['appearance']),'proof23')


def test_proof_use_change_requires_revalidation_not_whole_retro(setup):
    root,c,b,_=setup;start(setup);proof_fixture(root,c)
    new=copy.deepcopy(b);new['retrospective_proof_uses']=[dict(id='cloth23',conditions={'rig':'new'},purpose='diagnostic')]
    # Plan admission is separately exercised by existing pipeline tests. Here
    # inject the validated fixture plan through the trusted transition boundary.
    def transition(con):
        state=c._state(con,'t');state['brief']=new
        state['fingerprint']=wf.validate_brief(root,new,'production')
        rt.plan(con,state,'changed-proof-plan',new,root)
        return state
    c._change('t','use-new-rig','fixture',{},transition)
    key='__proof__:t:cloth23'
    assert c.retrospective_packet('t')['gates'][key]['reason']=='targeted_revalidation'
    with pytest.raises(wf.Blocked):c.packet('t')
    response(root,c,key);admit(root,c,key)
    assert c.packet('t')['stage']=='EXECUTING'
    with c.connect() as con:assert rt.snapshot(con,'t')['proofs']['cloth23']['conditions']=={'rig':'old'}


def test_shared_proof_blocks_only_registered_dependent_task(setup):
    root,c,b,_=setup;start(setup);proof_fixture(root,c)
    start(setup,task='dependent');start(setup,task='unrelated')
    def transition(con):
        state=c._state(con,'dependent')
        state['brief']['retrospective_proof_uses']=[dict(task='t',id='cloth23',conditions={'rig':'old'})]
        state['fingerprint']=wf.validate_brief(root,state['brief'],'production')
        rt.plan(con,state,'dependent-proof-plan',state['brief'],root)
        return state
    c._change('dependent','dependency','fixture',{},transition)
    observed(root,c,'regression',regressed=True)
    with pytest.raises(wf.Blocked,match='DEPENDENT_PROOF_HELD'):c.packet('dependent')
    assert c.packet('unrelated')['stage']=='EXECUTING'


def test_removing_proof_dependency_cannot_silently_drop_history(setup):
    root,c,b,_=setup;start(setup);proof_fixture(root,c)
    with c.transaction() as con:
        state=c._state(con,'t');new=copy.deepcopy(b)
        new['retrospective_proof_uses']=[dict(id='cloth23',conditions={'rig':'old'})]
        rt.plan(con,state,'using-proof',new,root)
        rt.plan(con,state,'dropping-proof',b,root)
    assert '__dependencies__' in c.retrospective_packet('t')['gates']


def test_replacing_registered_proof_cannot_silently_repin_consumers(setup):
    root,c,b,_=setup;start(setup);proof_fixture(root,c)
    with c.transaction() as con:
        state=c._state(con,'t');state['brief']['retrospective_proof_uses']=[dict(id='cloth23',conditions={'rig':'old'})]
        rt.plan(con,state,'using-proof',state['brief'],root)
        proof=copy.deepcopy(rt.snapshot(con,'t')['proofs']['cloth23'])
        proof['additional_note']='New qualification record, not automatically adopted'
        rt.proof(root,con,state,'replacement',proof)
        with pytest.raises(wf.Blocked,match='PROOF_VERSION_CHANGED'):rt.check_proofs(root,con,state)


def test_explicit_legacy_migration_keeps_counts_and_creates_unknown_hold(setup):
    root,c,_,_=setup;start(setup)
    # Simulate a pre-policy database in this disposable fixture only.
    with c.transaction() as con:
        con.execute('DROP TABLE retrospective_events')
        con.execute('DROP TABLE retrospective_cache397')
    c=wf.Controller(root,'state.sqlite3')
    with pytest.raises(wf.Blocked,match='MIGRATION'):c.packet('t')
    before=c.state('t')
    c.migrate_retrospective('t',bind(root,'authority.md'),dict(state_digest=pk.digest(before),
        evidence={'audit':bind(root,'evidence.jpg')},coverage='Frozen legacy record',unknowns='History not inferred from counter'),'migrate')
    assert c.state('t')['cycle']==before['cycle']
    assert '__migration__' in c.retrospective_packet('t')['gates']
    with pytest.raises(wf.Blocked):c.packet('t')
