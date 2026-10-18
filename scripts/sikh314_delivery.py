"""Assemble unchanged cleared audio and protected Pashtun with derivative picture."""
import json,sys,subprocess,hashlib,shutil
from pathlib import Path
from PIL import Image
import numpy as np
from scipy.io import wavfile
from sikh305_delivery import sheets
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh314'
FF='/opt/homebrew/bin/ffmpeg'
PASHTUN=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
EXPECTED='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
AUDIO=ROOT/'.runtime/art-direction/series01-sikh305/audio-04'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def run(*args):subprocess.run([FF,'-v','error',*args],check=True)
def main():
    op,v=sys.argv[1],int(sys.argv[2]);assert 1<=v<=7
    native=BASE/f'build-{v:02d}';movie=BASE/f'movie-{v:02d}';out=BASE/f'delivery-{v:02d}'
    if op=='sheets':
        sheets(native,native/'review-sheets',columns=4,rows=3,width=260);return
    if op=='freeze':
        dest=native/'source';dest.mkdir(exist_ok=False)
        for rel,h in json.loads((native/'bindings.json').read_text()).items():
            if Path(rel).suffix=='.py':
                assert sha(ROOT/rel)==h,rel
                p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p)
        return
    if op=='reopencheck':
        controls=[]
        for p in sorted((BASE/f'reopen-{v:02d}').glob('frame-*.png')):
            a=np.asarray(Image.open(native/p.name)).astype(np.int16);b=np.asarray(Image.open(p)).astype(np.int16)
            assert a.shape==b.shape
            d=np.abs(a-b)
            controls.append(dict(frame=p.name,maximum_channel_difference=int(d.max()),changed_channels=int(np.count_nonzero(d)),original_sha256=sha(native/p.name),reopened_sha256=sha(p)))
        assert len(controls)==17
        result=dict(scope='17 matched480x85432sample fresh-process controls, not full movie replay',threshold_max_channel=1,status='PASS' if all(c['maximum_channel_difference']<=1 for c in controls) else 'FAIL',controls=controls)
        (ROOT/f'results/sikh314/reopen-{v}/comparison.json').write_text(json.dumps(result,indent=2));print(result['status']);return
    if op=='controls':
        dest=out/'encoded-controls';dest.mkdir(exist_ok=False)
        for f in (1,88,106,109,126,140,165,200,285,294,300,310,315,326,340,440,450,466,469,475,528,600,696):
            run('-i',str(out/'sikh-29s.mp4'),'-vf',f'select=eq(n\\,{f-1})','-frames:v','1',str(dest/f'frame-{f:04d}.png'))
        sheets(dest,out/'encoded-review',columns=4,rows=2,width=260);return
    if op=='edit':
        assert sha(PASHTUN)==EXPECTED
        manifest=json.loads((AUDIO/'manifest.json').read_text())
        for name,h in manifest['files'].items():assert sha(AUDIO/name)==h
        frames=sorted((movie/'frames').glob('frame-*.png'));assert len(frames)==696
        assert all(Image.open(p).size==(720,1280) for p in frames)
        out.mkdir(exist_ok=False)
        label="drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='PRINCIPAL RIDER PROXY - AV REVIEW':fontsize=15:fontcolor=white@0.8:box=1:boxcolor=black@0.35:x=12:y=h-28"
        pic=out/'sikh-picture.mp4'
        run('-framerate','24','-i',str(movie/'frames/frame-%04d.png'),'-vf',label,'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(pic))
        run('-i',str(pic),'-i',str(AUDIO/'sikh-mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'sikh-29s.mp4'))
        filt='[0:v]setsar=1,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,setsar=1,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
        run('-i',str(PASHTUN),'-i',str(pic),'-i',str(AUDIO/'joined-mix.wav'),'-filter_complex',filt,'-map','[v]','-map','2:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'pashtun-sikh-49s.mp4'))
        result={'source_native':str((native/'sequence.blend').relative_to(ROOT)),'native_sha256':sha(native/'sequence.blend'),'pashtun_original_sha256':EXPECTED,'pashtun_rerendered':False,'source_audio_manifest_sha256':sha(AUDIO/'manifest.json'),'direct_listening':'AWAITING_DIRECTOR_AV','direct_playback':'AWAITING_DIRECTOR_AV','new_paid_calls':0,'frames':[{ 'frame':i+1,'sha256':sha(p)} for i,p in enumerate(frames)],'media':[]}
        for name,seconds in [('sikh-29s.mp4',29),('pashtun-sikh-49s.mp4',49)]:
            p=out/name;meta=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
            assert abs(float(meta['format']['duration'])-seconds)<.05
            run('-xerror','-i',str(p),'-f','null','-')
            result['media'].append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),duration=seconds,decode='PASS'))
        sr,j=wavfile.read(AUDIO/'joined-mix.wav');sr0,a=wavfile.read(ROOT/'.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav')
        assert sr==sr0==48000 and np.array_equal(j[:sr*20],a)
        assert np.isfinite(j).all() and np.max(abs(j))<.99
        result['pashtun_pcm_exact']=True
        (out/'verification.json').write_text(json.dumps(result,indent=2))
        sheets(movie/'frames',out/'chronology',columns=6,rows=4,width=240)
    else:raise ValueError('Unknown fixed operation')
if __name__=='__main__':main()
