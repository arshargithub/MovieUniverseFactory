"""Synthetic protocol controls. No Blender, provider or artistic qualification."""
from copy import deepcopy
import json
import pytest
from movie_factory import work_units as u, production_workflow as wf, production_knowledge as pk
from movie_factory import retrospective as rt
from test_production_workflow import setup, direction, bind
from test_work_units367 import contract, reviewed
from test_retrospective350 import observed
import planning_fixtures as pf


def brief386(setup):
    root,_,b,_=setup;b=deepcopy(b);unit=contract(b);unit.update(version=2,discipline='appearance')
    b['references'][0]['role']='accepted_quality'
    b['reference_plan']['rear']['reference_digest']=pk.digest(b['references'][0])
    evidence=bind(root,'task.json')
    unit['appearance_proof']=dict(poses=[283,333,339],views=['front','side','oblique'],
        motion_source=evidence,interfaces=['neck/chest','chest/leg','seat/back'])
    unit['scope_decision']=dict(decision='split',rationale='Synthetic coherent chest mass first',
        independent_judgment='Standing and worst pose show mass with surrounding anatomy',
        coupled_context='Both shoulders and forelegs remain visible',worst_proof='339oblique plus stance',
        integration_proof='Full accepted rear and contacts',parent_task='t',allowance_binding=evidence,
        considered_outcomes=[dict(id='mass',disposition='current',criterion='Connected modest paired relief',reason='Primary visible result'),
                             dict(id='junction',disposition='deferred',criterion='No pinched roots',reason='Next unit, context retained')])
    unit['causal_experiment']=dict(unknown='Target versus deformation',hypothesis='Bad target contour drives web',
        method_family='positive_target',discriminator='Explicit contour in stance and descent',
        success_prediction='Supported relief',failure_prediction='Panel or pouch remains',
        failure_response='Reject target before interpolation',failed_alternatives=['Uniform smoothing'],evidence=[evidence])
    unit['scope_challenge']=dict(status='PASS',observation='Synthetic scope challenge',
        counterexample='A cropped success could hide a failed shoulder',evidence=[evidence])
    unit['dependencies']=[dict(id='action',binding=evidence,interfaces=['fixed action'],
        disposition='preserve',reason='Protect accepted motion')]
    b['work_unit']=unit;b['expert_plan']['challenge']['plan_digest']=pk.digest('temporary')
    from movie_factory import expert_planning as ep
    b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
    return b


def start386(setup):
    root,c,_,_=setup;b=brief386(setup)
    c.create('t','production',bind(root,'authority.md'),'create386',10,direction(b))
    for _ in range(4):
        packet=c.packet('t');result=pf.result(packet,b)
        if packet['planning_step']=='CHALLENGING':
            result['unit_scope_challenge']=dict(unit_digest=pk.digest(b['work_unit']),counterexample='Wrong positive shape can still pass metadata',
                checks={k:dict(status='PASS',observation='Synthetic scope/source comparison',evidence=[bind(root,'evidence.jpg')])
                        for k in ['independent_outcome','coupled_context','positive_target','causal_test','interfaces']})
        c.submit('t',packet['actor'],packet['ticket'],result,'stage386-'+packet['planning_step'])
    return root,c,b


@pytest.mark.parametrize('field',['scope_decision','causal_experiment','scope_challenge','dependencies'])
def test_scope_fields_required(setup,field):
    b=brief386(setup);del b['work_unit'][field]
    with pytest.raises(wf.Blocked):u.validate(b)


def test_task_and_parent_allowance_not_reset_by_child(setup):
    b=brief386(setup);state=dict(task='t',cycle=3,max_corrections=10,brief=b)
    u.native(state,dict(operation='nihang_save'))
    with pytest.raises(wf.Blocked,match='UNIT_ASSIGNMENT'):u.native({**state,'task':'new-child'},dict(operation='nihang_save'))
    with pytest.raises(wf.Blocked,match='PARENT_ALLOWANCE'):u.native({**state,'max_corrections':8},dict(operation='nihang_save'))


def test_multiple_independent_current_outcomes_rejected(setup):
    b=brief386(setup);b['work_unit']['scope_decision']['considered_outcomes'][1]['disposition']='current'
    with pytest.raises(wf.Blocked,match='ONE_CURRENT'):u.validate(b)


def test_existing_controller_requires_fresh_challenge(setup):
    root,c,_,_=setup;b=brief386(setup);c.create('t','production',bind(root,'authority.md'),'create',2,direction(b))
    for _ in range(3):
        p=c.packet('t');c.submit('t',p['actor'],p['ticket'],pf.result(p,b),'stage-'+p['planning_step'])
    p=c.packet('t')
    with pytest.raises(wf.Blocked,match='CHALLENGE_UNIT_SCOPE'):c.submit('t',p['actor'],p['ticket'],pf.result(p,b),'missing')


def reply386(root,c,ident):
    packet=c.retrospective_packet('t');unit=c.state('t')['brief']['work_unit']
    data=dict(cause='Synthetic wrong target',uncertainty='Target versus mapping',change_or_retain_rationale='Discriminate target first',
        preserve='Action',test='Matched stance and339',expected='Supported relief',failure_response='Replan target',
        target_stage='STRATEGIZING',plan=pk.digest(c.state('t')['brief']),gate_digest=pk.digest(packet['gates']['appearance']),
        evidence={'image':bind(root,'evidence.jpg')},scope_assessment=dict(decision='keep',unit_digest=pk.digest(unit),reason='One result with context'),
        causal_assessment=dict(category='positive_target',method_family='positive_target',changed_prediction='Reference-shaped contour',previous_result='FAIL'))
    c.retrospective('t','response',dict(key='appearance',response=data),'response'+ident)
    ch=dict(response_event='response'+ident,counterexample='Wrong target still possible',
        checks={k:dict(status='PASS',observation='Synthetic comparison') for k in ['causal_test','actual_method','preservation','authority']},
        evidence={'image':bind(root,'evidence.jpg')})
    return ch


def test_failed_trial_must_be_evaluated_before_next_remedy(setup):
    root,c,b=start386(setup);observed(root,c,'first',regressed=True)
    c.retrospective('t','admit',dict(key='appearance',challenge=reply386(root,c,'1')),'admit1')
    observed(root,c,'trial1',status='FAIL')
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'
    ch=reply386(root,c,'2')
    with pytest.raises(wf.Blocked,match='PRIOR_INTERVENTION_UNEVALUATED'):
        c.retrospective('t','admit',dict(key='appearance',challenge=ch),'admit2')
    c.retrospective('t','evaluate',dict(key='appearance',evaluation=dict(admission_event='admit1',result='ineffective',
        outcome_event='trial1',observation='Target failed',evidence={'image':bind(root,'evidence.jpg')})),'effect1')
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'
    c.retrospective('t','admit',dict(key='appearance',challenge=ch),'admit2')
    p=c.retrospective_packet('t');assert set(p['pending_effects386'])=={'admit2'}


def test_wrong_outcome_or_fake_effect_cannot_close_failure(setup):
    root,c,b=start386(setup);observed(root,c,'bad',regressed=True)
    c.retrospective('t','admit',dict(key='appearance',challenge=reply386(root,c,'1')),'admit1')
    observed(root,c,'failed',status='FAIL')
    for result,oid in [('effective','failed'),('ineffective','bad')]:
        with pytest.raises(wf.Blocked):
            c.retrospective('t','evaluate',dict(key='appearance',evaluation=dict(admission_event='admit1',result=result,
                outcome_event=oid,observation='Synthetic invalid claim',evidence={'image':bind(root,'evidence.jpg')})),'wrong'+result)


def test_inconclusive_failed_trial_disposition_does_not_close_art(setup):
    root,c,b=start386(setup);observed(root,c,'bad',regressed=True)
    c.retrospective('t','admit',dict(key='appearance',challenge=reply386(root,c,'1')),'admit1')
    observed(root,c,'uncertain',status='UNKNOWN')
    c.retrospective('t','evaluate',dict(key='appearance',evaluation=dict(admission_event='admit1',result='inconclusive',
        outcome_event='uncertain',observation='Evidence insufficient',evidence={'image':bind(root,'evidence.jpg')})),'effect')
    assert c.retrospective_packet('t')['gates']['appearance']['status']=='OPEN'


def reviewed386(b):
    r=reviewed(b);v=r['unit_review'];v['pose_views']={cell:deepcopy(v['criteria']['appearance']) for cell in u.appearance_cells(b['work_unit'])}
    v['cycle_disposition']=dict(category='scoped_image_proof_pass',hypothesis_result='effective',observation='Synthetic result only')
    v['dependency_checks']={'action':dict(status='PASS',observation='Unchanged source',changed_interfaces=[],evidence=['frame'])}
    return r


def test_changed_boundary_requires_revalidation(setup):
    b=brief386(setup);r=reviewed386(b);r['unit_review']['dependency_checks']['action']['changed_interfaces']=['fixed action']
    with pytest.raises(wf.Blocked,match='CHANGED_INTERFACE'):u.review(b,r,{'frame':{}})


def test_failed_appearance_cannot_be_reported_as_effective(setup):
    b=brief386(setup);r=reviewed386(b);r['unit_review']['largest_remaining_mismatch']['blocking']=True
    with pytest.raises(wf.Blocked,match='FAILED_CANNOT_PASS'):u.review(b,r,{'frame':{}})


def test_semantic_false_pass_still_explicit(setup):
    b=brief386(setup);b['work_unit']['primary_outcome']='Implausibly claim all anatomy and costume are perfect'
    u.validate(b)
    assert u.review(b,reviewed386(b),{'frame':{}})==([],[])
    # These are knowingly fabricated synthetic judgments. Metadata cannot see art.


def test_early_native_rejection_has_disposition_without_whole_clip(setup):
    unit=brief386(setup)['work_unit'];bad=dict(verdict='FAIL',open_defects=['web'])
    with pytest.raises(wf.Blocked,match='NATIVE_DISPOSITION'):u.component_disposition(unit,bad)
    bad['cycle_disposition']=dict(category='art_rejected',observation='Actual worst view fails')
    u.component_disposition(unit,bad)
    bad['cycle_disposition']['category']='scoped_image_proof_pass'
    with pytest.raises(wf.Blocked,match='FAILURE_CANNOT_PASS'):u.component_disposition(unit,bad)


def test_superseded_donor_scope_is_history_not_anatomy_pass(setup):
    root,c,b=start386(setup);observed(root,c,'oldscope',req='__old_donor__',status='UNKNOWN')
    decision=dict(decision='supersede_requirement_scope',task='t',keys=['__old_donor__'],director_reply='Return to previous horse',
        director_source=bind(root,'authority.md'),reason='Director abandons donor, current anatomy remains required')
    (root/'scope.json').write_text(json.dumps(decision))
    c.retrospective('t','supersede_scope',dict(key='__old_donor__',decision=bind(root,'scope.json'),reason=decision['reason']),'retire')
    assert c.retrospective_packet('t')['gates']['__old_donor__']['status']=='SUPERSEDED_SCOPE'
    observed(root,c,'actual',req='appearance',status='UNKNOWN')
    with pytest.raises(wf.Blocked,match='CURRENT_REQUIREMENT'):
        c.retrospective('t','supersede_scope',dict(key='appearance',decision=bind(root,'scope.json'),reason=decision['reason']),'hide-art')
