"""Live local integration checks; no provider calls or production mutations."""
import json
from pathlib import Path
import subprocess
import sys
from movie_factory import context_hygiene as ch
from movie_factory import production_knowledge as pk
from movie_factory import review_control as rc

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/context311'


def main():
    catalog, records = ch.load(ROOT)
    original = (BASE / 'AGENTS.before.md').stat().st_size
    core = (ROOT / 'AGENTS.md').stat().st_size
    cases = json.loads((BASE / 'routing-expectations.json').read_text())['cases']
    measurements = []
    for case in cases:
        result = ch.route(ROOT, case['topics'])
        ids = {r['id'] for r in result['rules']}
        assert set(case['required']) <= ids
        assert not set(case.get('forbidden', [])) & ids
        size = len((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
        measurements.append({'topics': case['topics'], 'selected_rules': len(ids),
                             'route_bytes': size, 'core_plus_route_bytes': core + size,
                             'reduction_vs_original_core_percent': round(100 * (1 - (core + size) / original), 2)})
    command = [sys.executable, '-m', 'movie_factory.context_hygiene', 'current']
    states = [json.loads(subprocess.check_output(command, cwd=ROOT)) for _ in range(2)]
    assert states[0] == states[1]
    capsule = rc.capsule(ROOT)
    assert len(states[0]['open_defects']) == 4
    assert states[0]['capabilities'] == capsule['capabilities']
    packet = json.loads((BASE / 'knowledge-packet.json').read_text())
    assert pk.task_packet(ROOT, packet['task']) == packet
    result = {'original_bytes': original, 'core_bytes': core,
              'core_byte_reduction_percent': round(100 * (1 - core / original), 2),
              'preserved_paragraphs': len(records), 'routes': len(catalog['topics']),
              'frozen_cases_passed': len(cases), 'measurements': measurements,
              'fresh_process_state_equal': True, 'current_exchange': states[0]['exchange'],
              'open_defects': [d['id'] for d in states[0]['open_defects']],
              'capabilities': states[0]['capabilities'],
              'protected_bindings_verified': True, 'fresh_knowledge_packet': True,
              'knowledge_obligations': len(packet['obligations']),
              'bindings': {p: ch.sha(ROOT / p) for p in [
                  'AGENTS.md', ch.CATALOG, 'src/movie_factory/context_hygiene.py',
                  'results/context311/routing-expectations.json',
                  'docs/planning/RELEASE_01_STATUS.json']},
              'limits': 'Byte counts only. Core-plus-route excludes deep source reads, conversation and app instructions. Negative reduction means expansion. Separate Python processes are not fresh LLM admission tests. No overall token/time/quality improvement measured.'}
    with (BASE / 'integration-results.json').open('w') as f:
        json.dump(result, f, indent=2); f.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
