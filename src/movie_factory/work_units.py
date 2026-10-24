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
    require(isinstance(unit, dict) and unit.get('version') == 1, 'UNIT_VERSION')
    for key in ('id', 'primary_outcome', 'phase', 'task'):
        require(nonempty(unit.get(key)), 'UNIT_FIELD:' + key)
    require(isinstance(unit.get('primary_outcome'), str), 'ONE_PRIMARY_OUTCOME')
    reqs, refs = rows(brief['requirements']), rows(brief['references'])
    require(unit.get('reference') in refs and refs[unit['reference']]['role'] == 'faithful_motion', 'UNIT_REFERENCE')
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
    return unit


def native(state, recipe):
    unit = validate(state['brief'])
    if not unit:
        return
    require(state['task'] == unit['task'] and unit['cycle_window'][0] <= state['cycle'] <= unit['cycle_window'][1], 'UNIT_ASSIGNMENT_EXPIRED')
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
    failed, missing = [], []
    for key, row in {**checks, **boundaries}.items():
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
    return failed, missing
