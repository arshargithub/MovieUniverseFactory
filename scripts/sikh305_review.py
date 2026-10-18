"""Record the actual scoped observations and fail closed on missing perception."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
from sikh305_delivery import ROOT, BASE, read, sha

# This is an evidence declaration, not an automatic perceptual evaluator.
# Each row states what was done and what remains unobserved.
OBS = {
    'authority': ('PASS', 'Applied Director305 scope and stop-location withdrawal.',
                  'No new paid calls, installations, cloud work, upload or principal admission.'),
    'strategy': ('PASS', 'Used integrated strategy, reference chronology and internal rejected controls.',
                 'Camera, support, horse action, contact effects and sound use explicit interfaces; failures09/10/12 retained.'),
    'visual_gate': ('NOT_RUN', 'Inspected all finishing frames sequentially and revealing controls.',
                    'This is image inspection; no direct real-time playback/listening capability was available. Full perceptual pass withheld.'),
    'anticipation': ('PASS', 'Bound thirteen requirements and additional camera/contact/dust failure hypotheses before final render.',
                     'Proof found crowd occlusion, neck-flex sign and camera endpoint errors; corrected before full render. No autonomous judgment claim.'),
    'stopping': ('NOT_RUN', 'Finished integrated media and technical checks without timer-based quality waiver.',
                 'Perceptual capability boundary remains; no production-ready or Director approval is asserted.'),
    'versioning': ('PASS', 'Preserved sources/rejected natives; bound final scene,696 frames and protected Pashtun.',
                   'Media hashes and eight fresh-process controls verified; local records are not remote backup.'),
    'economics': ('PASS', 'Captured native/local jobs and lifecycle; no provider call made in this pass.',
                  'Unknown engineering usage and coverage gaps remain explicit; no invented token total or global zero-cost claim.'),
    'representation': ('NOT_RUN', 'Kept principal as declared staging proxy and did not replace approved Sikh direction.',
                       'Final principal identity, editable face/cloth and same-film admission remain unqualified.'),
    'anatomy': ('NOT_RUN', 'Inspected horse support, full gather/rise/landing and joint controls.',
                'Shot-specific visible corrections do not admit final principal anatomy or a general equine rig.'),
    'motion': ('NOT_RUN', 'Authored shared event clock and inspected every frame plus numerical contact/camera traces.',
               'Reference causal phases are present in images; real-time speed, weight and acting remain unobserved directly.'),
    'secondary': ('NOT_RUN', 'Rebuilt world-space dust, contact clods, groom response and advected crop gusts.',
                  'Frame chronology checked for disappearance/intersection; natural temporal response is not certified without playback.'),
    'look': ('NOT_RUN', 'Inspected revised ground, hill, fields and lighting at delivery scale.',
             'Supporting look is a scoped candidate; principal proxy and lack of real-time review prevent whole-film artistic admission.'),
    'render_profile': ('FAIL', 'Rendered all696 frames at720x1280/64 Eevee samples; independently reopened eight32-sample diagnostic controls.',
                       'Strict1/255 repeat threshold failed: one red-channel value differs2/255 in frame140; seven controls meet threshold. No1080 native or general renderer qualification claim.'),
    'cache_safety': ('PASS', 'Used one serialized isolated offline Blender worker and protected source natives.',
                     'No embedded script execution, credentials or global preference changes; actual saved-scene reopening tested.'),
    'narrative': ('PASS', 'Reused exact accepted20s Pashtun source and PCM.',
                   'No new spoken quotation, voice take, script, provider call or Pashtun native rerender.'),
    'quotation': ('PASS', 'Preserved quotation graphics already present in protected Pashtun picture.',
                   'No new quotation/scan/attribution choice or release-rights conclusion made.'),
    'sound': ('NOT_RUN', 'Used recorded engine/friction/neigh and identified hoof foley; synchronized contacts, tested headroom and mono energy.',
              'Signal/provenance checks pass, but no direct hearing or auditory-quality certification is claimed.'),
    'captions': ('NOT_RUN', 'Kept existing picture and development labeling; added no new dialogue.',
                 'Release caption derivatives/device-safe-zone review remain separate and unperformed here.'),
    'rights': ('PASS', 'Screened five recording pages asCC0 and retained exact source/author/license/hash provenance.',
               'Only local adaptation used; no release/publication or blanket existing-asset clearance claimed.'),
    'narration_a': ('PASS', 'Preserved accepted Pashtun narration without a new take.',
                     'The protected20s PCM is exactly retained before final AAC encoding.'),
    'music_reference': ('PASS', 'Preserved selected music source and existing Sikh mapping, extending through29s.',
                         'No new generation, taste adjudication, narration ducking or source selection.'),
    'current_state': ('PASS', 'Read current authority and305 amendments; withdrew contradicted304 visual claims.',
                       'Pashtun acceptance remains separate from strict historical replay and final release; Sikh proxy remains explicit.'),
    'au_reference': ('PASS', 'Used original reference-b action and protected Pashtun/Sikh art authority.',
                      'Rejected controls were diagnostics, not new artistic acceptance targets.'),
    'au_deformation': ('NOT_RUN', 'Repaired shot-specific horse support and coordinated arm/sleeve/spear.',
                        'Principal garment/anatomical conversion is outside this staging-source correction and remains blocked.'),
    'au_performance': ('NOT_RUN', 'Separated head/poll motion, anticipation, rise, apex, landing and recovery.',
                        'Sequential inspection is recorded, not promoted to real-time performance judgment.'),
    'au_contact': ('NOT_RUN', 'Checked actual tire/boot support and rebuilt horse contact-born effects.',
                    'Numerical contacts do not admit final proxy fists, palms, rein grip or uncover contact.'),
    'au_surface': ('NOT_RUN', 'Reviewed continuous road/hill surfaces, ditch details and dust contrast.',
                    'Full finished-film moving-look acceptance remains separate from this image-reviewed development candidate.'),
    'au_staging': ('PASS', 'Checked approach/OTS, front braking cut, oblique leader exchange and rear-quarter launch.',
                    'All finishing frames inspected; no observed OTS lunge/crowd camera intersection/source23s framing jump. Full pacing still unobserved directly.'),
    'au_audio': ('NOT_RUN', 'Preserved music/voice, recorded source provenance and event synchronization.',
                  'Actual mix listening and phone-context perception cannot be inferred from loudness measurements.'),
    'au_reuse': ('NOT_RUN', 'Saved editable source, scene, stems, manifests and tested-use limits.',
                  'No new off-device upload or restore test authorized/performed for305 native media.'),
    'sikh_scope': ('PASS', 'Stayed with Sikh-only scene and existing proxy; no Gurkha or actor-generation branch.',
                    'Current stop/crowd, first brake, music and Pashtun remain protected;29s permits departure.'),
    'sikh_cloth': ('NOT_RUN', 'Kept principal proxy limitation explicit rather than admitting an interim cloth model.',
                    'Final connected-turban, uncover/beard/hand route is not qualified by this supporting-scene pass.'),
    'sikh_motion': ('NOT_RUN', 'Implemented complete approach/stop/greeting/rear/parting/launch/departure and reviewed chronological frames.',
                     'Final actor performance and real-time audiovisual believability remain unqualified.'),
    'sikh_geography': ('PASS', 'Inspected divided fields, access paths, ditch, trees, approach structures, moonlit scene and leader mound.',
                        'Camera geography is readable in frames; this is stylized scene work, not documentary authenticity or release acceptance.'),
}

def main():
    folder = ROOT/'results/sikh305/delivery-13'
    packet = read(folder/'packet.json')
    verification = read(folder/'verification.json')
    reopening = read(ROOT/'results/sikh305/reopen-13/comparison.json')
    assert verification['technical_checks'] == 'PASS'
    assert reopening['status'] in {'PASS','FAIL'}
    assert {r['id'] for r in packet['obligations']} == set(OBS)
    refs = [ROOT/'results/sikh305/STRATEGY.md', ROOT/'results/sikh305/INTERNAL_ITERATIONS.md',
            ROOT/'results/sikh305/CHRONOLOGICAL_REVIEW.md', ROOT/'results/sikh305/REVIEW.md',
            folder/'verification.json', ROOT/'results/sikh305/reopen-13/comparison.json',
            ROOT/'results/sikh305/audio-4/source-rights.json', ROOT/'results/sikh305/audio-4/verification.json',
            BASE/'delivery-13/manifest.json', BASE/'delivery-13/frames.json',
            BASE/'audio-04/manifest.json']
    evidence = [{'path':str(p.relative_to(ROOT)), 'sha256':sha(p)} for p in refs]
    checks = []
    for r in packet['obligations']:
        status,action,observation = OBS[r['id']]
        checks.append(dict(id=r['id'],kind=r['check_kind'],status=status,
                           action_taken=action,observation=observation,evidence=evidence))
    review = dict(packet_digest=packet['packet_digest'],checks=checks,
        hypotheses=[
            dict(prediction='Actor/camera independence can cause OTS lunge.',
                 observation='Every OTS frame inspected; normalized projection drift below0.001 in each axis.',
                 response='Camera position and aim share travel owner; braking starts after cut.',result='resolved'),
            dict(prediction='A mathematically nonshrinking dust cloud can still become an opaque wall.',
                 observation='Full stop aftermath expands, drifts and thins in chronological images.',
                 response='Density dilutes independently of growing extent; full aftermath retained.',result='resolved'),
            dict(prediction='Camera transition can jump even when position endpoints match.',
                 observation='Prior proof exposed mismatched aim; final frames across boundary are continuous.',
                 response='Unify position, aim and lens in one tested function.',result='resolved'),
            dict(prediction='Recorded sources and correct sync may still sound unconvincing in the mix.',
                 observation='No direct listening tool exists here; signal checks cannot decide this.',
                 response='Keep auditory admission blocked; present the complete mix with explicit capability limitation.',result='unresolved')],
        adjacent_regressions='Protected Pashtun source/PCM exact; current stop/crowd retained; all696 chronological frames plus encoded controls and eight native reopen controls checked. Strict repeat FAIL at one2/255 red-channel value in frame140 remains visible. Proxy hands/cloth and real-time motion/audio remain unadmitted.',
        stopping_reason='Integrated development media and all available local checks complete. Genuine perception boundary: no direct real-time playback/listening tool. No full production-ready claim; Director can judge complete action/sound treatment, not a technical method choice.')
    gate = pk.check_review(ROOT,packet,review)
    assert not gate['ready_for_review'], 'Missing perception must not be promoted to production PASS'
    (folder/'review.json').write_text(json.dumps(review,indent=2)+'\n')
    (folder/'production-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    print(json.dumps(gate,indent=2))

if __name__ == '__main__': main()
