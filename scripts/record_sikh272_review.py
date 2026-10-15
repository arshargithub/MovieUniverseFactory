"""Freeze the manual272 failure assessment; never infers visual PASS from files."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from movie_factory import production_knowledge as pk

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    out=ROOT/'results/sikh272';assessment='results/sikh272/ASSESSMENT.md'
    old=json.loads((ROOT/'.runtime/knowledge-pilot213/sikh272-construct-06.json').read_text())
    task=old['task'].copy();task.update(id='sikh272-method-disposition',intent='Record actual failed construction and method boundary; no positive candidate handoff.')
    inputs=list(task['inputs'])+[assessment,'scripts/record_sikh272_review.py',
        'docs/planning/RELEASE_01_PLAN.md','docs/planning/RELEASE_01_STATUS.json',
        '.runtime/art-direction/series01-sikh272/construction-study/PROMPT.md']
    for n in range(1,7):
        folder=ROOT/f'.runtime/art-direction/series01-sikh272/candidate-{n:02}'
        inputs.extend(str(p.relative_to(ROOT)) for p in folder.iterdir() if p.suffix in {'.json','.png','.py'})
    task['inputs']={p:digest(ROOT/p) for p in sorted(set(inputs))}
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise RuntimeError(packet['blockers'])
    (out/'packet.json').write_text(json.dumps(packet,indent=2)+'\n')
    (out/'packet.md').write_text(pk.packet_markdown(packet))
    failures={'visual_gate':'FAIL','representation':'FAIL','anatomy':'FAIL','look':'FAIL',
        'au_reference':'FAIL','au_deformation':'NOT_RUN','au_performance':'NOT_RUN',
        'au_contact':'NOT_RUN','au_surface':'NOT_RUN','motion':'NOT_RUN','secondary':'NOT_RUN',
        'sikh_cloth':'NOT_RUN','sikh_motion':'NOT_RUN'}
    observations={
        'authority':'Native derivatives only; no paid calls/installations/publication/accepted-source changes. New service route proposed, not executed.',
        'strategy':'Changed fan coverage, changed surface representation, tested existing authored layout and eye registration. All fail integrated floor; route stopped at method boundary.',
        'visual_gate':'06 front/both obliques/profile/rear/crown/clay inspected; weak face/lids, constructed moustache, neck-root hairs and deficient crown/back. No candidate handoff.',
        'anticipation':'Predicted shell/groom/eye/ensemble failures tested; adjacent profile hair regression identified. No automatic aesthetic-judgment claim.',
        'stopping':'No viable foundation. Stop unsuccessful representation route, not lower quality or ask to accept diagnostic06. Proposed new geometry-source route needs service/license decision.',
        'versioning':'Original references/source digests bound; all six job receipts and five native hashes retained. No fresh reopen/media backup claim.',
        'economics':'Ledger captures five successful builds and one sandbox crash; early context and exact model/token usage unknown. One built-in raster generation, no external paid API call.',
        'representation':'Continuous relief eliminates sheet intersections but creates ribbed shell. Donor layout retains inadequate crown/back. Groom remains constructed with stray neck roots.',
        'anatomy':'Eye projection improves in06 but lid integration remains unqualified; changing brows/nose too prevents isolated causal attribution.',
        'look':'Native failed whole form compared with v03 and accepted Pashtun. No matching-light artistic PASS or finish campaign.',
        'rights':'Existing verified turban acquisition retained. Meshy only researched; no acceptance of its service/license or image upload. Built-in study is internal non-authoritative interpretation.',
        'current_state':'271 rejection remains binding, Pashtun provisional acceptance protected.272 earns no accepted asset or release-gate increment.',
        'au_reference':'Bound original identity, illustrated C and accepted co-star, but new native result fails that floor; generated study is not adopted.',
        'sikh_scope':'Sikh only; action before music. Character and sequence remain incomplete; no new story/style choice adopted.'}
    checks=[]
    for r in packet['obligations']:
        status=failures.get(r['id'],'PASS')
        checks.append(dict(id=r['id'],kind=r['check_kind'],status=status,
            action_taken='Applied272 recorded scope/disposition; retain unresolved and unrun evidence, no admission by relabeling.',
            observation=observations.get(r['id'],'Not run in this failed static-form construction. No old cloth, rig/contact or motion qualification transfers.'),
            evidence=[dict(path=assessment,sha256=digest(ROOT/assessment))]))
    review=dict(packet_digest=packet['packet_digest'],scope='Failure/method-boundary report; native candidate admission remains blocked.',checks=checks,
        hypotheses=[dict(prediction='Native primary forms can clear approved identity and same-film floor before finish.',
            observation='Five completed controls fail; actual eyes, groom and cloth views expose unresolved form defects.',
            response='No artistic admission. Stop this method and propose a distinct geometry-source test.',result='unresolved')],
        adjacent_regressions='06 profile exposes beard roots extending toward neck; eye retreat removes protrusions but leaves narrow weak eyelid read. Accepted sources untouched.',
        stopping_reason='Unsuccessful construction route; no viable foundation or production completion claimed. New external service/license route requires Director choice and preflight.')
    (out/'review.json').write_text(json.dumps(review,indent=2)+'\n')
    gate=pk.check_review(ROOT,packet,review)
    (out/'gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    # Intentional negative admission is the expected outcome of this recorder.
    if gate['ready_for_review']:raise AssertionError('Failed art must never be admitted')
    forbidden=[s for s in gate['failures'] if any(x in s for x in ('STALE','MISMATCH','MISSING','INVALID','UNKNOWN_CHECK','DUPLICATE'))]
    if forbidden:raise AssertionError(forbidden)
    print(json.dumps(gate,indent=2))

if __name__=='__main__':main()
