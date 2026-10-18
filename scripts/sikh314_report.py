"""Bind manually recorded review observations to the exact local media.

This packages evidence; it does not judge images, motion or sound.
"""
import json,hashlib
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sikh314'
BASE=ROOT/'.runtime/art-direction/series01-sikh314'
def read(p):return json.loads(p.read_text())
def bound(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return {'path':str(p.relative_to(ROOT)),'sha256':h.hexdigest()}
def main():
    notes=read(OUT/'review-notes.json')
    assert notes['chronology_inspected_frames']==696
    assert notes['direct_audio'] is False and notes['direct_motion'] is False
    verification=read(BASE/'delivery-07/verification.json')
    audit=read(BASE/'audit-07/audit.json');assert all(audit['protected_checks'].values())
    paths=[BASE/'build-07/sequence.blend',BASE/'delivery-07/sikh-29s.mp4',BASE/'delivery-07/pashtun-sikh-49s.mp4',BASE/'delivery-07/verification.json',BASE/'audit-07/audit.json',OUT/'reopen-7/comparison.json',OUT/'review-notes.json']
    paths += [ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4',ROOT/'.runtime/art-direction/series01-sikh256/references/reference-b.mov']
    paths+=sorted((BASE/'delivery-07/encoded-controls').glob('*.png'))
    paths+=sorted((BASE/'delivery-07/chronology').glob('*.jpg'))
    queue=dict(schema=1,mode='EXCHANGE313_MANUAL_DIRECTOR_AV_QUEUE',status='AWAITING_DIRECTOR_AV',artifacts=[bound(p) for p in paths],checks=notes['checks'],defects=notes['defects'],strict_replay=read(OUT/'reopen-7/comparison.json')['status'],old305_strict_replay='FAIL_PRESERVED',protected_pashtun_sha256=verification['pashtun_original_sha256'],pashtun_rerendered=False,new_paid_calls=0,remote_push=False,remote_backup=False,limits='Same-agent visual/timed-frame/source checks, not independent review, direct hearing, direct-motion perception, final principal admission or release approval.')
    (OUT/'review-queue.json').write_text(json.dumps(queue,indent=2))
    task=read(OUT/'movie-7/task.json');task['id']='sikh314-final-review'
    # Reconcile actual current reviewed sources, not old builder success labels.
    task['inputs']={p['path']:p['sha256'] for p in queue['artifacts']}
    task['inputs'].update({str(p.relative_to(ROOT)):bound(p)['sha256'] for p in (OUT/'STRATEGY.md',ROOT/'docs/knowledge/review_control/README.md')})
    packet=pk.task_packet(ROOT,task)
    (OUT/'final-task.json').write_text(json.dumps(task,indent=2));(OUT/'final-packet.json').write_text(json.dumps(packet,indent=2))
    evidence=[bound(OUT/'review-queue.json'),bound(OUT/'review-notes.json')]
    passed={'authority','strategy','versioning','economics','cache_safety','rights','current_state','au_reference','au_reuse','sikh_scope'}
    review=dict(packet_digest=packet['packet_digest'],checks=[dict(id=o['id'],kind=o['check_kind'],status='PASS' if o['id'] in passed else 'NOT_RUN',action_taken='Applied scoped strategy and explicit313 manual human-AV queue; see named checks and observations.',observation='Exact evidence-bound local derivative; audiovisual closure and production qualification remain pending. Scope and source checks are separately recorded.',evidence=evidence) for o in packet['obligations']],hypotheses=notes['hypotheses'],adjacent_regressions=notes['adjacent_regressions'],stopping_reason='Complete integrated candidate queued for the Director-owned audiovisual assessment under313; not strict gate admission or final production.')
    (OUT/'knowledge-review.json').write_text(json.dumps(review,indent=2))
    (OUT/'knowledge-gate.json').write_text(json.dumps(pk.check_review(ROOT,packet,review),indent=2))
    print(OUT/'review-queue.json')
if __name__=='__main__':main()
