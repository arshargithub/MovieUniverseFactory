"""Reproduce offline state-machine replay, not a fresh artistic qualification.

Uses existing media without rendering, uploading or executing model calls.
Output must be a new repo-local directory. Retains exact failed/accepted scope.
"""
import argparse
import json
from pathlib import Path

from movie_factory import production_knowledge as pk
from movie_factory.production_workflow import Controller, Blocked


ROOT = Path(__file__).resolve().parents[1]
TASK = 'results/workflow323/task.json'
AUTHORITY = 'results/workflow323/STRATEGY.md'
NEGATIVE = '.runtime/art-direction/series01-sikh320/delivery-10/nihang-crowd-review.mp4'
POSITIVE = '.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
REFERENCE = '.runtime/art-direction/series01-sikh256/references/reference-b.mov'
APPEARANCE = 'results/sikh321/preserved-comparisons/appearance.jpg'
PHASES = 'results/sikh321/preserved-comparisons/phase-comparison.jpg'


def binding(path):
    return {'path': path, 'sha256': pk.file_hash(ROOT / path)}


def ref(rid, role, path, scope, fidelity, allowed, not_authority, instruction):
    result = {'id': rid, 'role': role, 'binding': binding(path),
              'authority': 'Director323 reference roles; prior321 rejection or253 acceptance as applicable',
              'scope': scope, 'fidelity': fidelity, 'allowed_variation': allowed,
              'not_authority': not_authority,
              'aspects': [{'id': 'screen_requirement', 'instruction': instruction, 'requirements': ['visible']}]}
    if role == 'faithful_motion':
        result['time_range_seconds'] = [14, 19]
        result['aspects'].append({'id': 'full_speed_performance', 'instruction': 'Compare rhythm, fluidity, weight and landing at full speed',
                                  'requirements': ['temporal']})
    return result


def make_brief(positive=False):
    packet = pk.task_packet(ROOT, pk.read_json(ROOT, TASK))
    refs = [ref('accepted_film', 'exact_asset' if positive else 'accepted_quality', POSITIVE,
                'Exact provisional accepted20s reuse' if positive else 'Visible production construction quality',
                'Preserve bytes and approval scope' if positive else 'Same-film visible forms and materials',
                'No changes to accepted clip' if positive else 'Different character, costume, lighting and action',
                'No release approval, strict renderer replay qualification or identity transfer',
                'Compare applicable acceptance scope, not pixel-match different characters')]
    if not positive:
        refs += [ref('rear_motion', 'faithful_motion', REFERENCE, '14–19s horse/rider rearing',
                     'Faithful coordinated gather, drive, active crest, descent, weight and recovery',
                     'Production camera, actor identity and scenery within accepted direction',
                     'Not motion capture, measured force data or permission to copy incidental background',
                     'Compare whole-body pose transitions and contact, not just nonzero keyframes'),
                 ref('rejected320', 'negative_control', NEGATIVE, 'Known rejected leader/rearing passage',
                     'Must not be admitted unchanged', 'Use only for diagnosis and regression tests',
                     'Not an accepted aesthetic target', 'Reject the same failed bytes and visible defects')]
    paths = [TASK, AUTHORITY, 'docs/knowledge/NIHANG_REARING_REVIEW_FAILURE_321.md',
             'results/sikh321/disposition.json', 'docs/knowledge/CURRENT_PRODUCTION_STATE.md']
    return {'schema': 1, 'route': 'production', 'offline_only': True,
            'intent': 'Offline replay of known candidate disposition, not scene repair',
            'audience_result': 'Prevent another known failed handoff while preserving exact accepted work',
            'strategy': 'Replay stage contracts with source-bound audit judgments',
            'early_proof': 'Appearance failure and negative-control bytes veto pending human AV queue',
            'scope': 'Offline existing-evidence replay', 'exclusions': 'Rendering, live models, paid calls, upload, release',
            'protected': ['Accepted Pashtun20s unchanged; no native/source media edits'], 'open_decisions': [],
            'source_bindings': {str(i): binding(p) for i, p in enumerate(paths)},
            'knowledge_task': TASK, 'knowledge_digest': packet['packet_digest'],
            'knowledge_mapping': {r['id']: {'requirements': ['visible'],
                'reason': 'Offline policy replay only; source audit and strategy reconcile this obligation, not new production qualification'}
                for r in packet['obligations']},
            'requirements': [
                {'id': 'visible', 'criterion': 'No known visible same-film or pose failure in claimed scope', 'modes': ['image'], 'director_av': False},
                {'id': 'temporal', 'criterion': 'Full-speed audiovisual judgment remains with Director', 'modes': ['direct_motion', 'direct_audio'], 'director_av': True}],
            'capabilities': {'image': True, 'timed_images': True, 'technical': True, 'authority': True,
                             'direct_motion': False, 'direct_audio': False},
            'references': refs, 'reference_plan': {r['id']: {'reference_digest': pk.digest(r),
                'application': r['aspects'][0]['instruction']} for r in refs}}


def send(c, task, result, eid):
    p = c.packet(task)
    return c.submit(task, p['actor'], p['ticket'], result, eid)


def run_case(c, task, brief, positive):
    c.create(task, 'production', binding(AUTHORITY), task + '-create', 2,
             {**{k: brief[k] for k in ('intent', 'references', 'protected')}, 'deliverable_id': task + '-scope'})
    planner_packet = c.packet(task)
    send(c, task, brief, task + '-brief')
    verdicts = []
    for i in range(1 if positive else 3):
        p = c.packet(task)
        candidate = {'version': f'offline-replay-{i}', 'artifacts': {'clip': binding(POSITIVE if positive else NEGATIVE)}}
        send(c, task, {'fingerprint': p['fingerprint'], 'candidate': candidate,
            'reference_uses': {r['id']: {'reference_digest': pk.digest(r),
                'application': 'Replay preserved source; no implementation claim. ' + r['fidelity']} for r in brief['references']}}, task + f'-build-{i}')
        p = c.packet(task)
        evidence = {'appearance': {'binding': binding(APPEARANCE), 'mode': 'image',
                    'scope': 'Right accepted Pashtun comparator only' if positive else 'Leader outfit and saddle versus accepted comparator',
                    'candidate_digest': pk.digest(candidate)},
                    'poses': {'binding': binding(PHASES), 'mode': 'timed_images',
                    'scope': 'Audited reference/candidate poses, not direct playback', 'candidate_digest': pk.digest(candidate)}}
        observation = ('Exact accepted Pashtun byte reuse; right comparator has readable layered cloth and supported forms. '
                       'Prior253 approval is retained, not newly conferred; strict renderer replay remains failed.' if positive else
                       'Candidate has long straight hind support and column-like neck at crest; outfit reads as shell and saddle as slab. '
                       'Reference shows compact bent support, tucked forelegs and changing arch. Existing321 rejection retained.')
        status = 'PASS' if positive else 'FAIL'
        review = {'fingerprint': p['fingerprint'], 'candidate_digest': pk.digest(candidate),
            'checks': [{'id': 'visible', 'status': status, 'observation': observation,
                        'comparison': 'Reference roles and known authority explicitly scoped', 'evidence': ['appearance']},
                       {'id': 'temporal', 'status': 'NOT_RUN', 'observation': 'No new direct AV perception',
                        'comparison': 'Director313 route; historical acceptance/rejection preserved', 'evidence': []}],
            'evidence': evidence, 'reference_checks': {r['id']: {
                'reference_digest': pk.digest(r), 'observation': observation,
                'comparison': r['fidelity'] + '; not authority for: ' + r['not_authority'],
                'evidence': ['poses', 'appearance'] if r['id'] == 'rear_motion' else ['appearance'],
                'aspects': [{'id': a['id'], 'status': 'NOT_RUN' if a['requirements'] == ['temporal'] else status,
                            'observation': 'Director full-speed reference comparison pending' if a['requirements'] == ['temporal'] else observation}
                           for a in r['aspects']]}
                for r in brief['references']},
            'audience_read': observation, 'strongest_counterexample': 'No new temporal judgment and no general review qualification',
            'adjacent_review': 'Offline fixture does not modify native assets or certify other shots',
            'open_visible_defects': [] if positive else ['D321-01', 'D321-02', 'D321-03', 'D321-04']}
        result = send(c, task, review, task + f'-review-{i}')
        verdicts.append({'cycle': i, 'stage': result['stage'], 'findings': result['findings']})
    delivered = None
    try: delivered = c.deliver(task, task + '-deliver')['receipt']
    except Blocked as error: delivered = {'blocked': str(error)}
    return {'brief': brief, 'planner_reference_ids': [r['id'] for r in planner_packet['direction']['references']],
            'verdicts': verdicts, 'delivery': delivered, 'events': c.events(task)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT / 'results' / 'workflow323') or output.exists():
        raise ValueError('New output directory within results/workflow323 required')
    output.mkdir(parents=True)
    c = Controller(ROOT, str((output / 'controller.sqlite3').relative_to(ROOT)))
    results = {'scope': 'Offline policy replay using known judgments; not blinded perceptual validation',
               'negative': run_case(c, 'rejected320', make_brief(), False),
               'positive': run_case(c, 'accepted253-reuse', make_brief(True), True)}
    directional = ref('sikh_direction', 'directional_design',
        '.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
        'Principal Sikh illustrated identity, not Nihang leader identity',
        'Rugged elongated face, broad natural beard and painted presence',
        'Coherent native proportions, unseen geometry and practical construction',
        'Pixel reconstruction, native approval, incidental buildings and generated cloth topology',
        'Judge recognizable protected traits without treating image as literal ground truth')
    results['directional_contract_example'] = directional
    results['limits'] = ['No live agent driver or OS sandbox boundary', 'No automatic perceptual truth check',
                         'Known cases are regressions, not held-out accuracy estimates',
                         'Positive is exact accepted reuse, not new native/render qualification']
    (output / 'replay.json').write_text(json.dumps(results, indent=2) + '\n')
    summary = ['# Offline workflow replay', '', results['scope'], '', '| Case | Transition |', '| --- | --- |']
    for name in ('negative', 'positive'):
        summary.append('| ' + name + ' | ' + ' → '.join(e['stage'] for e in results[name]['events']) + ' |')
    summary += ['', 'No new media or release approval. See replay.json for bound reference contracts, observations and limitations.']
    (output / 'REPLAY.md').write_text('\n'.join(summary) + '\n')
    print(json.dumps({'output': str(output.relative_to(ROOT)), 'negative_stage': c.state('rejected320')['stage'],
                      'positive_stage': c.state('accepted253-reuse')['stage'], 'rendered': False, 'provider_calls': 0}))


if __name__ == '__main__': main()
