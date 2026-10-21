"""Director326 routing policy. Model choice is not permission to call or pass."""
from copy import deepcopy

from . import production_knowledge as pk
from .production_workflow import require

SOL = 'gpt-6.1-sol'
ASTRA = 'gpt-6-astra'
ACTORS = ('planner', 'builder', 'reviewer')
TRIGGERS = {'foundational_strategy', 'unsupported_structural_assumption',
            'unresolved_diagnosis', 'contradictory_evidence', 'repeated_missed_defects'}


def policy(profile, escalations=None):
    """Trusted parent chooses task risk; no semantic domain detection claimed."""
    value = {'version': 1, 'profile': profile, 'escalations': escalations or {}}
    validate(value)
    return deepcopy(value)


def validate(value):
    require(isinstance(value, dict) and set(value) == {'version', 'profile', 'escalations'}, 'ROUTING_POLICY_SHAPE')
    require(value['version'] == 1 and value['profile'] in {'general', 'specialist_3d'}, 'ROUTING_PROFILE')
    require(isinstance(value['escalations'], dict) and set(value['escalations']) <= set(ACTORS), 'ROUTING_ACTOR')
    for record in value['escalations'].values():
        require(isinstance(record, dict) and set(record) == {'trigger', 'reason', 'evidence'}, 'ESCALATION_SHAPE')
        require(record['trigger'] in TRIGGERS and isinstance(record['reason'], str) and record['reason'].strip(), 'ESCALATION_REASON')
        require(isinstance(record['evidence'], dict) and bool(record['evidence']), 'ESCALATION_EVIDENCE')
        require(all(isinstance(p, str) and isinstance(h, str) and len(h) == 64
                    for p, h in record['evidence'].items()), 'ESCALATION_BINDING')


def resolve(value, actor, root):
    validate(value)
    require(actor in ACTORS, 'ROUTING_ACTOR')
    # Validate all bindings on each dispatch, including a later review override.
    for record in value['escalations'].values():
        for path, sha in record['evidence'].items():
            source = (root / path).resolve()
            require(source.is_relative_to(root.resolve()) and source.is_file(), 'ESCALATION_PATH')
            require(pk.file_hash(source) == sha, 'STALE_ESCALATION_EVIDENCE')
    escalation = value['escalations'].get(actor)
    specialist = value['profile'] == 'specialist_3d' and actor == 'builder'
    return {'model': ASTRA if specialist or escalation else SOL, 'effort': 'high',
            'actor': actor, 'policy_digest': pk.digest(value),
            'reason': escalation['reason'] if escalation else ('difficult_3d_execution' if specialist else 'default_sol_high'),
            'escalation': escalation}


def validate_route(route, actor):
    require(isinstance(route, dict) and route.get('model') in {SOL, ASTRA}
            and route.get('effort') == 'high' and route.get('actor') == actor
            and isinstance(route.get('policy_digest'), str) and len(route['policy_digest']) == 64,
            'EXPLICIT_RUNTIME_ROUTE_REQUIRED')
