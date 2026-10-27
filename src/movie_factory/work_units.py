"""367 scoped positive-reference contracts. Coverage gates, not artistic truth.

Legacy immutable briefs remain readable. Trusted references marked unit_required
make this contract mandatory in every subsequent plan, execution and review.
No field validator can tell whether a plausible visual assertion is truthful.
"""
from .production_workflow import require, nonempty, rows


def validate(brief):
    unit = brief.get('work_unit')
    required = any(r.get('unit_required') is True for r in brief['references'])
    require(unit is not None or not required, 'WORK_UNIT_REQUIRED')
    if unit is None:
        return None
    require(isinstance(unit, dict) and unit.get('version') in {1, 2}, 'UNIT_VERSION')
    for key in ('id', 'primary_outcome', 'phase', 'task'):
        require(nonempty(unit.get(key)), 'UNIT_FIELD:' + key)
    require(isinstance(unit.get('primary_outcome'), str), 'ONE_PRIMARY_OUTCOME')
    reqs, refs = rows(brief['requirements']), rows(brief['references'])
    discipline=unit.get('discipline','motion')
    require(discipline in {'motion','appearance'}, 'UNIT_DISCIPLINE')
    roles={'faithful_motion'} if discipline=='motion' else {'directional_design','accepted_quality','exact_asset'}
    require(unit.get('reference') in refs and refs[unit['reference']]['role'] in roles, 'UNIT_REFERENCE')
    if discipline=='appearance':
        proof=unit.get('appearance_proof',{})
        poses,views=proof.get('poses'),proof.get('views')
        require(isinstance(poses,list) and len(poses)>=3 and len(set(poses))==len(poses)
                and all(type(f) is int and 252<=f<=441 for f in poses), 'UNIT_APPEARANCE_POSES')
        require(isinstance(views,list) and len(views)>=3 and len(set(views))==len(views)
                and all(nonempty(v) for v in views), 'UNIT_APPEARANCE_VIEWS')
        require(proof.get('motion_source') in brief['source_bindings'].values(), 'UNIT_APPEARANCE_MOTION_SOURCE')
        require(isinstance(proof.get('interfaces'),list) and len(proof['interfaces'])>=3
                and all(nonempty(v) for v in proof['interfaces']), 'UNIT_APPEARANCE_INTERFACES')
    allowed, frozen = unit.get('allowed_domains'), unit.get('frozen_domains')
    require(isinstance(allowed, list) and allowed and all(nonempty(v) for v in allowed), 'UNIT_ALLOWED_DOMAINS')
    require(isinstance(frozen, list) and frozen and all(nonempty(v) for v in frozen), 'UNIT_FROZEN_DOMAINS')
    require(not set(allowed) & set(frozen), 'UNIT_DOMAIN_CONFLICT')
    criteria = rows(unit.get('positive_criteria', []))
    require(criteria and set(criteria) <= set(reqs), 'UNIT_POSITIVE_REQUIREMENTS')
    for key, row in criteria.items():
        require(not reqs[key]['director_av'], 'UNIT_IMAGE_CRITERION_CANNOT_PASS_AV')
        for field in ('reference_feature', 'failure', 'comparison'):
            require(nonempty(row.get(field)), 'UNIT_POSITIVE_FIELD:' + field)
    boundaries = rows(unit.get('boundaries', []))
    require(boundaries, 'UNIT_BOUNDARIES_REQUIRED')
    for row in boundaries.values():
        require(row.get('state') == ['pose', 'velocity', 'contacts'] and nonempty(row.get('consumer')), 'UNIT_BOUNDARY_STATE')
    controls = rows(unit.get('negative_controls', []))
    require(controls, 'UNIT_CALIBRATION_REQUIRED')
    for row in controls.values():
        require(row.get('expected') == 'FAIL' and nonempty(row.get('failure')), 'UNIT_REJECTED_CONTROL')
        require(row.get('binding') in brief['source_bindings'].values(), 'UNIT_CONTROL_UNBOUND')
    calibration = unit.get('calibration', {})
    require(set(calibration) == set(controls), 'UNIT_CALIBRATION_COVERAGE')
    for row in calibration.values():
        require(row.get('verdict') == 'FAIL' and nonempty(row.get('observation')), 'UNIT_CONTROL_STILL_PASSES')
    require(unit.get('operations') and set(unit['operations']) <= {'nihang_patch', 'nihang_save', 'nihang_render', 'nihang_frames', 'nihang_rig_inspect'}, 'UNIT_OPERATIONS')
    require(isinstance(unit.get('edit_kinds'), list) and unit['edit_kinds'] and all(nonempty(x) for x in unit['edit_kinds']), 'UNIT_EDIT_KINDS')
    lo, hi = unit.get('cycle_window', [None, None])
    require(type(lo) is int and type(hi) is int and 0 <= lo <= hi, 'UNIT_CYCLE_WINDOW')
    if unit['version'] == 2:
        scope_contract(brief, unit)
    return unit


def scope_contract(brief, unit):
    """386: require a reasoned scope/experiment, without pretending to judge art."""
    bound = list(brief['source_bindings'].values())
    scope = unit.get('scope_decision', {})
    require(scope.get('decision') in {'keep', 'split', 'merge'}, 'UNIT_SCOPE_DECISION')
    for key in ('rationale', 'independent_judgment', 'coupled_context', 'worst_proof', 'integration_proof'):
        require(nonempty(scope.get(key)), 'UNIT_SCOPE_' + key.upper())
    parts = rows(scope.get('considered_outcomes', []))
    require(parts, 'UNIT_SCOPE_ALTERNATIVES')
    for part in parts.values():
        require(part.get('disposition') in {'current', 'coupled', 'deferred'} and
                nonempty(part.get('criterion')) and nonempty(part.get('reason')), 'UNIT_SCOPE_PART')
    require(sum(p['disposition']=='current' for p in parts.values()) == 1, 'UNIT_ONE_CURRENT_OUTCOME')
    require(scope.get('parent_task') == unit['task'] and
            scope.get('allowance_binding') in bound, 'UNIT_SHARED_ALLOWANCE')
    experiment = unit.get('causal_experiment', {})
    for key in ('unknown', 'hypothesis', 'method_family', 'discriminator', 'success_prediction',
                'failure_prediction', 'failure_response'):
        require(nonempty(experiment.get(key)), 'UNIT_EXPERIMENT_' + key.upper())
    require(isinstance(experiment.get('failed_alternatives'), list) and
            all(nonempty(v) for v in experiment['failed_alternatives']), 'UNIT_PRIOR_METHODS')
    proof = experiment.get('evidence', [])
    require(proof and all(b in bound for b in proof), 'UNIT_EXPERIMENT_EVIDENCE')
    challenge = unit.get('scope_challenge', {})
    require(challenge.get('status') == 'PASS' and nonempty(challenge.get('observation')) and
            nonempty(challenge.get('counterexample')) and challenge.get('evidence') and
            all(b in bound for b in challenge['evidence']), 'UNIT_SCOPE_CHALLENGE')
    dependencies = unit.get('dependencies')
    require(isinstance(dependencies, list), 'UNIT_DEPENDENCIES')
    for dep in dependencies:
        require(nonempty(dep.get('id')) and dep.get('binding') in bound and
                isinstance(dep.get('interfaces'), list) and dep['interfaces'] and
                all(nonempty(x) for x in dep['interfaces']) and
                dep.get('disposition') in {'preserve', 'revalidate'}, 'UNIT_DEPENDENCY')
        require(nonempty(dep.get('reason')), 'UNIT_DEPENDENCY_REASON')


def appearance_cells(unit):
    if unit.get('discipline','motion')!='appearance':return set()
    p=unit['appearance_proof']
    return {str(f)+':'+v for f in p['poses'] for v in p['views']}


def component_disposition(unit, verdict):
    """Keep per-native evidence classification, including early rejected proofs."""
    if not unit or unit.get('version') != 2:
        return
    data=verdict.get('cycle_disposition', {})
    require(data.get('category') in {'causal_control_only','art_rejected','scoped_image_proof_pass'}
            and nonempty(data.get('observation')), 'UNIT_NATIVE_DISPOSITION386')
    if verdict['verdict'] != 'PASS' or verdict['open_defects']:
        require(data['category'] != 'scoped_image_proof_pass', 'UNIT_NATIVE_FAILURE_CANNOT_PASS386')


def native(state, recipe):
    unit = validate(state['brief'])
    if not unit:
        return
    require(state['task'] == unit['task'] and unit['cycle_window'][0] <= state['cycle'] <= unit['cycle_window'][1], 'UNIT_ASSIGNMENT_EXPIRED')
    if unit['version'] == 2:
        require(unit['cycle_window'][1] <= state['max_corrections'], 'UNIT_PARENT_ALLOWANCE_EXCEEDED')
    require(recipe is not None and recipe['operation'] in unit['operations'], 'UNIT_UNDECLARED_OPERATION')
    if recipe['operation'] == 'nihang_patch':
        require(all(x['kind'] in unit['edit_kinds'] for x in recipe['edits']), 'UNIT_OUTSIDE_EDIT_SCOPE')


def execution(brief, result):
    unit = validate(brief)
    if not unit:
        return
    use = result.get('unit_application', {})
    require(use.get('id') == unit['id'], 'UNIT_EXECUTION_LOST')
    criteria = rows(unit['positive_criteria'])
    require(set(use.get('criteria', {})) == set(criteria) and all(nonempty(x) for x in use['criteria'].values()), 'UNIT_EXECUTION_COVERAGE')
    require(set(use.get('changed_domains', [])) <= set(unit['allowed_domains']), 'UNIT_OUTSIDE_DOMAIN')
    if unit.get('discipline')=='appearance':
        coverage=use.get('pose_views',{})
        require(set(coverage)==appearance_cells(unit) and all(nonempty(v) for v in coverage.values()), 'UNIT_APPEARANCE_EXECUTION_COVERAGE')
    require(set(use.get('boundaries', {})) == set(rows(unit['boundaries'])) and all(nonempty(x) for x in use['boundaries'].values()), 'UNIT_EXECUTION_BOUNDARIES')


def review(brief, result, evidence):
    unit = validate(brief)
    if not unit:
        return [], []
    data = result.get('unit_review', {})
    require(data.get('id') == unit['id'], 'UNIT_REVIEW_LOST')
    checks = data.get('criteria', {})
    require(set(checks) == set(rows(unit['positive_criteria'])), 'UNIT_REVIEW_COVERAGE')
    boundaries = data.get('boundaries', {})
    require(set(boundaries) == set(rows(unit['boundaries'])), 'UNIT_REVIEW_BOUNDARIES')
    posed={}
    if unit.get('discipline')=='appearance':
        posed=data.get('pose_views',{})
        require(set(posed)==appearance_cells(unit), 'UNIT_APPEARANCE_REVIEW_COVERAGE')
    failed, missing = [], []
    for key, row in {**checks, **boundaries, **posed}.items():
        require(row.get('status') in {'PASS', 'FAIL', 'NOT_RUN'}, 'UNIT_REVIEW_STATUS')
        require(nonempty(row.get('observation')) and nonempty(row.get('comparison')), 'UNIT_POSITIVE_COMPARISON')
        ids = row.get('evidence', [])
        require(isinstance(ids, list) and set(ids) <= set(evidence), 'UNIT_REVIEW_EVIDENCE')
        if row['status'] != 'NOT_RUN': require(ids, 'UNIT_COMPARISON_EVIDENCE_REQUIRED')
        if row['status'] == 'FAIL': failed.append('unit:' + key)
        if row['status'] == 'NOT_RUN': missing.append('unit:' + key)
    mismatch = data.get('largest_remaining_mismatch', {})
    require(type(mismatch.get('blocking')) is bool and nonempty(mismatch.get('observation')) and mismatch.get('evidence') and set(mismatch['evidence']) <= set(evidence), 'UNIT_STRONGEST_MISMATCH_REQUIRED')
    if mismatch['blocking']: failed.append('unit:remaining_mismatch')
    require(isinstance(data.get('outside_scope_changes'), list), 'UNIT_SCOPE_REVIEW_REQUIRED')
    if data['outside_scope_changes']: failed.append('unit:outside_scope_changes')
    if unit['version'] == 2:
        disposition = data.get('cycle_disposition', {})
        require(disposition.get('category') in {'causal_control_only', 'art_rejected', 'scoped_image_proof_pass'}, 'UNIT_CYCLE_CATEGORY')
        require(disposition.get('hypothesis_result') in {'effective', 'ineffective', 'inconclusive'} and
                nonempty(disposition.get('observation')), 'UNIT_CYCLE_EFFECT')
        if failed or missing:
            require(disposition['category'] != 'scoped_image_proof_pass' and
                    disposition['hypothesis_result'] != 'effective', 'UNIT_FAILED_CANNOT_PASS')
        dep_checks = data.get('dependency_checks', {})
        require(set(dep_checks) == {d['id'] for d in unit['dependencies']}, 'UNIT_DEPENDENCY_REVIEW')
        for key, dep in dep_checks.items():
            require(dep.get('status') in {'PASS','FAIL','NOT_RUN'} and
                    nonempty(dep.get('observation')) and isinstance(dep.get('changed_interfaces'), list), 'UNIT_DEPENDENCY_CHECK')
            ids = dep.get('evidence', [])
            require(ids and set(ids) <= set(evidence), 'UNIT_DEPENDENCY_EVIDENCE')
            if dep['changed_interfaces']:
                require(dep.get('revalidation') in {'PASS','FAIL','NOT_RUN'}, 'UNIT_CHANGED_INTERFACE_UNJUDGED')
                if dep['revalidation'] != 'PASS': failed.append('unit:dependency:' + key)
            if dep['status'] != 'PASS': failed.append('unit:dependency:' + key)
    return failed, missing
