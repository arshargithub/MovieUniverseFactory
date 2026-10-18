"""Assemble explicitly sourced retained/repaired frames and local review media."""
import sys,json,hashlib,shutil,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
from movie_factory import production_knowledge as pk
from movie_factory import sikh304_motion as motion
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh304'
FF='/opt/homebrew/bin/ffmpeg';FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
PROTECTED=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
EXPECTED='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def run(args):subprocess.run([FF,'-v','error',*args],check=True)
def diff(a,b):
    aa=np.asarray(Image.open(a).convert('RGB')).astype(int);bb=np.asarray(Image.open(b).convert('RGB')).astype(int)
    assert aa.shape==bb.shape
    d=np.abs(aa-bb);return {'max_channel_error':int(d.max()),'mean_abs_error':float(d.mean()),'pixels_over_1':int(np.count_nonzero(d.max(axis=2)>1))}
def assemble(v):
    parent=BASE/'movie-08';repair=BASE/f'repair-render-{v:02d}';native=BASE/f'repair-build-{v:02d}/sequence.blend'
    # Current originals remain frozen. In particular no overwrite of movie08.
    for folder in (parent,repair):
        for rel,h in read(folder/'source/bindings.json').items():assert sha(ROOT/rel)==h,rel
    inherited=read(parent/'frame-provenance.json');assert len(inherited['frames'])==528
    outside=[{'frame':f,**diff(parent/f'frames/frame-{f:04d}.png',repair/f'frame-{f:04d}.png')} for f in (1,275,356,450)]
    if any(r['max_channel_error']>1 for r in outside):raise ValueError('Outside-range replay requires reassessment: '+repr(outside))
    out=BASE/'delivery-02';out.mkdir(exist_ok=False);(out/'frames').mkdir();rows=[]
    for f in range(1,529):
        owner=repair if 276<=f<=355 else parent;src=owner/f'frames/frame-{f:04d}.png'
        assert Image.open(src).size==(720,1280)
        h=sha(src)
        if owner==parent:assert h==inherited['frames'][f-1]['sha256']
        dest=out/'frames'/src.name;shutil.copy2(src,dest);assert sha(dest)==h
        rows.append({'frame':f,'source':str(src.relative_to(ROOT)),'sha256':h})
    manifest={'native':str(native.relative_to(ROOT)),'native_sha256':sha(native),'parent_native':inherited['native'],
              'parent_bindings':sha(parent/'source/bindings.json'),'repair_bindings':sha(repair/'source/bindings.json'),
              'outside_range_controls':outside,'rendered_replacement_range':[276,355],'retained_frame_count':448,
              'fps':24,'size':[720,1280],'frames':rows}
    (out/'frames.json').write_text(json.dumps(manifest,indent=2))
def compare(v):
    out=BASE/'delivery-02';rp=BASE/f'repair-reopen-{v:02d}'
    rows=[{'frame':f,**diff(out/f'frames/frame-{f:04d}.png',rp/f'frame-{f:04d}.png')} for f in (1,130,148,315,450)]
    record={'scope':'Five fresh-process controls against assembled retained/repaired sequence','rows':rows,'strict_1_pass':all(r['max_channel_error']<=1 for r in rows)}
    (out/'repeat-comparison.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
def edit(v,prepare=False):
    out=BASE/'delivery-02';audio=BASE/'audio-01';task=read(ROOT/f'results/sikh304/repair-render-{v}/task.json')
    task.update(id='sikh304-delivery02',operation='audio',phase='execution')
    for p in (Path(__file__),out/'frames.json',PROTECTED,audio/'sikh-mix.wav',audio/'joined-mix.wav'):
        task['inputs'][str(p.relative_to(ROOT))]=sha(p)
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh304/delivery02';proof.mkdir(exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(proof/(name+'.json')).write_text(json.dumps(data,indent=2))
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if prepare:return
    assert sha(PROTECTED)==EXPECTED
    label=f"drawtext=fontfile={FONT}:text='DEVELOPMENT - PRINCIPAL RIDER PROXY':fontsize=15:fontcolor=white@0.8:box=1:boxcolor=black@0.35:x=12:y=h-28"
    pic=out/'sikh-picture.mp4'
    run(['-framerate','24','-i',str(out/'frames/frame-%04d.png'),'-vf',label,'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(pic)])
    run(['-i',str(pic),'-i',str(audio/'sikh-mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'sikh-22s.mp4')])
    filt='[0:v]setsar=1,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,setsar=1,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
    run(['-i',str(PROTECTED),'-i',str(pic),'-i',str(audio/'joined-mix.wav'),'-filter_complex',filt,'-map','[v]','-map','2:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'pashtun-sikh-42s.mp4')])
    vf=f"scale=144:256,drawtext=fontfile={FONT}:text='%{{eif\\:n+1\\:d}}':fontsize=12:fontcolor=white:box=1:boxcolor=black@0.6:x=3:y=3,tile=8x8"
    run(['-framerate','24','-i',str(out/'frames/frame-%04d.png'),'-vf',vf,str(out/'chronology-%02d.png')])
    (out/'manifest.json').write_text(json.dumps({'pashtun_source_sha256':sha(PROTECTED),'pashtun_rerendered':False,'audio':{p.name:sha(p) for p in (audio/'sikh-mix.wav',audio/'joined-mix.wav')},'frames_manifest_sha256':sha(out/'frames.json'),'files':{p.name:sha(p) for p in out.glob('*.mp4')},'new_paid_calls':0},indent=2))
def verify(v):
    out=BASE/'delivery-02';m=read(out/'frames.json');media=[]
    assert sha(ROOT/m['native'])==m['native_sha256']
    for row in m['frames']:assert sha(ROOT/row['source'])==row['sha256']==sha(out/f"frames/frame-{row['frame']:04d}.png")
    assert sha(PROTECTED)==EXPECTED
    rate,j=wavfile.read(BASE/'audio-01/joined-mix.wav');rate0,a=wavfile.read(ROOT/'.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav')
    assert rate==rate0==48000 and np.array_equal(j[:20*rate],a)
    trace=read(BASE/'build-08/coordinated-motion.json');clearance=read(BASE/'build-08/camera-bank-clearance.json')
    assert not clearance['occlusions']
    contacts={n:max(abs(r[n+'_gap']) for r in trace) for n in ('front','rear')}
    support=[r['support_boot_gap'] for r in trace if r['support_hold']==1]
    assert max(contacts.values())<.003 and max(abs(x) for x in support)<.003
    dt=.001
    acceleration=lambda t:-(motion.travel(t+dt)-2*motion.travel(t)+motion.travel(t-dt))/dt**2*motion.RATE**2
    launch=[acceleration(t) for t in np.linspace(21.41,25.99,460)]
    brake=[acceleration(t) for t in np.linspace(3.601,7.499,3900)]
    assert min(launch)>=-.01 and max(launch)<3.65 and min(brake)>-7.4 and max(brake)<.01
    for name,sec in (('sikh-22s.mp4',22),('pashtun-sikh-42s.mp4',42)):
        p=out/name;meta=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
        assert abs(float(meta['format']['duration'])-sec)<.05
        vs=next(s for s in meta['streams'] if s['codec_type']=='video');au=next(s for s in meta['streams'] if s['codec_type']=='audio')
        assert vs['codec_name']=='h264' and vs['pix_fmt']=='yuv420p' and au['codec_name']=='aac'
        run(['-xerror','-i',str(p),'-f','null','-'])
        media.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'duration':float(meta['format']['duration']),'size':[vs['width'],vs['height']],'decode':'PASS'})
    record={'status':'TECHNICAL_DELIVERY_CHECKS_PASS','media':media,'native':m['native'],'frames':528,'rendered_replacement':80,'retained_exact_frames':448,'pashtun_source_sha256':EXPECTED,'pashtun_join_pcm_exact':True,'outside_range_controls':m['outside_range_controls'],'reopen':read(out/'repeat-comparison.json'),'tire_contact_max_gap_m':contacts,'supported_boot_gap_m':[min(support),max(support)],'bank_occlusions':0,'launch_acceleration_m_s2':[min(launch),max(launch)],'braking_acceleration_m_s2':[min(brake),max(brake)],'limits':['Frame inspection and decoding are not real-time viewing or listening.','Principal proxy is not production admission.','No new remote backup or publication.']}
    (ROOT/'results/sikh304/verification.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':
    op,v=sys.argv[1],int(sys.argv[2])
    if v not in (1,2,3) or op not in ('assemble','compare','edit','verify'):raise ValueError('Unadmitted delivery')
    if op=='edit':edit(v,'--prepare' in sys.argv)
    else:{'assemble':assemble,'compare':compare,'verify':verify}[op](v)
