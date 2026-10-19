"""Local encode and protected join, exact decoded control evidence."""
import sys,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
from sikh315_run import BASE,ROOT,sha,source_for
from sikh305_delivery import sheets
FF='/opt/homebrew/bin/ffmpeg';PASHTUN=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
def run(*args):subprocess.run([FF,'-v','error',*args],check=True)
def main():
    op,v=sys.argv[1],int(sys.argv[2]);assert op in ('sheets','proof','edit','controls','reopencheck') and 1<=v<=16
    native=source_for('movie',v).parent;out=BASE/f'delivery-{v:02d}';audio=BASE/f'audio-{v:02d}'
    if op=='sheets':sheets(native,native/'sheets',columns=4,rows=3,width=260);return
    if op=='proof':
        p=BASE/f'proof-{v:02d}';sheets(p/'frames',p/'chronology',columns=6,rows=4,width=240)
        for label,start,count in (('rear',275,82),('launch',414,93)):
            run('-framerate','24','-start_number',str(start),'-i',str(p/'frames/frame-%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(p/(label+'.mp4')))
        return
    if op=='reopencheck':
        original=BASE/f'movie-{v:02d}/frames' if v>=9 else native
        rows=[]
        for p in sorted((BASE/f'reopen-{v:02d}').glob('frame-*.png')):
            a=np.asarray(Image.open(original/p.name)).astype(np.int16);b=np.asarray(Image.open(p)).astype(np.int16);assert a.shape==b.shape
            rows.append({'frame':p.name,'maximum_channel_difference':int(np.max(abs(a-b))),'original_sha':sha(original/p.name),'reopen_sha':sha(p)})
        assert len(rows)==19
        (ROOT/f'results/sikh315/reopen-{v}/comparison.json').write_text(json.dumps({'threshold':1,'status':'PASS' if all(r['maximum_channel_difference']<=1 for r in rows) else 'FAIL','controls':rows},indent=2));return
    if op=='controls':
        dest=out/'encoded-controls';dest.mkdir(exist_ok=False)
        for f in (1,80,126,150,283,294,306,315,324,333,342,350,420,435,450,465,480,500,600,680,696):run('-i',str(out/'sikh-29s.mp4'),'-vf',f'select=eq(n\\,{f-1})','-frames:v','1',str(dest/f'frame-{f:04d}.png'))
        sheets(dest,out/'encoded-review',columns=4,rows=2,width=260);return
    assert sha(PASHTUN)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    manifest=json.loads((audio/'manifest.json').read_text())
    for name,h in manifest['files'].items():assert sha(audio/name)==h
    frames=sorted((BASE/f'movie-{v:02d}/frames').glob('frame-*.png'));assert len(frames)==696
    assert all(Image.open(p).size==(720,1280) for p in frames)
    out.mkdir(exist_ok=False);pic=out/'sikh-picture.mp4'
    label="drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='PRINCIPAL RIDER PROXY - AV REVIEW':fontsize=15:fontcolor=white@0.8:box=1:boxcolor=black@0.35:x=12:y=h-28"
    run('-framerate','24','-i',str(BASE/f'movie-{v:02d}/frames/frame-%04d.png'),'-vf',label,'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(pic))
    run('-i',str(pic),'-i',str(audio/'sikh-mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'sikh-29s.mp4'))
    filt='[0:v]setsar=1,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,setsar=1,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
    run('-i',str(PASHTUN),'-i',str(pic),'-i',str(audio/'joined-mix.wav'),'-filter_complex',filt,'-map','[v]','-map','2:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'pashtun-sikh-49s.mp4'))
    media=[]
    for name,seconds in (('sikh-29s.mp4',29),('pashtun-sikh-49s.mp4',49)):
        p=out/name;meta=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_format','-of','json',str(p)]));assert abs(float(meta['format']['duration'])-seconds)<.05
        run('-xerror','-i',str(p),'-f','null','-');media.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'duration':seconds,'decode':'PASS'})
    sr,j=wavfile.read(audio/'joined-mix.wav');sr0,a=wavfile.read(ROOT/'.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav');assert sr==sr0==48000 and np.array_equal(j[:20*sr],a)
    (out/'verification.json').write_text(json.dumps({'native':str(native/'sequence.blend'),'native_sha':sha(native/'sequence.blend'),'pashtun_rerendered':False,'pashtun_pcm_exact':True,'media':media,'frames':[{'name':p.name,'sha256':sha(p)} for p in frames],'direct_motion_audio':'AWAITING_DIRECTOR313','release_admission':False},indent=2))
    sheets(BASE/f'movie-{v:02d}/frames',out/'chronology',columns=6,rows=4,width=240)
if __name__=='__main__':main()
