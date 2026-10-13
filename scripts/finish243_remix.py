"""Closed local correction of Director-rejected242 music suppression.

No hearing claim, provider call, tempo change or picture render. Original-rate
speech gets a silent insertion, music shallow phrase-shaped volume automation.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from finish242_audition import ROOT, MUSIC, load, sha
from finish237_audio import RATE, wav
from movie_factory import production_knowledge as pk

OUT=ROOT/'.runtime/art-direction/series01-finish243'
OLD=ROOT/'.runtime/art-direction/series01-finish242'
VIDEO=OLD/'edit03/pashtun-music-first-audition.mp4'
DURATION=22.5
OFFSET=.95
INSERT=1.12
SPLIT=5.395
PHRASES=[(1.10,2.96),(3.34,6.21),(7.60,11.4962916667)]


def music_envelope(t):
    # Smooth raised-cosine transitions; no block-long suppression or broad EQ.
    depth=np.zeros_like(t)
    for start,end in PHRASES:
        attack=np.clip((t-(start-.18))/.18,0,1)
        release=np.clip((end+.18-t)/.18,0,1)
        local=np.minimum((1-np.cos(np.pi*attack))/2,(1-np.cos(np.pi*release))/2)
        depth=np.maximum(depth,local)
    g=.66-.20*depth
    g*=np.clip(t/.05,0,1)
    g*=np.clip((DURATION-t)/.6,0,1)
    return g


def narration(source):
    cut=round(SPLIT*RATE);added=round(INSERT*RATE);shift=round(OFFSET*RATE)
    # Assert the actual insertion falls in silence; fail closed on a changed take.
    boundary_peak=float(np.max(abs(source[cut-240:cut+240])))
    assert boundary_peak<.001,boundary_peak
    output=np.zeros((round(DURATION*RATE),2))
    output[shift:shift+cut]=source[:cut]
    remaining=len(output)-(shift+cut+added)
    output[shift+cut+added:]=source[cut:cut+remaining]
    assert np.max(abs(source[cut+remaining:]),initial=0)==0,'Would truncate speech'
    assert np.array_equal(output[shift:shift+cut],source[:cut])
    assert np.array_equal(output[shift+cut+added:],source[cut:cut+remaining])
    return output,boundary_peak


def video_payload(path):
    # Hash encoded video packets without audio/container metadata.
    return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),
        '-map','0:v:0','-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-'])).hexdigest()


def measure(path):
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af',
        'loudnorm=I=-16.7:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1])


def main():
    task=json.loads((ROOT/'docs/knowledge/pilot/tasks/finish243-audio.json').read_text())
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if OUT.exists():raise ValueError('Preserve existing revision')
    OUT.mkdir()
    (OUT/'packet.json').write_text(json.dumps(packet,indent=2)+'\n')
    n=round(DURATION*RATE);t=np.arange(n)/RATE
    voice,peak=narration(load(ROOT/'.runtime/art-direction/series01-finish237/audio02/voice.wav'))
    excerpt=load(MUSIC)[round(76.25*RATE):round(98.75*RATE)]
    gain=music_envelope(t);music=excerpt*gain[:,None]
    physical=load(OLD/'audition01/physical-effects.wav');wind=load(OLD/'audition01/wind.wav')
    raw=voice+music+physical+wind
    # First use conservative headroom; then one constant trim, never compression.
    safety=min(1.,.82/max(np.max(abs(raw)),1e-9))
    for name,data in [('voice',voice),('music',music),('mix-premaster',raw*safety)]:wav(OUT/(name+'.wav'),data)
    before=measure(OUT/'mix-premaster.wav')
    trim=min(-16.7-float(before['input_i']),-1.8-float(before['input_tp']))
    final=raw*safety*(10**(trim/20));wav(OUT/'mix.wav',final)
    movie=OUT/'pashtun-music-breathing-room.mp4'
    subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-i',str(OUT/'mix.wav'),
        '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000',
        '-t','22.5','-movflags','+faststart',str(movie)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)
    assert video_payload(movie)==video_payload(VIDEO)
    # Exact phrase timestamps remain an approximation until listening alignment.
    (OUT/'narration.srt').write_text('''1
00:00:01,100 --> 00:00:02,960
We call them martial races.

2
00:00:03,340 --> 00:00:05,050
Their credentials are …

3
00:00:05,420 --> 00:00:06,210
impeccable.

4
00:00:07,600 --> 00:00:08,470
The Pathans:

5
00:00:08,630 --> 00:00:10,180
“a hardy and martial people.”

6
00:00:10,490 --> 00:00:11,500
Sir Winston Churchill.
''')
    result=dict(status='DIAGNOSTIC_LOCAL_REMIX_NOT_LISTENING_PASS',picture_payload_sha256=video_payload(movie),
        picture_byte_identical=True,duration_seconds=DURATION,voice_source_offset_seconds=OFFSET,
        inserted_silence_seconds=INSERT,approximate_post_impeccable_pause=1.39,
        first_speech=1.1,speech_end=11.4962916667,turn=11.75,
        speech_samples_identical_before_master_gain=True,splice_10ms_peak=peak,
        full_music_gain=.66,under_speech_music_gain=.46,duck_db=float(20*np.log10(.46/.66)),
        music_spectral_reduction=False,music_source_interval=[76.25,98.75],music_rate_unchanged=True,
        safety_gain=safety,constant_master_trim_db=trim,loudness=measure(movie),
        cues=[dict(time=round(float(x),3),music_gain=float(music_envelope(np.array([x]))[0])) for x in np.arange(0,22.5,.1)],
        hearing='NOT_RUN; no direct agent auditory assessment; Director243 feedback is source evidence, not a new pass',
        new_provider_calls=0,remaining='Original picture timing proxy; rights/caption delivery/final-native and music/voice acceptance open',
        sources={str(p.relative_to(ROOT)):sha(p) for p in [VIDEO,MUSIC,ROOT/'.runtime/art-direction/series01-finish237/audio02/voice.wav',OLD/'audition01/physical-effects.wav',OLD/'audition01/wind.wav']},
        outputs={p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['picture_byte_identical','approximate_post_impeccable_pause','speech_end','duck_db','loudness']}))


def record_review():
    """Explicit technical observations; never turn an unheard remix into PASS."""
    packet=json.loads((OUT/'packet.json').read_text())
    observations={
        'authority':('PASS','Apply Director243 correction without new authority.','Local audio only; no calls, installs, uploads or native edits.'),
        'strategy':('PASS','Repair the evidenced mix mechanism and use a controlled same-picture comparison.','Deep whole-block duck replaced by shallow phrase automation; keep theme, performance, music offset and footage.'),
        'visual_gate':('NOT_RUN','Verify encoded picture preservation and distinguish it from perception.','Video H264 payload hash is identical; integrated auditory/real-time emotional review not available.'),
        'anticipation':('NOT_RUN','Test lost music continuity, splice damage, turn overlap and pumping risk.','Sample/splice/automation/turn checks pass; audible pumping/intelligibility/emotional fit remain unverified.'),
        'stopping':('PASS','Stop at the requested integrated listening comparison, not a completed-unit claim.','One remux delivered; no native extension or new generation before the Director hears the changed balance.'),
        'versioning':('PASS','Preserve242 rejection and bind243 sources.','Song, prior take and picture unchanged; source hashes and separate revised voice/music/mix retained.'),
        'economics':('PASS','Reuse exact footage and locally remix.','No provider calls or rendering; lifecycle prospective; engineering tokens unknown.'),
        'narrative':('NOT_RUN','Preserve accepted words/pronunciation and insert silence only.','Speech samples retained; nominal1.39s pause; speech end11.496 before11.75 turn. Auditory performance fit unverified.'),
        'quotation':('PASS','Keep prior graphics and verified historical wording.','Exact encoded picture stream preserved; quote unchanged and clears before9.75 geography. Onscreen text precedes the slightly later spoken quotation; no claim of karaoke synchronization.'),
        'sound':('NOT_RUN','Use shallow3.14dB phrase dips and full-level pause without EQ hollowing.','Signal/decode/headroom pass; no direct listening or audible-quality claim.'),
        'captions':('NOT_RUN','Shift editable SRT to revised phrase map.','Caption timing is approximate; no fresh forced alignment or device safe-zone qualification.'),
        'rights':('NOT_RUN','Keep private diagnostic scope.','No publication or new media sources; prior final rights/plan/font clearance remains open.'),
        'narration_a':('PASS','Retain approved script and original spoken samples.','No new lines, altered attribution, moral-conflict ending or regenerated pronunciation.'),
        'music_reference':('PASS','Apply actual Director243 listening feedback rather than model music judgment.','Selected Harmonic Release excerpt unchanged; prior suppression is rejected, not an accepted reference mix.'),
    }
    paths=['.runtime/art-direction/series01-finish243/result.json','docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md','docs/planning/SERIES_01_PASHTUN_NARRATIVE_AUDIO_PROPOSAL.md']
    checks=[]
    for obligation in packet['obligations']:
        status,action,observation=observations[obligation['id']]
        checks.append(dict(id=obligation['id'],kind=obligation['check_kind'],status=status,action_taken=action,observation=observation,evidence=[dict(path=p,sha256=pk.file_hash(ROOT/p)) for p in paths]))
    review=dict(packet_digest=packet['packet_digest'],checks=checks,
        hypotheses=[dict(prediction='Added silence may clip a phoneme or push voice into turn.',observation='Measured quiet splice and preserved samples; speech ends0.254s before turn.',response='Kept rate and picture, moved entry within agreed1–2s range.',result='resolved'),
                    dict(prediction='Shallower phrase dips should preserve musical co-lead rather than sound switched off.',observation='Automation measured; actual audible success unverified.',response='Present diagnostic with limitation; do not infer hearing from meters.',result='unresolved')],
        adjacent_regressions='Encoded picture byte-identical, including prior timing-proxy and219 hand compromise. Source/voice rate and contact effects preserved. No visual redesign.',
        stopping_reason='Requested remix and technical controls complete; return integrated audition for actual listening, not final acceptance or a routine method decision.')
    gate=pk.check_review(ROOT,packet,review)
    for name,data in [('review.json',review),('gate.json',gate),('retrieval-regression.json',pk.evaluate(ROOT))]:
        path=OUT/name
        if path.exists():raise ValueError('Preserve review history')
        path.write_text(json.dumps(data,indent=2)+'\n')
    assert not gate['ready_for_review']
    assert all(x.endswith(':FAIL_OR_NOT_RUN') or x=='UNRESOLVED_HYPOTHESIS' for x in gate['failures']),gate
    print(json.dumps(gate))
    return 2


if __name__=='__main__':main()
