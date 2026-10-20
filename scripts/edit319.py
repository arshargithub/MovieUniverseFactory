"""319 picture edit with exact inherited audio and protected Pashtun reuse."""
import sys,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
from movie_factory import production_knowledge as pk
from sikh305_delivery import sheets
from sikh319 import ROOT,BASE,source_for
FF='/opt/homebrew/bin/ffmpeg'
AUDIO=ROOT/'.runtime/art-direction/series01-sikh318/audio-04'
PASHTUN=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
EXPECTED='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
def run(*args):subprocess.run([FF,'-v','error',*args],check=True)
def main():
    v=int(sys.argv[1]);assert 1<=v<=32
    native=source_for('movie',v);frames=sorted((BASE/f'movie-{v:02d}/frames').glob('frame-*.png'))
    assert [p.name for p in frames]==[f'frame-{f:04d}.png' for f in range(1,697)]
    assert pk.file_hash(PASHTUN)==EXPECTED
    audio=json.loads((AUDIO/'manifest.json').read_text())
    for name,h in audio['files'].items():assert pk.file_hash(AUDIO/name)==h
    task=json.loads((ROOT/f'results/sikh319/movie-{v}/task.json').read_text())
    task.update(id=f'sikh319-delivery-{v}',operation='audio',
        intent='Updated supporting cast integrated with unchanged318 timing/audio and protected Pashtun20s.',
        preserve_accepted_artifact=EXPECTED)
    inputs=[Path(__file__),ROOT/'scripts/sikh305_delivery.py',native,PASHTUN,
            ROOT/'docs/knowledge/CURRENT_PRODUCTION_STATE.md',AUDIO/'manifest.json']+[AUDIO/n for n in audio['files']]
    task['inputs'].update({str(p.relative_to(ROOT)):pk.file_hash(p) for p in inputs})
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    record=ROOT/f'results/sikh319/delivery-{v}';record.mkdir(exist_ok=True)
    for n,d in [('task',task),('packet',packet)]:(record/(n+'.json')).write_text(json.dumps(d,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(record/'packet.md');return
    out=BASE/f'delivery-{v:02d}';out.mkdir(exist_ok=False)
    for p in frames:
        with Image.open(p) as im:assert im.size==(720,1280);im.verify()
    pic=out/'sikh-picture.mp4'
    label="drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='PRINCIPAL RIDER PROXY - AV REVIEW':fontsize=15:fontcolor=white@0.8:box=1:boxcolor=black@0.35:x=12:y=h-28"
    run('-framerate','24','-i',str(BASE/f'movie-{v:02d}/frames/frame-%04d.png'),'-vf',label,'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(pic))
    run('-i',str(pic),'-i',str(AUDIO/'sikh-mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'sikh-29s.mp4'))
    filt='[0:v]setsar=1,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,setsar=1,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
    run('-i',str(PASHTUN),'-i',str(pic),'-i',str(AUDIO/'joined-mix.wav'),'-filter_complex',filt,'-map','[v]','-map','2:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'pashtun-sikh-49s.mp4'))
    media=[]
    for name,seconds in [('sikh-29s.mp4',29),('pashtun-sikh-49s.mp4',49)]:
        p=out/name;meta=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
        assert abs(float(meta['format']['duration'])-seconds)<.05
        run('-xerror','-i',str(p),'-f','null','-')
        media.append({'path':str(p.relative_to(ROOT)),'sha256':pk.file_hash(p),'duration':seconds,'decode':'PASS'})
    sr,j=wavfile.read(AUDIO/'joined-mix.wav');sr0,a=wavfile.read(ROOT/'.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav')
    assert sr==sr0==48000 and np.array_equal(j[:20*sr],a)
    controls=out/'encoded-controls';controls.mkdir()
    for f in (1,80,126,150,283,294,306,315,324,333,342,350,375,390,402,415,420,430,435,450,465,480,500,600,680,696):
        run('-i',str(out/'sikh-29s.mp4'),'-vf',f'select=eq(n\\,{f-1})','-frames:v','1',str(controls/f'frame-{f:04d}.png'))
    for k,t in enumerate((19.96,20.04),1):
        run('-ss',str(t),'-i',str(out/'pashtun-sikh-49s.mp4'),'-frames:v','1',str(out/f'join-boundary-{k:02d}.png'))
    sheets(BASE/f'movie-{v:02d}/frames',out/'chronology',columns=6,rows=4,width=240)
    sheets(controls,out/'encoded-review',columns=4,rows=2,width=260)
    verification={'native':str(native.relative_to(ROOT)),'native_sha':pk.file_hash(native),
        'pashtun_rerendered':False,'pashtun_pcm_exact':True,'audio_source':str(AUDIO.relative_to(ROOT)),
        'audio_unchanged_from318':audio['files'],'media':media,
        'frames':[{'name':p.name,'sha256':pk.file_hash(p)} for p in frames],
        'direct_motion':False,'direct_audio':False,'release_admission':False}
    assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
    (out/'verification.json').write_text(json.dumps(verification,indent=2))
    print(out)
if __name__=='__main__':main()
