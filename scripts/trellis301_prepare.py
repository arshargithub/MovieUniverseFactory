"""Local-only301 preparation. Does not import a cloud controller or credentials."""
import argparse
import hashlib
import json
from pathlib import Path

from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/trellis301'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def packet():
    paths = [
        'results/trellis301/STRATEGY.md', 'results/trellis300/QUALITY_REVIEW.md',
        'results/trellis298/ASSESSMENT.md', 'results/trellis298/STRATEGY.md',
        'results/trellis295/license-review296.json', 'results/trellis295/access-confirmed297.json',
        'results/sikh287/TRELLIS_PRODUCTION_PATHS.md',
        'docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md',
        'docs/knowledge/CURRENT_PRODUCTION_STATE.md', 'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250.md',
        'docs/planning/PROTECTION_CALIBRATION_255.md', 'docs/planning/SHOT_BEAT_QUALITY_BRIEF.md',
        'docs/planning/SERIES_01_SIKH_BASELINE_V01.md',
        'docs/decisions/0005-production-strategy-before-execution.md',
        '.runtime/trellis298d/retrieved/evidence/candidate.glb',
        '.runtime/trellis298d/retrieved/evidence/remeshed-source.safetensors',
        '.runtime/trellis298c/retrieved/evidence/head512/source.safetensors',
        '.runtime/trellis298c/retrieved/evidence/head512/geometry.json',
        'results/trellis298/cloud-c/teardown-verification.json',
        'results/trellis298/cloud-d/teardown-verification.json',
    ]
    task = dict(id='trellis301-controlled-quality', operation='modeling', phase='planning',
        entities=['sikh', 'sikh_beard', 'sikh_turban_cover'],
        query='Controlled source export opacity geometry texture comparison same-film source quality',
        intent='Prepare controlled head-quality comparison; cloud dispatch held for root budget/payload review; no actor pass',
        inputs={p: sha(ROOT / p) for p in paths}, open_decisions=[], max_context_characters=42000,
        execution_authority={'source': 'results/trellis301/STRATEGY.md',
            'scope': 'Director301 controlled comparison. Local preparation only until root dispatch review.'})
    result = pk.task_packet(ROOT, task)
    dump(OUT / 'task.json', task)
    dump(OUT / 'packet.json', result)
    (OUT / 'packet.md').write_text(pk.packet_markdown(result))
    print(json.dumps({'packet_digest': result['packet_digest'], 'dispatch_ready': result['dispatch_ready'],
                      'blockers': result['blockers'], 'phase': 'planning'}))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['packet'])
    args = parser.parse_args()
    if not packet()['dispatch_ready']:
        raise SystemExit(2)
