"""Traceability gates, not an automatic expert or semantic-quality oracle.

The trusted parent scopes beats from Director intent. Planning must derive
requirements; review must revisit intent even when all listed checks pass.
"""
import copy
from . import production_knowledge as pk
from .production_workflow import require, nonempty, rows

LENSES = ('story_performance', 'camera_editorial', 'animation_physics',
          'anatomy_contact', 'effects_environment', 'sound_music', 'production_reuse')

PLANNER_INSTRUCTION = '''Translate the supplied beat intents and reference roles into
an expert_plan. For each beat, assess all seven lenses, justify application or
omission, and derive concrete audience-visible requirements. Link each to a
method, coupled interfaces, actual-framing early proof, observable failure and
reference authority. Distinguish inferred craft choices from Director choices;
do not invent new creative authority. Challenge causal readability, unreported
failures, conflicting disciplines and optional work before admitting the plan.
Return the complete brief, not only strategy prose. A named lens is not its
application. If a requirement cannot be supported, report the gap, do not fill
fields with assurances. For unit_required references, retain one work_unit with
positive reference criteria, allowed/frozen domains, phase boundaries and rejected
calibration controls. New local-native units use version2: scope_decision,
causal_experiment, scope_challenge and version-bound dependencies. Scope is a
judgeable outcome, not a mesh/parameter box. Split independent failures and retain
necessary coupled context. Protect accepted behavior, not rejected source poses.
No stage tools or production changes are authorized.'''

REVIEWER_INSTRUCTION = '''Review original intent and reference roles as well as the
listed requirements. Return intent_checks for every beat with actual evidence,
plus planning_gaps for important omissions in the plan. A perfect checklist
score cannot offset failure of the intended audience experience. Keep direct
AV pending where unavailable, but never hide frame-visible defects there.
For a work_unit, explicitly compare every positive reference feature and phase
boundary, state the largest remaining mismatch and any outside-scope changes.
Do not treat the builder's application statements as visual proof. Every
intent_check must set scope=supported_evidence_only; a PASS there is not a
full-speed audiovisual verdict. Preserve the separate Director AV checks.'''


def plan_digest(brief):
    plan = {k: v for k, v in brief['expert_plan'].items() if k != 'challenge'}
    return pk.digest({'plan': plan, 'requirements': brief['requirements'],
                      'references': brief['references'], 'intent': brief['intent'],
                      'protected': brief['protected'],
                      **({'work_unit': brief['work_unit']} if 'work_unit' in brief else {}),
                      **({k: brief.get(k) for k in ('reference_readiness','reference_mapping')}
                         if 'reference_readiness' in brief else {})})


def contract():
    """Compact field guide carried in actual planner packets, not just docs."""
    return {'version': 1, 'lenses': list(LENSES),
            'beat_intents': 'Copy trusted direction.beat_intents exactly',
            'beats': ['id', 'audience_read', 'framing',
                      'lenses: every lens -> {applies:boolean, why:string, requirements:[requirement IDs]}'],
            'realizations': 'Every requirement ID -> {beats, lenses, derivation, method, interfaces, early_proof, failure_condition, reopen_when, priority, origin, reference_ids}',
            'priority': ['quality_floor', 'dramatic', 'optional'],
            'origin': ['director', 'reference', 'craft_inference'],
            'challenge': ['plan_digest: trusted parent hashes after reading this challenge',
                          'intent_coverage: every beat ID -> {reason, requirements}',
                          'cross_discipline_conflicts', 'omission_probe', 'scope_tradeoff', 'open_issues'],
            'review_boundary': 'Fresh review repeats original intent scan; planning_gaps veto even otherwise passing checks',
            'work_unit': 'Required when trusted reference.unit_required=true: one primary_outcome, phase, task, reference, positive_criteria, allowed/frozen_domains, pose/velocity/contact boundaries, negative_controls+FAIL calibration, permitted native operations/edit_kinds and cumulative cycle_window. Builder supplies unit_application; reviewer supplies unit_review with positive comparisons, boundary checks, largest_remaining_mismatch and outside_scope_changes. Coverage is not artistic truth.'}


def seal_planner_response(raw):
    """Supply a mechanical hash, never missing reasoning or synthetic defaults.

    Trusted adapters call this only on a COMPLETE planner brief after reading
    its challenge. Full workflow admission still verifies authority and sources.
    Hashing is not a second expert review.
    """
    result = copy.deepcopy(raw)
    require(isinstance(result.get('expert_plan', {}).get('challenge'), dict), 'PLANNING_CHALLENGE_REQUIRED')
    result['expert_plan']['challenge']['plan_digest'] = plan_digest(result)
    validate(result)
    return result


def validate(brief):
    from . import work_units
    work_units.validate(brief)
    plan = brief.get('expert_plan')
    require(isinstance(plan, dict) and plan.get('version') == 1, 'EXPERT_PLAN_REQUIRED')
    intents = plan.get('beat_intents')
    require(isinstance(intents, dict) and intents and all(nonempty(k) and nonempty(v) for k, v in intents.items()), 'BEAT_INTENTS_REQUIRED')
    beats = rows(plan.get('beats', []))
    require(set(beats) == set(intents), 'EXPERT_BEAT_COVERAGE')
    reqs = rows(brief['requirements'])
    methods = plan.get('realizations', {})
    require(set(methods) == set(reqs), 'EXPERT_REQUIREMENT_COVERAGE')
    refs = set(rows(brief['references']))
    linked = set()
    for bid, beat in beats.items():
        require(nonempty(beat.get('audience_read')) and nonempty(beat.get('framing')), 'BEAT_AUDIENCE_FRAMING')
        lenses = beat.get('lenses', {})
        require(set(lenses) == set(LENSES), 'EXPERT_LENS_COVERAGE')
        applied = False
        for name, lens in lenses.items():
            require(type(lens.get('applies')) is bool and nonempty(lens.get('why')), 'LENS_JUSTIFICATION')
            ids = lens.get('requirements')
            require(isinstance(ids, list) and len(set(ids)) == len(ids) and set(ids) <= set(reqs), 'LENS_REQUIREMENTS')
            require(bool(ids) == lens['applies'], 'LENS_APPLICATION_REQUIRED')
            for rid in ids:
                require(bid in methods[rid].get('beats', []) and name in methods[rid].get('lenses', []), 'LENS_TRACEABILITY')
            linked.update(ids)
            applied |= lens['applies']
        require(applied, 'NO_APPLIED_LENS')
    require(linked == set(reqs), 'ORPHAN_REQUIREMENT')
    for rid, method in methods.items():
        require(method.get('beats') and set(method['beats']) <= set(beats) and
                method.get('lenses') and set(method['lenses']) <= set(LENSES), 'REALIZATION_SCOPE')
        for b in method['beats']:
            for lens in method['lenses']:
                require(rid in beats[b]['lenses'][lens]['requirements'], 'REALIZATION_REVERSE_LINK')
        for field in ('derivation', 'method', 'early_proof', 'failure_condition', 'reopen_when'):
            require(nonempty(method.get(field)), 'MISSING_REALIZATION:' + field)
        require(method.get('interfaces') and all(nonempty(x) for x in method['interfaces']), 'INTERFACES_REQUIRED')
        require(method.get('priority') in {'quality_floor', 'dramatic', 'optional'}, 'REQUIREMENT_PRIORITY')
        require(method.get('origin') in {'director', 'reference', 'craft_inference'}, 'REQUIREMENT_ORIGIN')
        require(method.get('reference_ids') and set(method['reference_ids']) <= refs, 'REALIZATION_REFERENCES')
    challenge = plan.get('challenge', {})
    require(challenge.get('plan_digest') == plan_digest(brief), 'STALE_PLANNING_CHALLENGE')
    require(challenge.get('open_issues') == [], 'PLANNING_CHALLENGE_UNRESOLVED')
    coverage = challenge.get('intent_coverage', {})
    require(set(coverage) == set(beats), 'CHALLENGE_INTENT_COVERAGE')
    for bid, check in coverage.items():
        require(nonempty(check.get('reason')) and check.get('requirements') and
                set(check['requirements']) <= {r for r, m in methods.items() if bid in m['beats']},
                'CHALLENGE_INTENT_LINK')
    for field in ('cross_discipline_conflicts', 'omission_probe', 'scope_tradeoff'):
        require(nonempty(challenge.get(field)), 'MISSING_PLANNING_CHALLENGE:' + field)
    return plan_digest(brief)


def validate_execution(brief, result):
    from . import reference_readiness as rr
    rr.execution(brief, result)
    from . import work_units
    work_units.execution(brief, result)
    uses = result.get('requirement_uses', {})
    require(set(uses) == set(rows(brief['requirements'])), 'EXECUTION_REQUIREMENT_COVERAGE')
    for use in uses.values():
        require(use.get('plan_digest') == plan_digest(brief) and nonempty(use.get('application')), 'EXECUTION_PLAN_LOST')


def review_intent(brief, review, evidence):
    from . import work_units
    checks = review.get('intent_checks', {})
    require(set(checks) == set(brief['expert_plan']['beat_intents']), 'REVIEW_INTENT_COVERAGE')
    failed, missing = [], []
    for bid, check in checks.items():
        require(check.get('scope') == 'supported_evidence_only', 'INTENT_REVIEW_SCOPE')
        require(check.get('status') in {'PASS', 'FAIL', 'NOT_RUN'} and nonempty(check.get('observation'))
                and nonempty(check.get('comparison')), 'INTENT_OBSERVATION')
        ids = check.get('evidence', [])
        require(isinstance(ids, list) and set(ids) <= set(evidence), 'INTENT_EVIDENCE')
        if check['status'] != 'NOT_RUN': require(ids, 'INTENT_EVIDENCE_REQUIRED')
        if check['status'] == 'FAIL': failed.append('intent:' + bid)
        if check['status'] == 'NOT_RUN': missing.append('intent:' + bid)
    gaps = review.get('planning_gaps')
    require(isinstance(gaps, list) and all(nonempty(x) for x in gaps), 'PLANNING_GAP_SCAN_REQUIRED')
    unit_failed, unit_missing = work_units.review(brief, review, evidence)
    return failed + unit_failed, missing + unit_missing, gaps
