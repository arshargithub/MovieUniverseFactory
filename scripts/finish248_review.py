"""Record manually completed248 inspection, retaining unresolved production gates.

Run only after the agent has inspected raw/encoded chronology and named controls.
This does not perform perception or turn technical checks into Director acceptance.
"""
import hashlib
import json
from pathlib import Path
from movie_factory.production_knowledge import check_review

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.runtime/art-direction/series01-finish248'


def main():
    evidence_paths = [
        OUT/'chronology-review-notes.md', OUT/'encoded-review-notes.md',
        OUT/'fit07/admission.json', OUT/'render-admission.json',
        OUT/'reopen-verification.json', OUT/'delivery01/manifest.json',
        OUT/'audio02/manifest.json', OUT/'encoded-qc01/verification.json',
        ROOT/'docs/planning/SERIES_01_FINISH245_246_REVIEW.md',
    ]
    replay = json.loads((OUT/'reopen-verification.json').read_text())
    if len(replay['controls']) != 11:
        raise ValueError('Replay coverage absent')
    replay_ok = replay['all_strict_one_level']
    evidence = [{'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in evidence_paths]
    observations = {
        'authority': ('PASS', 'Restricted native changes to248 fist and20s cut;252 separately authorizes private MP4 review upload.', 'No new paid model call, installation, public release or other-character production. Existing247 sound/look preserved.'),
        'strategy': ('PASS', 'Tested rest-joint/weight cause before adding more curl; inspected bare then integrated hands before rendering.', 'Shifted MCP origins and continuous weights address the distal apparent bend; failed03–05 controls retained.'),
        'visual_gate': ('NOT_RUN', 'Inspected480 raw and480 encoded frames, full-size and caption controls; kept modalities distinct.', 'Scoped visual correction evidence is recorded. Actual phone/real-time audiovisual acceptance remains pending; still inspection is not playback or hearing.'),
        'anticipation': ('PASS', 'Sought finger-root, thumb, cuff, rein, neighboring arm/body and encoded-text regressions.', 'Compact grasp retained through inspected phases; protected face, wardrobe, action and quote remain visible. No known new frame-level blocker identified in this scope.'),
        'stopping': ('NOT_RUN', 'Completed integrated20s derivative for the explicitly requested cellphone review.', 'Production acceptance remains pending actual Director phone review and release checks; no universal anatomy/renderer qualification.'),
        'versioning': ('PASS', 'Verified source/cache hashes, protected geometry and all-frame nonfinger/camera preservation; checked independent reopening.', '480 native frames and complete20s clean/captioned exports are bound in manifests. Source/profile binding succeeded; separate strict pixel replay result remains failed.'),
        'economics': ('PASS', 'Recorded native/local jobs and reused247 audio/graphics rather than regenerate sound.', 'No248–252 paid model calls. Audit250 fixed-cutoff usage/runtime remains historical; new rendering does not silently rewrite that baseline. Private S3 review is not a project backup.'),
        'identity': ('PASS', 'Preserved accepted face/head/hair/body geometry and compared actual-shot controls.', 'No identity redesign; hands and associated contact are the bounded native edit.'),
        'anatomy': ('PASS', 'Compared both bare hands from palm/side/knuckle views, finished surfaces and actual framing.', 'Apparent knuckle bend now joins the closed palm; thumb rests above fingers without prior backward tip. PASS is shot-specific visible fist correction, not a universal hand rig.'),
        'motion': ('NOT_RUN', 'Verified protected nonfinger motion/camera numerically and inspected every native/encoded frame in chronological sheets.', 'No new frame-level discontinuity observed; actual-speed audiovisual/phone judgment remains unperformed by agent.'),
        'contact': ('PASS', 'Inspected visible fist/rein relationship during opening, turn and uphill; used separate revealing controls for occluded hands.', 'Closed finger mass, thumb, rein route and cuff remain joined in scoped evidence. Hidden anatomy is not inferred from OTS views.'),
        'garment': ('PASS', 'Protected accepted garment sources/caches and inspected wrists, sleeves, wraps and harness through chronology.', 'No new cuff gap, disappearing wrap or neighboring garment discontinuity observed; not a new general cloth qualification.'),
        'secondary': ('PASS', 'Preserved hair, mane, tail, cloth and dust action and checked rendered chronology for adjacent changes.', 'No new missing/black groom or detached dust volume observed. Accepted motion treatment retained, not independently requalified for every possible shot.'),
        'look': ('PASS', 'Retained selected palette/light/materials and inspected encoded controls.', 'Sun-bleached terrain, blue costume and dramatic wake remain in the selected treatment; no art-direction redesign.'),
        'geography': ('PASS', 'Inspected OTS, frontal turn and uphill transition chronology.', 'Checkpoint/escape option retained before turn; checkpoint established below then face prioritized. Determined continuation remains before20s cut.'),
        'sword': ('PASS', 'Preserved right-hip sheathed sword and inspected attachment in visible phases.', 'No new suspension/side or garment discontinuity observed; no weapon-animation scope added.'),
        'render_profile': ('PASS' if replay_ok else 'FAIL', 'Ran source-bound1080x1920/24fps/16sample Metal profile with independent fresh-open controls; preserved the original result without threshold relaxation.', 'Ten controls meet1/255; frame363 has two red-channel values differing2/255 near the bottom edge, all other differences at most1. Strict criterion therefore FAIL. This is not evidence of a visible anatomical defect, but production renderer qualification is withheld.'),
        'cache_safety': ('PASS', 'Used protected source/caches and reversible corrected natives; verified all frame hashes during delivery.', 'Original245/247 and failed248 evidence preserved. No arbitrary external asset code or credential file passed to Blender.'),
        'narrative': ('PASS', 'Preserved247 selected short Kirk speech and exact timing/gain before the ending trim.', 'Director248 called247 fantastic; no new take or words. Actual phone intelligibility still belongs to the requested device review.'),
        'quotation': ('PASS', 'Retained verified visual quotation/attribution and original weathered paper; inspected encoded text controls.', 'Complete text, face clearance and timing retained. Graphic is designed, not a claim of authentic Churchill handwriting.'),
        'sound': ('NOT_RUN', 'Compared248 PCM with selected247 before19.75s and preserved unfaded20s trailer join.', 'Only standalone last0.25s fades. No fresh direct agent listening; phone speaker impact, intelligibility and ending need requested device review.'),
        'captions': ('NOT_RUN', 'Retained editable SRT/VTT and checked three encoded narration caption controls.', 'Desktop encoded controls are separate from actual cellphone/platform UI checks, which remain open.'),
        'rights': ('NOT_RUN', 'Preserved asset/music provenance and limited252 egress to requested private review MP4.', 'Comprehensive public-release licensing audit remains separate. A private preview upload does not authorize public release.'),
        'narration_a': ('PASS', 'Retained only introductory two lines ending impeccable.', 'Quotation and full attribution stay visual only; whole-trailer moral-conflict ending not moved into this sequence.'),
        'music_reference': ('PASS', 'Reused exact Director-selected original theme and247 B offset/ramp.', 'No generated substitute, Gemini taste adjudication, changed surge anchor or invented agent listening.'),
    }
    for name in ('rein248', 'finish248-audio'):
        packet=json.loads((ROOT/f'.runtime/knowledge-pilot213/{name}.json').read_text())
        checks=[]
        for rule in packet['obligations']:
            status,action,observation=observations[rule['id']]
            checks.append(dict(id=rule['id'],kind=rule['check_kind'],status=status,action_taken=action,observation=observation,evidence=evidence))
        review=dict(packet_digest=packet['packet_digest'],scope='Complete248 derivative for explicit252 phone review, not production/release acceptance.',checks=checks,
            hypotheses=[dict(prediction='Moving finger roots could distort palm/cuff or change other performance.',observation='Bare and integrated controls plus chronological inspection and nonfinger preservation checks recorded.',response='Retained only source-bound corrected derivative with scoped contact evidence.',result='resolved'),dict(prediction='The shorter ending and inherited mix may read differently on the intended phone.',observation='Native/encode checks cannot establish actual device experience; Director specifically requests this review.',response='Provide private downloadable full clip; withhold provisional production acceptance pending review.',result='unresolved')],
            adjacent_regressions='Compared visible wrists, cuffs, arms, neck, identity, wraps, reins, horse, dust, terrain, geography, quote and caption controls; accepted nonfinger motion is numerically preserved. Limits recorded by modality.',
            stopping_reason='Integrated requested20s clip prepared for explicit Director-owned phone review. No routine technical checkpoint substituted for delivery; production gates remain blocked honestly by strict replay discrepancy and real-time/device/rights checks. No failed criterion is waived to provide the specifically requested review file.')
        path=ROOT/f'.runtime/knowledge-pilot213/{name}-final-review.json'
        path.write_text(json.dumps(review,indent=2)+'\n')
        gate=check_review(ROOT,packet,review)
        path.with_name(name+'-final-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
        print(json.dumps({'name':name,**gate},indent=2))


if __name__ == '__main__':
    main()
