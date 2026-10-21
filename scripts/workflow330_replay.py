"""Retrospective authored planning replay through the real controller; no LLM/media work."""
import argparse
import copy
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory import production_workflow as wf
from movie_factory import planning_pipeline as pp
from movie_factory import expert_planning as ep
from workflow328_evaluate import reconstruct

ROOT = Path(__file__).resolve().parents[1]


def binding(name):
    return {'path': name, 'sha256': pk.file_hash(ROOT / name)}


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def prepare(case, packet):
    b = reconstruct(case)
    reqs = [r['id'] for r in case['requirements']]
    for r in b['requirements']:
        r.update(modes=['timed_images'], director_av=False)
    prior = f"results/workflow328/evaluation/{case['id']}/prior-input.json"
    ref = {'id': 'cutoff-direction', 'role': 'directional_design', 'binding': binding(prior),
        'authority': 'Recorded Director input; reconstruction author already knows subsequent feedback',
        'scope': 'Original intent for retrospective planning only, not a media identity reference',
        'fidelity': case['reference_role'], 'allowed_variation': 'Agent-owned method hypotheses',
        'not_authority': 'No production acceptance, exact timing or later creative approval inferred',
        'aspects': [{'id': 'intent', 'instruction': case['intent'], 'requirements': reqs}]}
    source_paths = {'direction': prior,
        'learnings': 'docs/knowledge/EXPERT_LENS_PLANNING_328.md',
        'film_language': 'docs/planning/SERIES_01_ART_DIRECTION_C.md',
        'director_preferences': 'docs/planning/PLANNING_SUBSTAGES_329.md',
        'references': prior, 'controls': 'docs/knowledge/NIHANG_REARING_REVIEW_FAILURE_321.md',
        'constraints': 'results/workflow330/STRATEGY.md', 'task': 'results/workflow330/task.json'}
    sources = []
    for sid, path in source_paths.items():
        count = len((ROOT / path).read_text().splitlines())
        sources.append({'id': sid, 'category': 'constraints' if sid == 'task' else sid,
            'binding': binding(path), 'status': 'historical' if sid == 'controls' else 'adopted',
            'required': True, 'statement': 'Use bounded current source for this known-history reconstruction; not blind pre-cutoff evidence',
            'scope': 'Offline planning test; production requirements require a new domain-specific task packet',
            'lines': [1, min(count, 35)]})
    b.update(schema=1, route='production', audience_result=case['enhancement'],
        strategy='; '.join(r['method'] for r in case['requirements']),
        early_proof='; '.join(r['proof'] for r in case['requirements']),
        scope='Known-history offline planning reconstruction', exclusions='No execution, assets, model calls or independent quality claim',
        open_decisions=[], offline_only=True, source_bindings={s['id']: s['binding'] for s in sources},
        knowledge_task='results/workflow330/task.json', knowledge_digest=packet['packet_digest'],
        knowledge_mapping={o['id']: {'requirements': reqs, 'reason': o['action']} for o in packet['obligations']},
        capabilities={m: m not in {'direct_audio', 'direct_motion'} for m in wf.rc.MODES},
        references=[ref], reference_plan={'cutoff-direction': {'reference_digest': pk.digest(ref), 'application': case['challenge']}})
    b['expert_plan']['challenge']['plan_digest'] = ep.plan_digest(b)
    d = {'intent': b['intent'], 'protected': b['protected'], 'references': b['references'],
         'deliverable_id': 'workflow330-replay-' + case['id'], 'beat_intents': case['beats'],
         'knowledge_task': b['knowledge_task'], 'knowledge_digest': b['knowledge_digest'], 'context_sources': sources}
    return d, b


def artifacts(case, d, b, knowledge):
    reqs = [r['id'] for r in b['requirements']]; p = b['expert_plan']
    implication = {
        'direction': case['intent'], 'learnings': case['outcome'],
        'film_language': 'Judge intended shot at the accepted co-star quality floor, not against the rejected predecessor; illustrated is not a waiver for primitive forms.',
        'director_preferences': 'Preserve larger-than-life readable action and efficient quality; routine technical corrections stay internal, creative authority stays Director-owned.',
        'references': case['reference_role'],
        'controls': '321 shows correct requirements can coexist with a failed pose method and generous review; require a discriminating integrated proof.',
        'constraints': 'No media, live model, spend or approval follows from this planning reconstruction.',
        'task': 'Use the current scoped knowledge packet; this is not a new motion/render task.'}
    grounding = {'uses': {s['id']: {'disposition': 'apply', 'reason': implication[s['id']],
                                  'implication': implication[s['id']]} for s in d['context_sources']},
        'knowledge_uses': {o['id']: o['action'] for o in knowledge['obligations']},
        'reconciliation': 'Current328/329/321 sources supplement the bounded pilot. Author knows later feedback. Do not claim prevented Director inputs or universal retrieval.', 'unresolved': []}
    derived = {'requirements': b['requirements'], 'beats': p['beats'],
        'derivations': {rid: {k: m[k] for k in pp.DERIVATION_FIELDS} for rid, m in p['realizations'].items()},
        'context_mapping': {s['id']: {'requirements': reqs, 'reason': implication[s['id']]} for s in d['context_sources']},
        'knowledge_mapping': b['knowledge_mapping']}
    strategy = {'brief': b, 'method_choice': {'chosen': b['strategy'],
        'alternatives': 'Reject isolated cosmetic repair or generic smoothing before coupled proof: ' + case['challenge'],
        'evidence_status': 'hypothesis', 'discriminating_test': b['early_proof']},
        'steps': [{'id': 'proof', 'depends_on': [], 'requirements': reqs, 'kind': 'proof', 'acceptance': b['early_proof']},
                  {'id': 'integrate', 'depends_on': ['proof'], 'requirements': reqs, 'kind': 'build',
                   'acceptance': 'Original intent and intended framing must pass; direct AV stays pending.'}],
        'resource_scope': b['exclusions'], 'replan_triggers': '; '.join(r['failure'] for r in case['requirements'])}
    checks = {}
    source_for = {'grounding': 'learnings', 'expert_coverage': 'direction', 'film_alignment': 'film_language',
        'preferences': 'director_preferences', 'reference_roles': 'references', 'method': 'controls',
        'interfaces': 'controls', 'efficient_quality': 'constraints', 'authority': 'task'}
    for facet, sid in source_for.items():
        checks[facet] = {'status': 'PASS', 'source_ids': [sid], 'observation': implication[sid],
            'comparison': case['challenge'] + ' This admits an attempt, not a successful visual outcome.'}
    challenge = {'outcome': 'admit', 'checks': checks, 'issues': [], 'strongest_counterexample': case['challenge']}
    return dict(zip(pp.STEPS, (grounding, derived, strategy, challenge)))


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    controller = wf.Controller(ROOT, str((output / 'replay.sqlite3').relative_to(ROOT)))
    knowledge = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/workflow330/task.json'))
    assert knowledge['dispatch_ready']
    cases = json.loads((ROOT / 'results/workflow328/cases.json').read_text())['cases']
    results = []
    for case in cases:
        name = case['id']; folder = output / name; folder.mkdir()
        d, b = prepare(case, knowledge); a = artifacts(case, d, b, knowledge)
        controller.create(name, 'production', binding('results/workflow330/STRATEGY.md'), name+'-create', direction=d)
        sizes = []; blocked = []
        for step in pp.STEPS:
            packet = controller.packet(name); sizes.append(len(json.dumps(packet).encode()))
            write(folder / (step.lower()+'-packet.json'), {k: v for k, v in packet.items() if k != 'ticket'})
            result = dict(a[step], input_digest=packet['planning_input_digest']) if step == 'CHALLENGING' else {
                'input_digest': packet['planning_input_digest'], 'outcome': 'complete', 'artifact': a[step]}
            bad = copy.deepcopy(result)
            if step == 'GROUNDING': del bad['artifact']['uses']['film_language']
            if step == 'DERIVING': bad['artifact']['context_mapping']['director_preferences']['requirements'] = []
            if step == 'STRATEGIZING': bad['artifact']['brief']['intent'] = 'Disregard original intent'
            if step == 'CHALLENGING': bad['checks']['method']['status'] = 'NOT_RUN'
            try: controller.submit(name, packet['actor'], packet['ticket'], bad, name+'-bad-'+step)
            except ValueError as error: blocked.append({'stage': step, 'reason': str(error)})
            else: raise AssertionError('Negative control admitted')
            controller.submit(name, packet['actor'], packet['ticket'], result, name+'-'+step)
            write(folder / (step.lower()+'-artifact.json'), result)
        assert controller.state(name)['stage'] == 'EXECUTING' and len(blocked) == 4
        results.append({'case': name, 'negative_controls': blocked, 'packet_bytes': sizes,
            'comparison': case['outcome'], 'enhancement_hypothesis': case['enhancement'],
            'admission': 'HYPOTHESIS_FOR_ATTEMPT_ONLY; execution not performed'})
    report = {'method': 'Known-history analyst-authored replay through actual controller; no independent reasoning trial',
        'input_hash': pk.file_hash(ROOT / 'results/workflow328/cases.json'), 'engine': pp.engine_digest(),
        'results': results, 'negative_controls_blocked': sum(len(r['negative_controls']) for r in results),
        'predicted_savings_percent': None, 'observed_saved_director_inputs': None,
        'live_calls': 0, 'media_changed': False, 'production_approved': False}
    write(output / 'report.json', report)
    print(json.dumps({'cases': len(results), 'blocked': report['negative_controls_blocked'],
                      'largest_packet_bytes': max(max(r['packet_bytes']) for r in results)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='results/workflow330/replay')
    path = (ROOT / parser.parse_args().output).resolve()
    if not path.is_relative_to(ROOT / 'results/workflow330'): raise ValueError('Use workflow330 output')
    run(path)
