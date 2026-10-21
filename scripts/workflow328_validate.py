"""Offline regression and scoped knowledge evidence gate; no production calls."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from movie_factory import production_knowledge as pk
from workflow323_validate import TESTS

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='results/workflow328/validation')
    args = parser.parse_args()
    out = (ROOT / args.output).resolve()
    if not out.is_relative_to(ROOT / 'results/workflow328'): raise ValueError('Use workflow328 output')
    out.mkdir(exist_ok=False)
    run = subprocess.run([sys.executable, '-m', 'pytest', *TESTS,
        'tests/test_staged_runner.py', 'tests/test_expert_planning.py', '-q'],
        cwd=ROOT, capture_output=True, text=True)
    (out / 'tests.txt').write_text(run.stdout + run.stderr)
    if run.returncode:
        print(run.stdout + run.stderr); return run.returncode
    packet = pk.task_packet(ROOT, pk.read_json(ROOT, 'results/workflow328/task.json'))
    if not packet['dispatch_ready']: raise ValueError(packet['blockers'])
    actions = {
        'reuse_envelope': 'Extended existing controller and stage packets, not a second harness; preserved media and historical results.',
        'authority': 'Offline implementation and retrospective evaluation only; no model, render, upload, install or new allowance.',
        'strategy': 'Strategy and source-bound packet preceded implementation; earliest gate tests distinguish schema from semantic judgment.',
        'visual_gate': 'No visual admission.321 remains rejected and253 unchanged. Director AV remains separately pending.',
        'anticipation': 'Reconstructed four prior-intent cases; tested omissions, stale challenge, lost execution links and original-intent veto.',
        'stopping': 'Completed scoped implementation and known-history evaluation; did not relabel this as scene repair.',
        'versioning': 'Expert plan participates in brief fingerprint; exact beat intent and reference authority cannot change in planner submission.',
        'economics': 'No inference/render spend; no predicted savings percentage. Capture gap before lifecycle start remains unmeasured.',
        'retrieval': 'Fresh packet read before code; audit321 and shot brief manually reconciled. New source explicitly routed in core, not silently indexed.',
        'current_state': 'No new media acceptance or runtime High qualification. Legacy324 cannot invoke its incomplete planner after this gate change.',
        'au_reuse': 'Retrospective source IDs and chronology retained separately from later feedback; no historical media overwritten.',
        'au_review': '4 authored retrospective plans,12 malformed mutations blocked;4 bad valid methods pass schema. Not blind accuracy or saved director inputs.'}
    files = [out / 'tests.txt', ROOT / 'results/workflow328/evaluation/report.json',
        ROOT / 'src/movie_factory/expert_planning.py', ROOT / 'tests/test_expert_planning.py',
        ROOT / 'docs/knowledge/EXPERT_LENS_PLANNING_328.md']
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': pk.file_hash(p)} for p in files]
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Local workflow enforcement and retrospective reasoning audit only',
        'checks': [{'id': r['id'], 'status': 'PASS', 'kind': r['check_kind'],
            'action_taken': actions[r['id']], 'observation': 'Evidence supports scoped local code and audit claims, not artistic or predictive qualification.',
            'evidence': evidence} for r in packet['obligations']],
        'hypotheses': [
            {'prediction': 'An incomplete expert plan could reach execution', 'observation': 'Omitted beat/lens/method and stale challenge controls block.',
             'response': 'Keep explicit derivation and completeness challenge in actual stage packets.', 'result': 'resolved'},
            {'prediction': 'Schema success might be misrepresented as semantic qualification', 'observation': 'Four deliberately bad well-formed methods pass the schema; report explicitly records this limitation.',
             'response': 'Qualified the claim, not artistic judgment: require original-intent reasoning review and prospective escape measurement; no automated artistic-truth claim.', 'result': 'resolved'}],
        'adjacent_regressions': 'Focused workflow, runner, review, knowledge and context suites tested; not a claim about the entire repository suite.',
        'stopping_reason': 'Requested offline implementation and retrospective test complete; production and independent judgment qualification remain separate.'}
    gate = pk.check_review(ROOT, packet, review)
    for name, value in [('knowledge-review.json', review), ('knowledge-gate.json', gate)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'tests': run.stdout.strip().splitlines()[-1], 'knowledge_gate': gate,
                      'live_calls': 0, 'production_approved': False}))
    return 0 if gate['ready_for_review'] else 2


if __name__ == '__main__': raise SystemExit(main())
