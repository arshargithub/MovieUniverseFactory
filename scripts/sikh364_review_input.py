"""Author exact scoped review observations; never submit or manufacture AV judgment."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

r = Path(__file__).resolve().parents[1]
o = r / 'results/sikh363'

def bind(path):
    return dict(path=path, sha256=pk.file_hash(r / path))

paths = {
    'static': ('results/sikh363/STATIC_REVIEW364.md', 'technical', 'Actual image observations and intended-framing exclusions.'),
    'chronology': ('results/sikh363/CHRONOLOGICAL_REVIEW364.md', 'technical', 'All106 source timed frames; full-speed AV explicitly pending.'),
    'encoded': ('results/sikh363/ENCODED_REVIEW364.md', 'technical', 'Actual decoded samples and media profile; no playback/listening claim.'),
    'manifest': ('results/sikh363/media-manifest.json', 'technical', 'All106 source-frame hashes, exact clip and stream properties.'),
    'clock': ('.runtime/factory-native/sikh363-motion-c41-save/performance363.json', 'technical', 'Exact final source/retime/contact/camera/gaze report; grasp metrics are not hoof constraints.'),
    'support': ('results/sikh363/CLOCK_AND_SUPPORT364.md', 'technical', 'Measured control limits, event clock and separate image observations.'),
    'rig': ('results/sikh363/RIG123_CONTROL.json', 'technical', 'Actual314 anatomical segment ratios only; not all-frame hoof-ground proof.'),
    'cloth': ('results/sikh363/CLOTH121_PROOF.json', 'technical', 'Real189-frame final-action solver cache with pins, edge/vertex pole guards and settings.'),
    'chest': ('results/sikh363/CHEST113_RESULT.md', 'technical', 'Actual Basis and corresponding shape/nap repair; rejected112 not retained.'),
    'preserved': ('.runtime/context-hygiene/runs/sikh363-protected-hash/stdout.log', 'technical', 'Verified unchanged accepted Pashtun and99 source hashes.'),
    'repeat': ('results/sikh363/CANONICAL42_ALL.json', 'technical', 'All16 actual314 controls pixel equal; no universal replay qualification.'),
    'reference': ('.runtime/art-direction/sikh363-reference-rear-crop.jpg', 'image', 'Actual faithful action-reference phases; no direct-motion claim.'),
    'accepted': ('.runtime/art-direction/series01-finish248/opening08/actual-450.png', 'image', 'Unmodified accepted film comparator, not an identity or lighting match.'),
    'fist': ('.runtime/factory-native/sikh363-motion-c41-right_hand/frame-0314.png', 'image', 'Actual new right fist at crest; curled phalanges and thumb across index/middle.'),
    'front': ('.runtime/factory-native/sikh363-motion-c42-repeat/frame.png', 'image', 'Actual reopened final314 at intended camera.'),
    'back_stance': ('.runtime/factory-native/sikh363-appearance-c123-reverse/frame-0283.png', 'image', 'Current no-edit reverse283 cuff/shoulder/waist/seat.'),
    'back_crest': ('.runtime/factory-native/sikh363-appearance-c123-reverse/frame.png', 'image', 'Current no-edit reverse314 raised sleeve, crown/neck/seat.'),
    'back_arrival': ('.runtime/factory-native/sikh363-appearance-c123-reverse/frame-0333.png', 'image', 'Current no-edit reverse333 recovery and retained hoist.'),
    'decoded': ('.runtime/art-direction/sikh364-review/decoded/samples.jpg', 'image', '17 actual decoded samples across cuts, cue, rear and recovery, not playback.'),
}
for i in range(1,17):
    paths[f'frames{i:02d}'] = (f'results/sikh363/contact-sheets/batch{i:02d}.jpg', 'image', 'Actual chronological source frames plus repeated314; all sheets inspected.')
evidence = {k: dict(binding=bind(p), mode=mode, scope=scope) for k,(p,mode,scope) in paths.items()}
media = json.loads((o/'media-manifest.json').read_text())
derived = dict(clip=media['video'], manifest=bind('results/sikh363/media-manifest.json'))

appearance = {
    'preservation': 'Only new serial job derivatives were written. Accepted Pashtun and99 source hashes remain unchanged; old failures, native sources and task history are retained. No crowd, principal, new identity, upload or release action.',
    'form': 'At whole-mounted shot size, the wrapped crown, supported indigo coat/ochre layers, lower flare and fitted pad remain readable. Actual reverse283/314/333 checks the raised shoulder/arm and waist/seat rather than assuming a front-only fit.',
    'interfaces': 'Current intended frames and reverse controls retain neck/crown, shoulder/sleeve, cuff/grasp, band/robe/seat and pad/horse continuity. Right thumb no longer hooks backward; chest fairing is applied to actual Basis and matching shape/nap layers rather than hidden by clothes. Flag is tied at three points with real cloth deformation.',
    'evidence': 'All106 actual frames252..357, reference phases, accepted film comparator, final reverse controls and decoded samples are present and inspected. Profile432x768/16,24fps; complete58-frame leader shot plus24 actual frames each side. Hashes and repeat controls prove provenance, not artistic truth.',
    'whole_look': 'At the actual whole-mounted framing, textured indigo/ochre layers, beard/crown, skin variation, dark coat, head/ears/muzzle, mane/tail and differentiated tack read as one supporting actor/horse. No identified frame-visible layer or contact blocker. Diagnostic close face remains below principal portrait tier and is not qualified for that use; same-agent judgment is fallible.',
}
motion = {
    'preservation': appearance['preservation'] + ' Final42 is a no-edit copy of121 with41 timing;123 inspections do not change action or cache.',
    'support': 'All timed phases inspected for visible hind support, folded/returning forelegs and hoof inversion. Actual314 inventory corroborates24 anatomical segment lengths within3.52e-5 relative difference. This is not all-frame numeric hoof-ground proof; projected contacts and real-time weight remain separately limited.',
    'phases': 'Horse prep clock is exactly retained through300. Material spear drive reaches291, rise follows; hoist293..304 stays raised as permission. Airborne43 to21frames, short active crest314..317, reaching descent through326, image-visible arrival327/328 and absorption333. No prolonged held near-ground pose in timed frames. Full-speed naturalness remains human-pending.',
    'rider': 'Head/neck/attachments turn toward exchange and shaft stays clear of face. Rider/arm/grasp/seat follow shared final clock; right fist and rein contact checked at283/314/333. Anatomical chest has no prior pendant bulge/ridge. Real flag121 solves on exact final pole action with original three ties and both collision modes, not a transferred rigid or retimed cloth layer.',
    'evidence': 'All106 final source frames, all16 repeat controls, actual phase/hand/chest/flag/back controls, exact cache/action bindings and encoded samples inspected. Video is24fps silent with one-second real context each side. Static/timed/source evidence is not direct motion or audio.',
    'director_motion': 'NOT_RUN: Director313 must judge full-speed faithful-reference fluidity, landing weight, crest length, preparation readability, coordinated rider response and flag permission signal in the exact clip. No agent playback or listening claimed.',
}
comparison = 'Original Director363/364 intent, faithful reference-b14..19s and accepted-film floor; not incremental improvement over a rejected candidate. Full-speed motion remains explicit Director313 judgment.'
sets = {
    'preservation': ['preserved','manifest','repeat','clock'],
    'form': ['static','front','back_stance','back_crest','back_arrival','accepted','frames09','frames11'],
    'interfaces': ['static','fist','back_stance','back_crest','back_arrival','cloth','chest','frames06','frames11','frames12'],
    'whole_look': ['static','front','accepted','back_stance','back_crest','frames09','frames11','decoded'],
    'support': ['support','rig','reference','frames06','frames09','frames11','frames12'],
    'phases': ['chronology','clock','support','reference','frames05','frames06','frames09','frames10','frames11','frames12'],
    'rider': ['static','clock','cloth','chest','fist','back_crest','frames05','frames09','frames11'],
    'evidence': list(evidence),
}
for label, applications, intent in [('appearance',appearance,'appearance'),('motion',motion,'rear')]:
    checks = [dict(id=k,status='NOT_RUN' if k=='director_motion' else 'PASS',observation=v,comparison=comparison,evidence=[] if k=='director_motion' else sets[k]) for k,v in applications.items()]
    ref_use = {'reference_rear': 'Actual reference governs loading/lift/brief crest/reaching arrival/absorption and spear cue. All current phases and attached costume/seat checked; no full-speed equivalence is self-certified.'}
    refs = {'reference_rear':dict(observation=ref_use['reference_rear'],comparison=comparison,evidence=['reference','chronology','clock','frames06','frames09','frames11','back_crest'],aspects=[dict(id='whole_pose',status='PASS',observation='Source and timed-image portion inspected across complete action; visible coupling/costume ownership present. Actual real-time fluidity remains NOT_RUN.')])}
    if label=='appearance':
        ref_use['accepted_film'] = 'Actual accepted Pashtun450 compared at respective shot roles: layered credible materials/forms, not identity, tying style, equal pixel density or lighting duplication.'
        refs['accepted_film'] = dict(observation=ref_use['accepted_film'],comparison=comparison,evidence=['accepted','static','front','back_crest','decoded'],aspects=[dict(id='supporting_same_film',status='PASS',observation='Supporting mounted-shot material/garment integration and living-character detail inspected; principal close portrait and Director overall effect not qualified.')])
    review = dict(checks=checks,evidence=evidence,reference_checks=refs,
        audience_read='A mounted leader drives the signal, horse gathers and rears briskly, then lands with the spear held high as permission. Human playback must judge whether that intention reads with adequate weight and fluidity.',
        strongest_counterexample='A mechanically coherent source and clean stills can still feel robotic, too quick or weightless. Real cloth does not automatically read as natural motion. Full-speed Director AV remains required. A closer principal portrait would exceed this supporting-shot qualification.',
        adjacent_review='Actual reverse raised sleeve/shoulder, neck/crown, waist/seat/pad, fist/rein/cuff, head attachments, chest/foreleg junction, flag/pole/face, landing debris and real cuts reviewed. Principal/crowd/terrain/audio remain outside this isolated scope.',
        open_visible_defects=[],intent_checks={intent:dict(scope='supported_evidence_only',status='PASS',observation='Complete scoped source, technical, image and timed-image duties inspected with current evidence. Director full-speed judgment remains NOT_RUN; no known source/frame defect is waived.',comparison=comparison,evidence=list(evidence))},planning_gaps=[])
    data=dict(version='sikh364-final41-clock-cloth121-106frames-'+label,applications=applications,reference_applications=ref_use,review=review,derived_media=derived)
    p=o/(label+'-final-input.json');assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n')
print('Manually authored scoped observations prepared; controller submission and fresh gates still required.')
