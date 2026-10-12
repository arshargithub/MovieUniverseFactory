"""Closed21s picture/sound assembly. No music, generation or publication.

Requires complete, source-bound rendered sequences. All source frames and audio
remain intact. Output is an audition until the separate review gate is satisfied.
"""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-finish237'
PAGE=r'''[Script Info]
ScriptType: v4.00+
PlayResX: 432
PlayResY: 768
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Page,Baskerville,20,&H00332D26,&H00332D26,&H004A4134,&H60000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Quote,Baskerville,28,&H003B3027,&H003B3027,&H003B3027,&H00000000,0,-1,0,0,100,100,0,0,1,0,0,8,0,0,0,1
Style: Author,Baskerville,18,&H003B3027,&H003B3027,&H003B3027,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:05.00,0:00:08.18,Page,,0,0,0,,{\pos(0,0)\fad(400,350)\c&H9AB5C9&\alpha&H28&\p1}m 30 20 l 396 25 399 153 377 151 334 154 283 150 210 153 154 151 85 154 33 150 31 113 34 73 30 20{\p0}
Dialogue: 1,0:00:05.00,0:00:08.18,Page,,0,0,0,,{\pos(0,0)\fad(400,350)\c&H718AA1&\alpha&H60&\p1}m 43 31 l 386 35 385 37 43 33 m 44 148 l 386 148 386 149 44 149{\p0}
Dialogue: 2,0:00:05.05,0:00:08.18,Author,,0,0,0,,{\pos(216,38)\fad(350,350)\fs14\fsp2}THE PATHANS
Dialogue: 2,0:00:05.15,0:00:08.18,Quote,,0,0,0,,{\pos(216,62)\fad(350,350)}“a hardy and\Nmartial people”
Dialogue: 2,0:00:05.30,0:00:08.18,Author,,0,0,0,,{\pos(216,125)\fad(350,350)}— Sir Winston Churchill
'''
SRT='''1
00:00:00,150 --> 00:00:02,010
We call them martial races.

2
00:00:02,390 --> 00:00:04,100
Their credentials are …

3
00:00:04,470 --> 00:00:05,260
impeccable.

4
00:00:05,530 --> 00:00:06,400
The Pathans:

5
00:00:06,560 --> 00:00:08,110
“a hardy and martial people.”

6
00:00:08,420 --> 00:00:09,430
Sir Winston Churchill.
'''
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def inspect_sources():
    rows=[]
    for folder,start,count in [('opening03-full',0,198),('route04-full',198,306)]:
        src=BASE/folder;r=json.loads((src/'result.json').read_text())
        if not r['complete'] or [x['index'] for x in r['frames']]!=list(range(start,start+count)):raise ValueError('Incomplete chronology '+folder)
        native=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'/('finish237-'+folder.removesuffix('-full'))/'scene.blend'
        if digest(native)!=r['source_sha256']:raise ValueError('Native changed')
        for row in r['frames']:
            path=src/f"frame-{row['index']:04d}.png"
            if digest(path)!=row['sha256']:raise ValueError('Frame changed')
            rows.append(dict(index=row['index'],path=str(path),sha256=row['sha256']))
    return rows
def main():
    if sys.argv[1:]==['proof']:
        ass=BASE/'quote-proof02.ass';image=BASE/'book-on-native02.png'
        if ass.exists() or image.exists():raise ValueError('Preserve prior graphic proof')
        ass.write_text(PAGE)
        subprocess.run(['ffmpeg','-v','error','-i',str(BASE/'opening03-full/frame-0136.png'),'-vf',f'setpts=PTS+5.666667/TB,ass={ass}','-frames:v','1',str(image)],check=True)
        print(str(image));return
    if sys.argv[1:]:raise ValueError('No free-form edit commands')
    rows=inspect_sources();out=BASE/'edit01'
    if out.exists():raise ValueError('Preserve prior edit')
    mix=BASE/'audio02/music-free-mix.wav'
    if not mix.is_file():raise ValueError('No contact-derived mix')
    out.mkdir();(out/'frames').mkdir()
    for row in rows:os.link(row['path'],out/'frames'/f"frame-{row['index']:04d}.png")
    (out/'quote-overlay.ass').write_text(PAGE);(out/'narration.srt').write_text(SRT)
    for captions in (False,True):
        video=out/('pashtun-21s-captioned.mp4' if captions else 'pashtun-21s-music-free.mp4')
        vf='ass='+str(out/'quote-overlay.ass')
        if captions:vf+=",subtitles="+str(out/'narration.srt')+":force_style='FontName=Arial,FontSize=12,Outline=1,MarginV=34'"
        subprocess.run(['ffmpeg','-v','warning','-framerate','24','-i',str(out/'frames/frame-%04d.png'),'-i',str(mix),'-vf',vf,
            '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000',
            '-movflags','+faststart','-t','21','-metadata','comment=Music-free review preview; designed quotation graphic, not archival facsimile',str(video)],check=True)
        subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    result=dict(duration_seconds=21,frames=rows,mix_sha256=digest(mix),quote_source='Churchill, The Story of the Malakand Field Force, Chapter I; verified edition printed page25',
        graphic='Designed book-page quotation; not a scan/facsimile. Clears before geography shot.',
        captions='Editable SRT plus burned-caption derivative; approximate phrase timing until listening verification.',
        music='NONE; Director selecting separately',status='ASSEMBLED_PENDING_INTERNAL_VISUAL_AND_AUDITORY_REVIEW',
        outputs={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['duration_seconds','status','music']}))
if __name__=='__main__':main()
