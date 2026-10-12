"""Record curated FINISH237 review; auditory gaps must keep the gate closed.

This does not perform perception. Observations below are the agent's recorded
image review, with separately bounded numerical evidence. No automatic PASS
is derived from rendering, provider output, or a selected music source.
"""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-finish237'
UNIT='docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md'
LOG='.runtime/art-direction/series01-finish237/progressive-review.md'
ENC='.runtime/art-direction/series01-finish237/encoded-qc01/result.json'
REP='.runtime/art-direction/series01-finish237/reopen-parity.json'
AUDIT='.runtime/art-direction/series01-finish237/route-audit05.json'
AUDIO='.runtime/art-direction/series01-finish237/audio02/manifest.json'
ERROR='.runtime/art-direction/series01-finish237/audio-qc-result-capacity-recheck.json'
NARR='docs/planning/SERIES_01_PASHTUN_NARRATIVE_AUDIO_PROPOSAL.md'

# Status, action, observation, actual evidence. Known grip219 is a bounded
# preview exception, not a repaired anatomical fist or new Director acceptance.
OBS={
 'authority':('PASS','Apply237 preview authority and239 source-only intake.',
   'No music generation, purchase, install, cloud render or publication. New calls stayed inside the existing initial cap; accepted masters unchanged.',[UNIT,NARR]),
 'strategy':('PASS','Apply three independent clocks and interface review before final assembly.',
   'Preserved original-speed route, separated attention from gait and world travel; retained failed dust/cut candidates and corrected causes.',[UNIT,LOG]),
 'visual_gate':('NOT_RUN','Inspect all504 chronological raw frames and actual encoded cut/text/end samples, with failure-seeking controls.',
   'Image review found and repaired one fractional camera-cut frame. This is not an invented real-time audiovisual listening/playback pass; integrated perceptual pacing/sound remains unverified.',[LOG,ENC,ERROR]),
 'anticipation':('PASS','Test hook loss, gait slowdown, boundary pops, dust occlusion and quote obstruction.',
   'Immediate gallop preserved; route02 dust and04 frame245 failed and were repaired before assembly. Quote clears before OTS, mounted danger and escape are visible together.',[LOG,UNIT]),
 'stopping':('PASS','Separate technical completion from genuine perceptual blocker; do not spend blindly to obtain approval.',
   'Stop further listening retries after two explicit capacity503 responses. Share only a diagnostic audition, retain NOT_RUN and request creative voice assessment; no full-unit or release qualification.',[ERROR,UNIT]),
 'versioning':('PASS','Bind originals, derivative natives, frame reuse, stems and encoded outputs; reopen native samples.',
   'Immutable sources preserved;14 reopen samples and camera-only neighboring-frame reuse checked separately. Local Git is not native/audio backup.',[REP,ENC,AUDIT]),
 'economics':('PASS','Record jobs/activity and authorized provider ledger separately.',
   'Three new voice/effects requests; conservative AUDIO-220 commitment1.54USD of3USD. Exact per-call cost and engineering tokens remain unknown; no5USD extension.',[UNIT,'.runtime/art-direction/series01-audio223/provider/budget.jsonl']),
 'identity':('PASS','Preserve accepted152/169 identity and current218 derivative appearance.',
   'No anatomy/material redesign. Chronological close frames retain face, natural hair, double wrap and selected palette; no requalification of hidden anatomy.',[LOG,REP]),
 'anatomy':('PASS','Inspect visible neck, shoulders and riding pose for new retiming regressions.',
   'No new gross neckline/shoulder deformation observed at preview framing; source-body evaluated control and preserved-route channels checked. Scope is regression, not new universal anatomical approval.',[LOG,AUDIT]),
 'motion':('NOT_RUN','Check mapped clocks, complete chronological frames and preserved-route channels.',
   'No global slowdown or duplicate-frame extension. Full real-time perceptual pacing review is not claimed from frame sheets; preserve this limitation alongside successful numerical controls.',[LOG,AUDIT]),
 'contact':('PASS','Carry the Director219-authorized grip compromise and check support regressions at actual framing.',
   'The distal knuckle/pivot flaw remains disclosed and is NOT an anatomy PASS. No new gross rein/seat support loss observed in chronological images; reopen for distracting final coverage or new use.',[LOG,'docs/planning/SERIES_01_REIN_CONTACT_214.md']),
 'garment':('PASS','Inspect two wrap routes and shoulder support across changed opening and reused route.',
   'Two chest courses above harness remain readable; headfall follows the extended attention motion. No new gross detached shoulder strip or disappearing course observed in scoped image review.',[LOG,AUDIT]),
 'secondary':('PASS','Inspect hair, mane, tail, sword and dust across prefix joins and shot boundaries.',
   'World-space dust offset failure corrected; progression remains active to503. This is authored preview motion, not general wind/cloth physics qualification.',[LOG]),
 'look':('PASS','Preserve the selected sun-bleached painterly palette and inspect quote placement.',
   'No appearance redesign. Terrain/painted background and costume remain source treatment; visible paper stays above face and clears before geography.',[LOG,ENC]),
 'geography':('PASS','Check escape glance then rear-view-right OTS and intended frontal cut.',
   'Both mounted checkpoint and detour are visible in OTS;05 removes the single cliff-facing interpolated frame before the frontal turn.',[LOG,ENC]),
 'sword':('PASS','Inspect right-hip rearward scabbard support after world-travel extension.',
   'Suspension travels with rider in opening and OTS; no prop redesign or new collision-generalization claim.',[LOG,AUDIT]),
 'render_profile':('PASS','Use local CPU6 threads, one worker, persistent dataOFF and fixed432x768 preview profile.',
   'Both504-frame21s24fps H264/AAC outputs decode;14 reopened samples checked. No Metal default, cloud spending or final-resolution qualification.',[REP,ENC]),
 'cache_safety':('PASS','Verify source/cache hashes, vertex counts and modifier order in native reopen handlers.',
   'Reopen completes for both immutable natives; failed original frame and startup/audit attempts retained. No arbitrary runtime-generated Blender code.',[REP,'scripts/finish237_review.py']),
 'narrative':('NOT_RUN','Assemble approved nineteen-word private-officer script with editable phrase timing.',
   'Speech ends9.4263s before10.25s turn without speeding spoken samples. Corrected Kirk-direction take and Pathan pronunciation have no perceptual verification or Director acceptance yet.',[AUDIO,ERROR,NARR]),
 'quotation':('PASS','Use the verified five-word Churchill excerpt with full attribution, separate from fictional framing.',
   'Designed aged-page graphic, not archival scan; clear of face/geography in actual encoded frames. Source work/edition/page preserved in narrative records.',[NARR,ENC]),
 'sound':('NOT_RUN','Build editable voice, wind and native-phase hoof/turn effects, leaving music empty.',
   'Technical decoding/levels and contact-phase image spot checks complete; weight, naturalness, pronunciation and audible sync remain unheard. Gemini taste review is not used; two technical listening requests503.',[AUDIO,ERROR,LOG]),
 'captions':('NOT_RUN','Export editable English SRT and optional burned-caption derivative.',
   'Actual encoded text is legible and clear of face. Phrase timing is approximate until heard; phone/platform UI safe zones are untested, not delivery-qualified.',[ENC,AUDIO]),
 'rights':('NOT_RUN','Preserve source provenance and preview authority; keep final release clearance separate.',
   'Suno originals/stems and exact Director selection recorded, but exact generation/plan eligibility and final audiovisual rights are not fully cleared. No publication.',[NARR,'artifacts/imports/suno-theme-01/source-details/director-selection.json']),
 'narration_a':('PASS','Retain revised222/223 A, superseding215 ending.',
   'No closing trust line or premature moral-conflict narration; full Sir Winston Churchill attribution and book graphic retained. Performance approval remains separate.',[NARR,'scripts/finish237_edit.py']),
}

def main():
    for kind in ('motion','audio'):
        packet=json.loads((OUT/f'{kind}-packet-final.json').read_text())
        checks=[]
        for r in packet['obligations']:
            status,action,observation,paths=OBS[r['id']]
            checks.append(dict(id=r['id'],kind=r['check_kind'],status=status,
                action_taken=action,observation=observation,
                evidence=[dict(path=p,sha256=pk.file_hash(ROOT/p)) for p in paths]))
        review=dict(packet_digest=packet['packet_digest'],scope='FINISH237 diagnostic preview; no completed integrated perceptual or release PASS',checks=checks,
            hypotheses=[dict(prediction='Continuous retiming can interpolate across a hard camera cut.',observation='Original04 global245 faced the cliff between OTS and frontal shots.',response='Camera-only05 discrete boundary repair, neighbor parity and encoded244/245/246 review.',result='resolved'),
                dict(prediction='Completed media can be misrepresented as successful listening evidence.',observation='Decode succeeds but technical listening503 has no verdict.',response='Keep sound, narrative performance, caption timing and integrated perceptual checks NOT_RUN; no blind retries or ready claim.',result='resolved')],
            adjacent_regressions='Image review covers neck/shoulders, arms, shawl routes, hair/mane/tail, reins and disclosed219 grip compromise, sword, dust, geography, text occlusion and source protections. Frame review is not an auditory or real-time pacing pass.',
            stopping_reason='Technical preview assembled and checked; exact integrated listening/perceptual blocker disclosed. Director-selected music is ingested but not mixed. No release gate advances.')
        dest=OUT/f'{kind}-review-final.json';gate=OUT/f'{kind}-gate-final.json'
        if dest.exists() or gate.exists():raise ValueError('Preserve existing review')
        dest.write_text(json.dumps(review,indent=2)+'\n')
        result=pk.check_review(ROOT,packet,review);gate.write_text(json.dumps(result,indent=2)+'\n')
        print(kind,json.dumps(result))
        assert not result['ready_for_review'], 'Auditory/perceptual gaps must not pass'
        assert all(x.endswith(':FAIL_OR_NOT_RUN') for x in result['failures']), 'Unexpected stale/missing evidence'
    raise SystemExit(2)

if __name__=='__main__':main()
