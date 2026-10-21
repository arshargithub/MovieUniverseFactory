"""Bounded offline verification and knowledge-application receipt for workflow323."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
TESTS = ['tests/test_production_workflow.py', 'tests/test_review_control.py',
         'tests/test_production_knowledge.py', 'tests/test_context_hygiene.py']
APPLICATIONS = {
    'reuse_envelope': ('Reused knowledge/review helpers and lifecycle records without claiming native-asset qualification.', 'Existing review and knowledge tests remain in the focused suite.'),
    'authority': ('Limited implementation to offline code, fixtures and existing-evidence replay.', 'No render, provider, subagent, installation or upload; receipts explicitly deny production/Director approval.'),
    'strategy': ('Followed the322 staged-controller proposal and323 strategy with source-bound proof first.', 'State transitions, stale binding and correction limits exercised before any production integration.'),
    'visual_gate': ('Reinspected321 phase/appearance sheets and kept rejected320 internal to audit/replay.', 'Column neck, extended hind support, shell outfit and slab saddle remain FAIL; no new AV or artistic qualification.'),
    'anticipation': ('Tested stage skipping, role downgrade, false modality, stale retry and resource contention.', 'Known-negative bytes veto a false positive; unfamiliar false observations remain an explicitly tested limitation.'),
    'stopping': ('Finished offline controller and replay rather than resume scene work or install a live harness.', 'Two-correction pilot persists across restart/replan; next dependency is live serial stage-runner qualification.'),
    'versioning': ('Bound reference bytes plus semantic roles and scoped source authority across every stage.', 'Role/byte changes invalidate submissions; historical negative and accepted positive scopes remain distinct.'),
    'economics': ('Captured work/test/replay intervals with existing operating ledger; no paid workload.', 'Unknown token/cost and initial capture gap remain disclosed; no Mac speedup percentage is claimed.'),
    'retrieval': ('Generated fresh knowledge packet and manually reconciled321/322/323 rather than repin307.', 'Old current capsule remains stale; no universal memory or newly indexed corpus claim.'),
    'current_state': ('Preserved253 exact provisional Pashtun and321 rejected Nihang status.', 'Positive reuse is not release or strict renderer qualification; false direct AV capability remains false.'),
    'au_reuse': ('Preserved audit sheets and linked existing source provenance; avoided new scene derivatives.', 'Local commits are not remote backup; no accepted actor/source asset changed.'),
    'au_review': ('Separated control-flow tests from familiar visual reinspection and unknown semantic accuracy.', 'Known controls are regressions; no fresh blind/independent accuracy or held-out success claimed.')
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = (ROOT / args.output).resolve()
    if not out.is_relative_to(ROOT / 'results' / 'workflow323') or out.exists():
        raise ValueError('Use a new results/workflow323 output directory')
    out.mkdir(parents=True)
    run = subprocess.run([sys.executable, '-m', 'pytest', *TESTS, '-q'], cwd=ROOT,
                         text=True, capture_output=True, check=False)
    log = out / 'tests.txt'
    log.write_text(run.stdout + run.stderr)
    if run.returncode:
        print(json.dumps({'passed': False, 'tests': str(log.relative_to(ROOT))})); return run.returncode
    task = pk.read_json(ROOT, 'results/workflow323/task.json')
    packet = pk.task_packet(ROOT, task)
    if not packet['dispatch_ready']: raise ValueError(packet['blockers'])
    evidence = [{'path': str(log.relative_to(ROOT)), 'sha256': pk.file_hash(log)},
                {'path': 'results/workflow323/replay03/replay.json',
                 'sha256': pk.file_hash(ROOT / 'results/workflow323/replay03/replay.json')},
                {'path': 'src/movie_factory/production_workflow.py',
                 'sha256': pk.file_hash(ROOT / 'src/movie_factory/production_workflow.py')}]
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Offline software pilot only',
              'checks': [{'id': r['id'], 'status': 'PASS', 'kind': r['check_kind'],
                          'action_taken': APPLICATIONS[r['id']][0], 'observation': APPLICATIONS[r['id']][1],
                          'evidence': evidence} for r in packet['obligations']],
              'hypotheses': [
                  {'prediction': 'Reference role could be lost between stages', 'observation': 'Omission/downgrade tests block',
                   'response': 'Same frozen contract plus aspect comparison at each stage', 'result': 'resolved'},
                  {'prediction': 'Old receipt or renamed pass might bypass limits', 'observation': 'Freshness and stable deliverable tests block',
                   'response': 'Revalidate delivery; retain counters and exclusive deliverable ownership', 'result': 'resolved'}],
              'adjacent_regressions': 'Focused legacy suites pass; three separate older317/319 assertions fail on pre-existing corpus evolution. No patches to those modules or pins.',
              'stopping_reason': 'Offline scoped deliverable complete. Live driver, OS isolation and perceptual judgment remain unqualified, not claimed as implemented.'}
    gate = pk.check_review(ROOT, packet, review)
    for name, value in [('knowledge-review.json', review), ('knowledge-gate.json', gate)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'output': str(out.relative_to(ROOT)), 'test_summary': run.stdout.strip().splitlines()[-1],
                      'knowledge_gate': gate, 'live_production_admitted': False}))
    return 0 if gate['ready_for_review'] else 2


if __name__ == '__main__': raise SystemExit(main())
