"""Record this pass's explicit manual findings, not an automatic visual judge."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh257_contract import ROOT, digest

BASE = ROOT / '.runtime/art-direction/series01-sikh257'
PACKET = ROOT / '.runtime/knowledge-pilot213/sikh257-layout_eevee-03.json'


def evidence(relative):
    return {'path': relative, 'sha256': digest(ROOT / relative)}


def main():
    packet = json.loads(PACKET.read_text())
    report = 'docs/planning/SERIES_01_SIKH_EXECUTION_257.md'
    sheet = '.runtime/art-direction/series01-sikh257/layout_eevee-03/review-sequence.jpg'
    receipt = '.runtime/art-direction/series01-sikh257/jobs/sikh257-layout_eevee-03.receipt.json'
    findings = {
        'authority': ('PASS', 'Kept Sikh-only scope, one cloth and nonrecurring personal recognition; no new external paid calls, install or publication.'),
        'strategy': ('PASS', 'Recorded wrapped support transfer and body/tunic integration reassessment; final cloth must not be fitted around a disposable head.'),
        'visual_gate': ('FAIL', 'Cap-like turban and coarse hands remain; native sequence withheld, not a completed visual handoff. Frame inspection is not direct playback.'),
        'anticipation': ('FAIL', 'Predicted garment and contact risks were tested; their complete visual exit is not achieved. Departure framing removes occluders but weakens corridor visibility.'),
        'stopping': ('FAIL', 'Native quality floor is not met. Only the separately labeled proposed character-look decision is being surfaced; no native PASS or scope closure.'),
        'versioning': ('PASS', 'Protected Pashtun and previous failed versions unchanged; final job binds inputs and snapshots source; new media local only.'),
        'economics': ('PASS', 'Lifecycle and job capture retained; early receipt walltime has provenance limits.32 native receipts include25 return-code successes and7 failures, not25 visual passes. Unknown token/cost stays unknown.'),
        'representation': ('FAIL', 'Generic head/body and cap-shaped cloth are diagnostic representations; generated concept is not evidence they achieved the illustrated quality floor.'),
        'anatomy': ('NOT_RUN', 'Fixed-length IK tested and neck proxy revised, but full final anatomy and hand-joint articulation are unqualified.'),
        'motion': ('FAIL', 'Complete312-frame staging exists; natural performance, supported final contact and corridor read remain unqualified.'),
        'secondary': ('NOT_RUN', 'Face span has a held lowered endpoint; launch dynamics are not proved. Dust is a declared world-space card preview.'),
        'look': ('FAIL', 'Native rough does not meet the illustrated style. Two separate generated look proposals remain unapproved and cannot substitute for moving evidence.'),
        'render_profile': ('NOT_RUN', 'Eevee360x64012fps is only a blocking profile. No final-resolution or strict reopen qualification and no promotion over protected Pashtun profile.'),
        'cache_safety': ('PASS', 'Fixed allowlisted handlers, isolated Blender preferences and immutable output versions; no credentials or asset scripts executed.'),
        'rights': ('NOT_RUN', 'Local reference study only. Body component and horse provenance need final release reconciliation; source references are not publication assets.'),
        'current_state': ('PASS', 'Preserved253 acceptance and255 recovery boundary;257 is Sikh-only unfinished development.'),
        'au_reference': ('PASS', 'Used original C as medium only and drawings as attributes; proposed face is not adopted or a literal reconstruction requirement.'),
        'au_deformation': ('NOT_RUN', 'Reach/length controls do not establish final deformation or anatomy. Cloth collision domain changed with tunic and needs final integrated proof.'),
        'au_performance': ('NOT_RUN', 'Chronological frame evidence does not certify real-time performance or complete horse rear/landing support.'),
        'au_contact': ('NOT_RUN', 'Hands remain coarse palm proxies; no final knuckle/grip proof is asserted.'),
        'au_surface': ('NOT_RUN', 'Proposed illustrated nighttime look reviewed separately; final moving material/dust hierarchy not achieved.'),
        'au_staging': ('FAIL', 'Approach/stop/greet/response/departure exist, but crowd clearance visibility weakened after camera change; requires correction.'),
        'au_reuse': ('NOT_RUN', 'Donors and tested-use limits recorded; new assets have no remote recovery copy or portable final reuse qualification.'),
        'sikh_scope': ('PASS', 'Continuous cloth, personal recognition without recurring leader, Sikh-only and action-before-music all retained.'),
        'sikh_cloth': ('FAIL', 'One indexed cloth exists with support transfer, but appearance, actual final grip and released/relaunch behavior are not qualified.'),
        'sikh_motion': ('FAIL', 'Rough support/gesture sequence built; horse and hand performance plus visible crowd corridor remain below the agreed exit.'),
        'sikh_geography': ('FAIL', 'Flat divided fields, trees, low mound and moon present. Rough crops/night surfaces lack required richness; not finished Punjab art direction.'),
    }
    checks = []
    for rule in packet['obligations']:
        status, observation = findings[rule['id']]
        checks.append({'id': rule['id'], 'kind': rule['check_kind'], 'status': status,
                       'action_taken': 'Applied the scoped strategy, inspected native chronological evidence and recorded the separate technical/creative limits in execution257.',
                       'observation': observation,
                       'evidence': [evidence(report), evidence(sheet), evidence(receipt)]})
    review = {
        'packet_digest': packet['packet_digest'],
        'scope': 'Actual native development gate. Expected BLOCK; no completed-sequence handoff. Generated creative proposals have separate pending Director status.',
        'checks': checks,
        'hypotheses': [
            {'prediction': 'A connected simulated strip might still fail the wrapped turban read and launch behavior.',
             'observation': 'Cap-like native silhouette and held lower end remain.',
             'response': 'Withhold native pass; use actual selected head/envelope before permanent fitting and test complete released motion.', 'result': 'unresolved'},
            {'prediction': 'Removing foreground crowd occlusion could remove story information.',
             'observation': 'Closer departure camera clears the view but reduces legibility of the opened corridor.',
             'response': 'Keep this staging defect internal and restore an establishing corridor view before finishing.', 'result': 'unresolved'},
        ],
        'adjacent_regressions': 'Checked neck proxy, slip-release continuity, cloth/tunic and hand spaces, source protection and crowd framing; no final anatomical, real-time or simulation PASS.',
        'stopping_reason': 'No native completion claimed. Genuine Director-owned character-look decision is separate from the still-blocked native deliverable; all failed controls preserved.'
    }
    (BASE / 'internal-review.json').write_text(json.dumps(review, indent=2) + '\n')
    gate = pk.check_review(ROOT, packet, review)
    (BASE / 'native-gate.json').write_text(json.dumps(gate, indent=2) + '\n')
    media = ['sikh-moonlit-concept-v01.png', 'sikh-uncovered-concept-v01.png', 'concept-prompt.txt', 'portrait-prompt.txt', 'layout_eevee-03/sikh-rough-26s.mp4']
    manifest = {'scope': 'Proposed creative studies and withheld native diagnostic', 'director_status': 'PENDING',
                'generation_method': 'built-in image generation, two calls', 'usage_tokens': None, 'allocated_subscription_cost': None,
                'native_ready': False, 'remote_backed_up': False,
                'files': [evidence(str((BASE / p).relative_to(ROOT))) for p in media]}
    (BASE / 'deliverable-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(gate, indent=2))
    raise SystemExit(0 if gate['ready_for_review'] else 2)


if __name__ == '__main__':
    main()
