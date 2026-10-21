"""Deterministic contracts, including explicit semantic limits; no live calls."""
import copy
import json
import pytest
from movie_factory import planning_pipeline as pp
from movie_factory import production_workflow as wf
from movie_factory import staged_runner as sr
from test_production_workflow import setup, direction, bind, build, review, submit
import planning_fixtures as pf


def at(setup, step='GROUNDING', limit=2):
    root, c, b, _ = setup
    c.create('t', 'production', bind(root, 'authority.md'), 'create', limit, direction(b))
    for s in pp.STEPS:
        if s == step: break
        p = c.packet('t'); c.submit('t', p['actor'], p['ticket'], pf.result(p, b), s)
    return c.packet('t')


def send(c, p, result, eid='test'):
    return c.submit('t', p['actor'], p['ticket'], result, eid)


@pytest.mark.parametrize('step', pp.STEPS)
def test_restart_exact_inputs_and_idempotence_at_every_substage(setup, step):
    root, c, b, _ = setup; p = at(setup, step); r = pf.result(p, b)
    before = c.state('t')
    reopened = wf.Controller(root, 'state.sqlite3')
    assert reopened.packet('t') == p
    state = send(reopened, p, r)
    assert send(reopened, p, r) == state
    assert len(c.events('t')) == len(pp.STEPS[:pp.STEPS.index(step)]) + 2
    r['input_digest'] = 'tampered'
    with pytest.raises(wf.Blocked): send(reopened, p, r)
    assert before['cycle'] == state['cycle'] == 0


@pytest.mark.parametrize('step', pp.STEPS)
@pytest.mark.parametrize('change', ['digest', 'actor', 'skip'])
def test_cannot_skip_or_reuse_stage_authority(setup, step, change):
    _, c, b, _ = setup; p = at(setup, step); r = pf.result(p, b)
    if change == 'digest': r['input_digest'] = 'previous'
    if change == 'actor': p['actor'] = 'builder'
    if change == 'skip': r = {'input_digest': p['planning_input_digest'], 'outcome': 'admit', 'issues': []}
    with pytest.raises((ValueError, KeyError)): send(c, p, r)
    assert c.state('t')['planning_step'] == step


@pytest.mark.parametrize('mutation', ['missing_domain', 'unknown_status', 'no_scope', 'sensitive', 'unbound_task'])
def test_context_admission(setup, mutation):
    root, c, b, _ = setup; d = direction(b)
    if mutation == 'missing_domain': d['context_sources'].pop()
    if mutation == 'unknown_status': d['context_sources'][0]['status'] = 'accepted_because_model_says_so'
    if mutation == 'no_scope': d['context_sources'][0]['scope'] = ''
    if mutation == 'sensitive': d['context_sources'][0]['binding']['path'] = '.env'
    if mutation == 'unbound_task': d['knowledge_task'] = 'other.json'
    with pytest.raises(ValueError): c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=d)
    assert c.events('t') == []


@pytest.mark.parametrize('mutation', ['source', 'learning', 'required', 'unresolved', 'implication'])
def test_grounding_cannot_be_empty_summary(setup, mutation):
    _, c, b, _ = setup; p = at(setup); r = pf.result(p, b); a = r['artifact']
    if mutation == 'source': del a['uses']['film_language']
    if mutation == 'learning': a['knowledge_uses'] = {}
    if mutation == 'required': a['uses']['director_preferences']['disposition'] = 'context_only'
    if mutation == 'unresolved': a['unresolved'] = ['Does the chosen reference still apply?']
    if mutation == 'implication': a['uses']['direction']['implication'] = ''
    with pytest.raises(wf.Blocked): send(c, p, r)


@pytest.mark.parametrize('mutation', ['lens', 'learning', 'preference', 'context', 'reverse', 'orphan'])
def test_derivation_must_apply_not_name(setup, mutation):
    _, c, b, _ = setup; p = at(setup, 'DERIVING'); r = pf.result(p, b); a = r['artifact']
    if mutation == 'lens': del a['beats'][0]['lenses']['camera_editorial']
    if mutation == 'learning': a['knowledge_mapping']['rule']['requirements'] = []
    if mutation == 'preference': a['context_mapping']['director_preferences']['requirements'] = []
    if mutation == 'context': a['context_mapping']['learnings']['reason'] = ''
    if mutation == 'reverse': a['derivations']['appearance']['lenses'].append('sound_music')
    if mutation == 'orphan': a['requirements'].append({'id': 'orphan'})
    with pytest.raises(wf.Blocked): send(c, p, r)


@pytest.mark.parametrize('mutation', ['intent', 'reference', 'requirement', 'source', 'method', 'proof_order', 'cycle', 'unproved'])
def test_strategy_preserves_contract_and_progressive_commitment(setup, mutation):
    _, c, b, _ = setup; p = at(setup, 'STRATEGIZING'); r = pf.result(p, b); a = r['artifact']
    if mutation == 'intent': a['brief']['intent'] = 'A different movie'
    if mutation == 'reference': a['brief']['references'][0]['role'] = 'directional_design'
    if mutation == 'requirement': a['brief']['requirements'][0]['criterion'] = 'Only incremental improvement'
    if mutation == 'source': a['brief']['source_bindings'] = {}
    if mutation == 'method': a['method_choice']['discriminating_test'] = ''
    if mutation == 'proof_order': a['steps'].reverse()
    if mutation == 'cycle': a['steps'][0]['depends_on'] = ['build']
    if mutation == 'unproved': a['steps'][1]['depends_on'] = []
    with pytest.raises(wf.Blocked): send(c, p, r)


@pytest.mark.parametrize('mutation', ['facet', 'evidence', 'failure', 'pending', 'issue'])
def test_challenge_is_a_gate_not_signature(setup, mutation):
    _, c, b, _ = setup; p = at(setup, 'CHALLENGING'); r = pf.result(p, b)
    if mutation == 'facet': del r['checks']['method']
    if mutation == 'evidence': r['checks']['method']['source_ids'] = ['invented']
    if mutation == 'failure': r['checks']['method']['status'] = 'FAIL'
    if mutation == 'pending': r['checks']['method']['status'] = 'NOT_RUN'
    if mutation == 'issue': r['issues'] = [{'id': 'a', 'target': 'STRATEGIZING', 'reason': 'Wrong method', 'counterexample': 'Known failed', 'repair': 'New proof'}]
    with pytest.raises(wf.Blocked): send(c, p, r)


@pytest.mark.parametrize('target', pp.STEPS[:3])
def test_targeted_repair_invalidates_only_downstream_and_conserves_limits(setup, target):
    root, c, b, _ = setup; p = at(setup, 'CHALLENGING'); before = c.state('t')
    r = pf.result(p, b); r['outcome'] = 'revise'; r['checks']['method']['status'] = 'FAIL'
    r['issues'] = [{'id': 'known-failure', 'target': target, 'reason': 'Method lacks support',
                    'counterexample': '321 had requirements but wrong pose strategy', 'repair': 'Reconstruct supported pose first'}]
    state = send(c, p, r)
    assert state['stage'] == 'BRIEFING' and state['planning_step'] == target and state['cycle'] == 1
    assert state['planning_artifacts'] == {s: before['planning_artifacts'][s] for s in pp.STEPS[:pp.STEPS.index(target)]}
    assert 'brief' not in state and 'candidate' not in state
    pf.complete(c, 't', b, 'repair')
    assert c.replan('t', 'STRATEGIZING', 'Second in-scope repair', 'again')['cycle'] == 2
    pf.complete(c, 't', b, 'repair2')
    assert c.replan('t', 'STRATEGIZING', 'Still failing', 'exhausted')['stage'] == 'REPLAN_REQUIRED'
    with pytest.raises(wf.Blocked): c.packet('t')
    assert c.state('t')['max_corrections'] == 2
    with pytest.raises(wf.Blocked, match='DELIVERABLE_ALREADY_TRACKED'):
        c.create('renamed', 'production', bind(root, 'authority.md'), 'rename', direction=direction(b))


def test_material_decisions_only(setup):
    _, c, b, _ = setup; p = at(setup)
    r = {'input_digest': p['planning_input_digest'], 'outcome': 'needs_director',
         'decision': {'category': 'algorithm', 'reason': 'Select interpolation', 'recommendation': 'A',
                      'options': [{'option': 'A', 'consequence': 'Technical'}, {'option': 'B', 'consequence': 'Technical'}]}}
    with pytest.raises(wf.Blocked, match='NOT_DIRECTOR'): send(c, p, r)
    r['decision']['category'] = 'style'
    r['decision']['reason'] = 'Required new look changes accepted identity'
    assert send(c, p, r)['stage'] == 'DIRECTOR_DECISION'
    with pytest.raises(wf.Blocked): c.replan('t', 'GROUNDING', 'Ignore decision', 'bypass')


def test_sources_actual_excerpts_deduplicated_and_challenge_unbiased(setup):
    _, c, _, _ = setup; p = at(setup, 'CHALLENGING')
    assert len(p['source_context']['documents']) == 1
    assert next(iter(p['source_context']['documents'].values()))['text'] == '{}'
    assert p['grounding_knowledge']['obligations'] == [{'id': 'rule'}]
    assert 'challenge' not in p['planning_inputs']['STRATEGIZING']['brief']['expert_plan']
    assert 'challenge' in c.state('t')['planning_artifacts']['STRATEGIZING']['brief']['expert_plan']
    assert p['direction']['references'][0]['role'] == 'faithful_motion'


def test_execution_and_review_keep_original_source_evidence(setup):
    root, c, b, _ = setup; p = at(setup, 'CHALLENGING')
    send(c, p, pf.result(p, b))
    assert c.packet('t')['source_context'] == p['source_context']
    build(root, c)
    assert c.packet('t')['source_context'] == p['source_context']
    assert c.packet('t')['grounding_knowledge'] == p['grounding_knowledge']
    assert 'builder_record' not in c.packet('t')


def test_overflow_requires_explicit_excerpt_not_truncation(setup):
    root, c, b, _ = setup
    (root / 'large.md').write_text('x'*12001 + '\nselected line\n')
    d = direction(b); d['context_sources'][0]['binding'] = bind(root, 'large.md')
    with pytest.raises(wf.Blocked, match='SELECT_EXCERPT'):
        c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=d)
    d['context_sources'][0]['lines'] = [2, 2]
    c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=d)
    assert any(doc['text'] == 'selected line' for doc in c.packet('t')['source_context']['documents'].values())


def test_stale_sources_and_engine_require_reviewed_rebase(setup, monkeypatch):
    root, c, b, _ = setup; at(setup, 'DERIVING'); original = c.state('t')['direction']
    (root / 'task.json').write_text('{"updated":true}')
    with pytest.raises(ValueError): c.packet('t')
    sources = copy.deepcopy(original['context_sources'])
    for s in sources: s['binding'] = bind(root, 'task.json')
    state = c.reground('t', sources, 'task.json', 'knowledge-v1', 'Reviewed fixture source change', 'reground')
    assert state['planning_step'] == 'GROUNDING' and state['cycle'] == 1
    assert state['direction']['references'] == original['references']
    monkeypatch.setattr(pp, 'engine_digest', lambda: 'changed-engine')
    with pytest.raises(wf.Blocked, match='ENGINE_CHANGED'): c.packet('t')


def test_reground_cannot_promote_hypothesis_to_authority(setup):
    _, c, _, _ = setup; at(setup)
    d = c.state('t')['direction']; sources = copy.deepcopy(d['context_sources'])
    sources[0]['status'] = 'hypothesis'
    with pytest.raises(wf.Blocked, match='AUTHORITY_CHANGED'):
        c.reground('t', sources, d['knowledge_task'], d['knowledge_digest'], 'Change status', 'bad')
    assert c.state('t')['cycle'] == 0


def test_reviewed_revision_preserves_evidence_and_deduplicates_bindings(setup):
    root, c, b, _ = setup; at(setup)
    b['source_bindings']['alias'] = copy.deepcopy(b['source_bindings']['task'])
    c.revise('t', b, bind(root, 'authority.md'), 'Explicit scoped revision', 'revision')
    p = c.packet('t')
    assert p['direction_revision']['reason'] == 'Explicit scoped revision'
    assert next(iter(p['direction_revision']['source_context']['documents'].values()))['text'] == 'SYNTHETIC authority.md'


def test_transitive_proof_dependencies_allowed(setup):
    _, c, b, _ = setup; p = at(setup, 'STRATEGIZING'); r = pf.result(p, b)
    step = copy.deepcopy(r['artifact']['steps'][1]); step.update(id='polish', depends_on=['build'])
    r['artifact']['steps'].append(step)
    assert send(c, p, r)['planning_step'] == 'CHALLENGING'


def test_parent_seals_explicit_hash_placeholder_not_artistic_judgment(setup):
    _, c, b, _ = setup; p = at(setup, 'STRATEGIZING'); r = pf.result(p, b)
    r['artifact']['brief']['expert_plan']['challenge']['plan_digest'] = '__PARENT_COMPUTES__'
    state = send(c, p, r)
    assert state['planning_step'] == 'CHALLENGING'
    sealed = state['planning_artifacts']['STRATEGIZING']['brief']
    assert sealed['expert_plan']['challenge']['plan_digest'] == pp.ep.plan_digest(sealed)
    assert r['artifact']['brief']['expert_plan']['challenge']['plan_digest'] == '__PARENT_COMPUTES__'


def test_well_formed_wrong_method_still_requires_reasoned_challenge(setup):
    """Deliberate semantic false negative, preserved as a limitation."""
    _, c, b, _ = setup; p = at(setup, 'STRATEGIZING'); r = pf.result(p, b)
    r['artifact']['method_choice']['chosen'] = 'Keep whole horse rigid, slow down the landing'
    send(c, p, r)
    p = c.packet('t')
    # A rubber-stamp reviewer still passes. Schema is not an artistic evaluator.
    assert send(c, p, pf.result(p, b), 'rubber-stamp')['stage'] == 'EXECUTING'


def test_live_budget_not_expanded_by_offline_six_stage_tests(setup):
    _, c, _, _ = setup
    with pytest.raises(wf.Blocked, match='QUALIFICATION_CALL_CAP'):
        sr.SerialRunner(c, 'live.sqlite3', max_calls=6)
    sr.SerialRunner(c, 'offline.sqlite3', max_calls=6, offline_simulation=True)
    with pytest.raises(wf.Blocked, match='RUNNER_MODE_CHANGE'):
        sr.SerialRunner(c, 'offline.sqlite3', max_calls=4)
    proto = object.__new__(sr.CodexProtocol)
    with pytest.raises(wf.Blocked, match='SIMULATION_CANNOT'):
        proto.infer({'offline_simulation': True})
