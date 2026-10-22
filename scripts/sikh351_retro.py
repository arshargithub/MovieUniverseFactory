"""Retained failure admission, not artistic closure."""
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance'
def bind(path):return dict(path=path,sha256=pk.file_hash(r/path))
ev={p:bind(p) for p in ['results/sikh348/CAUSAL_LEDGER.md','results/sikh348/NEXT_PROOF.md','results/sikh351/GROUNDING_RECONCILIATION.md','results/sikh351/challenge.json']}
c.retrospective(task,'outcome',dict(attempt='appearance-c52-retained',role='production',origin='reviewed348-history',
    observations=[dict(requirement='form',status='FAIL',foundation=True,observation='Bare52 hard upper-arm/elbow form exists beneath failed body-shell garment. Root cause unresolved;46 roll-only already failed.')],evidence=ev),'sikh351-legacy-form')
for key in ('__migration__','form'):
    gate=c.retrospective_packet(task)['gates'][key]
    response=dict(cause='350 policy exposed unmigrated history;348 establishes representation and review failures, not proven bone cause.' if key=='__migration__' else 'Hypotheses: rest mesh, weight ownership, split-joint frame or custom pose. Clothing is independently unsuitable.',
        uncertainty='No whole actor qualification. Actual source control results still required.',
        change_or_retain_rationale='Retain immutable history,23 cloth control and52 source. Replace cosmetic iteration with bare matched causal controls.',
        preserve='Original335 task, cycles53–57, motion12, accepted co-star and failed23–52 evidence.',
        test='Verify retained counter/history/source reconciliation.' if key=='__migration__' else 'Matched rest/native bend/custom front/back and actual joint/weight inventory.',
        expected='History preserved and sources fresh, without artistic closure.' if key=='__migration__' else 'Identify whether deformation originates before or during custom posing; then repair demonstrated cause before garment transfer.',
        failure_response='Keep blocked finding; repair affected grounding/strategy within same allowance. No false PASS or new task.',
        target_stage='STRATEGIZING',plan=pk.digest(c.state(task)['brief']),gate_digest=pk.digest(gate),evidence=ev)
    event='sikh351-response-'+key;c.retrospective(task,'response',dict(key=key,response=response),event)
    challenge=dict(response_event=event,checks={
        'causal_test':dict(status='PASS',observation='Controls distinguish rest/native/custom without claiming a root cause beforehand.'),
        'actual_method':dict(status='PASS',observation='Read handler: transient rig/visibility/light edits only; actual bones and weight inventory returned.'),
        'preservation':dict(status='PASS',observation='No native save in diagnostic, original52 and23 untouched; main and motion task limits retained.'),
        'authority':dict(status='PASS',observation='Explicit five appearance corrections; no new motion cycle or spend.')},
        counterexample='Fresh bookkeeping can coexist with a visibly malformed arm; migration closure must never close form.',evidence=ev)
    c.retrospective(task,'admit',dict(key=key,challenge=challenge),'sikh351-admit-'+key)
c.retrospective(task,'outcome',dict(attempt='sikh351-migration-proof',role='diagnostic',origin='current-source-counter-audit',
    observations=[dict(requirement='__migration__',status='PASS',observation='Appearance53/max57 retains original authority/history. Motion12/max12 unchanged. Fresh351 knowledge packet reconciles330 addition explicitly; failed native52 not promoted.')],evidence=ev),'sikh351-migration-proof')
c.retrospective(task,'evaluate',dict(key='__migration__',evaluation=dict(result='effective',outcome_event='sikh351-migration-proof',observation='Administrative reconciliation only; form remains TESTING, not accepted.',evidence=ev)),'sikh351-migration-effect')
print({k:v['status'] for k,v in c.retrospective_packet(task)['gates'].items()})
