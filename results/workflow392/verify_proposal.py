"""Read-only production/source verification for a proposal, not admission."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/workflow392'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    c = sqlite3.connect('file:' + str(ROOT / '.runtime/factory-entry.sqlite3') + '?mode=ro', uri=True)
    states = {}
    for task in ('sikh335-supporting-appearance', 'sikh335-continuous-performance'):
        state = json.loads(c.execute('SELECT state FROM events WHERE task=? ORDER BY seq DESC LIMIT 1', (task,)).fetchone()[0])
        states[task] = {k: state[k] for k in ('cycle', 'max_corrections', 'stage', 'fingerprint')}
    old = json.loads((ROOT / 'results/sikh391/PRODUCTION_BOUNDARY_VERIFY.json').read_text())
    assert states['sikh335-supporting-appearance'] == old['after']
    native_count = c.execute('SELECT COUNT(*) FROM native_runs').fetchone()[0]
    assert native_count == old['native_runs_after']
    cy = {json.loads(r[0])['cycle'] for r in c.execute('SELECT state FROM events WHERE task=?', ('sikh335-supporting-appearance',))}
    spans = [(124, 156), (177, 226), (227, 251), (252, 261)]
    coverage = []
    for lo, hi in spans:
        expected = set(range(lo, hi + 1))
        assert expected <= cy
        coverage.append(dict(first=lo, last=hi, charged_slots=len(expected)))
    masters = json.loads((ROOT / 'results/sikh391/PROTECTED_MASTERS_VERIFY.json').read_text())
    for row in masters.values():
        row['actual'] = sha(ROOT / row['path'])
        row['unchanged'] = row['actual'] == row['expected']
        assert row['unchanged']
    pins = json.loads((ROOT / 'results/sikh391/AUDIT_SOURCE_BINDINGS.json').read_text())
    for row in pins:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    sources = [
        'docs/knowledge/ROUTER_FIRST_332.md',
        'docs/knowledge/PLANNING_PIPELINE_330.md',
        'docs/knowledge/context/README.md',
        'docs/knowledge/README.md',
        'docs/decisions/0005-production-strategy-before-execution.md',
        'docs/knowledge/pilot/README.md',
        'docs/knowledge/review_control/README.md',
        'src/movie_factory/native_admission.py',
        'results/sikh391/AUDIT.md',
        'results/sikh391/AUDIT_METRICS.json',
        'results/sikh390/GRAFT261_READBACK.json',
    ]
    pins.extend(dict(path=s, sha256=sha(ROOT / s)) for s in sources)
    unique = {x['path']: x for x in pins}
    (OUT / 'SOURCE_BINDINGS.json').write_text(json.dumps(list(unique.values()), indent=2) + '\n')
    probe = json.loads((OUT / 'POLICY_PROBE_RESULTS.json').read_text())
    assert len(probe['cases']) == 34
    assert all(x['actual'] == x['expected'] for x in probe['cases'])
    result = dict(
        canonical_state=states, appearance_unchanged=True,
        native_runs=native_count, new_native_runs=0,
        inherited_horse_slot_coverage=coverage,
        inherited_horse_charged_slots=sum(x['charged_slots'] for x in coverage),
        protected_masters=masters, source_binding_count=len(unique),
        offline_authored_decision_cases=34,
        production_policy_implemented=False, production_admission=False,
        context_status='Historic307 freshness block retained; proposal/audit only.',
        limits=['Not perceptual qualification.', 'Not migration or projection-equivalence qualification.',
                'No new production, model, spend, upload or publication authority.'])
    (OUT / 'VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('protected_masters', 'canonical_state')}, indent=2))


if __name__ == '__main__':
    main()
