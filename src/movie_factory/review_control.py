"""Pinned scoped review admission. Checks declarations, NOT perceptual truth.

Only `deliver` emits review-ready artifact references. It rechecks all bindings;
no cached PASS or development-label override is accepted. Not a chat interceptor.
"""
import argparse
import json
from pathlib import Path

from movie_factory import production_knowledge as pk

REGISTRY = 'docs/knowledge/review_control/active.json'
MODES = {'image', 'timed_images', 'direct_motion', 'direct_audio', 'technical', 'authority'}


class Blocked(ValueError):
    pass


def path(root, rel):
    if not isinstance(rel, str) or Path(rel).is_absolute():
        raise Blocked('RELATIVE_PATH_REQUIRED')
    p = (root / rel).resolve()
    if not p.is_relative_to(root.resolve()) or any(x in {'.env', '.git', '.aws'} for x in Path(rel).parts):
        raise Blocked('UNSAFE_PATH')
    return p


def read(root, rel):
    return json.loads(path(root, rel).read_text())


def binding(root, b):
    if set(b) != {'path', 'sha256'} or pk.file_hash(path(root, b['path'])) != b['sha256']:
        raise Blocked('STALE_BINDING')


def unique(rows):
    if not isinstance(rows, list) or not rows:
        raise Blocked('EMPTY_REQUIRED_ROWS')
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'] or row['id'] in result:
            raise Blocked('INVALID_OR_DUPLICATE_ID')
        result[row['id']] = row
    return result


def load(root):
    registry = read(root, REGISTRY)
    for key in ('contract', 'state'):
        binding(root, registry[key])
    contract = read(root, registry['contract']['path'])
    state = read(root, registry['state']['path'])
    if contract['schema'] != 1 or state['schema'] != 1 or state['contract_id'] != contract['id']:
        raise Blocked('SCHEMA_OR_CONTRACT_MISMATCH')
    requirements = unique(contract['requirements'])
    for req in requirements.values():
        if not req['criterion'].strip() or not req['modes'] or not set(req['modes']) <= MODES:
            raise Blocked('INVALID_REQUIREMENT')
    if contract['production_approval'] is not False or not contract['protected'] or not contract['exclusions']:
        raise Blocked('MISSING_AUTHORITY_BOUNDARIES')
    if set(state['checks']) != set(requirements):
        raise Blocked('STATE_SCOPE_MISMATCH')
    if any(v not in {'PASS', 'FAIL', 'NOT_RUN'} for v in state['checks'].values()):
        raise Blocked('INVALID_CHECK_STATUS')
    for defect in state['defects']:
        if defect['requirement'] not in requirements or defect['status'] != 'OPEN':
            raise Blocked('INVALID_DEFECT_STATE')
    if len({d['id'] for d in state['defects']}) != len(state['defects']):
        raise Blocked('DUPLICATE_DEFECT')
    if not state['artifacts'] or not state['bindings']:
        raise Blocked('MISSING_BINDINGS')
    for b in [*state['bindings'].values(), *state['artifacts'].values()]:
        binding(root, b)
    # Reuse the existing knowledge engine, including its stale-corpus behavior.
    task = read(root, state['knowledge_task'])
    fresh = pk.task_packet(root, task)
    if not fresh['dispatch_ready'] or fresh['packet_digest'] != state['knowledge_digest']:
        raise Blocked('STALE_OR_BLOCKED_KNOWLEDGE')
    # Every current routed obligation must be explicitly reconciled, not silently
    # removed by calling a whole-production failure a scoped review.
    mappings = contract['knowledge_mapping']
    if set(mappings) != {r['id'] for r in fresh['obligations']}:
        raise Blocked('KNOWLEDGE_COVERAGE_GAP')
    for mapping in mappings.values():
        if not mapping['reason'].strip() or not mapping['checks'] or not set(mapping['checks']) <= set(requirements):
            raise Blocked('INVALID_KNOWLEDGE_MAPPING')
    engine = {name: pk.file_hash(path(root, name)) for name in (
        'src/movie_factory/review_control.py', 'src/movie_factory/production_knowledge.py')}
    fingerprint = pk.digest({'registry': registry, 'contract': contract, 'state': state,
                             'knowledge': fresh['packet_digest'], 'engine': engine})
    return contract, state, fingerprint


def capsule(root):
    c, s, digest = load(root)
    # No builder success story, historical manifests or repeated evidence lists.
    return {'schema': 1, 'fingerprint': digest, 'intent': c['intent'],
            'protected': c['protected'], 'exclusions': c['exclusions'],
            'requirements': c['requirements'], 'current_checks': s['checks'],
            'open_defects': s['defects'], 'references': s['bindings'],
            'artifacts': s['artifacts'], 'capabilities': s['capabilities'],
            'next_transition': 'INTERNAL_REVIEW_ONLY; deliver must revalidate; no production approval',
            'limits': 'Evidence declarations are not a perceptual oracle. No paid/cloud/production authority.'}


def assess(root, review):
    c, s, digest = load(root)
    failures = []
    if review.get('fingerprint') != digest:
        failures.append('STALE_REVIEW')
    if review.get('purpose') != 'scoped_review':
        failures.append('UNSUPPORTED_HANDOFF_PURPOSE')
    if review.get('candidate') != s['artifacts']:
        failures.append('CANDIDATE_MISMATCH')
    checks = unique(review.get('checks', []))
    wanted = unique(c['requirements'])
    if set(checks) != set(wanted):
        failures.append('CHECK_COVERAGE_MISMATCH')
    evidence = review.get('evidence', {})
    if not isinstance(evidence, dict):
        raise Blocked('INVALID_EVIDENCE')
    for evidence_id, e in evidence.items():
        if not evidence_id or e.get('mode') not in MODES or not e.get('observation_scope', '').strip():
            failures.append('INVALID_EVIDENCE_DESCRIPTOR')
            continue
        binding(root, e['binding'])
        # A declared modality must be available in this qualified review route.
        if s['capabilities'].get(e['mode']) is not True:
            failures.append('UNAVAILABLE_EVIDENCE_MODE:' + evidence_id)
        if e.get('candidate_digest') != pk.digest(s['artifacts']):
            failures.append('EVIDENCE_CANDIDATE_MISMATCH:' + evidence_id)
    for rid, requirement in wanted.items():
        row = checks.get(rid, {})
        if row.get('status') != 'PASS':
            failures.append(rid + ':NOT_PASS')
        if not row.get('observation', '').strip() or not row.get('comparison', '').strip():
            failures.append(rid + ':MISSING_OBSERVATION_COMPARISON')
        refs = row.get('evidence', [])
        if not isinstance(refs, list) or not refs or any(ref not in evidence for ref in refs):
            failures.append(rid + ':MISSING_EVIDENCE')
        else:
            modes = {evidence[ref]['mode'] for ref in refs}
            if not set(requirement['modes']) <= modes:
                failures.append(rid + ':WRONG_EVIDENCE_MODE')
        # Open failures cannot become PASS through a row edit alone.
        for defect in s['defects']:
            if defect['requirement'] == rid:
                closure = review.get('defect_closures', {}).get(defect['id'], {})
                if (row.get('status') != 'PASS' or not closure.get('test', '').strip()
                        or not closure.get('observation', '').strip()
                        or not closure.get('evidence')
                        or not set(closure['evidence']) <= set(refs)):
                    failures.append('OPEN_DEFECT:' + defect['id'])
    if set(review.get('defect_closures', {})) - {d['id'] for d in s['defects']}:
        failures.append('UNKNOWN_DEFECT_CLOSURE')
    adjacent = review.get('adjacent_review', {})
    if not adjacent.get('observation', '').strip() or adjacent.get('status') != 'PASS' or not adjacent.get('evidence'):
        failures.append('MISSING_OR_FAILED_ADJACENT_REVIEW')
    elif not set(adjacent['evidence']) <= set(evidence):
        failures.append('INVALID_ADJACENT_EVIDENCE')
    return {'ready_for_scoped_review': not failures, 'production_approved': False,
            'director_approved': False, 'fingerprint': digest,
            'failures': sorted(set(failures)),
            'limits': 'Checks evidence bindings, scope and declarations, not artistic truth or arbitrary chat.'}


def deliver(root, review, output):
    result = assess(root, review)
    if not result['ready_for_scoped_review']:
        return result
    # Receipt is immutable; every invocation revalidates, never trusts old PASS.
    dest = path(root, output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    receipt = {**result, 'review_digest': pk.digest(review), 'artifacts': review['candidate']}
    with dest.open('x') as f:
        json.dump(receipt, f, indent=2)
        f.write('\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('command', choices=['capsule', 'check', 'deliver'])
    parser.add_argument('--review')
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    try:
        if args.command == 'capsule':
            result = capsule(args.root)
        else:
            review = read(args.root, args.review)
            result = (deliver(args.root, review, args.output) if args.command == 'deliver'
                      else assess(args.root, review))
        print(json.dumps(result, indent=2))
        return 0 if result.get('ready_for_scoped_review', True) else 2
    except (Blocked, pk.KnowledgeError, OSError, ValueError, TypeError, KeyError, AttributeError) as e:
        print(json.dumps({'ready_for_scoped_review': False, 'error': str(e)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
