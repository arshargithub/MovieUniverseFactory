import copy
import json
import sqlite3
import pytest
from movie_factory import production_governance as g, production_contracts as pc
from movie_factory import production_workflow as wf, production_knowledge as pk
from test_production_workflow import setup, start, build, review, submit, bind
from governance_fixtures397 import attach, checks


def state(task='t', cycle=0, limit=100):
    return dict(task=task,route='production',mode='offline',cycle=cycle,max_corrections=limit,stage='EXECUTING')


@pytest.fixture
def ledger(tmp_path):
    c=sqlite3.connect(':memory:');g.install(c)
    c.execute('CREATE TABLE heavy_job(slot INTEGER)')
    (tmp_path/'authority.md').write_text('Synthetic explicit authority')
    a=bind(tmp_path,'authority.md')
    for ident,kind,parent in [('r','release',None),('m','milestone','r'),('c','capability','m'),('f','family','c')]:
        g.define_node(tmp_path,c,ident,dict(id=ident,kind=kind,parent=parent,limit=100,purpose='fixture',authority=a))
    st=state()
    g.migrate(tmp_path,c,st,'migrate',dict(task='t',state_digest=pk.digest(st),authority=a,baseline_slots=0,
        original_limit=100,features=['chest'],historical_age={'chest':0},history_evidence={'source':a},
        unknowns=[],profile=g.DEFAULTS,node='f',remaining_allocation=100))
    return tmp_path,c,a


def fail_cycles(con,start,end):
    for i in range(start,end):
        if i and i%10==0:
            s=g.snapshot(con);p=g.task_progress(s,'t')
            g.append(con,'review'+str(i),'scope_review',dict(task='t',effect_counts={'chest':0},
                reviewed_ages=p['feature_age'],proof_stamps=p['proof_stamps']))
        st=state(cycle=i);g.reserve(con,st);g.finish_cycle(con,st,'FAIL','end'+str(i))


def test_twentieth_completed_failure_stops_across_new_method(ledger):
    root,c,a=ledger;fail_cycles(c,0,20)
    assert g.task_progress(g.snapshot(c),'t')['feature_age']=={'chest':20}
    with pytest.raises(wf.Blocked,match='NO_PROGRESS_STOP'):g.reserve(c,state(cycle=20))
    g.define_node(root,c,'f2',dict(id='f2',kind='family',parent='c',limit=0,purpose='different method',authority=a))
    g.rebind(root,c,state(),'move',dict(task='t',node='f2',authority=a))
    with pytest.raises(wf.Blocked,match='NO_PROGRESS_STOP'):g.reserve(c,state(cycle=20))


def test_new_cycle_name_cannot_recharge_or_reset(ledger):
    _,c,_=ledger;g.reserve(c,state());g.reserve(c,state())
    assert g.task_progress(g.snapshot(c),'t')['spent']==1
    assert g.snapshot(c)==g.snapshot(c,full=True)


def test_last_reserved_review_can_finish_at_stop(ledger):
    _,c,_=ledger;fail_cycles(c,0,20)
    assert g.guard(c,state(cycle=19),operation='review')['spent']==20


@pytest.mark.parametrize('limit',[True,-1,1.5,'10'])
def test_no_truthy_or_fractional_limits(ledger,limit):
    root,c,a=ledger
    with pytest.raises(wf.Blocked):g.define_node(root,c,'bad',dict(id='bad',kind='release',parent=None,
        limit=limit,purpose='bad',authority=a))


def test_allocation_aggregate_and_no_goal_relabel(ledger):
    root,c,a=ledger
    with pytest.raises(wf.Blocked,match='OVERALLOCATED'):
        g.define_node(root,c,'extra',dict(id='extra',kind='milestone',parent='r',limit=1,purpose='bad',authority=a))
    g.define_node(root,c,'root2',dict(id='root2',kind='release',parent=None,limit=1,purpose='other',authority=a))
    with pytest.raises(wf.Blocked,match='CANNOT_CHANGE_CAPABILITY'):
        g.rebind(root,c,state(),'move',dict(task='t',node='root2',authority=a))


def test_cache_corruption_blocks_and_full_replay_retains_truth(ledger):
    _,c,_=ledger;g.reserve(c,state())
    truth=g.snapshot(c,full=True)
    c.execute("UPDATE governance_cache397 SET state='{}'")
    with pytest.raises((wf.Blocked,KeyError)):g.snapshot(c)
    assert g.snapshot(c,full=True)==truth
    with pytest.raises(sqlite3.IntegrityError):c.execute('DELETE FROM governance_events397')


def test_migration_cannot_refund_original_limit(ledger):
    root,c,a=ledger;st=state('other',cycle=8,limit=9)
    with pytest.raises(wf.Blocked,match='CANNOT_GRANT'):
        g.migrate(root,c,st,'bad',dict(task='other',state_digest=pk.digest(st),authority=a,baseline_slots=8,
            original_limit=9,features=['chest'],historical_age={'chest':0},history_evidence={'s':a},
            unknowns=[],profile=g.DEFAULTS,node='f',remaining_allocation=10))


def test_native_missing_migration_is_not_offline_permission(ledger):
    _,c,_=ledger
    with pytest.raises(wf.Blocked,match='MIGRATION_REQUIRED'):
        g.guard(c,state('new')|{'mode':'local_native'})
    assert g.guard(c,state('old')) is None


def test_retirement_survives_an_increased_counter(ledger):
    root,c,a=ledger;g.retire(root,c,'retire',dict(node='c',reason='failed production qualification',authority=a))
    with pytest.raises(wf.Blocked,match='RETIRED'):g.reserve(c,state(limit=10000))


def test_real_controller_typed_review_and_restart(setup):
    root,c,b,_=setup;start(setup)
    # Replan only to install the frozen typed brief; no native fixture or calls.
    attach(root,c,b)
    c.replan('t','STRATEGIZING','Add397synthetic contract','replan397')
    submit(c,'t',b,'plan397');build(root,c,event='build397')
    r=checks(b,review(root,c))
    value=submit(c,'t',r,'review397')
    assert value['stage']=='READY_FOR_DIRECTOR_AV'
    assert c.governance_status('t')['spent']==1
    assert c.governance_status('t')==c.governance_status('t',full=True)
    restarted=wf.Controller(root,'state.sqlite3')
    assert restarted.governance_status('t')==c.governance_status('t')
    assert not value['production_approved']


def test_overall_pass_with_failed_cell_is_rejected(setup):
    root,c,b,_=setup;start(setup);attach(root,c,b)
    c.replan('t','STRATEGIZING','typed','replan397');submit(c,'t',b,'plan397');build(root,c)
    r=checks(b,review(root,c));r['contract_checks397'][0]['cells'][0]['status']='FAIL'
    with pytest.raises(wf.Blocked,match='CONTRADICTS'):submit(c,'t',r,'bad-review')
    assert c.state('t')['stage']=='REVIEWING'


def test_scope_is_a_causal_contract_not_just_keep_reason(setup):
    root,c,b,_=setup;start(setup);attach(root,c,b)
    d=copy.deepcopy(b['production_contract397']['scope'])
    d['changes'].append(dict(domain='binding',control='independent uncontrolled change'))
    with pytest.raises(wf.Blocked,match='MULTIPLE_CONTRASTS'):pc.scope_contract(root,d)
    d['necessary_coupling']='Explicit anatomical coupling counterexample'
    pc.scope_contract(root,d)


def test_declared_build_cannot_precede_actual_target(setup):
    root,c,b,_=setup;start(setup);attach(root,c,b)
    d=b['production_contract397'];d['operations'][0]['class']='fit'
    with pytest.raises(wf.Blocked,match='TARGET_BEFORE'):pc.validate(root,b)


def test_mandatory_context_overflow_never_truncates():
    packet={'planning_step':'GROUNDING','planning_inputs':{},'authority':{'id':'a'},'required':'x'*1000}
    with pytest.raises(wf.Blocked,match='OVERFLOW'):pc.compact_packet(packet,{},maximum=50)
    p=pc.compact_packet(packet,{},maximum=2000)
    assert p['required']==packet['required'] and p['authority']==packet['authority']


def test_packet_phase_projection_keeps_full_manifest():
    p={'planning_step':'DERIVING','planning_inputs':{'GROUNDING':{'required':['r']},'STRATEGIZING':{'large':'history'}}}
    result=pc.compact_packet(p,{})
    assert set(result['planning_inputs'])=={'GROUNDING'}
    assert set(result['dependency_manifest397'])==set(p['planning_inputs'])


def test_new_scope_review_cannot_lie_about_counts(ledger):
    root,c,a=ledger
    with pytest.raises(wf.Blocked):g.scope_review(root,c,state(),'s',{'task':'t','decision':'keep',
        'effect_counts':{'chest':0},'diagnostic':{},'next_operation':'fit'})


def test_two_ineffective_experiments_cannot_be_hidden_by_finding_count(ledger):
    _,c,_=ledger
    for eid,experiment,req in [('e1','one','a'),('e2','one','b'),('e3','two','a')]:
        g.append(c,eid,'effect',dict(task='t',feature='chest',experiment=experiment,requirement=req,result='ineffective'))
    p=g.task_progress(g.snapshot(c),'t')
    assert p['ineffective_interventions']['chest']==2 and p['decision']=='REASSESS'
    with pytest.raises(wf.Blocked,match='SCOPE_REASSESSMENT'):g.reserve(c,state())


def test_tenth_cycle_requires_investment_review_not_director_acceptance(ledger):
    _,c,_=ledger;fail_cycles(c,0,10)
    with pytest.raises(wf.Blocked,match='INVESTMENT_REVIEW'):g.reserve(c,state(cycle=10))
    assert g.task_progress(g.snapshot(c),'t')['decision']=='REASSESS'


def test_regression_revokes_progress_credit_but_retains_old_scoped_evidence(ledger):
    _,c,_=ledger
    g.append(c,'p','proof',dict(id='p',task='t',cycle=0,feature='chest',conditions={'pose':'old'},evidence={}))
    st=state(cycle=1)|{'brief':{'production_contract397':{'feature_map':{'form':['chest']}}}}
    g.capture_outcomes(c,st,[{'requirement':'form','status':'FAIL'}],'bad')
    assert g.snapshot(c)['proofs']['p']['valid'] is True
    assert g.task_progress(g.snapshot(c),'t')['proof_stamps']['chest']=='historical-baseline'


def test_split_requires_actual_child_proof_graph(setup):
    root,c,b,_=setup;start(setup);attach(root,c,b)
    d=copy.deepcopy(b['production_contract397']['scope']);d['decision']='split'
    with pytest.raises((ValueError,wf.Blocked)):pc.scope_contract(root,d)
    d['children']=[dict(id='target',question='Is form convincing?',acceptance='Matched reference',depends_on=[],
                       proof_kind='target_form',criteria=['appearance'],operation_ids=['proof']),
                   dict(id='deformation',question='Is form preserved?',acceptance='Raised pose',depends_on=['target'],
                        proof_kind='pose_form',criteria=['appearance'],operation_ids=['deform'])]
    d['current_child']='target';pc.scope_contract(root,d)


def test_known_bad_artifact_cannot_pass_typed_review(setup):
    root,c,b,_=setup;start(setup);attach(root,c,b)
    candidate={'version':'bad','artifacts':{'bad':bind(root,'reference.mov')}}
    b['references'][0]['role']='negative_control'
    with pytest.raises(wf.Blocked,match='KNOWN_REJECTED'):
        pc.review(root,b,candidate,{'contract_checks397':[dict(id=x['id']) for x in b['requirements']]})


def test_public_governance_request_retry_is_idempotent(setup):
    root,c,b,_=setup;start(setup)
    a=bind(root,'authority.md');d=dict(id='r',kind='release',parent=None,limit=0,purpose='test',authority=a)
    c.governance('t','node',d,'request397');c.governance('t','node',d,'request397')
    with pytest.raises(wf.Blocked,match='REQUEST_ID_CONFLICT'):c.governance('t','node',dict(d,limit=1),'request397')


def test_task_allocation_cannot_override_original_authority_or_retirement(ledger):
    root,c,a=ledger;fail_cycles(c,0,20)
    approval=dict(decision='approve_task_allocation',task='t',old_allocation=100,new_allocation=99,human_source=a)
    (root/'grant.json').write_text(json.dumps(approval));d=dict(task='t',allocation=99,authority=bind(root,'grant.json'))
    with pytest.raises(wf.Blocked,match='NO_NEW_ALLOWANCE'):g.amend_task_allocation(root,c,state(cycle=20,limit=20),'bad-grant',d)
    g.amend_task_allocation(root,c,state(cycle=20,limit=100),'grant',d)
    with pytest.raises(wf.Blocked,match='NO_PROGRESS_STOP'):g.reserve(c,state(cycle=20,limit=100))


def test_nondefault_watchdog_requires_exact_director_profile(ledger):
    root,c,a=ledger;st=state('other')
    profile=dict(review_after=12,stop_after=24,context_bytes=24576)
    approved=dict(decision='approve_governance_profile',task='other',profile=profile,human_source=a)
    (root/'profile.json').write_text(json.dumps(approved))
    d=dict(task='other',state_digest=pk.digest(st),authority=a,baseline_slots=0,original_limit=100,
           features=['chest'],historical_age={'chest':0},history_evidence={'s':a},unknowns=[],
           profile=profile,node='f',remaining_allocation=0,profile_authority=bind(root,'profile.json'))
    g.migrate(root,c,st,'profile-ok',d)
    assert g.snapshot(c)['tasks']['other']['profile']==profile


def test_new_task_on_same_capability_cannot_reset_feature_age(ledger):
    root,c,a=ledger;fail_cycles(c,0,20);st=state('renamed',cycle=0)
    data=dict(task='renamed',state_digest=pk.digest(st),authority=a,baseline_slots=0,original_limit=100,
      features=['chest'],historical_age={'chest':0},history_evidence={'s':a},unknowns=[],
      profile=g.DEFAULTS,node='f',remaining_allocation=0)
    g.migrate(root,c,st,'renamed-task',data)
    assert g.task_progress(g.snapshot(c),'renamed')['feature_age']['chest']==20
    with pytest.raises(wf.Blocked,match='NO_PROGRESS_STOP'):g.reserve(c,st)
    bad=dict(data,task='renamed-again',features=['new-label'],historical_age={'new-label':0})
    other=state('renamed-again');bad['state_digest']=pk.digest(other)
    with pytest.raises(wf.Blocked,match='FEATURE_IDENTITY'):g.migrate(root,c,other,'hide-feature',bad)


def test_proof_order_survives_cache_sorting_and_restart(ledger):
    _,c,_=ledger
    g.append(c,'z','proof',dict(id='z',task='t',cycle=99,feature='chest',conditions={},evidence={}))
    g.append(c,'a','proof',dict(id='a',task='t',cycle=1,feature='chest',conditions={},evidence={}))
    assert g.task_progress(g.snapshot(c),'t')['proof_stamps']['chest']=='a'
    assert g.task_progress(g.snapshot(c,full=True),'t')==g.task_progress(g.snapshot(c),'t')


def test_economics_keeps_scenario_separate_and_does_not_invent_C(ledger):
    _,c,_=ledger;fail_cycles(c,0,3);v=g.economics(g.snapshot(c))
    assert v['prospective_reserved_cycles']==3 and v['scenario']['fraction']==.125
    assert v['scenario']['same_productivity_total'] is None
    assert v['qualified_release']['fraction'] is None
    assert g.economics(g.snapshot(c),baseline_cycles=100,total_envelope=400)['scenario']['required_improvement']==pytest.approx(7/3)
    with pytest.raises(wf.Blocked):g.economics(g.snapshot(c),baseline_cycles=100,total_envelope=100)
