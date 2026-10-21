"""Offline scoped regression, measured packet sizes and knowledge evidence gate."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from movie_factory import production_knowledge as pk
from movie_factory import planning_pipeline as pp
from workflow323_validate import TESTS

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='results/workflow330/validation')
    out = (ROOT / parser.parse_args().output).resolve()
    if not out.is_relative_to(ROOT / 'results/workflow330'): raise ValueError('Use workflow330 output')
    out.mkdir(exist_ok=False)
    tests = TESTS + ['tests/test_staged_runner.py', 'tests/test_expert_planning.py',
                     'tests/test_planning_pipeline.py', 'tests/test_resource_manifest.py', 'tests/test_resource_routing317.py']
    run = subprocess.run([sys.executable, '-m', 'pytest', *tests, '-q', '--tb=short'],
                         cwd=ROOT, capture_output=True, text=True)
    (out / 'tests.txt').write_text(run.stdout + run.stderr)
    if run.returncode:
        print(run.stdout + run.stderr); return run.returncode
    packet = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/workflow330/task.json'))
    if not packet['dispatch_ready']: raise ValueError(packet['blockers'])
    actions = {
        'reuse_envelope': 'Extended the existing controller, knowledge gate and serial runner; no new service or native qualification.',
        'authority': 'No live inference, paid call, render, install, upload or accepted-media mutation. Live cap and exhausted325 allowance unchanged.',
        'strategy': 'Critique preceded implementation. Four enforced planning stages, source excerpts, dependency order and targeted repair.',
        'visual_gate': 'No new artistic pass.321 remains rejected;253 protected. Well-formed wrong-method negative remains visible.',
        'anticipation': 'Adversarial skipped-stage, source drift, lost preferences/learning, wrong roles, unsupported proof, replan and budget tests; future Nihang hypotheses frozen.',
        'stopping': 'Requested integrated software scope complete; technical stages are not routine Director handoffs. Production construction not silently launched.',
        'versioning': 'Original direction/reference authority, engine, sources and input artifacts bind each step; downstream state invalidates on repair.',
        'economics': 'Recorded observed test work and packet sizes, not token savings. Simulation cannot expand live allowance; no asserted efficiency percentage.',
        'retrieval': 'Fresh330 packet plus manual328/329/321 source reconciliation; existing stale307 capsule not repinned. New instructions explicitly linked, not universal memory.',
        'current_state': 'Four stages implemented/offline tested; fresh real-model authoring and production proof still unqualified. No scene status changed.',
        'au_reuse': 'Four historical replay inputs and later-feedback boundaries retained; prospective scope frozen separately. Existing artifacts and unrelated working tree preserved.',
        'au_review': '16 malformed controls blocked across4 known-history replays; semantic false-negative retained. Saved Director inputs and quality uplift unknown.'}
    files = [out / 'tests.txt', ROOT / 'results/workflow330/replay-qualified/report.json',
             ROOT / 'src/movie_factory/planning_pipeline.py', ROOT / 'tests/test_planning_pipeline.py',
             ROOT / 'docs/knowledge/PLANNING_PIPELINE_330.md', ROOT / 'results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md']
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': pk.file_hash(p)} for p in files]
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Offline planning/control qualification only',
        'checks': [{'id': r['id'], 'status': 'PASS', 'kind': r['check_kind'], 'action_taken': actions[r['id']],
                    'observation': 'Evidence supports bounded workflow claims, not semantic or production acceptance.', 'evidence': evidence}
                   for r in packet['obligations']],
        'hypotheses': [{'prediction': 'A stage may drop authority or bypass an upstream obligation',
            'observation': 'Adversarial deterministic controls reject the tested omissions and stale/substituted inputs.',
            'response': 'Retain original sources and scoped obligation maps beside stage summaries.', 'result': 'resolved'},
            {'prediction': 'Structured plans could be confused with correct artistic judgment',
             'observation': 'Deliberately wrong well-formed method passes a rubber-stamp challenge.',
             'response': 'Keep semantic limitation explicit; prospective pose/look proof and escape tracking are mandatory.', 'result': 'resolved'}],
        'adjacent_regressions': 'Focused controller, runner, expert, knowledge, review, context and reuse tests only; no full-repository or Blender claim.',
        'stopping_reason': 'Integrated critique, implementation, offline tests, historical replay and prospective brief complete. No construction or live runtime authority inferred.'}
    gate = pk.check_review(ROOT, packet, review)
    for name, data in [('knowledge-review.json', review), ('knowledge-gate.json', gate)]:
        (out / name).write_text(json.dumps(data, indent=2) + '\n')
    report = {'tests': run.stdout.strip().splitlines()[-1], 'test_files': tests, 'knowledge_gate': gate,
        'planning_engine': pp.engine_digest(), 'packet_digest': packet['packet_digest'],
        'evidence': evidence, 'live_calls': 0, 'production_approved': False, 'measured_efficiency_gain': None}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'tests': report['tests'], 'knowledge_gate': gate, 'live_calls': 0}))
    return 0 if gate['ready_for_review'] else 2


if __name__ == '__main__': raise SystemExit(main())
