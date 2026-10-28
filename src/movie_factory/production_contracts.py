"""Typed397 contracts: deterministic evidence/order checks, fallible art judgment."""
import json
import math
from . import production_knowledge as pk
from . import review_control as rc
from .production_governance import need

KINDS = {'measurement', 'evidence', 'judgment', 'authority'}
PROOFS = {'transport', 'target_form', 'pose_form', 'continuous', 'finish'}


def text(v):
    return isinstance(v, str) and bool(v.strip())


def scope_contract(root, d):
    for k in ('question', 'first_operation', 'success_next', 'failure_next',
              'smaller_proof', 'coupling_counterexample', 'discriminator'):
        need(text(d.get(k)), 'SCOPE_' + k.upper())
    need(d['success_next'] != d['failure_next'], 'NONDISCRIMINATING_SCOPE')
    need(d.get('decision') in {'split', 'keep', 'merge', 'change_method', 'retire'}, 'SCOPE_DECISION')
    need(isinstance(d.get('prerequisites'), list), 'SCOPE_PREREQUISITES')
    if d['decision']=='split':
        children=rc.unique(d.get('children',[]));need(len(children)>=2,'SPLIT_NEEDS_CHILD_PROOFS')
        seen=set()
        for child in children.values():
            need(text(child.get('question')) and text(child.get('acceptance')) and
                 isinstance(child.get('depends_on'),list) and set(child['depends_on'])<=seen,'CHILD_PROOF_DEPENDENCY')
            seen.add(child['id'])
        need(d.get('current_child') in children,'CURRENT_CHILD_REQUIRED')
    need(d.get('changes') and all(text(x.get('domain')) and text(x.get('control'))
                                 for x in d['changes']), 'CAUSAL_CHANGE_SET')
    groups = {x['control'] for x in d['changes']}
    need(len(groups) == 1 or text(d.get('necessary_coupling')), 'UNCONTROLLED_MULTIPLE_CONTRASTS')
    need(d.get('invariants') and all(x.get('owner') in {'director', 'consumer', 'method', 'numeric'}
            and text(x.get('condition')) for x in d['invariants']), 'INVARIANT_OWNERSHIP')
    need(isinstance(d.get('evidence'), dict) and d['evidence'], 'SCOPE_EVIDENCE')
    for b in d['evidence'].values(): rc.binding(root, b)


def validate(root, brief, steps=None, *, required=False):
    d = brief.get('production_contract397')
    need(d is not None or not required, 'STAGE_CONTRACT_REQUIRED')
    if d is None: return None
    need(d.get('version') == 1 and text(d.get('family')) and text(d.get('capability')),
         'CONTRACT_VERSION_LINEAGE')
    criteria = rc.unique(d.get('criteria', []))
    reqs = rc.unique(brief['requirements'])
    need(set(criteria) == set(reqs), 'CRITERION_COVERAGE')
    refs = rc.unique(brief['references'])
    for k, c in criteria.items():
        need(type(c.get('critical')) is bool and c.get('kind') in KINDS, 'CRITERION_TYPE')
        for key in ('anchor', 'assessor', 'coordinate_space', 'profile', 'invalidation'):
            need(text(c.get(key)), 'CRITERION_' + key.upper())
        need(c.get('references') and set(c['references']) <= set(refs), 'CRITERION_REFERENCE')
        need(c.get('cells') and len(set(c['cells'])) == len(c['cells']) and
             all(text(x) for x in c['cells']), 'CRITERION_CELLS')
        need(type(c.get('human_av')) is bool and c['human_av'] == reqs[k]['director_av'], 'CRITERION_OWNER')
        if c['kind'] == 'measurement':
            need(c.get('comparator') in {'eq', 'lte', 'gte'} and type(c.get('threshold')) in {int, float}
                 and math.isfinite(c['threshold']) and text(c.get('metric_key')), 'METRIC_DEFINITION')
            need(text(c.get('calibration')) and text(c.get('negative_control')), 'METRIC_CALIBRATION')
        else:
            need(c.get('threshold') is None and c.get('comparator') is None, 'SUBJECTIVE_NUMBER_IS_NOT_MEASUREMENT')
    need(set(d.get('feature_map', {})) == set(reqs) and all(isinstance(v, list) and v
         and all(text(x) for x in v) for v in d['feature_map'].values()), 'FEATURE_MAP')
    scope_contract(root, d['scope'])
    operations = d.get('operations')
    need(isinstance(operations, list) and operations, 'OPERATION_CONTRACT')
    seen, available = set(), {p['kind'] for p in d.get('input_proofs', [])}
    need(available <= PROOFS,'INPUT_PROOF_KIND')
    plan_steps = rc.unique(steps) if steps is not None else None
    for op in operations:
        need(text(op.get('id')) and op['id'] not in seen, 'OPERATION_ID')
        need(isinstance(op.get('requires'), list) and set(op['requires']) <= available, 'UNQUALIFIED_PREREQUISITE_ORDER')
        need(isinstance(op.get('produces'), list) and set(op['produces']) <= PROOFS, 'PROOF_KIND')
        need(op.get('class') in {'control', 'target', 'fit', 'binding', 'cache', 'finish', 'integration'}, 'OPERATION_CLASS')
        if op['class'] in {'fit', 'binding'}: need('target_form' in op['requires'], 'TARGET_BEFORE_FITTING')
        if op['class'] in {'cache', 'finish'}: need('pose_form' in op['requires'], 'POSE_BEFORE_DENSE_FINISH')
        need(set(op.get('prerequisite_steps', [])) <= seen, 'PROOF_STEP_ORDER')
        if plan_steps is not None:
            need(op['id'] in plan_steps and set(op.get('prerequisite_steps', [])) <= set(plan_steps[op['id']]['depends_on']),
                 'ACTUAL_STEP_DEPENDENCY_MISMATCH')
            need(op.get('recipe') == plan_steps[op['id']].get('native_recipe'), 'ACTUAL_OPERATION_BINDING')
        seen.add(op['id']); available.update(op['produces'])
    if plan_steps is not None: need(seen == set(plan_steps), 'UNCONTRACTED_OPERATION')
    need(d['scope']['first_operation'] == operations[0]['id'], 'FIRST_PROOF_NOT_EXECUTABLE')
    return d


def native_operation(root, state, step, recipe, prior_runs, prior_reviews):
    d = state['brief'].get('production_contract397')
    need(d is not None, 'NATIVE_CONTRACT_REQUIRED')
    op = next((x for x in d['operations'] if x['id'] == step), None)
    need(op is not None, 'NATIVE_OPERATION_NOT_CONTRACTED')
    kinds = {e['kind'] for e in (recipe or {}).get('edits', [])}
    # A conservative reviewed classification, not inference from a model's label.
    # Broad inherited custom handlers require a positive form; new classifications
    # need reviewed integration. Raw numeric controls are not an art proof.
    if 'mounted_horse_cache376' in kinds:
        need(op['class'] == 'cache' and 'pose_form' in op['requires'], 'ACTUAL_CACHE_REQUIRES_POSE_PROOF')
    elif kinds - {'bone_pose', 'bone_location', 'bone_scale', 'mesh'}:
        need(op['class'] in {'fit', 'binding', 'integration'} and 'target_form' in op['requires'],
             'CUSTOM_AUTHORING_REQUIRES_TARGET_PROOF')
    elif 'mesh' in kinds:
        need(op['class'] in {'target', 'fit'}, 'GEOMETRY_IS_NOT_TRANSPORT')
    supplied = {p['kind'] for p in d.get('input_proofs', [])}
    for dep in op.get('prerequisite_steps', []):
        need(dep in prior_runs and dep in prior_reviews, 'PREREQUISITE_NOT_REVIEWED')
        prior = next(x for x in d['operations'] if x['id'] == dep)
        verdict = prior_reviews[dep]
        need(verdict['verdict'] == 'PASS' and not verdict['open_defects'], 'PREREQUISITE_FAILED')
        for kind in prior['produces']:
            if kind != 'transport':
                need(any(k == 'frame' or k.startswith('frame_') for k in prior_runs[dep]['artifacts']),
                     'ART_PROOF_REQUIRES_NATIVE_IMAGE')
                need(verdict.get('proof_kinds397') and kind in verdict['proof_kinds397'], 'UNQUALIFIED_PROOF_KIND')
            supplied.add(kind)
    need(set(op['requires']) <= supplied, 'ACTUAL_PROOF_PREREQUISITE_MISSING')
    return op


def native_review(state, step, run, verdict):
    d = state['brief'].get('production_contract397')
    if d is None: return []
    op = next(x for x in d['operations'] if x['id'] == step)
    claimed = verdict.get('proof_kinds397', [])
    need(isinstance(claimed, list) and set(claimed) <= set(op['produces']), 'UNPLANNED_PROOF_CLAIM')
    if verdict['verdict'] != 'PASS': need(not claimed, 'FAILED_PROOF_CANNOT_QUALIFY')
    if set(claimed) - {'transport'}:
        need(any(k == 'frame' or k.startswith('frame_') for k in run['artifacts']), 'ART_PROOF_REQUIRES_NATIVE_IMAGE')
        need('continuous' not in claimed, 'CONTINUOUS_MOTION_REQUIRES_DIRECTOR_AV')
        need(set(claimed)-{'transport'} <= {x.get('proof_kind') for x in verdict.get('subproofs397',[])},
             'ART_PROOF_NEEDS_TYPED_SUBPROOF')
    return claimed


def review(root, brief, candidate, result, *, subset=None):
    d = brief.get('production_contract397')
    if d is None: return [], [], []
    criteria = rc.unique(d['criteria'])
    if subset is not None: criteria = {k: criteria[k] for k in subset}
    checks = rc.unique(result.get('contract_checks397', []))
    need(set(checks) == set(criteria), 'TYPED_REVIEW_COVERAGE')
    evidence = result.get('evidence', {})
    bad, missing, passed_features = [], [], []
    digest = pk.digest(candidate)
    rejected={r['binding']['sha256'] for r in brief['references'] if r['role']=='negative_control'}
    need(not rejected.intersection(b['sha256'] for b in candidate['artifacts'].values()),'KNOWN_REJECTED_ARTIFACT')
    reqs = rc.unique(brief['requirements'])
    for key, c in criteria.items():
        v = checks[key]
        need(v.get('status') in {'PASS', 'FAIL', 'UNKNOWN', 'NOT_RUN'}, 'TYPED_VERDICT')
        need(text(v.get('observation')), 'TYPED_OBSERVATION')
        cells = rc.unique(v.get('cells', []))
        need(set(cells) == set(c['cells']), 'TYPED_CELL_COVERAGE')
        failed, unknown = False, False
        for cell in cells.values():
            need(cell.get('status') in {'PASS', 'FAIL', 'UNKNOWN', 'NOT_RUN'}, 'CELL_VERDICT')
            if cell['status'] in {'NOT_RUN', 'UNKNOWN'}:
                unknown = True; continue
            ids = cell.get('evidence', [])
            need(ids and set(ids) <= set(evidence), 'CELL_EVIDENCE')
            for eid in ids:
                e = evidence[eid]; rc.binding(root, e['binding'])
                need(e.get('candidate_digest') == digest and e.get('mode') in reqs[key]['modes'], 'CELL_CANDIDATE_MODE')
            need(set(reqs[key]['modes']) <= {evidence[x]['mode'] for x in ids}, 'CELL_MODALITY_COVERAGE')
            if c['kind'] == 'measurement':
                measurement = next((evidence[x] for x in ids if evidence[x]['mode'] == 'technical'), None)
                need(measurement is not None, 'MEASUREMENT_ARTIFACT_REQUIRED')
                p = rc.path(root, measurement['binding']['path'])
                need(p.stat().st_size <= 1024*1024 and p.suffix == '.json', 'MEASUREMENT_BOUND')
                raw = json.loads(p.read_text())
                need(raw.get('coordinate_space') == c['coordinate_space'] and raw.get('profile') == c['profile']
                     and raw.get('candidate_digest') == digest and raw.get('cell') == cell['id'], 'MEASUREMENT_CONDITIONS')
                value = raw.get(c['metric_key'])
                need(type(value) in {int, float} and math.isfinite(value), 'MEASUREMENT_VALUE')
                t = c['threshold']; computed = {'eq': value == t, 'lte': value <= t, 'gte': value >= t}[c['comparator']]
                need((cell['status'] == 'PASS') is computed, 'MEASUREMENT_VERDICT_CONTRADICTION')
            if cell['status'] == 'FAIL': failed = True
        if c['human_av']:
            need(v['status'] != 'PASS' and all(x['status'] != 'PASS' for x in cells.values()), 'HUMAN_AV_CANNOT_SELF_PASS')
        need(not (v['status'] == 'PASS' and (failed or unknown)), 'AGGREGATE_CONTRADICTS_CELLS')
        if failed or v['status'] == 'FAIL': bad.append(key)
        elif unknown or v['status'] in {'UNKNOWN', 'NOT_RUN'}:
            if not c['human_av']: missing.append(key)
        else: passed_features.extend(d['feature_map'][key])
    # Contradictions with the existing review are checked, not overridden.
    if subset is None:
        old = rc.unique(result['checks'])
        for k in checks:
            need(not (old[k]['status'] == 'PASS' and checks[k]['status'] != 'PASS'), 'LEGACY_AGGREGATE_CONTRADICTION')
    return bad, missing, sorted(set(passed_features))


def compact_packet(packet, governance, *, maximum=24576):
    """Lossless dependency manifest, stage-specific bodies, hard mandatory floor.

    Does not shrink host conversation. Overflow blocks; it never drops rules.
    """
    p = json.loads(json.dumps(packet))
    bodies = p.get('planning_inputs', {})
    dependencies = {k: pk.digest(v) for k, v in bodies.items()}
    step = p.get('planning_step')
    needed = {'GROUNDING': [], 'DERIVING': ['GROUNDING'],
              'STRATEGIZING': ['GROUNDING', 'DERIVING'],
              'CHALLENGING': list(bodies)}.get(step, [])
    p['planning_inputs'] = {k: bodies[k] for k in needed if k in bodies}
    if step == 'CHALLENGING' and 'STRATEGIZING' in p['planning_inputs']:
        # The brief is already in STRATEGIZING; no duplicated top-level copy.
        p.pop('brief', None)
    p['dependency_manifest397'] = dependencies
    p['governance397'] = governance
    p['packet_digest397'] = pk.digest(p)
    dynamic = {k: v for k, v in p.items() if k not in {'source_context', 'grounding_knowledge'}}
    encoded = json.dumps(dynamic, sort_keys=True, ensure_ascii=False).encode()
    need(len(encoded) <= maximum, 'CONTEXT_OVERFLOW_RECONCILE_NO_TRUNCATION')
    return p
