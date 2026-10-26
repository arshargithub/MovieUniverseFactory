"""Offline policy fixtures. PASS fixtures do not certify artistic judgment."""
import copy
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from movie_factory import production_workflow as wf
from movie_factory import production_knowledge as pk
import expert_fixtures as ef
import planning_fixtures as pf


def bind(root, name):
    return {'path': name, 'sha256': pk.file_hash(root / name)}


def make_brief(root):
    ref = {'id': 'rear', 'role': 'faithful_motion', 'binding': bind(root, 'reference.mov'),
           'authority': 'Synthetic Director fidelity choice', 'scope': 'Whole body poses',
           'fidelity': 'Faithful coupled gather, crest and landing',
           'allowed_variation': 'Camera and character identity',
           'not_authority': 'No copying background or inferring measured forces',
           'time_range_seconds': [14, 19],
           'aspects': [{'id': 'poses', 'instruction': 'Compare whole pose family', 'requirements': ['appearance']}]}
    return ef.attach({'schema': 1, 'route': 'production', 'intent': 'Synthetic offline proof',
            'audience_result': 'Convincing weight', 'strategy': 'Representative pose proof',
            'early_proof': 'Reject failed silhouette', 'scope': 'Synthetic', 'exclusions': 'Live execution',
            'open_decisions': [], 'offline_only': True, 'protected': ['accepted master'],
            'source_bindings': {'task': bind(root, 'task.json')}, 'knowledge_task': 'task.json',
            'knowledge_digest': 'knowledge-v1',
            'knowledge_mapping': {'rule': {'requirements': ['appearance'], 'reason': 'Synthetic obligation'}},
            'requirements': [
                {'id': 'appearance', 'criterion': 'Convincing forms at intended framing', 'modes': ['image'], 'director_av': False},
                {'id': 'temporal', 'criterion': 'Full-speed fluidity', 'modes': ['direct_motion'], 'director_av': True}],
            'capabilities': {m: m not in {'direct_audio', 'direct_motion'} for m in wf.rc.MODES},
            'references': [ref],
            'reference_plan': {'rear': {'reference_digest': pk.digest(ref), 'application': 'Reconstruct whole poses'}}})


@pytest.fixture
def setup(tmp_path, monkeypatch):
    for name in ('reference.mov', 'candidate.bin', 'evidence.jpg', 'authority.md'):
        (tmp_path / name).write_text('SYNTHETIC ' + name)
    (tmp_path / 'task.json').write_text('{}')
    fresh = {'dispatch_ready': True, 'packet_digest': 'knowledge-v1', 'obligations': [{'id': 'rule'}]}
    monkeypatch.setattr(pk, 'task_packet', lambda root, task: copy.deepcopy(fresh))
    controller = wf.Controller(tmp_path, 'state.sqlite3')
    return tmp_path, controller, make_brief(tmp_path), fresh


def start(setup, task='t', limit=2):
    root, c, brief, _ = setup
    c.create(task, 'production', bind(root, 'authority.md'), task + '-create', limit, direction(brief, task))
    submit(c, task, brief, task + '-plan')
    return c


def direction(brief, task='t'):
    return {**{k: brief[k] for k in ('intent', 'references', 'protected')}, 'deliverable_id': task + '-deliverable',
            **pf.direction_fields(brief),
            'beat_intents': brief['expert_plan']['beat_intents']}


def submit(c, task, result, event):
    if 'expert_plan' in result and c.state(task)['stage'] == 'BRIEFING':
        return pf.complete(c, task, result, event)
    packet = c.packet(task)
    return c.submit(task, packet['actor'], packet['ticket'], result, event)


def build(root, c, task='t', event='build'):
    packet = c.packet(task)
    result = {'fingerprint': packet['fingerprint'],
              'requirement_uses': ef.uses(packet['brief']),
              'reference_uses': {r['id']: {'reference_digest': pk.digest(r), 'application': 'Used full pose mapping'} for r in packet['brief']['references']},
              'candidate': {'version': event, 'artifacts': {'clip': bind(root, 'candidate.bin')}}}
    if 'reference_readiness' in packet['brief']:
        from reference_fixtures378 import application
        result['reference_application']=application(packet['brief']['reference_readiness'])
    submit(c, task, result, task + '-' + event)
    return result


def review(root, c, task='t', status='PASS'):
    packet = c.packet(task)
    candidate = pk.digest(packet['candidate'])
    ref = packet['brief']['references'][0]
    return {'fingerprint': packet['fingerprint'], 'candidate_digest': candidate,
            'intent_checks': ef.intent_checks(packet['brief'], 'FAIL' if status == 'FAIL' else 'PASS'), 'planning_gaps': [],
            'checks': [
                {'id': 'appearance', 'status': status, 'observation': 'Synthetic whole-form observation', 'comparison': 'Compared reference silhouette', 'evidence': ['frame']},
                {'id': 'temporal', 'status': 'NOT_RUN', 'observation': 'Director playback pending', 'comparison': 'No direct motion capability', 'evidence': []}],
            'evidence': {'frame': {'binding': bind(root, 'evidence.jpg'), 'mode': 'image', 'scope': 'Whole actor', 'candidate_digest': candidate}},
            'reference_checks': {'rear': {'reference_digest': pk.digest(ref), 'observation': 'Compared whole poses',
                                        'comparison': 'Reference is motion authority, not identity', 'evidence': ['frame'],
                                        'aspects': [{'id': 'poses', 'status': status, 'observation': 'Synthetic comparison'}]}},
            'audience_read': 'Synthetic weight read', 'strongest_counterexample': 'Timing still needs playback',
            'adjacent_review': 'Synthetic support check', 'open_visible_defects': []}


def test_full_path_and_pending_human_is_not_production(setup):
    root, c, _, _ = setup; start(setup)
    build(root, c)
    state = submit(c, 't', review(root, c), 'review')
    assert state['stage'] == 'READY_FOR_DIRECTOR_AV'
    receipt = c.deliver('t', 'deliver')['receipt']
    assert not receipt['production_approved'] and not receipt['director_approved']
    assert receipt['offline_replay_only']
    assert [e['stage'] for e in c.events('t')] == ['BRIEFING'] * 4 + ['EXECUTING', 'REVIEWING', 'READY_FOR_DIRECTOR_AV', 'READY_FOR_DIRECTOR_AV']


def test_n_two_survives_restart_and_replan(setup):
    root, c, brief, _ = setup; start(setup)
    for i in range(3):
        build(root, c, event=f'build{i}')
        state = submit(c, 't', review(root, c, status='FAIL'), f'review{i}')
        c = wf.Controller(root, 'state.sqlite3')
    assert state['stage'] == 'REPLAN_REQUIRED' and state['cycle'] == 2
    c.revise('t', brief, bind(root, 'authority.md'), 'Replan without counter reset', 'replan')
    assert c.state('t')['stage'] == 'REPLAN_REQUIRED'
    with pytest.raises(wf.Blocked): c.packet('t')
    with pytest.raises(wf.Blocked): c.deliver('t', 'deliver')


@pytest.mark.parametrize('stage', ['BRIEFING', 'EXECUTING', 'REVIEWING'])
def test_stage_skip_cannot_deliver(setup, stage):
    root, c, brief, _ = setup
    c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=direction(brief))
    if stage != 'BRIEFING': submit(c, 't', brief, 'plan')
    if stage == 'REVIEWING': build(root, c)
    with pytest.raises(wf.Blocked, match='NOT_READY'): c.deliver('t', 'deliver')


@pytest.mark.parametrize('field', ['role', 'scope', 'fidelity', 'allowed_variation', 'not_authority', 'authority', 'time_range_seconds', 'aspects'])
def test_reference_semantics_required_in_brief(setup, field):
    _, _, b, _ = setup
    del b['references'][0][field]
    with pytest.raises((wf.Blocked, KeyError)): wf.validate_brief(setup[0], b, 'production')


@pytest.mark.parametrize('stage', ['planner', 'builder', 'reviewer'])
def test_reference_contract_required_every_stage(setup, stage):
    root, c, brief, _ = setup
    if stage == 'planner':
        c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=direction(brief))
        brief['reference_plan'] = {}
        with pytest.raises(wf.Blocked, match='REFERENCE'): submit(c, 't', brief, 'plan')
    else:
        start(setup)
        if stage == 'builder':
            p = c.packet('t')
            result = {'fingerprint': p['fingerprint'], 'reference_uses': {}, 'candidate': {}, 'requirement_uses': ef.uses(p['brief'])}
        else:
            build(root, c); result = review(root, c); result['reference_checks'] = {}
        with pytest.raises(wf.Blocked, match='REFERENCE'): submit(c, 't', result, 'bad')


@pytest.mark.parametrize('mutation', ['mode', 'candidate', 'fingerprint', 'reference_digest', 'missing_aspect', 'human_pass', 'missing_check', 'missing_evidence', 'counterexample'])
def test_invalid_review_rejected_without_transition(setup, mutation):
    root, c, _, _ = setup; start(setup); build(root, c); r = review(root, c)
    if mutation == 'mode': r['evidence']['frame']['mode'] = 'direct_motion'
    if mutation == 'candidate': r['candidate_digest'] = 'wrong'
    if mutation == 'fingerprint': r['fingerprint'] = 'old'
    if mutation == 'reference_digest': r['reference_checks']['rear']['reference_digest'] = 'old'
    if mutation == 'missing_aspect': r['reference_checks']['rear']['aspects'] = []
    if mutation == 'human_pass': r['checks'][1]['status'] = 'PASS'
    if mutation == 'missing_check': r['checks'].pop()
    if mutation == 'missing_evidence': r['checks'][0]['evidence'] = []
    if mutation == 'counterexample': r['strongest_counterexample'] = ''
    with pytest.raises(wf.Blocked): submit(c, 't', r, 'invalid')
    assert c.state('t')['stage'] == 'REVIEWING'


def test_visible_defect_cannot_hide_in_human_queue(setup):
    root, c, _, _ = setup; start(setup); build(root, c); r = review(root, c)
    r['open_visible_defects'] = ['shell-like clothing']
    state = submit(c, 't', r, 'reject')
    assert state['stage'] == 'EXECUTING' and state['cycle'] == 1
    assert 'visible:shell-like clothing' in state['findings']['failures']


def test_reference_failure_vetoes_generic_pass(setup):
    root, c, _, _ = setup; start(setup); build(root, c); r = review(root, c)
    r['reference_checks']['rear']['aspects'][0]['status'] = 'FAIL'
    assert submit(c, 't', r, 'reject')['stage'] == 'EXECUTING'


def test_evidence_collection_does_not_spend_artistic_cycles_and_is_bounded(setup):
    root, c, _, _ = setup; start(setup); build(root, c)
    for i in range(3):
        r = review(root, c, status='NOT_RUN')
        state = submit(c, 't', r, 'missing' + str(i))
    assert state['stage'] == 'BLOCKED' and state['cycle'] == 0


@pytest.mark.parametrize('file', ['reference.mov', 'candidate.bin', 'evidence.jpg', 'task.json', 'authority.md'])
def test_stale_bytes_block_delivery_including_idempotent_retry(setup, file):
    root, c, _, _ = setup; start(setup); build(root, c)
    submit(c, 't', review(root, c), 'review'); c.deliver('t', 'deliver')
    (root / file).write_text('CHANGED')
    for eid in ('deliver', 'new-deliver'):
        with pytest.raises((wf.Blocked, wf.rc.Blocked)): c.deliver('t', eid)


def test_revised_reference_role_invalidates_old_ticket_review(setup):
    root, c, brief, _ = setup; start(setup); build(root, c)
    p = c.packet('t'); r = review(root, c)
    brief['references'][0]['role'] = 'directional_design'
    brief['reference_plan']['rear']['reference_digest'] = pk.digest(brief['references'][0])
    brief['expert_plan']['challenge']['plan_digest'] = ef.ep.plan_digest(brief)
    c.revise('t', brief, bind(root, 'authority.md'), 'Synthetic explicit Director revision', 'revise')
    with pytest.raises(wf.Blocked, match='WRONG_STAGE'): c.submit('t', 'reviewer', p['ticket'], r, 'old-review')
    assert c.packet('t')['direction']['references'][0]['role'] == 'directional_design'
    assert c.packet('t')['planning_step'] == 'GROUNDING'
    pf.complete(c, 't', brief, 'revised-plan')
    assert c.packet('t')['brief']['references'][0]['role'] == 'directional_design'


def test_actor_and_ticket_separation(setup):
    _, c, brief, _ = setup; start(setup); p = c.packet('t')
    with pytest.raises(wf.Blocked): c.submit('t', 'planner', p['ticket'], brief, 'bad-role')
    with pytest.raises(wf.Blocked): c.submit('t', 'builder', 'wrong', {}, 'bad-ticket')
    assert 'ticket' not in c.state('t') and 'ticket' not in str(c.events('t'))


def test_reviewer_packet_has_no_builder_success_narrative(setup):
    root, c, _, _ = setup; start(setup); build(root, c)
    p = c.packet('t')
    assert 'builder_record' not in p and 'reference_uses' not in p
    assert 'references' in p['brief'] and p['candidate']


def test_idempotence_conflict_and_append_only(setup):
    root, c, brief, _ = setup; start(setup)
    before = len(c.events('t'))
    c.create('t', 'production', bind(root, 'authority.md'), 't-create', 2, direction(brief))
    assert len(c.events('t')) == before
    with pytest.raises(wf.Blocked): c.create('t', 'production', bind(root, 'authority.md'), 't-create', 3, direction(brief))
    with c.connect() as con:
        with pytest.raises(sqlite3.IntegrityError): con.execute('DELETE FROM events')


def test_global_heavy_lease_recovery_and_no_redispatch(setup):
    root, c, _, _ = setup; start(setup, 'a'); start(setup, 'b')
    c.job('a', 'render1', 'acquire', 'acquire')
    c = wf.Controller(root, 'state.sqlite3')
    with pytest.raises(wf.Blocked, match='BUSY'): c.job('b', 'render2', 'acquire', 'acquire-b')
    with pytest.raises(wf.Blocked, match='OWNER'): c.job('b', 'render1', 'release', 'bad-release')
    with pytest.raises(wf.Blocked, match='JOB_STILL'): build(root, c, 'a')
    c.job('a', 'render1', 'release', 'release')
    with pytest.raises(wf.Blocked, match='DUPLICATE'): c.job('a', 'render1', 'acquire', 'retry')
    c.job('b', 'render2', 'acquire', 'acquire-b')


def test_competing_process_connections_one_lease(setup):
    root, c, _, _ = setup; start(setup, 'a'); start(setup, 'b')
    def acquire(name):
        try: wf.Controller(root, 'state.sqlite3').job(name, name, 'acquire', 'job-' + name); return True
        except wf.Blocked: return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(acquire, ['a', 'b'])) == [False, True]


@pytest.mark.parametrize('route', ['show', 'research', 'plan', 'operations'])
def test_lightweight_routes_no_production_ceremony(setup, route):
    root, c, _, _ = setup
    c.create(route, route, bind(root, 'authority.md'), 'create-' + route)
    with pytest.raises(wf.Blocked): c.packet(route)
    c.complete_lightweight(route, {'offline_only': True, 'verification': 'Fixture verification only',
                                 'artifacts': {'result': bind(root, 'evidence.jpg')}}, 'complete-' + route)
    assert c.deliver(route, 'deliver-' + route)['receipt']['offline_replay_only']


def test_unknown_live_unauthorized_or_unmapped_brief_blocks(setup):
    root, _, brief, fresh = setup
    for key, value in [('offline_only', False), ('open_decisions', ['new identity']), ('knowledge_mapping', {})]:
        bad = copy.deepcopy(brief); bad[key] = value
        with pytest.raises(wf.Blocked): wf.validate_brief(root, bad, 'production')
    fresh['dispatch_ready'] = False
    with pytest.raises(wf.Blocked): wf.validate_brief(root, brief, 'production')


def test_visible_check_cannot_be_reclassified_as_director_av(setup):
    root, _, brief, _ = setup; brief['requirements'][0]['director_av'] = True
    with pytest.raises(wf.Blocked, match='VISIBLE_FAILURE'): wf.validate_brief(root, brief, 'production')


def test_planning_receives_and_cannot_downgrade_director_reference(setup):
    root, c, brief, _ = setup
    c.create('t', 'production', bind(root, 'authority.md'), 'create', direction=direction(brief))
    assert c.packet('t')['direction']['references'][0]['role'] == 'faithful_motion'
    changed = copy.deepcopy(brief)
    changed['references'][0]['role'] = 'directional_design'
    changed['reference_plan']['rear']['reference_digest'] = pk.digest(changed['references'][0])
    with pytest.raises(wf.Blocked, match='STRATEGY_AUTHORITY_CHANGED'): submit(c, 't', changed, 'downgrade')


def test_known_rejected_exact_candidate_vetoes_well_formed_false_pass(setup):
    root, c, brief, _ = setup
    brief['references'][0].update(role='negative_control', binding=bind(root, 'candidate.bin'))
    brief['reference_plan']['rear']['reference_digest'] = pk.digest(brief['references'][0])
    brief['expert_plan']['challenge']['plan_digest'] = ef.ep.plan_digest(brief)
    start(setup); build(root, c)
    result = submit(c, 't', review(root, c), 'false-positive')
    assert 'KNOWN_REJECTED_ARTIFACT:rear' in result['findings']['failures']
    assert result['stage'] == 'EXECUTING'


def test_directional_image_requires_traits_not_pixel_reconstruction(setup):
    root, c, brief, _ = setup
    ref = brief['references'][0]
    ref.update(role='directional_design', fidelity='Rugged elongated face and broad natural beard',
               allowed_variation='Coherent native proportions and unseen geometry',
               not_authority='Literal pixels, background and generated cloth topology')
    brief['reference_plan']['rear']['reference_digest'] = pk.digest(ref)
    brief['expert_plan']['challenge']['plan_digest'] = ef.ep.plan_digest(brief)
    start(setup); build(root, c)
    assert c.packet('t')['brief']['references'][0] == ref
    assert submit(c, 't', review(root, c), 'review')['stage'] == 'READY_FOR_DIRECTOR_AV'


def test_unrecognised_candidate_false_observation_is_not_semantically_detected(setup):
    # Important limit: declarations can be false. No perceptual oracle is claimed.
    root, c, _, _ = setup; start(setup); build(root, c)
    r = review(root, c)
    r['checks'][0]['observation'] = 'Intentionally unverified but well-formed claim'
    assert submit(c, 't', r, 'false-claim-control')['stage'] == 'READY_FOR_DIRECTOR_AV'


def test_references_missing_before_planning_block(setup):
    root, c, _, _ = setup
    with pytest.raises(wf.Blocked, match='DIRECTOR_CONTEXT'): c.create('t', 'production', bind(root, 'authority.md'), 'create')


def test_renaming_task_cannot_reset_deliverable_budget(setup):
    root, c, brief, _ = setup; start(setup)
    with pytest.raises(wf.Blocked, match='DELIVERABLE_ALREADY_TRACKED'):
        c.create('renamed-pass', 'production', bind(root, 'authority.md'), 'renamed', 2, direction(brief))


@pytest.mark.parametrize('interval', [[0, float('inf')], [0, float('nan')], [-1, 5], [5, 2]])
def test_invalid_motion_ranges_block(setup, interval):
    root, _, brief, _ = setup; brief['references'][0]['time_range_seconds'] = interval
    with pytest.raises(wf.Blocked): wf.validate_brief(root, brief, 'production')


def test_reference_temporal_aspect_requires_director_not_static_pass(setup):
    root, c, brief, _ = setup
    brief['references'][0]['aspects'].append({'id': 'rhythm', 'instruction': 'Compare full-speed rhythm', 'requirements': ['temporal']})
    brief['reference_plan']['rear']['reference_digest'] = pk.digest(brief['references'][0])
    brief['expert_plan']['challenge']['plan_digest'] = ef.ep.plan_digest(brief)
    start(setup); build(root, c)
    r = review(root, c)
    r['reference_checks']['rear']['aspects'].append({'id': 'rhythm', 'status': 'PASS', 'observation': 'Not supported by images'})
    with pytest.raises(wf.Blocked, match='REFERENCE_AV'): submit(c, 't', r, 'false-motion')
    r['reference_checks']['rear']['aspects'][1]['status'] = 'NOT_RUN'
    result = submit(c, 't', r, 'pending-motion')
    assert result['stage'] == 'READY_FOR_DIRECTOR_AV'
    assert 'reference:rear:rhythm' in result['findings']['pending_director_av']


def test_reference_aspect_cannot_mix_visible_and_human_owners(setup):
    root, _, brief, _ = setup
    brief['references'][0]['aspects'][0]['requirements'].append('temporal')
    with pytest.raises(wf.Blocked, match='MIXED_OWNERS'): wf.validate_brief(root, brief, 'production')
