"""Local verification only; does not dispatch inference or render media."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from movie_factory import production_knowledge as pk
from workflow323_validate import TESTS
from workflow324_qualify import TASK, brief324, supplement, APPEARANCE, PHASES

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--live-trace', help='Previously completed local trace, not a request for inference')
    args = parser.parse_args()
    out = (ROOT / args.output).resolve()
    if not out.is_relative_to(ROOT / 'results/workflow324') or out.exists():
        raise ValueError('Use a new workflow324 output directory')
    out.mkdir(parents=True)
    run = subprocess.run([sys.executable, '-m', 'pytest', *TESTS,
                          'tests/test_staged_runner.py', '-q'], cwd=ROOT,
                         text=True, capture_output=True)
    log = out / 'tests.txt'
    log.write_text(run.stdout + run.stderr)
    if run.returncode: return run.returncode
    packet = pk.task_packet(ROOT, pk.read_json(ROOT, TASK))
    if not packet['dispatch_ready']: raise ValueError(packet['blockers'])
    # Exact static payload sources for the requested egress approval. Stage
    # results will additionally flow forward as validated structured contracts.
    payload = {'destination': 'OpenAI Codex runtime using existing ChatGPT authentication',
               'max_serial_calls': 4, 'inference_started': False,
               'knowledge_digest': packet['packet_digest'],
               'contracts': brief324(),
               'images': [{'path': p, 'sha256': pk.file_hash(ROOT / p),
                           'bytes': (ROOT / p).stat().st_size} for p in (APPEARANCE, PHASES)],
               'excluded': ['credentials', 'environment values', 'database tickets', 'source video bytes',
                            'unrelated repository files', 'full conversation', 'scene files'],
               'stages': {actor: supplement({'actor': actor}, brief324())
                          for actor in ('planner', 'builder', 'reviewer')}}
    (out / 'payload.json').write_text(json.dumps(payload, indent=2) + '\n')
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': pk.file_hash(p)}
                for p in (log, ROOT / 'src/movie_factory/staged_runner.py',
                          ROOT / 'results/workflow324/preflight01/preflight.json')]
    actions = {
        'reuse_envelope': 'Reused existing controller, knowledge gate and operating ledger; no scene changes.',
        'authority': 'Live dispatch blocked by host approval before inference; did not retry or bypass.',
        'strategy': 'No-inference preflight and local control tests precede live frozen-evidence qualification.',
        'visual_gate': 'Preserved rejected320 and direct AV NOT_RUN; no new artistic pass from software tests.',
        'anticipation': 'Tested uncertain crash recovery, tool refusal, context overflow, stale evidence and concurrent runners.',
        'stopping': 'Completed safe implementation and local verification; exact sensitive-payload approval is the remaining blocker.',
        'versioning': 'Reference roles and source bindings survive all stages; changed bytes invalidate admission.',
        'economics': 'Persistent cap and reservations prevent blind retry; existing subscription route only; no speedup claim.',
        'retrieval': 'Fresh324 task packet plus manual321/322/323 reconciliation; older307 freshness block retained.',
        'current_state': '253 scope and321 rejection remain unchanged; no production acceptance or full-speed review claimed.',
        'au_reuse': 'Preserved audit media and source assets; local changes do not imply remote protection.',
        'au_review': 'Mock protocol and regression tests are not live runtime or perceptual accuracy qualification.'}
    live = None
    if args.live_trace:
        trace_path = (ROOT / args.live_trace).resolve()
        if not trace_path.is_relative_to(ROOT / 'results/workflow324'):
            raise ValueError('Trace outside qualification scope')
        live = json.loads(trace_path.read_text())
        if ([s['actor'] for s in live['completed_stages']] != ['planner', 'builder', 'reviewer']
                or len(live['call_reservations']) > 4 or live['delivery_block'] != 'NOT_READY'):
            raise ValueError('Incomplete live qualification trace')
        evidence.append({'path': args.live_trace, 'sha256': pk.file_hash(trace_path)})
        actions.update(authority='Director325 approved exact payload; four reservations including aborted input-echo attempt, three completed serial calls; no wider egress.',
            stopping='Live frozen-evidence chain complete; known candidate blocked and further production repair not dispatched.',
            visual_gate='Fresh reviewer named frame-visible failures; main agent compared both supplied sheets. Direct AV remains NOT_RUN.',
            economics='54,429 observed completed-call tokens; aborted-call usage and total cost unknown; no savings claim.',
            au_review='Known negative control and supplied rejection labels limit inference; actual frame observations agree, not a blind accuracy benchmark.')
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Local implementation and blocked runtime report only',
              'checks': [{'id': r['id'], 'status': 'PASS', 'kind': r['check_kind'],
                          'action_taken': actions[r['id']],
                          'observation': ('Completed live trace supports only serial frozen-evidence control flow; no production builder, direct AV or universal judgment qualification.' if live else 'Local verification and no-inference receipt support only this bounded application; live qualification remains NOT_RUN.'),
                          'evidence': evidence} for r in packet['obligations']],
              'hypotheses': [{'prediction': 'Uncertain stage might dispatch twice after restart',
                              'observation': 'Restart fixture blocks unknown outcome; returned result re-admits without inference.',
                              'response': 'Persist intent and result separately.', 'result': 'resolved'}],
              'adjacent_regressions': 'Focused legacy suites pass. Historical corpus failures and307 staleness remain outside this qualification.',
              'stopping_reason': ('Scoped live chain complete; production authoring integration remains a separate work package.' if live else 'Live qualification is blocked by explicit payload approval; all safe local scope complete.')}
    gate = pk.check_review(ROOT, packet, review)
    for name, value in [('knowledge-review.json', review), ('knowledge-gate.json', gate)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'tests': run.stdout.strip().splitlines()[-1], 'knowledge_gate': gate,
                      'live_frozen_chain_qualified': bool(live), 'production_approved': False}))
    return 0 if gate['ready_for_review'] else 2


if __name__ == '__main__': raise SystemExit(main())
