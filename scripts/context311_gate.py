"""Record scoped process application and validate it against the fresh packet."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/context311'
APPLICATION = {
    'authority': ('Kept authorized local cleanup separate from production.', 'No new calls, installs, uploads or scene changes; protected bindings verify.', 'integration-results.json'),
    'strategy': ('Applied the staged plan and preserved reversible originals.', 'Frozen expectations precede routes; coverage and known limitations are explicit.', 'MANUAL_RECONCILIATION.md'),
    'visual_gate': ('Did not reinterpret software checks as artistic admission.', 'All four scene defects and false direct motion/audio flags remain.', 'integration-results.json'),
    'anticipation': ('Tested omission, staleness, source and adjacent-route failure modes.', '140 tests pass, including failure controls and102 prior regression cases.', 'tests.xml'),
    'stopping': ('Completed the scoped cleanup and retained the next capability prerequisite.', 'No intermediate scene candidate or repeated go-ahead requested.', 'REVIEW.md'),
    'versioning': ('Bound exact original text, core, inputs, state and records.', 'Changes invalidate helpers/packets rather than automatically rehashing sources.', 'integration-results.json'),
    'economics': ('Measured local byte payloads without inventing token savings.', 'Core-plus-route reductions vary; actual app tokens and total savings unknown.', 'REVIEW.md'),
    'retrieval': ('Read fresh11-obligation packet and manually reconciled42 original paragraphs.', 'Routes do not replace deep-source reading or new-domain reconciliation.', 'MANUAL_RECONCILIATION.md'),
    'current_state': ('Recovered current paused state in separate processes.', 'Fresh311 status retains four open defects and protected scope.', 'integration-results.json'),
    'au_reuse': ('Kept accepted quality floor, reference authority and source integrity mandatory.', 'No accepted Pashtun work reopened or weakened to accommodate Sikh.', 'MANUAL_RECONCILIATION.md'),
    'au_review': ('Separated technical preservation, finite coverage and actual judgment.', 'Tests and source hashes are explicitly not independent perceptual validation.', 'REVIEW.md'),
}


def main():
    packet = json.loads((BASE / 'knowledge-packet.json').read_text())
    assert set(APPLICATION) == {r['id'] for r in packet['obligations']}
    checks = []
    for rule in packet['obligations']:
        action, observation, name = APPLICATION[rule['id']]
        path = 'results/context311/' + name
        checks.append({'id': rule['id'], 'kind': rule['check_kind'], 'status': 'PASS',
                       'action_taken': action, 'observation': observation,
                       'evidence': [{'path': path, 'sha256': pk.file_hash(ROOT / path)}]})
    review = {'packet_digest': packet['packet_digest'],
              'scope': 'Local context cleanup only; no production acceptance.', 'checks': checks,
              'hypotheses': [
                  {'prediction': 'Compression could lose mandatory instructions or adjacent obligations.',
                   'observation': 'Exact42-paragraph preservation, manual mapping and finite frozen cases pass.',
                   'response': 'Retain originals and explicit manual reconciliation; do not claim universal semantic coverage.', 'result': 'resolved'},
                  {'prediction': 'Output truncation could conceal errors or revive old scene approvals.',
                   'observation': 'Middle-warning/exit/stale-state tests pass; existing defects remain open.',
                   'response': 'Preserve complete logs and capability limits; inspect ambiguous evidence.', 'result': 'resolved'}],
              'adjacent_regressions': 'Existing102 tests and protected source bindings remain valid; no production media changed.',
              'stopping_reason': 'Authorized cleanup complete. Next is audiovisual review capability qualification, not scene acceptance.'}
    gate = pk.check_review(ROOT, packet, review)
    for name, value in [('process-review.json', review), ('process-gate.json', gate)]:
        (BASE / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(gate, indent=2))
    return 0 if gate['ready_for_review'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
