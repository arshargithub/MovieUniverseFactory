"""Bind the manually reviewed301 diagnostic outcome; never admit an actor."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from trellis301_prepare import ROOT, sha, dump


def main():
    out = ROOT / 'results/trellis301'
    cloud = out / 'cloud-1024'
    returned = ROOT / '.runtime/trellis301/cascade/retrieved/evidence'
    packet = json.loads((cloud / 'packet.json').read_text())
    teardown = json.loads((cloud / 'teardown-verification.json').read_text())
    assert not any(teardown['remaining'].values()), 'Cloud closure is not verified'
    # Keep the original unknown-cost settlement immutable. Its original null
    # response ID belongs to pre-launch staging cleanup, not a second paid run.
    from trellis301_cascade import ledger, LOCAL
    ledger_path = LOCAL / 'budget.jsonl'
    ledger_sha = sha(ledger_path)
    events = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    settled = [event for event in events if event['event_type'] == 'settled']
    assert len(settled) == 1 and settled[0]['cost_units'] is None and settled[0]['response_id'] is None
    summary = ledger().summary()
    assert summary['committed_usd'] == summary['reserved_unknown_usd'] == 3.5
    assert sha(ledger_path) == ledger_sha
    dump(cloud / 'budget-events.json', events)
    dump(cloud / 'budget-final.json', summary)
    dump(cloud / 'budget-reconciliation.json', {
        'reservation_id': settled[0]['reservation_id'], 'raw_ledger_sha256':ledger_sha,
        'raw_events_changed':False, 'original_unknown_settlement_event':settled[0]['event_id'],
        'worker_instance':'i-0fdc266d5cc5b0883', 'teardown_receipt_sha256':sha(cloud / 'teardown-verification.json'),
        'held_usd':3.5, 'actual_total_billed_usd':None,
        'reason':'Pre-launch cleanup recorded unknown settlement with null response; preserve it and link the actual single worker separately. No refund/released allowance inferred.'})
    failure = json.loads((returned / 'generation-failure.json').read_text())
    assert failure['type'] == 'RuntimeError' and 'CuMesh' in failure['message']
    assert failure['predecode_checkpoint_count'] == 1
    metadata = json.loads((returned / 'predecode/latents.json').read_text())
    assert sha(returned / 'predecode/latents.safetensors') == metadata['latents_sha256']
    assert sha(ROOT / '.runtime/trellis301/cascade/checkpoint/latents.safetensors') == metadata['latents_sha256']
    assert not (returned / 'head1024/candidate.glb').exists()
    files = [out / 'CASCADE_REVIEW.md', cloud / 'teardown-verification.json',
             cloud / 'retrieved-manifest.json', returned / 'generation-failure.json',
             returned / 'predecode/latents.json', out / 'export-review.json']
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in files]
    failed = {'visual_gate', 'representation', 'anatomy', 'look', 'au_surface'}
    unrun = {'motion', 'secondary', 'au_deformation', 'au_performance', 'au_contact', 'sikh_cloth', 'sikh_motion'}
    notes = {
        'authority': 'Exact302 private payload approval; single worker, original15USD bound, no extra10 or public release.',
        'strategy': 'Controlled export comparisons followed by one same-input/seed/sampler1024 test; source, conversion and actor remain distinct.',
        'anticipation': 'Decoder checkpoint anticipated failure; missing raw pre-repair checkpoint and allocator telemetry identified for correction.',
        'stopping': 'Single admitted cloud test ended in native repair OOM; recovered evidence and verified teardown. Further paid recovery is not silently dispatched.',
        'versioning': 'Returned manifest and independently downloaded latent hashes verified. No1024GLB/native replay exists; previous export reopen evidence remains separate.',
        'economics': 'All owned temporary resource classes independently absent; raw holds retained, total actual billing unknown.',
        'rights': 'No changed provider/model/dependency/export rights route; exact private payload consent and no credentials or unrelated content.',
        'current_state': 'Approved Sikhv03 and Pashtun253 preserved. Development scene300 is not final actor/release acceptance.',
        'au_reference': 'Root directly compared512 exports with approved Sikhv03 and accepted Pashtun.1024 has no viewable mesh and receives no visual pass.',
        'sikh_scope': 'Source-quality discriminator only; body, cloth and animated actor remain outside the completed test.'}
    checks = []
    for obligation in packet['obligations']:
        key = obligation['id']
        status = 'FAIL' if key in failed else 'NOT_RUN' if key in unrun else 'PASS'
        assert key in notes or key in failed or key in unrun, 'Unreviewed obligation: ' + key
        observation = notes.get(key, '512 source remains visually rejected;1024 quality NOT_RUN after native repair failure.' if status == 'FAIL' else 'No timed actor/deformation/contact/cloth evidence in this static-source diagnostic.')
        checks.append({'id':key, 'kind':obligation['check_kind'], 'status':status,
                       'action_taken':'Root manual diagnostic/visual source review; no automatic perceptual pass.',
                       'observation':observation, 'evidence':evidence})
    review = {'packet_digest':packet['packet_digest'], 'scope':'Completed diagnostic attempt with1024 output blocker; not production admission',
        'checks':checks, 'hypotheses':[
            {'prediction':'Export retention/atlas/opacity are sufficient to rescue512 source.',
             'observation':'Matched controls remain below approved source/co-star floor.',
             'response':'Reject export-only rescue.', 'result':'resolved'},
            {'prediction':'48GB capacity allows the full1024 path to complete.',
             'observation':'Decoders returned but native CuMesh repair initialization failed; no output mesh.',
             'response':'Preserve checkpoint; isolate decode/repair lifetimes with telemetry before another paid test.', 'result':'resolved'}],
        'adjacent_regressions':'Accepted assets unchanged; higher-retention512 beard roughness remains visible;1024 anatomy and motion unobserved.',
        'stopping_reason':'Admitted single-worker test exhausted with specific native repair memory blocker; no1024visual result; paid recovery requires separate admission.'}
    dump(out / 'outcome-review.json', review)
    gate = pk.check_review(ROOT, packet, review)
    dump(out / 'outcome-production-gate.json', gate)
    print(json.dumps({'checkpoint_hash_verified':True, 'source1024_quality':'NOT_RUN', 'gate':gate}, indent=2))


if __name__ == '__main__':
    main()
