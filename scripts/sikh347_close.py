"""Preserve exhausted347 authority and measured evidence, without media admission."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk, production_workflow as wf
from movie_factory.task_router import DATABASE

r = Path(__file__).resolve().parents[1]
c = wf.Controller(r, DATABASE)
out = r/'results/sikh335/closure347'
out.mkdir(exist_ok=True)
def write(name, value):
    p = out/name
    text = json.dumps(value, indent=2)+'\n'
    if p.exists():
        assert p.read_text() == text
    else:
        p.write_text(text)
states = {}
for task, limit in [('sikh335-supporting-appearance',52),('sikh335-continuous-performance',12)]:
    s = c.state(task)
    assert s['stage'] == 'REPLAN_REQUIRED' and s['cycle'] == s['max_corrections'] == limit
    states[task] = {k:s[k] for k in ('stage','cycle','max_corrections','planning_step')}
write('controller-state.json', states)
paths = ['results/sikh335/REASSESSMENT_347.md','results/sikh335/LEARNINGS_347.md','results/sikh335/look01/rejection-c52.json']
paths += [f'results/sikh335/look01/{v}-visual-review-c52.json' for v in ('leader_front','leader_reverse','leader_anatomy','leader_contact','render')]
evidence = [dict(path=p, sha256=pk.file_hash(r/p)) for p in paths]
packet = pk.read_json(r,'.runtime/knowledge-pilot213/sikh347-current.json')
checks = [dict(id=o['id'],kind=o['check_kind'],status='FAIL' if o['id'] in
    {'construction_interfaces','visual_gate','au_contact','au_surface','au_deformation'} else 'NOT_RUN',
    action_taken='Preserved all five corrections and rejected final five-view controls; withheld crowd propagation and media handoff.',
    observation='Beard/edges advance but body-shell garment and anatomy controls fail. New saddle binding error51 retained. Whole-form construction route has not converged.',
    evidence=evidence) for o in packet['obligations']]
write('knowledge-review.json', dict(packet_digest=packet['packet_digest'],scope='Exhausted correction closure, not production admission',checks=checks,
    hypotheses=[dict(prediction='Restricted relaxation and altered skinning can turn the inherited body-shell garment into a convincing mounted coat.',result='failed',
        observation='Final front/reverse show inflated shoulders, sleeve pocket and body-shell form; bare controls also expose upstream deformation.',
        response='Propose discriminating bare-anatomy proof then genuinely independent garment construction before any surface polish. Upper-arm roll cause remains unverified.',evidence=evidence)],
    adjacent_regressions=dict(status='FAIL',observation='48 skin breakthrough and49 belt regression preserved. Final anatomy, elbow cloth and same-film finish remain blocked.',evidence=evidence),
    stopping_reason='Five347 corrections consumed at appearance52. Motion12 unchanged. No artistic/AV pass. New correction authority required for changed construction route.'))
jobs = []
for p in sorted((r/'.runtime/factory-native').glob('sikh347-*/runner-status.json')):
    d = json.loads(p.read_text())
    jobs.append(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),elapsed=d.get('elapsed'),exit_code=d.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,job_count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),
    scope='Serial native process occupancy including failure; not agent-only work, total turn time or Director idle. Do not add to overlapping work interval.'))
log = r/'.runtime/context-hygiene/runs/sikh347-tests-final/stdout.log'
write('verification.json',dict(tests=26,test_log=str(log.relative_to(r)),test_log_sha256=pk.file_hash(log),
    scope='Focused geometry/admission regression tests, not artistic or audiovisual qualification.'))
gate = r/'.runtime/knowledge-pilot213/sikh347-gate.json'
if gate.exists():
    write('knowledge-gate.json', dict(source=str(gate.relative_to(r)),sha256=pk.file_hash(gate),result=json.loads(gate.read_text()),
        note='Exit2 retained. First invocation used an unsupported output destination and wrote no gate; rerun used the prescribed pilot derived-output directory. No failed obligation waived.'))
print(json.dumps(states))
