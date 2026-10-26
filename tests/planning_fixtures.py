"""Synthetic offline artifacts. Not a production planner or admission judgment."""
from copy import deepcopy
from movie_factory import planning_pipeline as pp


def direction_fields(brief):
    binding = next(b for b in brief['source_bindings'].values() if b['path'] == brief['knowledge_task'])
    return {'knowledge_task': brief['knowledge_task'], 'knowledge_digest': brief['knowledge_digest'],
        **({'reference_scope':brief['reference_readiness']['scope']} if 'reference_readiness' in brief else {}),
        'context_sources': [{'id': c, 'category': c, 'binding': binding, 'status': 'adopted',
            'required': True, 'statement': 'Synthetic ' + c, 'scope': 'Offline control fixture only'} for c in pp.CATEGORIES]}


def result(packet, brief):
    step = packet['planning_step']
    ids = [r['id'] for r in brief['requirements']]
    mappings = {s['id']: {'requirements': [ids[0]], 'reason': 'Synthetic grounded application'} for s in packet['direction']['context_sources']}
    p = brief['expert_plan']
    if step == 'GROUNDING':
        data = {'uses': {s: {'disposition': 'apply', 'reason': 'Synthetic applicability',
                            'implication': 'Synthetic ' + s} for s in mappings},
            'knowledge_uses': {s: 'Synthetic obligation application' for s in brief['knowledge_mapping']},
            'reconciliation': 'Synthetic corpus reconciled, no universal recall claim', 'unresolved': []}
    elif step == 'DERIVING':
        data = {'requirements': brief['requirements'], 'beats': p['beats'],
            'derivations': {rid: {k: m[k] for k in pp.DERIVATION_FIELDS} for rid, m in p['realizations'].items()},
            'context_mapping': mappings, 'knowledge_mapping': brief['knowledge_mapping']}
    elif step == 'STRATEGIZING':
        data = {'brief': brief, 'method_choice': {'chosen': 'Synthetic pose proof', 'alternatives': 'Reject synthetic retiming only',
            'evidence_status': 'hypothesis', 'discriminating_test': 'Synthetic whole pose comparison'},
            'steps': [{'id': 'proof', 'depends_on': [], 'requirements': ids, 'kind': 'proof', 'acceptance': 'Synthetic reference comparison'},
                      {'id': 'build', 'depends_on': ['proof'], 'requirements': ids, 'kind': 'build', 'acceptance': 'Synthetic integrated evidence'}],
            'resource_scope': 'No calls or render; fixture only', 'replan_triggers': 'Synthetic bad supported pose'}
    else:
        value = {'input_digest': packet['planning_input_digest'], 'outcome': 'admit', 'issues': [],
            'checks': {f: {'status': 'PASS', 'observation': 'Synthetic facet observation', 'comparison': 'Synthetic original intent',
                           'source_ids': [next(iter(mappings))]} for f in pp.FACETS},
            'strongest_counterexample': 'Synthetic semantic result is not real film qualification'}
        if 'reference_readiness' in brief:
            from reference_fixtures378 import challenge
            value['reference_challenge']=challenge(brief['reference_readiness'])
        return value
    if 'reference_readiness' in brief and step in {'GROUNDING','DERIVING'}:
        data['reference_readiness']=deepcopy(brief['reference_readiness'])
        if step=='DERIVING':data['reference_mapping']=deepcopy(brief['reference_mapping'])
    return deepcopy({'input_digest': packet['planning_input_digest'], 'outcome': 'complete', 'artifact': data})


def complete(controller, task, brief, prefix):
    for _ in range(4):
        packet = controller.packet(task)
        if packet['stage'] != 'BRIEFING': break
        state = controller.submit(task, packet['actor'], packet['ticket'], result(packet, brief), prefix + '-' + packet['planning_step'])
    return state
