"""Collect completed offline receipts and review the software-only knowledge gate.

Does not run production tools, migrate live tasks, or rehash the knowledge corpus.
"""
import json
import re
import sqlite3
from pathlib import Path
from movie_factory import production_knowledge as pk, retrospective as rt

root=Path(__file__).resolve().parents[1]
out=root/'results/workflow350'
def bind(path):return dict(path=path,sha256=pk.file_hash(root/path))
def save(name,value):
    with (out/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')

testdir='.runtime/context-hygiene/runs/retrospective350-final/'
receipt=pk.read_json(root,testdir+'receipt.json')
assert receipt['exit_code']==0
log=(root/(testdir+'stdout.log')).read_text()
assert re.search(r'452 passed in [\d.]+s',log) and not (root/(testdir+'stderr.log')).read_text()
replay=pk.read_json(root,'results/workflow350/replay-final.json')
assert replay['engine']==rt.engine() and replay['passed'] and len(replay['cases'])==7
states={}
with sqlite3.connect('file:'+str(root/'.runtime/factory-entry.sqlite3')+'?mode=ro',uri=True) as con:
    for task,limit in [('sikh335-supporting-appearance',52),('sikh335-continuous-performance',12)]:
        row=con.execute('SELECT state,state_hash FROM events WHERE task=? ORDER BY seq DESC LIMIT 1',(task,)).fetchone()
        state=json.loads(row[0]);assert pk.digest(state)==row[1]
        assert state['cycle']==limit and state['max_corrections']==limit
        states[task]=dict(state_hash=row[1],**{k:state[k] for k in ('stage','cycle','max_corrections')})
        if con.execute("SELECT 1 FROM sqlite_master WHERE name='retrospective_events'").fetchone():
            assert con.execute('SELECT COUNT(*) FROM retrospective_events WHERE task=?',(task,)).fetchone()[0]==0
files=['src/movie_factory/retrospective.py','src/movie_factory/production_workflow.py',
       'src/movie_factory/native_admission.py','src/movie_factory/planning_pipeline.py','src/movie_factory/production_allowance.py',
       'tests/test_retrospective350.py','docs/knowledge/RETROSPECTIVE_WORKFLOW_350.md',
       'docs/knowledge/PLANNING_PIPELINE_330.md','results/workflow350/replay-final.json']
report=dict(tests=log.strip().splitlines()[-1],test_receipt=bind(testdir+'receipt.json'),test_stdout=bind(testdir+'stdout.log'),
    test_stderr=bind(testdir+'stderr.log'),historical_cases=7,evidence=[bind(p) for p in files],
    live_states_read_only=states,production_migrations=0,native_processes=0,provider_calls=0,
    new_spend=0,uploads=0,production_approved=False,measured_efficiency_gain=None,
    semantic_negative_control='False well-formed PASS remains undetectable; passing this regression demonstrates the limitation, not visual qualification.')
save('verification.json',report)
actions={
 'reuse_envelope':('Reuse existing resource manifests and bind exact proof versions and conditions.','Changed rig conditions, proof removal, source replacement and dependent-task holds are exercised.'),
 'authority':('Keep implementation offline and preserve original limits.','Live appearance52/52 and motion12/12 read-only states remain unmigrated; no native/provider calls or added spend.'),
 'strategy':('Implement349 in the existing event controller and native bridge.','Earliest recurrence/restart/test-admission proof passes; seven historical classifications exercise targeted versus causal responses.'),
 'visual_gate':('Keep software review distinct from production visual approval.','The false-PASS negative control still escapes; no new image, motion or AV qualification claimed.'),
 'anticipation':('Probe stale receipts, corrected history, concurrent callbacks, changed proofs, exhaustion and transactional failure.','The focused suite passes including capability invalidation and rollback before a native review could be retained without its finding.'),
 'stopping':('Close only the software scope and identify the next production proof.','Existing construction allowances are exhausted; historical replay is not prospective reduction in Director inputs.'),
 'versioning':('Pin policy and exact evidence in append-only events and recheck admissions.','Changed source bytes, proof versions and test plans block; explicit migration retains counts and creates an unknown-evidence obligation.'),
 'economics':('Use local mocked/offline tests and record a partial verification interval.','No paid calls or new dependencies; overall work time and improvement percentage remain unmeasured.'),
 'retrieval':('Use the fresh350 software packet and manually reconcile348 source findings.','Active controller findings enter packets; no unsupported claim that the global catalog already indexes all new historical conclusions.'),
 'current_state':('Read actual current production task snapshots without migrating them.','Appearance52/52 and motion12/12 retained; accepted Pashtun media and production assets not edited.'),
 'au_reuse':('Separate retained neutral proof from changed actor qualification.','Frozen c23 positive and changed-use cases have different outcomes; numerical landing proof does not qualify whole rearing.'),
 'au_review':('Preserve original method failures and test the review mechanism itself.','c13 missing proof, c35 representation regression and c48 falsifier trigger when correctly classified; semantic truth remains a review responsibility.')}
packet=pk.read_json(root,'.runtime/knowledge-pilot213/workflow350.json')
assert set(actions)=={x['id'] for x in packet['obligations']}
evidence=[bind('results/workflow350/verification.json'),bind('results/workflow350/replay-final.json'),bind('docs/knowledge/RETROSPECTIVE_WORKFLOW_350.md')]
review=dict(packet_digest=packet['packet_digest'],scope='Software implementation only; not production artistic qualification',
    checks=[dict(id=o['id'],kind=o['check_kind'],status='PASS',action_taken=actions[o['id']][0],observation=actions[o['id']][1],evidence=evidence) for o in packet['obligations']],
    hypotheses=[dict(prediction='A manual replan could exhaust the limit without triggering synthesis.',observation='Review identified an uncovered manual transition; the final test exercises this path.',response='Centralized exhaustion-event capture and tested extension retention.',result='resolved'),
                dict(prediction='An unrelated PASS or changed proof could clear a finding.',observation='Negative-control/worker PASS, changed conditions and replacement proof tests block the claimed effect or reuse.',response='Bind effect to post-admission production/diagnostic evidence and exact proof version.',result='resolved'),
                dict(prediction='A structurally valid false visual PASS can evade policy.',observation='The explicit false-PASS test confirms this semantic limitation.',response='Limit qualification to declared-evidence workflow; retain source review and prospective test.',result='resolved')],
    adjacent_regressions='Reviewed lightweight routing, shared correction limits, native recovery, reference roles, proof manifests, staged runner and prior knowledge/review controls. No production assets changed.',
    stopping_reason='Offline implementation, API/migration procedure and seven frozen classifications complete. Next requires authorized prospective bare-deformation and preserved-garment transfer proof; no efficiency or artistic pass claimed.')
save('review.json',review)
gate=pk.check_review(root,packet,review)
save('knowledge-gate.json',gate)
print(json.dumps(dict(tests=report['tests'],gate=gate,live_states=states),indent=2))
raise SystemExit(0 if gate['ready_for_review'] else 2)
