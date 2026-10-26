"""Director360 Sol defaults and explicitly approved, bounded Astra assignments."""
from copy import deepcopy

from . import production_knowledge as pk
from .production_workflow import require

SOL = 'gpt-6.1-sol'
ASTRA = 'gpt-6-astra'
ACTORS = ('planner', 'builder', 'reviewer')
TRIGGERS = {'foundational_strategy', 'unsupported_structural_assumption',
            'unresolved_diagnosis', 'contradictory_evidence', 'repeated_missed_defects'}
SCOPE_KEYS = ('task', 'actor', 'stage', 'cycle', 'planning_step', 'planning_input_digest',
              'fingerprint', 'authority', 'direction', 'retrospective', 'candidate',
              'source_context', 'grounding_knowledge', 'direction_revision', 'reference_escalation_basis')


def scope_digest(packet):
    require(isinstance(packet, dict) and all(k in packet for k in ('task', 'actor', 'stage', 'cycle')),
            'ESCALATION_SCOPE_CONTEXT_REQUIRED')
    return pk.digest({k: packet[k] for k in SCOPE_KEYS if k in packet})


def _binding(value):
    return (isinstance(value, dict) and set(value) == {'path', 'sha256'}
            and isinstance(value['path'], str) and bool(value['path'])
            and isinstance(value['sha256'], str) and len(value['sha256']) == 64)


def _source(root, binding, error):
    require(_binding(binding), error)
    p = (root / binding['path']).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(), error)
    require(pk.file_hash(p) == binding['sha256'], error)
    return p


def policy(profile, escalations=None):
    """Trusted parent chooses task risk; no semantic domain detection claimed."""
    value = {'version': 2, 'profile': profile, 'escalations': escalations or {}}
    validate(value)
    return deepcopy(value)


def validate(value):
    require(isinstance(value, dict) and set(value) == {'version', 'profile', 'escalations'}, 'ROUTING_POLICY_SHAPE')
    require(value['version'] != 1, 'LEGACY_ROUTING_REQUIRES_RECONCILIATION')
    require(value['version'] == 2 and value['profile'] in {'general', 'specialist_3d'}, 'ROUTING_PROFILE')
    require(isinstance(value['escalations'], dict) and set(value['escalations']) <= set(ACTORS), 'ROUTING_ACTOR')
    for record in value['escalations'].values():
        require(isinstance(record, dict) and set(record) == {'id', 'trigger', 'reason', 'evidence',
                'retrospective', 'assignment', 'director_approval'}, 'ESCALATION_APPROVAL_REQUIRED')
        require(isinstance(record['id'], str) and 0 < len(record['id']) <= 128, 'ESCALATION_ID')
        require(record['trigger'] in TRIGGERS and isinstance(record['reason'], str) and record['reason'].strip(), 'ESCALATION_REASON')
        require(isinstance(record['evidence'], dict) and bool(record['evidence']), 'ESCALATION_EVIDENCE')
        require(all(isinstance(p, str) and isinstance(h, str) and len(h) == 64
                    for p, h in record['evidence'].items()), 'ESCALATION_BINDING')
        require(_binding(record['retrospective']) and _binding(record['director_approval']),
                'ESCALATION_APPROVAL_REQUIRED')
        a = record['assignment']
        require(isinstance(a, dict) and set(a) == {'task', 'packet_digest', 'runner_database', 'max_calls', 'expected_output', 'success_test'},
                'ESCALATION_ASSIGNMENT')
        require(isinstance(a['task'], str) and bool(a['task']) and isinstance(a['packet_digest'], str)
                and len(a['packet_digest']) == 64 and type(a['max_calls']) is int and 1 <= a['max_calls'] <= 4
                and all(isinstance(a[k], str) and a[k].strip() for k in ('runner_database', 'expected_output', 'success_test')),
                'ESCALATION_ASSIGNMENT')


def approved(record, root):
    """Verify trusted-parent records; hashes do not authenticate a human identity."""
    for path, sha in record['evidence'].items():
        _source(root, {'path': path, 'sha256': sha}, 'STALE_ESCALATION_EVIDENCE')
    _source(root, record['retrospective'], 'STALE_RETROSPECTIVE_EVIDENCE')
    p = _source(root, record['director_approval'], 'STALE_DIRECTOR_APPROVAL')
    a = pk.read_json(root, str(p.relative_to(root.resolve())))
    require(a.get('decision') == 'approve_astra_escalation' and a.get('assignment') ==
            {k: v for k, v in record.items() if k != 'director_approval'}, 'DIRECTOR_APPROVAL_SCOPE_MISMATCH')
    require(isinstance(a.get('director_reply'), str) and bool(a['director_reply'].strip()), 'DIRECTOR_REPLY_REQUIRED')
    _source(root, a.get('source'), 'DIRECTOR_APPROVAL_SOURCE_REQUIRED')


def resolve(value, actor, root, packet=None, used_calls=0):
    validate(value)
    require(actor in ACTORS, 'ROUTING_ACTOR')
    escalation = value['escalations'].get(actor)
    require(type(used_calls) is int and used_calls >= 0, 'ESCALATION_USAGE')
    reason = 'default_sol_high'
    if escalation:
        current = scope_digest(packet)
        a = escalation['assignment']
        if a['task'] != packet['task'] or a['packet_digest'] != current:
            escalation, reason = None, 'assignment_scope_expired'
        elif used_calls >= a['max_calls']:
            escalation, reason = None, 'assignment_call_limit_reached'
        else:
            approved(escalation, root)
            from . import reference_readiness as rr
            rr.escalation(root, packet)
            reason = escalation['reason']
    return {'model': ASTRA if escalation else SOL, 'effort': 'high',
            'actor': actor, 'policy_digest': pk.digest(value),
            'reason': reason, 'escalation': escalation,
            'assignment_call': used_calls + 1 if escalation else None}


def validate_route(route, actor):
    require(isinstance(route, dict) and route.get('model') in {SOL, ASTRA}
            and route.get('effort') == 'high' and route.get('actor') == actor
            and isinstance(route.get('policy_digest'), str) and len(route['policy_digest']) == 64,
            'EXPLICIT_RUNTIME_ROUTE_REQUIRED')
    if route['model'] == ASTRA:
        policy('general', {actor: route.get('escalation')})
        call = route.get('assignment_call')
        require(type(call) is int and 1 <= call <= route['escalation']['assignment']['max_calls'], 'ESCALATION_CALL_LIMIT')
    else:
        require(route.get('escalation') is None and route.get('assignment_call') is None, 'ROUTING_MODEL_CONTRADICTION')


def validate_request(request, root):
    route = request.get('runtime_route')
    validate_route(route, request['actor'])
    if route['model'] == ASTRA:
        e = route['escalation'];a = e['assignment']
        require(a['task'] == request.get('task') and a['packet_digest'] == scope_digest(request), 'ESCALATION_SCOPE_MISMATCH')
        approved(e, root)
        from . import reference_readiness as rr
        rr.escalation(root, request)
