"""Fixed local evidence packaging for rejected283 construction; no native dispatch."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from movie_factory import production_knowledge as pk

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    out=ROOT/'results/sikh283';media=ROOT/'.runtime/art-direction/series01-sikh283'
    task=json.loads((out/'sikh283-verify-12.json').read_text())['task']
    task['id']='sikh283-final-failed-admission'
    task['intent']='Record failed integrated character admission and proposed authority-bound change of input route; no production approval or new provider dispatch.'
    # Only these explicitly reviewed local changes differ after dispatch.
    for p in ('scripts/sikh283_head.py','tests/test_sikh283_head.py','results/sikh283/ASSESSMENT.md'):
        task['inputs'][p]=digest(ROOT/p)
    for p in ('scripts/sikh283_review.py','results/sikh283/IMAGE_STUDIES.md'):
        task['inputs'][p]=digest(ROOT/p)
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    (out/'final-packet.json').write_text(json.dumps(packet,indent=2)+'\n')
    (out/'final-packet.md').write_text(pk.packet_markdown(packet))
    files=[p for p in media.rglob('*') if p.is_file()]
    manifest={str(p.relative_to(ROOT)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(files)}
    (out/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    receipts={str(p.relative_to(ROOT)):json.loads(p.read_text()) for p in media.rglob('*-receipt.json')}
    (out/'native-receipts.json').write_text(json.dumps({'receipts':receipts,'sum_process_seconds':sum(v['seconds'] for v in receipts.values()),'limits':'Process-seconds include overlaps, failures and diagnostic inspect/verify jobs; not elapsed work or CPU core-seconds. Ledger job union is separately recorded.'},indent=2)+'\n')
    def evidence(paths):return [{'path':p,'sha256':digest(ROOT/p)} for p in paths]
    report=['results/sikh283/ASSESSMENT.md']
    images=['.runtime/art-direction/series01-sikh283/control-11/front.png','.runtime/art-direction/series01-sikh283/control-10/eye-detail.png','.runtime/art-direction/series01-sikh283/control-12/front.png','.runtime/art-direction/series01-sikh283/control-12/rear.png']
    moving=[f'.runtime/art-direction/series01-sikh283/control-11/contact-{i:02d}.png' for i in range(1,7)]
    observations={
      'authority':('PASS','Executed local head283 scope; no new Meshy generation, paid API call, installation or purchase. Built-in style studies remained within standing image authority.'),
      'strategy':('FAIL','Integrated strategy existed, but surface and groom iteration continued despite a weak whole-head form. Recorded this process failure; do not claim ideal early gating.'),
      'visual_gate':('FAIL','Generic/schematic face, conspicuous groom boundaries and shell-like crown remain below v03/Pashtun floor; no Director-ready candidate.'),
      'anticipation':('PASS','Predicted generic/doll face, root discontinuity, crown shell and transform failures were explicitly tested; unresolved failures remain in gate.'),
      'stopping':('PASS','Stop this failed construction route at a demonstrated method limit; proposed character-derived provider input and purchase need new authority. No cosmetic go-ahead requested.'),
      'versioning':('PASS','All originals and failed controls retained;11 and12 reopen samples agree exactly. Geometry hashes do not certify curve motion or visual quality.'),
      'economics':('PASS','Prospective activity and native job receipts retained; pre-capture effort and engineering token/cost allocation unknown. No inferred API-equivalent cost.'),
      'representation':('FAIL','Bilateral annular lids and procedural groom support control but not sufficiently authored character form. Generated projection is not a production albedo or topology repair.'),
      'anatomy':('FAIL','Eyes remain schematic, facial/brow integration incomplete, rear lower bust has an exposed open/overlapping boundary.'),
      'motion':('FAIL','144 chronological frames show closure, head turn, modest bow and return; this does not read as a convincing finished recognition/respect performance.'),
      'secondary':('NOT_RUN','No validated secondary beard/fabric dynamics. Small rigid attachment control is not secondary-motion qualification.'),
      'look':('FAIL','12 painted marks alter skin finish without achieving accepted co-star construction/material hierarchy.'),
      'rights':('PASS','Source free-plan provenance retained; modifications do not reset rights. Proposed paid/private content use is unapproved and no no-training claim is made.'),
      'current_state':('PASS','Pashtun remains provisionally accepted; Sikh native remains unaccepted. This diagnostic does not increment production acceptance.'),
      'au_reference':('PASS','Compared v03, original illustrated C, accepted Pashtun portrait and shot evidence; rejected candidates are not the quality floor.'),
      'au_deformation':('FAIL','Sampled reopen succeeds but brow hairs are skull-attached while skin expression changes; root coupling is not qualified. Rear bust defect remains.'),
      'au_performance':('FAIL','Mechanical head/eye motion present; intended expressive character performance not admitted.'),
      'au_contact':('NOT_RUN','No actual hand/tuck/cloth release or bike support. Interface strip alone cannot demonstrate contact.'),
      'au_surface':('FAIL','Projected skin retains lighting and transition limitations; groom roots and crown surface remain too constructed.'),
      'sikh_scope':('PASS','Sikh only; no body/costume/entrance/music escalation, no Gurkha dispatch.'),
      'sikh_cloth':('NOT_RUN','Separate crown and hanging interface do not prove connected one-cloth manufacture or release; target is preserved, not silently replaced.'),
      'sikh_motion':('FAIL','Head diagnostic only; uncovered recognition is not artistically qualified, bike-supported greeting remains outside this proof.')}
    checks=[]
    for o in packet['obligations']:
        status,observation=observations[o['id']]
        paths=report+(images if o['check_kind']=='review' else [])
        if o['id'] in ('motion','au_performance','sikh_motion'):paths+=moving
        if o['id']=='versioning':paths+=['.runtime/art-direction/series01-sikh283/control-11/verify.json','.runtime/art-direction/series01-sikh283/control-12/verify.json','results/sikh283/artifact-manifest.json']
        checks.append(dict(id=o['id'],kind=o['check_kind'],status=status,action_taken='Apply the scoped283 construction and failure-seeking review; preserve failures and deny character admission where unresolved.',observation=observation,evidence=evidence(paths)))
    review=dict(packet_digest=packet['packet_digest'],checks=checks,hypotheses=[
      dict(prediction='Working component eye plus generic face/groom/crown will make a credible same-film lead.',observation='Eleven completed native controls remain schematic and accessory-driven beside accepted Pashtun.',response='Reject admission and stop this construction route; propose character-specific input with explicit rights/spend decision.',result='unresolved'),
      dict(prediction='Pupil shading contributes to blank-eye appearance.',observation='10 closeup shows broad reflection;11 reduced specular exposes iris/pupil but anatomy still fails.',response='Retain limited shader correction, do not call the whole eye resolved.',result='resolved'),
      dict(prediction='Illustrated skin projection repairs same-film mismatch.',observation='12 adds marks but not missing form and introduces baked illumination/transitions.',response='Reject as production treatment; retain diagnostic raster provenance.',result='unresolved')],
      adjacent_regressions='02 inherited crown parent changed on reopen;07 uninitialized pigment attribute darkened face;10 shorter curled roots increased frizz.12 rear bust/crown and11 expression-root coupling remain failed. Protected sources unchanged.',
      stopping_reason='Integrated head not achieved. Failed method report only, no positive foundation recommendation. New proposed character-specific provider input and paid trial require Director authority.')
    (out/'review.json').write_text(json.dumps(review,indent=2)+'\n')
    gate=pk.check_review(ROOT,packet,review)
    (out/'gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    print(json.dumps(gate,indent=2))
    if gate['ready_for_review']:raise AssertionError('Known failure must remain blocked')

if __name__=='__main__':main()
