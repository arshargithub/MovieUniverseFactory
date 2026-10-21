"""Synthetic shape fixtures ONLY; never production plans or expert judgments."""
from movie_factory import expert_planning as ep


def attach(brief):
    ids = [r['id'] for r in brief['requirements']]
    brief['expert_plan'] = {
        'version': 1, 'beat_intents': {'beat': 'Synthetic supported action'},
        'beats': [{'id': 'beat', 'audience_read': 'Synthetic weight', 'framing': 'Synthetic whole body',
                   'lenses': {n: {'applies': n == 'animation_physics', 'why': 'Synthetic focused fixture, not production',
                                  'requirements': ids if n == 'animation_physics' else []} for n in ep.LENSES}}],
        'realizations': {rid: {'beats': ['beat'], 'lenses': ['animation_physics'],
            'derivation': 'Synthetic intent derivation', 'method': 'Synthetic pose reconstruction',
            'interfaces': ['Synthetic support and body'], 'early_proof': 'Synthetic crest control',
            'failure_condition': 'Synthetic unsupported body', 'reopen_when': 'Synthetic camera changes',
            'priority': 'quality_floor', 'origin': 'craft_inference',
            'reference_ids': [brief['references'][0]['id']]} for rid in ids}}
    brief['expert_plan']['challenge'] = {
        'plan_digest': ep.plan_digest(brief), 'open_issues': [],
        'intent_coverage': {'beat': {'reason': 'Synthetic complete scope', 'requirements': ids}},
        'cross_discipline_conflicts': 'Synthetic camera and contact alignment',
        'omission_probe': 'Synthetic adjacent knee failure considered',
        'scope_tradeoff': 'Synthetic no microscopic detail'}
    return brief


def uses(brief):
    return {r['id']: {'plan_digest': ep.plan_digest(brief), 'application': 'Synthetic method applied'}
            for r in brief['requirements']}


def intent_checks(brief, status='PASS'):
    return {b: {'status': status, 'scope': 'supported_evidence_only', 'observation': 'Synthetic frame-visible intent read',
                'comparison': 'Synthetic original intent, not builder assurance',
                'evidence': ['frame'] if status != 'NOT_RUN' else []}
            for b in brief['expert_plan']['beat_intents']}
