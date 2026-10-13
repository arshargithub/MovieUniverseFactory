"""Source-bound 20s finishing. No model/provider calls or native edits."""
import hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-finish248'
PREV=ROOT/'.runtime/art-direction/series01-finish247'
RATE=48000
AUDIO='audio02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
    from movie_factory.production_knowledge import task_packet,packet_markdown
    task=json.loads((ROOT/'docs/knowledge/pilot/tasks/finish247-audio.json').read_text())
    task.update(id='finish248-audio',intent='Preserve accepted247 B sound and graphics in20 second finger-corrected derivative; trim ending only, with unfaded join master and brief review-only tail fade.')
    paths=[ROOT/'docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md',Path(__file__),PREV/'audio02/mix.wav',PREV/'audio02/manifest.json',PREV/'graphics01/aged-paper.png']
    paths.extend(PREV/'graphics02'/name for name in ('manuscript.ass','narration.ass','narration.srt','narration.vtt'))
    for name in ('opening-final','route-final'):
        if (OUT/name/'result.json').exists():paths.append(OUT/name/'result.json')
    task['inputs']={str(p.relative_to(ROOT)):sha(p) for p in paths}
    task['execution_authority']['scope']='248 explicitly accepts247 and authorizes20s cut; preserve accepted sound, no new take/call/publication.'
    task['hypotheses_to_test']=['Ending trim must preserve determined continuation and not click or introduce a new music timing change.','Preserved quotation/captions must remain legible in encoded derivative.']
    task['execution_prerequisites']=['Read248 strategy, review final247 sound provenance and image/caption treatment.']
    path=ROOT/'docs/knowledge/pilot/tasks/finish248-audio.json';path.write_text(json.dumps(task,indent=2)+'\n')
    packet=task_packet(ROOT,task)
    p=ROOT/'.runtime/knowledge-pilot213/finish248-audio.json';p.write_text(json.dumps(packet,indent=2)+'\n');p.with_suffix('.md').write_text(packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
def preflight():
    from movie_factory.production_knowledge import task_packet
    p=task_packet(ROOT,json.loads((ROOT/'docs/knowledge/pilot/tasks/finish248-audio.json').read_text()))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
def cut_audio(x,rate):
    if rate!=RATE or x.ndim!=2 or x.shape[1]!=2 or len(x)<20*rate:raise ValueError('Expected full stereo48k source')
    raw=x[:20*rate].copy();review=raw.copy()
    n=round(.25*rate);review[-n:]*=np.linspace(1,0,n)[:,None]
    return raw,review
def audio():
    preflight()
    d=OUT/AUDIO;d.mkdir(exist_ok=False)
    source=PREV/'audio02/mix.wav';manifest=json.loads((PREV/'audio02/manifest.json').read_text())
    if sha(source)!=manifest['output_hashes']['mix.wav']:raise ValueError('Accepted mix changed')
    rate,x=wavfile.read(source)
    if x.dtype.kind=='i':x=x.astype(np.float64)/(2**(x.dtype.itemsize*8-1))
    elif x.dtype.kind=='f':x=x.astype(np.float64)
    else:raise ValueError('Unsupported source encoding')
    raw,review=cut_audio(x,rate)
    for name,data in [('unfaded-trailer-join',raw),('review-mix',review)]:wavfile.write(d/(name+'.wav'),rate,data.astype(np.float32))
    _,reread=wavfile.read(d/'review-mix.wav')
    error=float(np.max(np.abs(reread[:round(19.75*rate)]-x[:round(19.75*rate)])))
    if error>1e-7:raise ValueError('Accepted sound changed before end fade')
    (d/'manifest.json').write_text(json.dumps({'source_sha256':sha(source),'duration':20,'source_music_start':40.18,'unaltered_until_seconds':19.75,'unchanged_max_error':error,'review_tail_fade_seconds':.25,'unfaded_join_preserved':True,'voice_hoof_turn_music_timing_unchanged':True,'direct_listening':'NOT_RUN','new_paid_calls':0,'outputs':{p.name:sha(p) for p in d.glob('*.wav')}},indent=2)+'\n')
def frames():
    rows=[]
    for name,folder in [('opening08','opening-final'),('route09','route-final')]:
        rec=json.loads((OUT/folder/'result.json').read_text());native=json.loads((OUT/name/'result.json').read_text())
        if not rec['complete'] or rec['source_sha256']!=native['native_sha256']:raise ValueError('Incomplete/mismatched native renders')
        for r in rec['frames']:
            p=OUT/folder/r['file']
            if sha(p)!=r['sha256']:raise ValueError('Changed frame')
            rows.append({'index':r['index'],'frame':r['frame'],'path':str(p),'sha256':r['sha256'],'native_sha256':rec['source_sha256']})
    if [r['index'] for r in rows]!=list(range(480)):raise ValueError('Require480 unique chronological frames')
    return rows
def deliver():
    preflight()
    rows=frames();d=OUT/'delivery01';d.mkdir(exist_ok=False)
    concat=d/'frames.ffconcat';concat.write_text('ffconcat version 1.0\n'+''.join("file '"+r['path']+"'\noption framerate 24\nduration 0.0416666666667\n" for r in rows))
    graphics=PREV/'graphics02';paper=PREV/'graphics01/aged-paper.png'
    for ext in ('srt','vtt'):(d/('narration.'+ext)).write_bytes((graphics/('narration.'+ext)).read_bytes())
    color=['-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-color_range','tv']
    clean=d/'pashtun-20s.mp4';captioned=d/'pashtun-20s-captioned.mp4'
    filt='[2:v]scale=1040:410,format=rgba,fade=t=in:st=3.8:d=0.22:alpha=1,fade=t=out:st=8.25:d=0.25:alpha=1[paper];[0:v][paper]overlay=20:0:shortest=1,ass='+str(graphics/'manuscript.ass')+',scale=out_color_matrix=bt709:out_range=tv[v]'
    subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(OUT/AUDIO/'review-mix.wav'),'-loop','1','-framerate','24','-i',str(paper),'-filter_complex',filt,'-map','[v]','-map','1:a:0','-r','24','-frames:v','480','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p',*color,'-c:a','aac','-b:a','256k','-ar','48000','-t','20','-movflags','+faststart',str(clean)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf','ass='+str(graphics/'narration.ass'),'-c:v','libx264','-crf','17','-preset','slow','-pix_fmt','yuv420p',*color,'-c:a','copy','-movflags','+faststart',str(captioned)],check=True)
    checks=[]
    for p in (clean,captioned):
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
        v=next(s for s in info['streams'] if s['codec_type']=='video')
        if int(v['nb_read_frames'])!=480 or (v['width'],v['height'])!=(1080,1920) or abs(float(info['format']['duration'])-20)>.03:raise ValueError('Delivery format mismatch')
        checks.append({'file':p.name,'sha256':sha(p),'probe':info,'full_decode':True})
    (d/'manifest.json').write_text(json.dumps({'frames':rows,'duration':20,'deliveries':checks,'audio_manifest_sha256':sha(OUT/AUDIO/'manifest.json'),'graphics':{str(p.relative_to(ROOT)):sha(p) for p in (paper,graphics/'manuscript.ass',graphics/'narration.ass')},'publication':False,'direct_listening':'NOT_RUN'},indent=2)+'\n')
if __name__=='__main__':{'prepare':prepare,'audio':audio,'deliver':deliver}[sys.argv[1]]()
