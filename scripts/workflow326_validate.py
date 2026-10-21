"""Offline routing regression and knowledge gate. Never invokes a model."""
import json
from pathlib import Path
import subprocess
import sys

from movie_factory import production_knowledge as pk
from movie_factory import stage_routing
from workflow323_validate import TESTS

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / 'results/workflow326/validation'
    out.mkdir(exist_ok=False)
    run = subprocess.run([sys.executable, '-m', 'pytest', *TESTS,
                          'tests/test_staged_runner.py', '-q'], cwd=ROOT, capture_output=True, text=True)
    (out / 'tests.txt').write_text(run.stdout + run.stderr)
    if run.returncode: return run.returncode
    packet = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/workflow326/task.json'))
    if not packet['dispatch_ready']: raise ValueError(packet['blockers'])
    policy = pk.read_json(ROOT, 'results/workflow326/nihang-routing.json')
    routes = {a: stage_routing.resolve(policy, a, ROOT) for a in stage_routing.ACTORS}
    (out / 'routes.json').write_text(json.dumps(routes, indent=2) + '\n')
    actions = {
        'reuse_envelope': 'Extended existing SerialRunner, protocol and controller contracts; no replacement harness.',
        'authority': 'No new inference;325 allowance remains exhausted. Escalation cannot increase call cap.',
        'strategy': 'Strategy recorded before code edits; tested dispatch and bad-runtime controls before handoff.',
        'visual_gate': 'No visual admission asserted. Failed review still returns to correction in routed fixture.',
        'anticipation': 'Tested fallback, restart, stale escalation evidence, metadata mismatch and model override loss.',
        'stopping': 'Approved routing implementation complete; production authoring and live qualification excluded.',
        'versioning': 'Request and policy hashes bind stages; silent changes fail; explicit escalation retains history.',
        'economics': 'No model call or render. Early work capture gap disclosed; no savings estimate.',
        'retrieval': 'Fresh packet read and reconciled before handoff, but generated after initial implementation; process sequencing gap disclosed. New routing source linked manually, not universal retrieval.',
        'current_state': 'Accepted253 and rejected320/321 preserved; no new production pass.',
        'au_reuse': 'Protected source media untouched; local commits do not imply remote backup.',
        'au_review': 'Offline protocol and control tests only; live runtime settings and reviewer accuracy not qualified.'}
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': pk.file_hash(p)} for p in
                [out / 'tests.txt', out / 'routes.json', ROOT / 'src/movie_factory/stage_routing.py',
                 ROOT / 'src/movie_factory/staged_runner.py', ROOT / 'docs/engineering-intelligence/STAGE_MODEL_ROUTING.md']]
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Offline routing implementation only',
              'checks': [{'id': r['id'], 'status': 'PASS', 'kind': r['check_kind'],
                          'action_taken': actions[r['id']],
                          'observation': 'Current local regressions support the scoped code claim; no production or live quality claim.',
                          'evidence': evidence} for r in packet['obligations']],
              'hypotheses': [{'prediction': 'Changing stage model might erase call limit or bypass failed review',
                              'observation': 'Escalation-cap and failed routed-chain fixtures block both paths.',
                              'response': 'Retain controller and ledger authority across model changes.', 'result': 'resolved'}],
              'adjacent_regressions': 'Existing focused controller, review, knowledge and context suites pass; legacy corpus tests outside this suite unchanged.',
              'stopping_reason': 'Routing code complete; no live calls allowed by this scoped implementation.'}
    gate = pk.check_review(ROOT, packet, review)
    for name, obj in [('knowledge-review.json', review), ('knowledge-gate.json', gate)]:
        (out / name).write_text(json.dumps(obj, indent=2) + '\n')
    print(json.dumps({'tests': run.stdout.strip().splitlines()[-1], 'gate': gate,
                      'live_inference': False, 'production_approved': False}))
    return 0 if gate['ready_for_review'] else 2


if __name__ == '__main__': raise SystemExit(main())
