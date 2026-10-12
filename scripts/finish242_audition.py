"""Closed local music-first timing audition; NOT a native retime or listening pass.

Preserves sources, original-rate music and accepted speech. Editable ASS/SRT,
separate sound stems, exact picture/contact time map and manifest are retained.
No providers, credentials, Blender execution or publication.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal

from finish237_audio import RATE, put, wav
from finish237_edit import inspect_sources
from movie_factory import production_knowledge as pk

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / '.runtime/art-direction/series01-finish237'
OUT = ROOT / '.runtime/art-direction/series01-finish242/audition01'
MUSIC = ROOT / 'artifacts/imports/suno-theme-01/original/Harmonic Release.wav'
DURATION = 22.5
MUSIC_START = 76.25


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(path, channels=2):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le',
                                   '-ar', str(RATE), '-ac', str(channels), '-'])
    data = np.frombuffer(raw, dtype='<f4').astype(float)
    return data.reshape(-1, channels) if channels > 1 else data


def time_map(t):
    """Native237 seconds -> provisional242 seconds. Turn/end never slowed."""
    t = np.asarray(t)
    return np.where(t < 3, t * 4 / 3,
                    np.where(t < 4.75, t + 1,
                             np.where(t < 5.75, 5.75 + (t - 4.75) * 1.5, t + 1.5)))


def inverse_time(t):
    t = np.asarray(t)
    return np.where(t < 4, t * .75,
                    np.where(t < 5.75, t - 1,
                             np.where(t < 7.25, 4.75 + (t - 5.75) / 1.5, t - 1.5)))


def envelope(t, points):
    vals = np.interp(t, [p[0] for p in points], [p[1] for p in points])
    return vals


def build_sound():
    n = round(DURATION * RATE)
    t = np.arange(n) / RATE
    voice = np.zeros((n, 2))
    original_voice = load(OLD / 'audio02/voice.wav')
    offset = round(1.6 * RATE)
    available = min(len(original_voice), n-offset)
    assert np.max(np.abs(original_voice[available:]), initial=0) == 0, 'Never truncate speech'
    voice[offset:offset + available] = original_voice[:available]
    song = load(MUSIC)
    start = round(MUSIC_START * RATE)
    excerpt = song[start:start+n].copy()
    assert len(excerpt) == n
    # Full-rate contiguous source; no stem reconstruction, pitch or tempo edits.
    music_gain = envelope(t, [(0, .62), (1.1, .62), (1.65, .22), (10.9, .22),
                              (11.5, .66), (21.9, .66), (22.5, 0)])
    speech_space = envelope(t, [(0, 0), (1.1, 0), (1.65, 1), (10.9, 1), (11.5, 0)])
    mid = signal.sosfilt(signal.butter(2, [700, 3200], btype='bandpass', fs=RATE, output='sos'), excerpt, axis=0)
    music = (excerpt - .23 * mid * speech_space[:, None]) * music_gain[:, None]
    music[:2400] *= np.linspace(0, 1, 2400)[:, None]

    src = ROOT / '.runtime/art-direction/series01-audio223/provider'
    hoof = load(src / 'finish237-hoof-1.mp3', 1)
    energy = np.convolve(hoof * hoof, np.ones(480)/480, mode='same')
    onset = max(0, int(np.argmax(energy)) - 1200)
    h = hoof[onset:onset+round(.32*RATE)].copy()
    h = signal.sosfilt(signal.butter(2, [55, 4200], btype='bandpass', fs=RATE, output='sos'), h)
    h /= max(np.max(np.abs(h)), 1e-9)
    low = signal.sosfilt(signal.butter(2, 350, fs=RATE, output='sos'), h)
    low /= max(np.max(np.abs(low)), 1e-9)
    # Designed weight with audible low-mid harmonics, not sub-bass alone.
    q = np.arange(len(h))/RATE
    body = np.sin(2*np.pi*(105*q - 45*q*q)) * np.exp(-q*25)
    body += .26*np.sin(2*np.pi*190*q)*np.exp(-q*35)
    h = .66*h + .22*low + .28*body
    h /= max(np.max(np.abs(h)), 1e-9)
    h[:144] *= np.linspace(0, 1, 144)
    h[-1440:] *= np.linspace(1, 0, 1440)
    foley = np.zeros((n, 2))
    rng = np.random.default_rng(242)
    events = json.loads((OLD/'hoof-contacts.json').read_text())['events']
    cues = []
    for e in events:
        at = float(time_map(e['time']))
        leg = e['leg']
        gain = (.36 if at < 11.5 else .43)*[1.12, .94, .80, .87][leg]*rng.uniform(.94, 1.06)
        if 1.65 < at < 11.0:
            gain *= .82
        put(foley, h, at, gain, [-.08, .08, -.1, .1][leg])
        cues.append(dict(source_time=e['time'], time=at, leg=leg, gain=gain,
                         evidence='237 cache-derived event mapped through editorial proxy; not measured force contact'))
    turn = load(src/'turn-1.mp3', 1)
    turn = signal.sosfilt(signal.butter(2, [65, 6000], btype='bandpass', fs=RATE, output='sos'), turn)
    turn /= max(np.max(np.abs(turn)), 1e-9)
    put(foley, turn, 11.85, .46)
    oldwind = load(OLD/'audio02/wind.wav')
    # Ambience is not a contact clock. Continuous bed, gently loop/crossfade tail.
    wind = np.zeros((n, 2)); wind[:len(oldwind)] = oldwind
    wind[len(oldwind):] = oldwind[round(2*RATE):round(3.5*RATE)]
    join = len(oldwind); cross = round(.5*RATE)
    a = np.linspace(0, 1, cross)[:, None]
    wind[join-cross:join] = (1-a)*oldwind[-cross:] + a*oldwind[round(1.5*RATE):round(2*RATE)]
    wind[-round(.3*RATE):] *= np.linspace(1, 0, round(.3*RATE))[:, None]
    mix = voice + music + foley + wind
    gain = min(1., .85/max(np.max(np.abs(mix)), 1e-9))
    for name, data in [('voice', voice), ('music', music), ('physical-effects', foley), ('wind', wind), ('integrated-mix', mix*gain)]:
        wav(OUT/(name+'.wav'), data)
    seconds = []
    for s in range(35, 112):
        x = song[s*RATE:(s+1)*RATE]
        seconds.append(dict(source_second=s, rms_db=float(20*np.log10(np.sqrt(np.mean(x*x))+1e-12))))
    return dict(music_source_start=MUSIC_START, music_source_end=MUSIC_START+DURATION,
                music_arrival_anchor=dict(source=88, edit=11.75, provenance='Director approximate listening landmark'),
                voice_offset=1.6, speech_start=1.75, speech_end=11.0262916667,
                original_voice_samples_identical=bool(np.array_equal(voice[offset:offset+available], original_voice[:available])),
                trailing_silence_trimmed_seconds=(len(original_voice)-available)/RATE,
                voice_speed_changed=False, music_speed_changed=False, cues=cues, music_gain_points='0:.62,1.1:.62,1.65:.22,10.9:.22,11.5:.66,21.9:.66,22.5:0',
                master_gain=gain, peak=float(np.max(np.abs(mix*gain))),
                music_rms_per_second=seconds, listening='NOT_RUN; measurements do not establish emotion, intelligibility or fit')


def manuscript():
    # Editable vector paper silhouette and typeset original notebook quotation.
    # Cropped upper-page fragment dissolves into terrain: no box or archival scan.
    header = r'''[Script Info]
ScriptType: v4.00+
PlayResX: 432
PlayResY: 768
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ink,Apple Chancery,26,&H002E332F,&H002E332F,&H002E332F,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,0,0,0,1
Style: Credit,Baskerville,19,&H003D413A,&H003D413A,&H003D413A,&H00000000,0,-1,0,0,100,100,0,0,1,0,0,8,0,0,0,1
Style: Study,Arial,10,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events = []
    def line(layer, text, style='Ink', begin='0:00:06.65', end='0:00:09.70'):
        events.append(f'Dialogue: {layer},{begin},{end},{style},,0,0,0,,{text}')
    # Broad feathered substrate, no rectangular outline; upper gutter continues offscreen.
    line(0, r'{\an7\pos(0,0)\fad(450,400)\c&HBDD5E4&\alpha&H18&\blur12\p1}m -40 -35 l 478 -29 470 129 b 391 136 334 161 283 147 b 232 132 175 162 116 143 b 61 151 4 128 -40 140{\p0}')
    line(1, r'{\an7\pos(0,0)\fad(500,450)\c&HD7E5EE&\alpha&H08&\blur5\p1}m -40 -35 l 478 -29 470 106 b 391 127 334 137 283 133 b 232 124 175 139 116 131 b 61 137 4 114 -40 121{\p0}')
    # Only approved fictional framing/quotation used, not copied unrelated diary prose.
    line(2, r'{\pos(182,-10)\fad(550,400)\frz-2\fs22\alpha&H92&}Their credentials are … impeccable.')
    line(3, r'{\pos(211,18)\fad(400,350)\frz1\fs23}The Pathans:', begin='0:00:06.90')
    line(3, r'{\pos(215,48)\fad(400,350)\frz1\fs29}“a hardy and', begin='0:00:07.12')
    line(3, r'{\pos(221,80)\fad(400,350)\frz1\fs29}martial people”', begin='0:00:07.12')
    line(3, r'{\pos(252,120)\fad(350,350)\frz1}— Sir Winston Churchill', 'Credit', begin='0:00:07.35')
    line(2, r'{\an7\pos(0,0)\fad(550,400)\alpha&H88&\c&H657266&\p1}m 89 112 b 132 114 202 110 308 111 l 306 112 b 201 111 133 116 89 113{\p0}')
    line(5, r'{\pos(216,753)}EDIT / SOUND STUDY · provisional pre-turn timing', 'Study', '0:00:00.00', '0:00:22.50')
    return header+'\n'.join(events)+'\n'


def main():
    task = json.loads((ROOT/'docs/knowledge/pilot/tasks/finish242-audio.json').read_text())
    packet = pk.task_packet(ROOT, task)
    if not packet['dispatch_ready']:
        raise ValueError(packet['blockers'])
    if OUT.exists():
        raise ValueError('Preserve prior audition; no overwrite')
    assert sha(MUSIC) == '42234a4a8e44c70daf384d233a29b4e52bfb707f5ff22aa1b18efd5d97b1080b'
    sources = inspect_sources()
    OUT.mkdir(parents=True)
    (OUT/'packet.json').write_text(json.dumps(packet, indent=2)+'\n')
    (OUT/'packet.md').write_text(pk.packet_markdown(packet))
    sound = build_sound()
    (OUT/'sound.json').write_text(json.dumps(sound, indent=2)+'\n')
    (OUT/'manuscript.ass').write_text(manuscript())
    # Identical source-frame ordering with declared pre-turn timing repeats.
    # No generated/interpolated limb geometry; native full-speed extension deferred.
    mapping = np.floor(inverse_time(np.arange(540)/24)*24+1e-6).astype(int)
    mapping = np.clip(mapping, 0, 503)
    lines = ['ffconcat version 1.0']
    for idx in mapping:
        lines += [f"file '{sources[idx]['path']}'", 'option framerate 24', 'duration 0.0416666666667']
    lines += [f"file '{sources[-1]['path']}'", 'option framerate 24']
    (OUT/'picture.ffconcat').write_text('\n'.join(lines)+'\n')
    (OUT/'narration.srt').write_text('''1
00:00:01,750 --> 00:00:03,610
We call them martial races.

2
00:00:03,990 --> 00:00:05,700
Their credentials are …

3
00:00:06,070 --> 00:00:06,860
impeccable.

4
00:00:07,130 --> 00:00:08,000
The Pathans:

5
00:00:08,160 --> 00:00:09,710
“a hardy and martial people.”

6
00:00:10,020 --> 00:00:11,030
Sir Winston Churchill.
''')
    video = OUT/'pashtun-music-first-audition.mp4'
    subprocess.run(['ffmpeg','-v','warning','-safe','0','-f','concat','-i',str(OUT/'picture.ffconcat'),
                    '-i',str(OUT/'integrated-mix.wav'),'-vf',f'ass={OUT}/manuscript.ass',
                    '-r','24','-frames:v','540','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-t',str(DURATION),str(video)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    qc = subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    (OUT/'loudness.txt').write_text(qc.stderr)
    assert sha(MUSIC) == task['inputs'][str(MUSIC.relative_to(ROOT))]
    result = dict(status='DIAGNOSTIC_AUDITION_NOT_NATIVE_OR_LISTENING_PASS', duration=22.5, fps=24, frame_count=540,
                  source_frame_indices=mapping.tolist(), source_frames=sources, audio=sound,
                  proxy_only='Repeated frames in0–4s and5.75–7.25s; no motion qualification. Turn/ending use every original frame at24fps.',
                  new_provider_calls=0, final_rights='OPEN; private local audition only',
                  outputs={p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(video=str(video), status=result['status'], voice_samples_identical=sound['original_voice_samples_identical'])))


if __name__ == '__main__':
    main()
