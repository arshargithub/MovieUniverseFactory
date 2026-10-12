"""Record actual242 evidence, retaining the listening/native/rights blockers."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-finish242'
LOG='.runtime/art-direction/series01-finish242/review.md'
UNIT='docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md'
OBS={
 'authority':('PASS','Apply242 local audition scope.','No provider, credentials, native edits, upload or publication.',[UNIT,LOG]),
 'strategy':('PASS','Test actual original music with existing voice before native render.','One contiguous source cue; proxy status explicit; visual failures corrected internally.',[UNIT,LOG]),
 'visual_gate':('NOT_RUN','Inspect encoded chronology and individual quote/OTS frames.','Text visibility reviewed; real-time audiovisual judgment unavailable, not replaced by frame inspection.',[LOG]),
 'anticipation':('NOT_RUN','Test voice masking, quote occlusion, hook loss and altered motion.','Paper placement failure repaired; voice/music emotional fit and proxy pacing remain unheard/unresolved.',[LOG]),
 'stopping':('PASS','Keep scope at planned integrated creative audition.','No final-ready assertion; native extension held until actual combined taste judgment, not routine method approval.',[UNIT,LOG]),
 'versioning':('PASS','Preserve original song/voice/natives and explicit frame/time maps.','Source hashes verified; speech samples unchanged; rejected graphic and silent-tail build evidence retained.',[LOG,'.runtime/art-direction/series01-finish242/audition01/manifest.json']),
 'economics':('PASS','Reuse local media; start prospective lifecycle.','No new provider calls; engineering tokens and earlier uncaptured effort remain unknown.',[LOG]),
 'narrative':('NOT_RUN','Keep approved script/pronunciation and delay speech1.6s.','Speech fits before turn; emotional coherence against actual theme has no listening PASS.',[LOG]),
 'quotation':('PASS','Use original notebook fragment, not archival photo.','Exact quoted words/full author visible in encoded8.5s; fades before9.75s geography; historical source retained in narrative doc.',[LOG,'.runtime/art-direction/series01-finish242/edit03/qc-8.5.png','.runtime/art-direction/series01-finish242/edit03/qc-9.75.png']),
 'sound':('NOT_RUN','Mix original stereo, existing voice and weightier physical sources.','Decode/levels and source-onset mapping checked; no invented listening, phrase-fit or auditory sync acceptance.',[LOG,'.runtime/art-direction/series01-finish242/edit03/loudness.txt']),
 'captions':('NOT_RUN','Keep shifted editable SRT separate from manuscript.','Phrase timing approximate; platform safe zones and phone playback untested.',[LOG,'.runtime/art-direction/series01-finish242/audition01/narration.srt']),
 'rights':('NOT_RUN','Keep user sources/provenance and private-audition boundaries.','Final generation-plan/recording/font/visual clearance open; no archival photo reuse or publication.',[LOG]),
 'narration_a':('PASS','Retain approved revised A.','No added closing line or premature moral conflict; full source name retained.',[LOG,'scripts/finish242_audition.py']),
 'music_reference':('PASS','Use Director-selected source and timestamp preference.','Source76.25–98.75s,88s anchor at turn; no Gemini opinion or replacement generated music. Fit remains hypothesis.',[LOG]),
}


def main():
    packet=json.loads((OUT/'edit03/packet.json').read_text())
    checks=[]
    for r in packet['obligations']:
        status,action,observation,paths=OBS[r['id']]
        checks.append(dict(id=r['id'],kind=r['check_kind'],status=status,action_taken=action,observation=observation,
            evidence=[dict(path=p,sha256=pk.file_hash(ROOT/p)) for p in paths]))
    review=dict(packet_digest=packet['packet_digest'],checks=checks,
        hypotheses=[dict(prediction='Manuscript could hide face or become unreadable over trees.',observation='01 had misplaced paper;02 actual image readable and clear before OTS.',response='Corrected vector anchoring; inspected exported frames.',result='resolved'),
            dict(prediction='Restrained officer may feel disconnected despite the selected song.',observation='No direct auditory assessment available.',response='Keep NOT_RUN; provide only the authorized diagnostic audition for the planned listening decision.',result='unresolved')],
        adjacent_regressions='No native changes; turn/ending frame map exact. Pre-turn repeats disclosed, not native qualification.219 grip compromise remains. Quote/caption/cut/rights limits recorded.',
        stopping_reason='One integrated diagnostic proof completed; planned Director listening judgment remains. Do not claim production readiness or spend on native extension before cue/performance route judged.')
    for name,obj in [('review-final03.json',review),('gate-final03.json',pk.check_review(ROOT,packet,review)),('retrieval-regression03.json',pk.evaluate(ROOT))]:
        dest=OUT/name
        if dest.exists():raise ValueError('Preserve evidence')
        dest.write_text(json.dumps(obj,indent=2)+'\n')
    gate=pk.check_review(ROOT,packet,review)
    print(json.dumps(gate))
    assert not gate['ready_for_review']
    assert all(s.endswith(':FAIL_OR_NOT_RUN') or s=='UNRESOLVED_HYPOTHESIS' for s in gate['failures']),gate
    raise SystemExit(2)


if __name__=='__main__':main()
