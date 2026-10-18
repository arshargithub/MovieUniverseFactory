"""Versioned local review media. Technical checks never confer a visual pass."""
import sys,json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.io import wavfile
from movie_factory import production_knowledge as pk
from movie_factory import sikh305_motion as motion
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh305'
FF='/opt/homebrew/bin/ffmpeg';FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
PROTECTED=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
EXPECTED='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text())
def run(args):subprocess.run([FF,'-v','error',*args],check=True)
def sheets(folder,output,step=1,columns=8,rows=6,width=180):
    files=sorted(folder.glob('frame-*.png'))[::step];page=[];output.mkdir(exist_ok=True)
    for a in range(0,len(files),columns*rows):
        chunk=files[a:a+columns*rows];height=round(Image.open(chunk[0]).height*width/Image.open(chunk[0]).width);sheet=Image.new('RGB',(columns*width,rows*(height+23)),(32,32,32));draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(chunk):
            im=Image.open(p).convert('RGB');im.thumbnail((width,height));x=(j%columns)*width;y=(j//columns)*(height+23);sheet.paste(im,(x,y));draw.text((x+4,y+height+3),p.stem,fill='white')
        dest=output/f'chronology-{a//(columns*rows)+1:02d}.jpg';sheet.save(dest,quality=93);page.append(str(dest.relative_to(ROOT)))
    return page
def prepare(v):
    task=read(ROOT/f'results/sikh305/movie-{v}/task.json');task.update(id=f'sikh305-delivery-{v}',operation='audio')
    task['entities']=sorted(set(task['entities']+['music_reference','officer']))
    task['query']='Complete Sikh scene and recorded effects; exact accepted Pashtun picture and audio reuse; no new narration or music selection; synchronized horse contacts and motorcycle slip'
    task['preserve_accepted_artifact']=EXPECTED
    audio_manifest=read(BASE/'audio-04/manifest.json')
    assert read(BASE/f'build-{v:02d}/impact-events.json')==read(BASE/'build-11/impact-events.json')
    inputs=[Path(__file__),PROTECTED,BASE/'audio-04/manifest.json',BASE/'audio-04/sikh-mix.wav',BASE/'audio-04/joined-mix.wav',BASE/f'build-{v:02d}/impact-events.json',ROOT/'scripts/sikh305_recorded_audio.py',ROOT/'scripts/sikh305_audio_check.py',ROOT/'results/sikh305/audio-4/source-rights.json',ROOT/'results/sikh305/audio-4/verification.json']
    inputs.extend(ROOT/r['file'] for r in audio_manifest['source_rights'])
    for p in inputs:
        task['inputs'][str(p.relative_to(ROOT))]=sha(p)
    packet=pk.task_packet(ROOT,task);dest=ROOT/f'results/sikh305/delivery-{v}';dest.mkdir(exist_ok=True)
    for n,d in [('task',task),('packet',packet)]:(dest/(n+'.json')).write_text(json.dumps(d,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
def edit(v):
    prepare(v);out=BASE/f'delivery-{v:02d}';out.mkdir(exist_ok=False);source=BASE/f'movie-{v:02d}/frames';frames=sorted(source.glob('frame-*.png'))
    assert len(frames)==motion.FRAMES and sha(PROTECTED)==EXPECTED
    for p in frames:assert Image.open(p).size==(720,1280)
    native=BASE/f'build-{v:02d}/sequence.blend'
    (out/'frames.json').write_text(json.dumps({'native':str(native.relative_to(ROOT)),'native_sha256':sha(native),'fps':24,'frames':[{'frame':i+1,'source':str(p.relative_to(ROOT)),'sha256':sha(p)} for i,p in enumerate(frames)]},indent=2))
    label=f"drawtext=fontfile={FONT}:text='DEVELOPMENT - PRINCIPAL RIDER PROXY':fontsize=15:fontcolor=white@0.8:box=1:boxcolor=black@0.35:x=12:y=h-28"
    pic=out/'sikh-picture.mp4';run(['-framerate','24','-i',str(source/'frame-%04d.png'),'-vf',label,'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(pic)])
    run(['-i',str(pic),'-i',str(BASE/'audio-04/sikh-mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'sikh-29s.mp4')])
    filt='[0:v]setsar=1,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,setsar=1,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
    run(['-i',str(PROTECTED),'-i',str(pic),'-i',str(BASE/'audio-04/joined-mix.wav'),'-filter_complex',filt,'-map','[v]','-map','2:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'pashtun-sikh-49s.mp4')])
    sheets(source,out/'chronology')
    (out/'manifest.json').write_text(json.dumps({'pashtun_original_sha256':sha(PROTECTED),'pashtun_rerendered':False,'files':{p.name:sha(p) for p in out.glob('*.mp4')},'new_paid_calls':0},indent=2))
def verify(v):
    out=BASE/f'delivery-{v:02d}';m=read(out/'frames.json');media=[]
    assert sha(PROTECTED)==EXPECTED and sha(ROOT/m['native'])==m['native_sha256']
    for r in m['frames']:assert sha(ROOT/r['source'])==r['sha256']
    rate,j=wavfile.read(BASE/'audio-04/joined-mix.wav');rate0,a=wavfile.read(ROOT/'.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav')
    assert rate==rate0==48000 and np.array_equal(j[:20*rate],a)
    for name,seconds in [('sikh-29s.mp4',29),('pashtun-sikh-49s.mp4',49)]:
        p=out/name;meta=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
        assert abs(float(meta['format']['duration'])-seconds)<.05
        vs=next(s for s in meta['streams'] if s['codec_type']=='video');au=next(s for s in meta['streams'] if s['codec_type']=='audio')
        assert vs['codec_name']=='h264' and vs['pix_fmt']=='yuv420p' and au['codec_name']=='aac'
        run(['-xerror','-i',str(p),'-f','null','-']);media.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'duration':float(meta['format']['duration']),'decode':'PASS'})
    native=BASE/f'build-{v:02d}';trace=read(native/'coordinated-motion.json')
    contacts={n:max(abs(r[n+'_gap']) for r in trace) for n in ('front','rear')}
    support=[r['support_boot_gap'] for r in trace if r['support_hold']==1]
    assert max(contacts.values())<.003 and max(abs(x) for x in support)<.003
    projections=read(native/'camera-relative.json');ots=[r['subject_screen'] for r in projections if 4.4<=r['source_t']<5.3]
    drift=np.ptp(np.array(ots)[:,:2],axis=0).tolist()
    record={'technical_checks':'PASS','media':media,'pashtun_source_unchanged':True,'pashtun_join_pcm_exact':True,'frames':len(trace),'tire_gap_max_m':contacts,'boot_gap_m':[min(support),max(support)],'OTS_screen_drift_xy':drift,'direct_real_time_playback_and_listening':'NOT_RUN','artistic_admission':'SEPARATE_REVIEW_REQUIRED'}
    (ROOT/f'results/sikh305/delivery-{v}/verification.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
def controls(v):
    """Decode actual delivery frames; these do not imply real-time playback."""
    out=BASE/f'delivery-{v:02d}';dest=out/'encoded-controls';dest.mkdir(exist_ok=False)
    selected=[1,88,106,109,126,140,165,200,285,294,300,310,315,326,340,440,450,466,469,475,528,600,696]
    for f in selected:
        run(['-i',str(out/'sikh-29s.mp4'),'-vf',f'select=eq(n\\,{f-1})','-frames:v','1',str(dest/f'frame-{f:04d}.png')])
    sheets(dest,out/'encoded-review',columns=4,rows=2,width=260)
def reopencheck(v):
    """Compare like-for-like diagnostic renders, never unlike movie profiles."""
    native=BASE/f'build-{v:02d}';reopened=BASE/f'reopen-{v:02d}';rows=[]
    for p in sorted(reopened.glob('frame-*.png')):
        a=np.asarray(Image.open(native/p.name)).astype(np.int16);b=np.asarray(Image.open(p)).astype(np.int16)
        assert a.shape==b.shape
        delta=np.abs(a-b)
        rows.append(dict(frame=p.name,maximum_channel_difference=int(delta.max()),changed_channels=int(np.count_nonzero(delta)),source_sha256=sha(native/p.name),reopened_sha256=sha(p)))
    assert len(rows)==8
    record=dict(scope='Eight480x85432-sample fresh-process diagnostic controls; not full696-frame repeat',threshold_max_channel=1,status='PASS' if all(r['maximum_channel_difference']<=1 for r in rows) else 'FAIL',controls=rows)
    (ROOT/f'results/sikh305/reopen-{v}/comparison.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':
    op,v=sys.argv[1],int(sys.argv[2]);assert 1<=v<=16
    if op=='sheets':
        for name in ('stop','rear','departure'):sheets(BASE/f'proof-{v:02d}'/name,BASE/f'proof-{v:02d}'/(name+'-sheets'),columns=6,rows=4,width=220)
    else:{'prepare':prepare,'edit':edit,'verify':verify,'controls':controls,'reopencheck':reopencheck}[op](v)
