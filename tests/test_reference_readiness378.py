"""Offline reference contracts. Synthetic media and claims are not visual proof."""
import copy
import json
import pytest
from movie_factory import reference_readiness as rr, reference_acquisition as ra
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import expert_planning as ep, stage_routing as routing
from movie_factory.budget import BudgetLedger, BudgetExceeded, BudgetError
from test_production_workflow import setup, direction, bind, start, build, review, submit
from test_task_router332 import request
import planning_fixtures as pf
import reference_fixtures378 as rf
from routing_fixtures360 import assignment


def physical(root,b):
    ref=b['references'][0]
    b['source_bindings']['reference']=ref['binding']
    need=dict(id='junction',purpose='physical_form',question='What is the chest/foreleg contour?',critical=True,coverage=['front','oblique'])
    q=dict(id=ref['id'],origin='director',observation='SYNTHETIC two-view coverage; no real anatomy claim',
           governs='Junction contour only',excluded_authority='Not palette, identity or motion timing',
           provenance='Synthetic Director fixture',rights_use='reference_only',
           coverage={'front':'Synthetic front contour','oblique':'Synthetic oblique volume'},evidence=[ref['binding']])
    ready=dict(version=1,scope=dict(version=1,id='chest-fixture',kind='micro_appearance',needs=[need]),
               decisions={'junction':dict(decision='reuse_existing',status='sufficient',reason='Synthetic coverage',
                   reopen_when='Required angle or pose is missing',references=[q])})
    b['reference_readiness']=ready;b['reference_mapping']={r['id']:['junction'] for r in b['requirements']}
    b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
    return ready


def test_native_grounding_requires_decision_before_any_execution(setup):
    root,_,b,_=setup;c=wf.Controller(root,'.runtime/factory-entry.sqlite3')
    c.route_request('r',request(root,['native_inspect']))
    c.create('t','production',bind(root,'authority.md'),'c',direction=direction(b),mode='local_native',admission='r')
    p=c.packet('t')
    with pytest.raises(wf.Blocked,match='REFERENCE_SCOPE_REQUIRED'):
        c.submit('t',p['actor'],p['ticket'],pf.result(p,b),'missing')
    assert c.state('t')['planning_step']=='GROUNDING' and c.state('t')['cycle']==0


def test_controller_propagates_contract_and_director_av_stays_pending(setup):
    root,c,b,_=setup;ready=physical(root,b);start(setup)
    assert c.packet('t')['reference_contract']['version']==1
    build(root,c);r=review(root,c);r['reference_readiness_review']=rf.review(ready)
    s=submit(c,'t',r,'review')
    assert s['stage']=='READY_FOR_DIRECTOR_AV'
    assert not c.deliver('t','delivery')['receipt']['production_approved']


def test_native_physical_plan_accepts_qualified_inputs_without_worker(setup):
    root,_,b,_=setup;physical(root,b);b['offline_only']=False
    c=wf.Controller(root,'.runtime/factory-entry.sqlite3');c.route_request('r',request(root,['native_inspect']))
    c.create('t','production',bind(root,'authority.md'),'c',direction=direction(b),mode='local_native',admission='r')
    assert pf.complete(c,'t',b,'qualified')['stage']=='EXECUTING'
    assert c.state('t')['cycle']==0


@pytest.mark.parametrize('mutation,error',[
    ('none','PHYSICAL_NEEDS_EVIDENCE'),('coverage','COVERAGE_GAP'),('observation','QUALIFICATION_OBSERVATION'),
    ('source','SOURCE_MEDIA_REQUIRED'),('unknown','UNKNOWN_SOURCE'),('status','NOT_SUFFICIENT')])
def test_qualification_rejects_missing_or_inadequate_declared_inputs(setup,mutation,error):
    root,_,b,_=setup;v=physical(root,b);d=v['decisions']['junction'];q=d['references'][0]
    if mutation=='none':d.update(decision='none_needed',status='not_needed',references=[])
    elif mutation=='coverage':q['coverage'].pop('front')
    elif mutation=='observation':q['observation']=''
    elif mutation=='source':q['evidence']=[bind(root,'evidence.jpg')]
    elif mutation=='unknown':q['id']='other'
    else:d['status']='awaiting_media'
    with pytest.raises(wf.Blocked,match=error):rr.validate(root,b['references'],v)


def test_stale_media_not_cleared_by_good_status(setup):
    root,_,b,_=setup;v=physical(root,b);(root/'reference.mov').write_text('changed')
    with pytest.raises(ValueError,match='STALE|stale|hash|HASH'):rr.validate(root,b['references'],v)


def test_generated_physical_target_requires_real_corroboration_but_design_does_not(setup):
    root,_,b,_=setup;v=physical(root,b);q=v['decisions']['junction']['references'][0];q['origin']='built_in_image'
    with pytest.raises(wf.Blocked,match='UNCORROBORATED'):rr.validate(root,b['references'],v)
    v['scope']['needs'][0]['purpose']='design'
    rr.validate(root,b['references'],v)
    real=copy.deepcopy(q);real.update(id='real',origin='image_search');b['references'].append(dict(b['references'][0],id='real'))
    v['scope']['needs'][0]['purpose']='physical_form';q['validated_against']=['real'];v['decisions']['junction']['references'].append(real)
    rr.validate(root,b['references'],v)


def test_dropped_reference_mapping_or_source_is_blocked(setup):
    root,_,b,_=setup;v=physical(root,b)
    data=dict(reference_readiness=v,reference_mapping=b['reference_mapping'],requirements=b['requirements'],derivations=b['expert_plan']['realizations'])
    rr.derivation({'reference_readiness':v},data)
    bad=copy.deepcopy(data);bad['reference_mapping'].pop('appearance')
    with pytest.raises(wf.Blocked,match='REQUIREMENT_COVERAGE'):rr.derivation({'reference_readiness':v},bad)
    bad=copy.deepcopy(data);bad['derivations']['appearance']['reference_ids']=[]
    with pytest.raises(wf.Blocked,match='SOURCE_LOST'):rr.derivation({'reference_readiness':v},bad)


def test_changed_reference_invalidates_plan_and_stage_challenge(setup):
    root,_,b,_=setup;v=physical(root,b);prior=ep.plan_digest(b);challenge=rf.challenge(v)
    v['decisions']['junction']['reason']='Changed scope justification'
    assert ep.plan_digest(b)!=prior
    with pytest.raises(wf.Blocked,match='CHALLENGE_STALE'):rr.challenge(root,v,dict(outcome='admit',reference_challenge=challenge))


def test_execution_and_review_cannot_omit_reference_aspect(setup):
    root,c,b,_=setup;v=physical(root,b);start(setup);p=c.packet('t')
    result=dict(fingerprint=p['fingerprint'],requirement_uses=__import__('expert_fixtures').uses(b),
                reference_uses={'rear':dict(reference_digest=pk.digest(b['references'][0]),application='Synthetic')},
                candidate=dict(version='bad',artifacts={'clip':bind(root,'candidate.bin')}))
    with pytest.raises(wf.Blocked,match='REFERENCE_EXECUTION'):submit(c,'t',result,'badbuild')
    build(root,c);r=review(root,c)
    with pytest.raises(wf.Blocked,match='REFERENCE_REVIEW'):submit(c,'t',r,'badreview')
    r['reference_readiness_review']=rf.review(v);r['reference_readiness_review']['aspects']['junction']['status']='FAIL'
    s=submit(c,'t',r,'failreview');assert s['stage']=='EXECUTING' and s['cycle']==1


def test_explicit_gap_triggers_retro_immediately_and_requires_grounding(setup):
    root,c,b,_=setup;v=physical(root,b);start(setup)
    c.retrospective('t','outcome',dict(role='diagnostic',attempt='one',evidence={'image':bind(root,'evidence.jpg')},observations=[dict(requirement='appearance',status='FAIL',observation='Missing reverse view',reference_gap=True)]),'gap')
    p=c.retrospective_packet('t');assert p['gates']['appearance']['reason']=='reference_inputs_inadequate'
    assert p['reference_contract']['version']==1 and c.state('t')['cycle']==0
    a=dict(readiness_digest=pk.digest(v),diagnosis='reference_gap',disposition='supplement',reason='Missing angle',aspects=['junction'],evidence=[bind(root,'evidence.jpg')])
    with pytest.raises(wf.Blocked,match='REQUIRES_GROUNDING'):rr.assessment(root,v,dict(target_stage='STRATEGIZING',reference_assessment=a))
    rr.assessment(root,v,dict(target_stage='GROUNDING',reference_assessment=a))
    a.update(diagnosis='execution',disposition='retain');rr.assessment(root,v,dict(target_stage='STRATEGIZING',reference_assessment=a))
    response=dict(cause='Insufficient reverse-view target',uncertainty='Additional imagery may not solve construction',
        change_or_retain_rationale='Supplement, not weaken existing authority',preserve='Accepted motion',test='Qualify missing view',
        expected='Explicit positive contours',failure_response='Retain unresolved goal',target_stage='STRATEGIZING',
        plan=pk.digest(c.state('t')['brief']),gate_digest=pk.digest(p['gates']['appearance']),evidence={'image':bind(root,'evidence.jpg')},reference_assessment=a)
    with pytest.raises(wf.Blocked,match='REQUIRES_GROUNDING'):
        c.retrospective('t','response',dict(key='appearance',response=response),'wrongresponse')
    response.update(target_stage='GROUNDING',reference_assessment=dict(a,diagnosis='reference_gap',disposition='supplement'))
    c.retrospective('t','response',dict(key='appearance',response=response),'response')
    assert c.state('t')['cycle']==0 and c.state('t')['max_corrections']==2


def test_astra_micro_assignment_requires_adequate_target_and_failure_basis(setup):
    root,_,b,_=setup;v=physical(root,b)
    p=dict(task='t',actor='builder',stage='EXECUTING',cycle=0,brief=b)
    rec=assignment(root,p);pol=routing.policy('specialist_3d',{'builder':rec})
    with pytest.raises(wf.Blocked,match='ESCALATION_BASIS'):routing.resolve(pol,'builder',root,p)
    p['reference_escalation_basis']=dict(readiness_digest=pk.digest(v),hypothesis='execution_gap',reason='Target clear but failed actual construction',evidence=[bind(root,'evidence.jpg')])
    rec=assignment(root,p);pol=routing.policy('specialist_3d',{'builder':rec})
    assert routing.resolve(pol,'builder',root,p)['model']==routing.ASTRA
    assert routing.resolve(routing.policy('specialist_3d'),'builder',root,p)['model']==routing.SOL


def test_semantic_negative_control_remains_explicit(setup):
    root,_,b,_=setup;v=physical(root,b)
    # These bytes are NOT a horse video. Honesty/visual sufficiency cannot be
    # inferred from a well-formed claim; retain this admitted negative control.
    assert (root/'reference.mov').read_text().startswith('SYNTHETIC')
    assert rr.validate(root,b['references'],v)==pk.digest(v)


def paid(root,cap=1,calls=1):
    def write(name,v):
        (root/name).write_text(json.dumps(v));return bind(root,name)
    qualification=write('qualification.json',{k:'confirmed' for k in ('commercial_output_rights','input_privacy','deployment_export','cost_bound')})
    plan=dict(method='generated_video',id='ref',purpose='motion',question='Test hypothetical timing',provider='mock',model='mock',prompt='SYNTHETIC',ledger_stage='reference',ledger_scope='reference',max_request_usd=1,inputs=[],qualification=qualification)
    source=write('human.json',{'reply':'SYNTHETIC approve one mocked call'})
    approval=write('approval.json',dict(decision='approve_reference_video',request_digest=pk.digest(plan),director_reply='SYNTHETIC approval',source=source,max_total_usd=cap,max_calls=calls,ledger_path='budget.jsonl'))
    kwargs=dict(campaign_limit=cap,scope_limits={'reference':cap},stage_limits={'reference':(cap,calls)},request_limit=calls)
    return plan,approval,BudgetLedger(root/'budget.jsonl',**kwargs),kwargs


def test_acquisition_ownership_and_mocked_dispatch_reservation_before_call(tmp_path):
    assert not ra.route('built_in_image')['requires_director_spend']
    assert not ra.route('image_search')['requires_director_spend']
    assert ra.route('generated_video')['requires_persistent_budget']
    p,a,ledger,_=paid(tmp_path);seen=[]
    def provider(plan):
        events=[json.loads(x) for x in ledger.path.read_text().splitlines()]
        assert events[-1]['event_type']=='reserved';seen.append(plan)
        return {'id':'mock','cost_usd':.2}
    receipt=ra.dispatch_video(tmp_path,p,a,ledger,provider)
    assert seen==[p] and receipt['status']=='candidate_not_qualified_reference'
    with pytest.raises(BudgetExceeded):ra.dispatch_video(tmp_path,p,a,ledger,provider)


@pytest.mark.parametrize('change,error',[('approval','APPROVAL_SCOPE'),('rights','UNQUALIFIED_PROVIDER'),('path','LEDGER_SCOPE'),('cap','LEDGER_LIMIT')])
def test_paid_failure_blocks_before_provider_and_reservation(tmp_path,change,error):
    p,a,ledger,_=paid(tmp_path)
    if change=='rights':
        (tmp_path/'qualification.json').write_text('{}');p['qualification']=bind(tmp_path,'qualification.json')
    else:
        v=json.loads((tmp_path/'approval.json').read_text())
        if change=='approval':v['request_digest']='wrong'
        elif change=='path':v['ledger_path']='new.jsonl'
        else:v['max_total_usd']=.1
        (tmp_path/'approval.json').write_text(json.dumps(v));a=bind(tmp_path,'approval.json')
    with pytest.raises(wf.Blocked,match=error):ra.dispatch_video(tmp_path,p,a,ledger,lambda _:pytest.fail('must not dispatch'))
    assert len(ledger.path.read_text().splitlines())==1


def test_unknown_charge_survives_restart_and_new_run_ids(tmp_path):
    p,a,ledger,kwargs=paid(tmp_path)
    with pytest.raises(RuntimeError):ra.dispatch_video(tmp_path,p,a,ledger,lambda _:(_ for _ in ()).throw(RuntimeError('mock failure')))
    ledger=BudgetLedger(tmp_path/'budget.jsonl',**kwargs)
    events=[json.loads(x) for x in ledger.path.read_text().splitlines()]
    assert events[-1]['cost_units'] is None
    with pytest.raises(BudgetExceeded):ra.dispatch_video(tmp_path,p,a,ledger,lambda _:pytest.fail('no retry allowance'))
    p['id']='another-run'
    v=json.loads((tmp_path/'approval.json').read_text());v['request_digest']=pk.digest(p)
    (tmp_path/'approval.json').write_text(json.dumps(v));a=bind(tmp_path,'approval.json')
    with pytest.raises(BudgetExceeded):ra.dispatch_video(tmp_path,p,a,ledger,lambda _:pytest.fail('new run must not reset campaign'))
    with pytest.raises(BudgetError):BudgetLedger(tmp_path/'budget.jsonl',**(kwargs|{'campaign_limit':2}))
