"""Verify audit evidence and state, not artistic quality; write local receipts."""
import json
import re
from datetime import datetime, timezone

from audit_nihang348 import ROOT, OUT, binding, digest, write
from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger, episode_report


def main():
    inventory = json.loads((OUT/'cycle-inventory.json').read_text())['rows']
    assert len(inventory) == 66
    sources = {}
    for row in inventory:
        for item in row['sources']:
            assert digest(ROOT/item['path']) == item['sha256'], item['path']
            sources[item['path']] = item
    counts = {}
    for branch, total, saved in [('look01', 52, 30), ('motion01', 12, 7)]:
        rows = [r for r in inventory if r['branch'] == branch and r['cycle'] > 0]
        assert len(rows) == total
        assert sum(r['has_returned_save'] for r in rows) == saved
        counts[branch] = dict(numbered_corrections=total, returned_save=saved,
                              without_returned_save=total-saved)
    controller = Controller(ROOT, DATABASE)
    states = json.loads((OUT/'state-at-audit.json').read_text())
    for task, expected in states.items():
        actual = controller.state(task)
        assert all(actual[k] == v for k, v in expected.items()), task
    docs = [OUT/name for name in ('RETROSPECTIVE.md', 'CAUSAL_LEDGER.md', 'NEXT_PROOF.md')]
    links = []
    for doc in docs:
        for target in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
            path = (doc.parent/target.split('#')[0]).resolve()
            assert path.is_file(), str(path)
            links.append(binding(path))
    packet = json.loads((ROOT/'.runtime/knowledge-pilot213/sikh348-audit.json').read_text())
    for path, sha in packet['task']['inputs'].items():
        assert digest(ROOT/path) == sha, path
    evidence = [binding(d) for d in docs]
    viewed_images = [
        '.runtime/factory-native/sikh342-look-c23-neutral_front/frame.png',
        '.runtime/factory-native/sikh342-look-c23-bend_side/frame.png',
        '.runtime/factory-native/sikh344-look-c34-leader_front/frame.png',
        '.runtime/factory-native/sikh344-look-c35-leader_front/frame.png',
        '.runtime/factory-native/sikh347-look-c52-leader_front/frame.png',
        '.runtime/factory-native/sikh347-look-c52-leader_anatomy/frame-0327.png',
        '.runtime/art-direction/series01-sikh321/comparisons/phase-comparison.jpg',
        '.runtime/art-direction/series01-sikh321/comparisons/appearance.jpg',
    ]
    write('audit-validation.json', dict(status='PASS', scope='Receipt counts, hashes, links and unchanged task caps only; not semantic or artistic qualification.',
        counts=counts, verified_original_sources=len(sources), source_links=links,
        viewed_image_bindings=[binding(ROOT/p) for p in viewed_images],
        reports=evidence, states=states, packet_digest=packet['packet_digest']))
    write('knowledge-review.json', dict(packet_digest=packet['packet_digest'],
        scope='Read-only audit closure; production obligations remain unqualified.',
        checks=[dict(id=o['id'],kind=o['check_kind'],status='NOT_RUN',
            action_taken='Audited historical application and specified next discriminating proof; did not execute new production qualification.',
            observation='Audit is complete, but this check must not imply construction, motion, appearance or audiovisual admission.',
            evidence=evidence) for o in packet['obligations']],
        hypotheses=[dict(prediction='A neutral garment alone is the missing next step.',result='failed',
            observation='23 already supplies a useful scoped proof; later changed-actor transfer and35 shell replacement lose its form.',
            response='Discriminate bare deformation and garment-transfer interfaces first.',evidence=evidence)],
        adjacent_regressions=dict(status='NOT_RUN',observation='No new media changed; previous production defects not waived.',evidence=evidence),
        stopping_reason='Audit deliverable complete. Construction caps unchanged and exhausted. No production handoff.'))
    print(json.dumps(dict(audit_checks='PASS',counts=counts,verified_sources=len(sources),states=states)))


def close_activity():
    ledger = Ledger(ROOT/'.runtime/experiment-ops.sqlite3')
    events = ledger.events()
    if not any(e['event_id'] == 'sikh348-work-end' for e in events):
        ledger.append(dict(event_id='sikh348-work-end',experiment_id='SIKH335',episode_id='first',
            utc=datetime.now(timezone.utc).isoformat(),event_type='work_ended',phase='design',
            activity_id='sikh348-retrospective',note='Audit artifacts complete; initial source recovery and subsequent final handoff not measured. No experiment closure.'))
    selected = [e for e in ledger.events() if e.get('activity_id') == 'sikh348-retrospective']
    write('operating-audit.json',dict(scope='Only audit348 measured activity, not whole campaign or historical savings.',
        events=selected,report=episode_report(selected)))


if __name__ == '__main__':
    import sys
    if '--close-activity' in sys.argv:
        close_activity()
    else:
        main()
