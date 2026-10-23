"""Retain actual scoped results and block delivery of an unfinished actor."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.task_router import DATABASE

r = Path(__file__).resolve().parents[1]
out = r / 'results/sikh353'
c = wf.Controller(r, DATABASE)

def write(name, value):
    p = out / name
    text = json.dumps(value, indent=2) + '\n'
    if p.exists():
        assert p.read_text() == text, name
    else:
        p.write_text(text)

states = {}
for task, limit in [('sikh335-supporting-appearance', 67),
                    ('sikh335-continuous-performance', 16)]:
    state = c.state(task)
    assert state['cycle'] == state['max_corrections'] == limit
    assert state['stage'] == 'REPLAN_REQUIRED'
    states[task] = {k: state[k] for k in ('stage', 'cycle', 'max_corrections', 'planning_step')}
write('controller-close.json', states)

paths = ['CLOSEOUT.md', 'LEARNINGS.md', 'GESTURE16_DIAGNOSIS.md',
         'MOTION_INTEGRATION_FINDING.md', 'leader_front-visual-c67.json',
         'leader_reverse-visual-c67.json', 'motion-visual-c16.json']
evidence = [dict(path='results/sikh353/' + p, sha256=pk.file_hash(out / p)) for p in paths]
passed = {'authority', 'versioning', 'stopping', 'economics', 'current_state', 'sikh_scope'}
failed = {'anatomy', 'visual_gate', 'au_deformation', 'construction_interfaces',
          'au_contact', 'au_surface', 'look', 'anticipation', 'au_reuse',
          'animal_coordination', 'motion', 'au_performance', 'strategy'}
notes = {
    'authority': 'Ten total corrections retained on the two original tasks; no new external spend or uploads.',
    'versioning': 'Original and failed native derivatives preserved with source/output hashes; no accepted principal overwritten.',
    'stopping': 'Known appearance failure blocks production review; cumulative limits exhausted, not reset or bypassed.',
    'economics': 'Only local scoped proofs, serial native jobs; no paid provider, new tool or cloud operation.',
    'current_state': 'Latest353 priority reconciled explicitly against stale307 capsule; no claim that the corpus was refreshed.',
    'sikh_scope': 'Leader/horse only; crowd construction deferred exactly as latest Director requested.',
    'strategy': 'Causal waist/arrival/strike tests helped, but appearance finishing stayed too local and did not resolve whole-form deficiencies.',
    'crowd_support': 'Deferred by current authority; no crowd construction or qualification.',
    'render_profile': 'Diagnostic and production sample profiles identified; no final continuous render or delivery profile qualification.',
    'cache_safety': 'No new simulation-cache validity proof; do not infer cache qualification from save/reopen.',
    'secondary': 'No completed whole-performance cloth, groom and secondary-action qualification.',
    'sikh_motion': 'Isolated leader motion samples only; complete Sikh performance and audiovisual passage remain unqualified.',
    'reuse_envelope': 'Scoped fixes retained as candidates; no full asset/shot reuse envelope qualified.',
}
for prefix in ('appearance-', 'motion-'):
    packet = pk.read_json(r, f'results/sikh353/{prefix}knowledge-packet.json')
    checks = [dict(id=o['id'], kind=o['check_kind'],
                   status='FAIL' if o['id'] in failed else 'PASS' if o['id'] in passed else 'NOT_RUN',
                   action_taken='Retain six appearance and four motion corrections on original tasks; inspect actual poses and source-reference controls; reject whole deliverable and defer crowd.',
                   observation=notes.get(o['id'], 'Scoped waist, attachment, consuming-branch arrival and spear-grip repairs do not qualify the actor or complete performance. Visible whole-form defects remain; no AV readiness claimed.'),
                   evidence=evidence) for o in packet['obligations']]
    write(prefix + 'knowledge-review.json', dict(
        packet_digest=packet['packet_digest'], scope='Exhaustion audit, not production-media admission',
        checks=checks,
        hypotheses=[dict(prediction='Local interface and shader corrections suffice for the whole leader.',
                         result='failed', observation='Appearance67 remains visibly assembled, with sash and saddle form failures.',
                         response='Preserve scoped fixes, keep whole-form gate failed; next proof must address visible construction before more surface decoration.', evidence=evidence)],
        adjacent_regressions=dict(status='FAIL', observation='65 omitted crown core;66 repaired assembly, but67 sash/tack and whole-actor form remain failed. All evidence retained.', evidence=evidence),
        stopping_reason='Ten total corrections exhausted; no crowd work or known-defect media handoff.'))

jobs = []
for path in sorted((r / '.runtime/factory-native').glob('sikh353-*/runner-status.json')):
    value = json.loads(path.read_text())
    jobs.append(dict(path=str(path.relative_to(r)), sha256=pk.file_hash(path),
                     elapsed=value.get('elapsed'), exit_code=value.get('exit_code')))
write('native-timings.json', dict(jobs=jobs, job_count=len(jobs),
    summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'], (int, float))),
    scope='Serial native process occupancy including failures, overlaps active work; not additive to elapsed time or model-only time.'))
print(states)
