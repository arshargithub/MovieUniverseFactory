"""One-time307 state construction from reviewed scope. Refuses to repin existing state."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/knowledge/review_control'
RESULT = ROOT / 'results/review307'


def bind(rel):
    return {'path': rel, 'sha256': pk.file_hash(ROOT / rel)}


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def main():
    if (DEST / 'active.json').exists():
        raise SystemExit('Already pinned; review source changes explicitly, never auto-repin.')
    task = dict(id='review307-controls', operation='knowledge', entities=['knowledge'],
                query='Scoped handoff enforcement current-state recovery visual evidence and calibration',
                intent='Implement306 process calibration only; no production/provider/cloud changes',
                phase='execution', inputs={p: bind(p)['sha256'] for p in [
                    'results/review307/STRATEGY.md',
                    'docs/knowledge/SIKH305_REVIEW_FAILURE_AUDIT306.md']},
                open_decisions=[], execution_authority={'source':'results/review307/STRATEGY.md',
                'scope':'Local review workflow and tests only'}, max_context_characters=48000)
    packet = pk.task_packet(ROOT, task)
    if not packet['dispatch_ready']:
        raise SystemExit(packet['blockers'])
    write(RESULT/'task.json', task); write(RESULT/'knowledge-packet.json', packet)
    with (RESULT/'knowledge-packet.md').open('x') as f:
        f.write(pk.packet_markdown(packet))
    specifications = [
        ('policy', ['authority','technical'], 'Apply agreed scoped quality floor; no development-label waiver, no new spend/tools/cloud; separate Director and final-production approval.'),
        ('references', ['authority','image'], 'Use reference-b15.5–19s for rear and accepted Pashtun as same-film quality anchor; preserve distinct identity/proxy scope; compare whole forms, not only the previous rejected candidate.'),
        ('camera', ['timed_images','direct_motion'], 'Steady OTS until front-side braking cut; preserve stop/crowd distance and first brake; oblique leader exchange, raised torch; continuous departure to horizon without arbitrary22s cutoff.'),
        ('rear', ['timed_images','direct_motion'], 'Reference-like spear cue, head bow, separate grip/weight transfer, powerful whole-body rise, brief balanced apex, heavy articulated landing and recovery; no hinged statue or slow foreleg lift.'),
        ('terrain', ['image'], 'Credible worn road, irregular drainage/banks, connected hill and approach farm structures; illustrated detail consistent with accepted film, not noise on smooth scoops.'),
        ('field_boundaries', ['image'], 'Earth access divisions belong to cultivated parcels with irregular, worn and rooted edges; no flat green carpet strips.'),
        ('debris', ['timed_images','direct_motion'], 'Dust expands/drifts/dilutes; solid tire and hoof debris follows landing, bounce/settling and persists while visible; no shrink-to-nothing or timed disappearance.'),
        ('horse_surface', ['image','timed_images'], 'Leader horse has convincing articulated anatomy, head/neck independence, coat/mane/tail response and intact forehooves in actual rear; supporting crowd/trees do not look like placeholders.'),
        ('departure', ['timed_images','direct_motion'], 'Brief legible traction loss, restrained lateral drift, traction recovery and forceful acceleration with a revealing camera; no superbike caricature.'),
        ('wind', ['timed_images','direct_motion'], 'Wheat responds to spatially varying gusts with lag, not synchronous pendulum motion; parcels continue into background.'),
        ('sound', ['technical','direct_audio'], 'Meaty period-bike engine, braking/slip and launch, horse neigh and weighty contacts synchronized to action in final music mix; no shuffle-only substitute or inaudible cue.'),
        ('technical', ['technical'], 'Decode, source/hash integrity, native dependency safety and existing strict replay obligations; retain actual failures, do not raise thresholds.'),
        ('protected', ['authority','technical'], 'Exact accepted20s Pashtun source and selected music retained; no Pashtun native rerender or unauthorized identity/narrative change.')]
    requirements=[dict(id=i,modes=m,criterion=c) for i,m,c in specifications]
    mapping={r['id']: {'checks':['policy','references','technical'],
        'reason':'307 knowledge-process implementation: apply existing routed obligation through scope/authority, reference-grounded review and evidence binding. Domain-specific305 requirements are manually reconciled in the contract, not inferred from knowledge-only routing.'}
        for r in packet['obligations']}
    contract=dict(schema=1,id='sikh-supporting-review307',
        intent='Corrected whole Sikh supporting scene plus unchanged-Pashtun joined preview; all305 observations except withdrawn farther-stop request.307 itself implements process only.',
        protected=['Accepted Pashtun20s and music','First brake feel','Current stopped bike/crowd positions','Approved Sikh direction; current proxy not admitted as principal'],
        exclusions=['Final principal head/body/connected face cloth integration is deferred under existing staging authority, not supporting-action quality.',
                    'Gurkha, new music/narration, cloud/TRELLIS/provider work and publication are outside this package.'],
        production_approval=False,requirements=requirements,knowledge_mapping=mapping)
    state=dict(schema=1,contract_id=contract['id'],
        checks={r['id']:('FAIL' if r['id'] in {'rear','terrain','field_boundaries','debris','technical'} else 'NOT_RUN') for r in requirements},
        defects=[dict(id='D305-'+i,requirement=i,status='OPEN',description=d) for i,d in [
            ('rear','Schematic articulated pose progression is not reference-level performance'),
            ('terrain','Smooth repeated drainage scoops and unconvincing ground'),
            ('field_boundaries','Flat green strips with straight exposed edges'),
            ('debris','Solid chips hidden after settling at fixed lifetime')]],
        artifacts={k:bind(p) for k,p in {
            'sikh':'.runtime/art-direction/series01-sikh305/delivery-13/sikh-29s.mp4',
            'joined':'.runtime/art-direction/series01-sikh305/delivery-13/pashtun-sikh-49s.mp4'}.items()},
        bindings={k:bind(p) for k,p in {
            'authority':'docs/knowledge/SIKH305_REVIEW_FAILURE_AUDIT306.md',
            'rear_reference':'.runtime/art-direction/series01-sikh256/references/reference-b.mov',
            'pashtun':'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4',
            'replay':'results/sikh305/reopen-13/comparison.json',
            'old_gate':'results/sikh305/delivery-13/production-gate.json',
            'knowledge_task':'results/review307/task.json'}.items()},
        knowledge_task='results/review307/task.json',knowledge_digest=packet['packet_digest'],
        capabilities=dict(image=True,timed_images=True,technical=True,authority=True,direct_motion=False,direct_audio=False))
    write(DEST/'contract.json',contract);write(DEST/'state.json',state)
    write(DEST/'active.json',dict(contract=bind('docs/knowledge/review_control/contract.json'),state=bind('docs/knowledge/review_control/state.json')))
    print(json.dumps({'dispatch_ready':True,'obligations':[r['id'] for r in packet['obligations']],
                     'requirements':len(requirements),'known_open_defects':len(state['defects'])}))


if __name__=='__main__':main()
