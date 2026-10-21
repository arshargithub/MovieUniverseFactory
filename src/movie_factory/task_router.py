"""First-step routing, not an authority grant or a natural-language oracle.

The trusted agent decomposes the request into operations and records why. The
router conservatively selects the workflow. Misdescribed prose remains a semantic
failure; unknown/mixed effects cannot silently select the cheapest route.
"""
from pathlib import Path
from . import production_knowledge as pk
from . import review_control as rc

OPERATIONS = {
    'display': 'show', 'status': 'show', 'explain': 'show',
    'research': 'research', 'plan': 'plan',
    'code': 'engineering', 'test': 'engineering', 'document': 'engineering',
    'backup': 'operations', 'upload': 'operations', 'publish': 'operations',
    'asset': 'production', 'motion': 'production', 'render': 'production',
    'sound': 'production', 'edit': 'production', 'native_inspect': 'production',
}
DATABASE = '.runtime/factory-entry.sqlite3'


def decide(request, parent=None):
    def need(ok, message):
        if not ok:
            raise ValueError(message)
    need(isinstance(request, dict), 'REQUEST_REQUIRED')
    for key in ('text', 'rationale'):
        need(isinstance(request.get(key), str) and request[key].strip(), 'ROUTING_' + key.upper())
    ops = request.get('operations')
    need(isinstance(ops, list) and ops and all(isinstance(o, str) for o in ops)
         and len(ops) == len(set(ops)) and set(ops) <= set(OPERATIONS), 'UNKNOWN_OR_MISSING_OPERATIONS')
    routes = {OPERATIONS[o] for o in ops}
    if request.get('continuation'):
        need(parent is not None, 'CONTINUATION_REQUIRES_EXISTING_TASK')
        need(set(ops) <= set(parent['request']['operations']), 'CONTINUATION_SCOPE_EXPANSION')
        route = parent['route']
    elif 'production' in routes:
        route = 'production'
    else:
        # A compound engineering/research request stays light, but all requested
        # effects remain recorded. External effects never acquire permission here.
        route = next(r for r in ('operations', 'engineering', 'plan', 'research', 'show') if r in routes)
    return {'schema': 1, 'route': route, 'production_workflow': route == 'production',
            'request': request, 'authority_granted': False,
            'semantic_classification': 'agent_declared_operations',
            'engine': pk.file_hash(Path(__file__))}


def validate(root, decision):
    rc.binding(root, decision['request']['authority'])
    if decision['engine'] != pk.file_hash(Path(__file__)):
        raise ValueError('ROUTER_CHANGED_RECONCILE_REQUEST')


def main(argv=None):
    import argparse
    import json
    from .production_workflow import Controller
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.cwd())
    p.add_argument('--request', required=True, help='Reviewed JSON, never credentials')
    p.add_argument('--id', required=True)
    p.add_argument('--continue-task')
    a = p.parse_args(argv)
    try:
        c = Controller(a.root, DATABASE)
        result = c.route_request(a.id, pk.read_json(a.root, a.request), a.continue_task)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as e:
        print(json.dumps({'blocked': True, 'error': str(e)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
