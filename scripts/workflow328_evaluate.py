"""Offline, known-history planning reconstruction. No model, scene or provider call."""
import copy
import json
from pathlib import Path
from movie_factory import expert_planning as ep
from movie_factory import production_knowledge as pk
from movie_factory.production_workflow import Blocked

ROOT = Path(__file__).resolve().parents[1]


def reconstruct(case):
    requirements = [{'id': r['id'], 'criterion': r['failure']} for r in case['requirements']]
    plan = {'version': 1, 'beat_intents': case['beats'], 'beats': [], 'realizations': {}}
    for bid, intent in case['beats'].items():
        lenses = {}
        for lens in ep.LENSES:
            relevant = [r for r in case['requirements'] if bid in r['beats'] and lens in r['lenses']]
            lenses[lens] = {'applies': bool(relevant), 'requirements': [r['id'] for r in relevant],
                'why': ' '.join(r['derivation'] for r in relevant) if relevant else case['unused'].get(lens,
                    'No separate requirement owned by this lens in this beat; coupled concerns are linked in the other applicable beat/lens rows. Reassess if framing or scope changes.')}
        plan['beats'].append({'id': bid, 'audience_read': intent, 'framing': case['framing'][bid], 'lenses': lenses})
    for r in case['requirements']:
        plan['realizations'][r['id']] = {**{k: r[k] for k in ('beats', 'lenses', 'derivation', 'method', 'interfaces')},
            'early_proof': r['proof'], 'failure_condition': r['failure'],
            'reopen_when': 'Camera, source authority, performance, contacts or coupled assets change; previous evidence no longer covers the shot.',
            'priority': 'quality_floor', 'origin': 'craft_inference', 'reference_ids': ['cutoff-direction']}
    b = {'intent': case['intent'], 'protected': ['Existing creative authority; no production change in this evaluation'],
         'references': [{'id': 'cutoff-direction', 'role': case['reference_role']}],
         'requirements': requirements, 'expert_plan': plan}
    plan['challenge'] = {'plan_digest': ep.plan_digest(b), 'open_issues': [],
        'intent_coverage': {bid: {'reason': intent, 'requirements': [r['id'] for r in case['requirements'] if bid in r['beats']]}
                            for bid, intent in case['beats'].items()},
        'cross_discipline_conflicts': case['challenge'], 'omission_probe': case['challenge'],
        'scope_tradeoff': 'Early representative proof before polish. No exact later Director preference is made mandatory; this is a planning hypothesis, not approved scene dispatch.'}
    return b


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    cases = json.loads((ROOT / 'results/workflow328/cases.json').read_text())['cases']
    history_path = ROOT / '.runtime/production-audit250/history.json'
    history = json.loads(history_path.read_text())
    messages = {m['id']: m for m in history['messages']}
    results = []
    for case in cases:
        folder = output / case['id']; folder.mkdir()
        if case.get('cutoff_message'):
            source = messages[case['cutoff_message']]
            ids = case.get('additional_input_messages', []) + [case['cutoff_message']]
            for mid in ids: assert messages[mid]['source_byte_offset'] <= source['source_byte_offset']
            prior = [{'message_id': mid, 'timestamp': messages[mid]['timestamp'],
                      'source_byte_offset': messages[mid]['source_byte_offset'], 'text': messages[mid]['text']}
                     for mid in ids]
            feedback = []
            for mid in case['later_messages']:
                m = messages[mid]
                assert m['source_byte_offset'] > source['source_byte_offset']
                feedback.append({'message_id': mid, 'timestamp': m['timestamp'],
                    'source_byte_offset': m['source_byte_offset'], 'text': m['text']})
        else:
            path = ROOT / case['cutoff_file']
            prior = [{'path': case['cutoff_file'], 'sha256': pk.file_hash(path), 'text': path.read_text()}]
            feedback = [{'path': p, 'sha256': pk.file_hash(ROOT / p)} for p in case['later_files']]
        # Distinct files make the temporal boundary inspectable. The author had
        # already seen later history; this segregation does NOT make it blind.
        (folder / 'prior-input.json').write_text(json.dumps(prior, indent=2) + '\n')
        (folder / 'later-feedback.json').write_text(json.dumps(feedback, indent=2) + '\n')
        b = reconstruct(case); ep.validate(b)
        (folder / 'reconstructed-plan.json').write_text(json.dumps(b, indent=2) + '\n')
        blocked = []
        for mutation in ('omit_lens', 'omit_method', 'stale_challenge'):
            bad = copy.deepcopy(b)
            if mutation == 'omit_lens': del bad['expert_plan']['beats'][0]['lenses']['camera_editorial']
            elif mutation == 'omit_method': del next(iter(bad['expert_plan']['realizations'].values()))['method']
            else: bad['expert_plan']['challenge']['plan_digest'] = 'stale'
            try: ep.validate(bad)
            except Blocked: blocked.append(mutation)
        assert len(blocked) == 3
        semantic = copy.deepcopy(b)
        next(iter(semantic['expert_plan']['realizations'].values()))['method'] = 'Ignore the actual audience intent and keep every moving subject rigid.'
        semantic['expert_plan']['challenge']['plan_digest'] = ep.plan_digest(semantic)
        ep.validate(semantic)  # Expected blind spot. Never count as quality success.
        results.append({'id': case['id'], 'requirements': len(b['requirements']),
            'beats': len(case['beats']), 'structural_negative_controls_blocked': blocked,
            'well_formed_bad_method_passes_schema': True,
            'assessment': case['outcome'], 'enhancement_hypothesis': case['enhancement']})
    result = {'method': 'Retrospective, analyst-authored, known history; no fresh model generation or blind predictive evaluation.',
        'history_capture_sha256': pk.file_hash(history_path),
        'cases_sha256': pk.file_hash(ROOT / 'results/workflow328/cases.json'),
        'structural_controls': '12/12 rejected malformed mutations; 4/4 well-formed bad methods passed, exposing semantic limitation.',
        'results': results, 'director_inputs_saved_measured': None, 'quality_uplift_measured': None,
        'production_approved': False, 'live_calls': 0}
    (output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    report = run(ROOT / 'results/workflow328/evaluation')
    print(json.dumps({'cases': len(report['results']), 'structural_controls': report['structural_controls'],
                      'blind': False, 'production_approved': False}))
