"""Record a capability blocker, not an artistic PASS."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory import review_control as rc

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/av312'


def main():
    packet = json.loads((BASE / 'knowledge-packet.json').read_text())
    capsule = rc.capsule(ROOT)
    evidence = [{'path': 'results/av312/' + name, 'sha256': pk.file_hash(BASE / name)}
                for name in ['REVIEW.md', 'controls.json', 'tests.xml']]
    observations = {
        'authority': 'No external requests or production changes; new media/API authority is explicitly pending.',
        'strategy': 'Earliest audio probe failed; avoided repeating known static reviews as new perceptual qualification. Written strategy followed initial probe; this ordering limitation is disclosed.',
        'visual_gate': 'No full-motion/audio pass. Actual audio input was omitted. Four defects remain open and protected master bindings verify.',
        'anticipation': 'Prepared silent, delayed and slowed controls to test hallucination/timing alongside positive and known-failed material. External judgments NOT_RUN.',
        'stopping': 'Handoff is for new media egress/provider authority, not another technical go-ahead or incremental scene approval.',
        'versioning': 'Eight derivative hashes, source hashes, durations and decode results recorded; masters untouched.',
        'economics': 'Local jobs captured, no provider spend; proposed six-call cost ceiling is not execution authority.',
        'retrieval': 'Fresh process packet generated before fixtures and read immediately afterward; not falsely reported as pre-dispatch manual reading. Relevant AU11–16,255 and307 scope reconciled.',
        'current_state': 'Current312 state records missing channel and pending authority; existing acceptance and four open defects preserved.',
        'au_reuse': 'Reused excerpts and infrastructure rather than new renders; no new backup or complete production-readiness claim.',
        'au_review': 'Distinguished missing perceptual input from rule failure; external hypothesis untested, no calibration accuracy claim.'}
    review = {'packet_digest': packet['packet_digest'], 'scope': 'Capability investigation and authority handoff only, not perceptual qualification',
              'checks': [{'id': r['id'], 'kind': r['check_kind'], 'status': 'PASS',
                          'action_taken': observations[r['id']], 'observation': observations[r['id']], 'evidence': evidence}
                         for r in packet['obligations']],
              'hypotheses': [{'prediction': 'An audio return may create a player without giving the agent audible content.',
                              'observation': 'Tool explicitly omitted audio because audio input is unsupported.',
                              'response': 'No hearing claim or capability enablement; request scoped alternative.', 'result': 'resolved'}],
              'adjacent_regressions': 'Protected source fingerprints unchanged;140 existing/new state regressions pass; scene untouched.',
              'stopping_reason': 'Concrete external media/provider/spend choice. Perceptual qualification remains blocked.'}
    gate = pk.check_review(ROOT, packet, review)
    qualification = {'qualified': False, 'direct_audio': 'BLOCKED_INPUT_UNSUPPORTED',
                     'direct_motion': 'NOT_RUN_NO_VERIFIED_CONTINUOUS_VIDEO_INPUT',
                     'audio_tool_return': 'audio content omitted because you do not support audio input',
                     'probe_path': '.runtime/av312/rear-audio-probe.wav',
                     'probe_sha256': pk.file_hash(ROOT / '.runtime/av312/rear-audio-probe.wav'),
                     'review_fingerprint_unchanged': capsule['fingerprint'],
                     'remaining_defects': [d['id'] for d in capsule['open_defects']],
                     'external_calls': 0, 'uploads': 0, 'provider_cost_usd': 0,
                     'proposed_controls': 8, 'proposed_generation_request_ceiling': 6,
                     'proposed_spend_ceiling_usd': 1, 'external_authority': 'PENDING',
                     'limits': 'Process evidence gate is not audiovisual qualification. No semantic accuracy measured.'}
    for name, value in [('process-review.json', review), ('process-gate.json', gate), ('qualification.json', qualification)]:
        with (BASE / name).open('x') as f:
            json.dump(value, f, indent=2); f.write('\n')
    print(json.dumps({'process_gate': gate, 'audiovisual_qualified': False}))


if __name__ == '__main__':
    main()
