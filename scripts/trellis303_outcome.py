"""Evidence-shape gate for a capacity-blocked recovery, never a visual pass."""
import json
from movie_factory import production_knowledge as pk
from trellis301_prepare import ROOT,sha,dump
import trellis303_cloud as m


def main():
    m.configure();out=m.OUT
    receipt=json.loads((out/'teardown-verification.json').read_text())
    assert not any(receipt['remaining'].values())
    assert not receipt['terminated_instances'] and not (out/'launch.json').exists()
    assert len(list(out.glob('capacity-failure-*.json')))==4
    assert len(list(out.glob('larger-capacity-failure-*.json')))==4
    # Preserve the dispatch packet. The only post-dispatch controller correction
    # adds its missing sys import for independent verification; manually reviewed.
    task=json.loads((out/'task.json').read_text())
    task['id']='trellis303-capacity-closure'
    task['inputs']['scripts/trellis303_cloud.py']=sha(ROOT/'scripts/trellis303_cloud.py')
    task['inputs']['scripts/trellis303_outcome.py']=sha(ROOT/'scripts/trellis303_outcome.py')
    packet=pk.task_packet(ROOT,task)
    dump(out/'outcome-task.json',task);dump(out/'outcome-packet.json',packet)
    assert packet['dispatch_ready'],packet['blockers']
    files=[out/name for name in ('REVIEW.md','INTERNAL_REVIEW.md','authority.json','local-checkpoint-check.json',
        'preflight.json','guard-test.json','payload.json','teardown-verification.json')]
    evidence=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in files]
    notes={
        'authority':'Exact18.33MB private payload and one3.50USD recovery approved; no GPU launched.',
        'strategy':'Saved-latent decode and fresh-process repair/export implemented; GPU proof blocked by capacity.',
        'anticipation':'Recorded raw geometry checkpoint, memory telemetry and source/ensemble visual failure hypotheses before dispatch.',
        'stopping':'Eight capacity failures; no created worker. Temporary resources removed, no blind model retry.',
        'versioning':'Latent SHA and payload frozen; originals preserved. No new native exists.',
        'economics':'One3.50USD hold, prior15 retained, actual billing unknown. No GPU inference ran.',
        'rights':'Same admitted runtime/models/export route; no new provider, input image, encoder or credential upload.',
        'current_state':'Approved Sikhv03 and accepted Pashtun/scene300 preserved; actor admission still blocked.',
        'au_reference':'Root inspected v03, known-failing512 and accepted Pashtun shot; preserved their distinct scopes.',
        'sikh_scope':'Static-source recovery only; no body/cloth/scene edits.'}
    checks=[]
    for obligation in packet['obligations']:
        key=obligation['id']
        checks.append({'id':key,'kind':obligation['check_kind'],'status':'PASS' if key in notes else 'NOT_RUN',
            'action_taken':'Manual capacity outcome review; no invented GPU or visual pass.',
            'observation':notes.get(key,'No recovered1024 render or performance evidence; corresponding admission unrun.'),
            'evidence':evidence})
    review={'packet_digest':packet['packet_digest'],'scope':'Prepared recovery blocked by AWS capacity; not source/actor admission',
        'checks':checks,'hypotheses':[
            {'prediction':'A same48GB worker can run within the approved reservation.',
             'observation':'Both fitting host sizes unavailable in four zones; no instance created.',
             'response':'Preserve frozen package, remove staging, retry only after renewed capacity/ledger admission.','result':'resolved'},
            {'prediction':'Separate decoder and native repair lifetimes recover the checkpoint.',
             'observation':'No GPU launched, so hypothesis is untested.',
             'response':'Do not infer quality or runtime failure from capacity.','result':'not_observed'}],
        'adjacent_regressions':'Accepted assets unchanged; new geometry, materials and motion NOT_RUN.',
        'stopping_reason':'AWS capacity unavailable; safe prepared independent work complete; integrated GPU comparison unfinished.'}
    dump(out/'outcome-review.json',review)
    gate=pk.check_review(ROOT,packet,review);dump(out/'outcome-production-gate.json',gate)
    dump(out/'budget-final.json',m.ledger().summary())
    dump(out/'budget-events.json',[json.loads(x) for x in (m.LOCAL/'budget.jsonl').read_text().splitlines()])
    print(json.dumps(gate,indent=2))


if __name__=='__main__':main()
