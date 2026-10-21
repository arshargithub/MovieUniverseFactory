"""Gate tests, including an explicit semantic counterexample; not artistic tests."""
import copy
import pytest
from movie_factory import expert_planning as ep
from movie_factory import production_workflow as wf
from test_production_workflow import setup, start, build, review, submit, direction, bind


@pytest.mark.parametrize('field', ['derivation', 'method', 'interfaces', 'early_proof',
                                  'failure_condition', 'reopen_when', 'priority', 'origin', 'reference_ids'])
def test_missing_realization_is_not_an_expert_plan(setup, field):
    b = setup[2]; del b['expert_plan']['realizations']['appearance'][field]
    with pytest.raises(wf.Blocked): ep.validate(b)


@pytest.mark.parametrize('mutation', ['missing_plan', 'missing_beat', 'missing_lens', 'no_reason',
    'no_requirements', 'orphan', 'stale', 'unresolved', 'no_probe', 'no_coverage', 'reverse_link'])
def test_planning_negative_controls(setup, mutation):
    b = setup[2]; p = b['expert_plan']
    if mutation == 'missing_plan': del b['expert_plan']
    if mutation == 'missing_beat': p['beats'] = []
    if mutation == 'missing_lens': del p['beats'][0]['lenses']['camera_editorial']
    if mutation == 'no_reason': p['beats'][0]['lenses']['camera_editorial']['why'] = ''
    if mutation == 'no_requirements': p['beats'][0]['lenses']['animation_physics']['requirements'] = []
    if mutation == 'orphan': del p['realizations']['temporal']
    if mutation == 'stale': p['realizations']['appearance']['method'] = 'Changed method'
    if mutation == 'unresolved': p['challenge']['open_issues'] = ['Unresolved authority']
    if mutation == 'no_probe': p['challenge']['omission_probe'] = ''
    if mutation == 'no_coverage': p['challenge']['intent_coverage'] = {}
    if mutation == 'reverse_link': p['realizations']['appearance']['lenses'].append('sound_music')
    with pytest.raises(wf.Blocked): ep.validate(b)


def test_planner_cannot_drop_director_beat_even_with_internally_valid_plan(setup):
    root, c, b, _ = setup
    d = direction(b); d['beat_intents'] = {**d['beat_intents'], 'exit': 'Continue determinedly'}
    c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=d)
    with pytest.raises(wf.Blocked, match='DERIVATION_BEAT_COVERAGE'): submit(c, 't', b, 'bad')
    assert c.state('t')['stage'] == 'BRIEFING'


def test_contract_reaches_real_stage_packets(setup):
    root, c, b, _ = setup
    c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=direction(b))
    p = c.packet('t')
    assert p['expert_contract'] == ep.contract() and p['planning_step'] == 'GROUNDING'
    assert 'authority' in p['expert_instruction']
    submit(c, 't', b, 'plan'); build(root, c)
    assert 'planning_gaps' in c.packet('t')['expert_instruction']


@pytest.mark.parametrize('mutation', ['missing', 'stale', 'blank'])
def test_execution_cannot_lose_plan(setup, mutation):
    root, c, b, _ = setup; start(setup)
    import expert_fixtures as ef
    result = {'requirement_uses': ef.uses(b)}
    if mutation == 'missing': del result['requirement_uses']['appearance']
    if mutation == 'stale': result['requirement_uses']['appearance']['plan_digest'] = 'old'
    if mutation == 'blank': result['requirement_uses']['appearance']['application'] = ''
    with pytest.raises(wf.Blocked): submit(c, 't', result, 'bad')
    assert c.state('t')['stage'] == 'EXECUTING'


def test_original_intent_can_veto_a_passing_checklist(setup):
    root, c, _, _ = setup; start(setup); build(root, c)
    r = review(root, c); r['intent_checks']['beat']['status'] = 'FAIL'
    s = submit(c, 't', r, 'intent-fail')
    assert s['stage'] == 'EXECUTING' and 'intent:beat' in s['findings']['failures']


@pytest.mark.parametrize('field', ['intent_checks', 'planning_gaps'])
def test_review_must_revisit_intent_and_omissions(setup, field):
    root, c, _, _ = setup; start(setup); build(root, c)
    r = review(root, c); del r[field]
    with pytest.raises(wf.Blocked): submit(c, 't', r, 'bad')


def test_planning_gap_replans_without_resetting_budget_or_requesting_method_approval(setup):
    root, c, b, _ = setup; start(setup); build(root, c)
    r = review(root, c); r['planning_gaps'] = ['Camera obscures the intended route choice']
    state = submit(c, 't', r, 'gap')
    assert state['stage'] == 'BRIEFING' and state['planning_step'] == 'DERIVING'
    with pytest.raises(wf.Blocked): c.deliver('t', 'bad-delivery')
    submit(c, 't', b, 'agent-repair')
    assert c.state('t')['stage'] == 'EXECUTING' and c.state('t')['cycle'] == 1


def test_honest_semantic_limit_bad_method_with_valid_links_is_not_detected(setup):
    b = setup[2]
    b['expert_plan']['realizations']['appearance']['method'] = 'Keep the entire horse rigid like a stone statue'
    b['expert_plan']['challenge']['plan_digest'] = ep.plan_digest(b)
    assert ep.validate(b)  # This is the LIMITATION, not a successful expert judgment.


def test_intent_scope_cannot_claim_unavailable_full_av(setup):
    root, c, _, _ = setup; start(setup); build(root, c)
    r = review(root, c); r['intent_checks']['beat']['scope'] = 'full_motion_certified'
    with pytest.raises(wf.Blocked, match='INTENT_REVIEW_SCOPE'): submit(c, 't', r, 'bad')


def test_parent_seal_only_hashes_complete_reasoning(setup):
    b = setup[2]; b['expert_plan']['challenge']['plan_digest'] = 'parent computes this'
    result = ep.seal_planner_response(b)
    assert ep.validate(result)
    assert b['expert_plan']['challenge']['plan_digest'] == 'parent computes this'
    del b['expert_plan']['realizations']['appearance']['method']
    with pytest.raises(wf.Blocked): ep.seal_planner_response(b)
