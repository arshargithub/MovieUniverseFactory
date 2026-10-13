"""Selected-B reversible post finish; no provider calls or native scene edits."""
import json, subprocess, sys
import numpy as np
from scipy import signal, ndimage
from finish242_audition import ROOT, MUSIC, load, sha
from finish245_audio import RATE, DURATION, SRC, music_gain, measure
from finish237_audio import put, wav
from finish245_edit import sources, manuscript, caption_ass, SRT

BASE = ROOT/'.runtime/art-direction/series01-finish245'
PREV = ROOT/'.runtime/art-direction/series01-finish246'
OUT = ROOT/'.runtime/art-direction/series01-finish247'
START = 40.18
AUDIO = 'audio02'

def audio():
    out=OUT/AUDIO
    if out.exists(): raise ValueError('Preserve existing audio')
    m=json.loads((BASE/'audio02/manifest.json').read_text())
    assert sha(MUSIC)==m['music_source_sha256']
    oldmix=load(PREV/'audio01/mix.wav'); oldmusic=load(PREV/'audio01/music.wav')
    n=len(oldmix); t=np.arange(n)/RATE; master=m['master_gain']
    music=load(MUSIC)[round(START*RATE):round((START+DURATION)*RATE)]*music_gain(t)[:,None]
    # Reconstruct precisely the existing impacts, using saved cue times/gains.
    hoof=load(SRC/'finish237-hoof-1.mp3',1)
    energy=ndimage.uniform_filter1d(hoof*hoof,480)
    peaks,_=signal.find_peaks(energy,distance=round(.23*RATE),prominence=.0004)
    peaks=sorted(peaks,key=lambda i:energy[i],reverse=True)[:4]
    old=[]; new=[]
    for peak in peaks:
        a=max(0,peak-round(.018*RATE)); h=hoof[a:a+round(.24*RATE)].copy()
        h=signal.sosfilt(signal.butter(2,[70,3400],fs=RATE,btype='bandpass',output='sos'),h)
        h/=max(np.max(abs(h)),1e-9); q=np.arange(len(h))/RATE
        body=np.sin(2*np.pi*(125*q-85*q*q))*np.exp(-q*27)+.45*np.sin(2*np.pi*235*q)*np.exp(-q*40)
        h=.65*h+.65*body; h/=max(np.max(abs(h)),1e-9)
        h[:96]*=np.linspace(0,1,96); h[-960:]*=np.linspace(1,0,960)
        old.append(h)
        # Strengthen audible low-mid contact, not a long sub-bass rumble.
        low=signal.sosfilt(signal.butter(2,[95,430],fs=RATE,btype='bandpass',output='sos'),h)
        v=h+.40*low
        v*=1+.18*np.exp(-q/0.032)
        v*=np.sqrt(np.mean(h*h))/np.sqrt(np.mean(v*v))*10**(1.2/20)
        new.append(v)
    before=np.zeros((n,2)); after=before.copy()
    for i,e in enumerate(m['events']):
        pan=[-.10,.10,-.08,.08][e['leg']]
        put(before,old[i%len(old)],e['time'],e['gain'],pan)
        put(after,new[i%len(new)],e['time'],e['gain'],pan)
    turn=load(SRC/'turn-1.mp3',1); turn/=max(np.max(abs(turn)),1e-9)
    original_physical=before.copy(); put(original_physical,turn,11.85,.54)
    error=float(np.max(abs(original_physical-load(BASE/'audio02/physical-effects.wav'))))
    assert error<3e-7, error
    # Protect the accepted spoken-word balance as well as exact voice samples.
    lift=np.interp(t,[0,1.25,1.5,m['voice_end'],m['voice_end']+.30,DURATION],[1,1,0,0,1,1])
    delta=(after-before)*lift[:,None]
    mix=oldmix+master*(music-oldmusic)+master*delta
    # Linked peak control affects only the impact bus, never voice/music/wind.
    # Fast attack, 45ms release; use oversampled peak evidence after writing.
    fixed=oldmix-master*before+master*(music-oldmusic)
    impacts=master*(before+delta)
    bound=.87
    allowed=np.ones_like(mix)
    positive=impacts>1e-9; negative=impacts < -1e-9
    allowed[positive]=(bound-fixed[positive])/impacts[positive]
    allowed[negative]=(-bound-fixed[negative])/impacts[negative]
    gain=np.clip(allowed.min(axis=1),0,1)
    gain=ndimage.minimum_filter1d(gain,481)
    for j in range(1,len(gain)): gain[j]=min(gain[j],gain[j-1]+(1-gain[j-1])/(.045*RATE))
    effective=(before+delta)*gain[:,None]
    delta=effective-before
    mix=oldmix+master*(music-oldmusic)+master*delta
    assert np.max(abs(mix))<.95, float(np.max(abs(mix)))
    out.mkdir(parents=True)
    for name,x in [('music',music),('hoof-before',before),('hoof-after',before+delta),('hoof-delta',delta),('mix',mix)]: wav(out/(name+'.wav'),x)
    residual=float(np.max(abs(load(out/'mix.wav')-master*music-master*delta-(oldmix-master*oldmusic))))
    assert residual<3e-7,residual
    levels=measure(out/'mix.wav'); assert float(levels['input_tp'])<-.9,levels
    voice=load(BASE/'audio02/voice.wav')*master; margins=[]
    for label,a,b in [('races',2.7,3.65),('impeccable',5.92,m['voice_end'])]:
        i,j=round(a*RATE),round(b*RATE); v=voice[i:j]; other=mix[i:j]-v
        margins.append({'word':label,'voice_over_competing_rms_db':float(20*np.log10(np.sqrt(np.mean(v*v))/np.sqrt(np.mean(other*other))))})
    record={'music_interval':[START,START+DURATION],'music_advance_seconds':START-39.25,'source51_at':51-START,'source52_at':52-START,'camera_cut':11.75,
      'shuffle_anchor':{'effect_starts':11.85,'first_strong_low_mid_impact':12.256,'music_low_mid_peak_source':52.436,'mapped_music_peak':52.436-START,'method':'Measured 60-800Hz 20ms energy peaks; timing evidence not direct hearing. Director follow-up anchors musical arrival to shuffle, not camera alone.'},
      'voice_source_sha256':sha(BASE/'audio02/voice.wav'),'voice_timing_gain_unchanged':True,'master_gain_unchanged':master,
      'events':m['events'],'events_unchanged':True,'old_physical_reconstruction_max_error':error,'hoof_only_peak_control_min_gain':float(gain.min()),
      'common_voice_wind_turn_residual_max':residual,'impact_design':'95-430Hz body + short attack emphasis; 1.2dB single-impact RMS lift outside speech; same event times/pan/duration; no extra impact layer under speech',
      'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [MUSIC,BASE/'audio02/manifest.json',PREV/'audio01/mix.wav',PREV/'audio01/music.wav']},
      'output_hashes':{p.name:sha(p) for p in out.glob('*.wav')},'levels':levels,'masking_margins':margins,'direct_listening':'NOT_RUN','new_paid_calls':0}
    (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps(record,indent=2))

def aged_manuscript():
    header=manuscript().split('Dialogue:')[0]
    def line(layer,text):
        return f'Dialogue: {layer},0:00:03.80,0:00:08.50,Paper,,0,0,0,,{{\\fad(220,250)}}{text}\n'
    def poly(points,color,alpha='00',blur=0,layer=0):
        coords=' l '.join(f'{x:.2f} {y:.2f}' for x,y in points)
        return line(layer,f'{{\\pos(0,0)\\blur{blur}\\c&H{color}&\\alpha&H{alpha}&\\p1}}m {coords}{{\\p0}}')
    rng=np.random.default_rng(247)
    top=[(x,14+rng.uniform(-3,3)) for x in np.linspace(14,420,70)]
    right=[(420+rng.uniform(-3,2),y) for y in np.linspace(14,146,25)]
    bottom=[(x,146+rng.uniform(-4,4)) for x in np.linspace(420,14,70)]
    left=[(14+rng.uniform(-2,3),y) for y in np.linspace(146,14,25)]
    edge=top+right+bottom+left
    body=poly([(x+1,y+2) for x,y in edge],'263C50','50',2)
    body+=poly(edge,'7196B4','00',.3)
    body+=poly([(x+(2 if x<216 else -2),y+(2 if y<80 else -2)) for x,y in edge],'B7CEE2','00',1)
    # Broad edge stains and foxing remain visible at actual portrait size.
    for i in range(90):
        x=float(rng.uniform(18,416)); y=float(rng.choice([rng.uniform(17,28),rng.uniform(131,145)]))
        rx=float(rng.uniform(2,13)); ry=float(rng.uniform(1,4))
        pts=[(x+rx*np.cos(a),y+ry*np.sin(a)) for a in np.linspace(0,2*np.pi,14)]
        body+=poly(pts,'547C9C',f'{int(rng.integers(100,190)):02X}',1.5,1)
    for i in range(430):
        x=float(rng.uniform(20,412)); y=float(rng.uniform(20,140)); w=float(rng.uniform(.15,1.4))
        body+=poly([(x,y),(x+w,y+.15),(x+w*.65,y+.6),(x-.2,y+.35)],'6684A1',f'{int(rng.integers(140,225)):02X}',.2,1)
    # A faded fold and stress cracks at edges; avoid cuts across key lettering.
    body+=poly([(52,18),(53,60),(50,105),(52,141),(54,141),(52,102),(55,61),(54,18)],'547D99','AA',1,1)
    body+=poly([(55,18),(56,59),(53,103),(55,140),(56,140),(55,103),(57,59),(56,18)],'DCE8F0','70',.7,1)
    for x,y,dx,dy in [(20,34,12,4),(419,63,-13,5),(111,145,3,-8),(326,15,-3,8),(411,121,-7,3)]:
        body+=poly([(x,y),(x+dx,y+dy),(x+dx*.55,y+dy*.7)],'3E668B','55',.25,2)
    for txt,y,size in [('The Pathans:',22,23),('“a hardy and',49,29),('martial people”',80,29),('— Sir Winston Churchill',119,18)]:
        font='Baskerville' if 'Churchill' in txt else 'Apple Chancery'
        body+=line(3,f'{{\\an8\\pos(216,{y})\\fn{font}\\fs{size}\\c&H24313B&}}{txt}')
    return header+body

def graphics():
    d=OUT/'graphics02'; d.mkdir(parents=True,exist_ok=False)
    header=manuscript().split('Dialogue:')[0]
    body=''
    for txt,y,size in [('The Pathans:',24,23),('“a hardy and',51,29),('martial people”',82,29),('— Sir Winston Churchill',119,18)]:
        font='Baskerville' if 'Churchill' in txt else 'Apple Chancery'
        body+=f'Dialogue: 3,0:00:03.80,0:00:08.50,Ink,,0,0,0,,{{\\fad(220,250)\\an8\\pos(216,{y})\\fn{font}\\fs{size}\\c&H24313B&}}{txt}\n'
    (d/'manuscript.ass').write_text(header+body)
    (d/'narration.ass').write_text(caption_ass()); (d/'narration.srt').write_text(SRT)
    (d/'narration.vtt').write_text('WEBVTT\n\n'+SRT.replace(',','.'))

def deliver():
    out=OUT/'delivery01'
    if out.exists(): raise ValueError('Preserve delivery')
    rows=sources(); out.mkdir(parents=True)
    concat=out/'frames.ffconcat'
    concat.write_text('ffconcat version 1.0\n'+''.join("file '"+r['path']+"'\noption framerate 24\nduration 0.0416666666667\n" for r in rows))
    color=['-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-color_range','tv']
    clean=out/'pashtun-B-refined.mp4'; captioned=out/'pashtun-B-refined-captioned.mp4'
    filt='[2:v]scale=1040:410,format=rgba,fade=t=in:st=3.8:d=0.22:alpha=1,fade=t=out:st=8.25:d=0.25:alpha=1[paper];[0:v][paper]overlay=20:0:shortest=1,ass='+str(OUT/'graphics02/manuscript.ass')+',scale=out_color_matrix=bt709:out_range=tv[v]'
    subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(OUT/'audio01/mix.wav'),'-loop','1','-framerate','24','-i',str(OUT/'graphics01/aged-paper.png'),'-filter_complex',filt,'-map','[v]','-map','1:a:0','-r','24','-frames:v','540','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p',*color,'-c:a','aac','-b:a','256k','-ar','48000','-t','22.5','-movflags','+faststart',str(clean)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf','ass='+str(OUT/'graphics02/narration.ass'),'-c:v','libx264','-crf','17','-preset','slow','-pix_fmt','yuv420p',*color,'-c:a','copy','-movflags','+faststart',str(captioned)],check=True)
    for p in [clean,captioned]: subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
    record={'native_frames':rows,'unchanged_native_frame_count':540,'duration':22.5,'resolution':[1080,1920],'audio_manifest_sha256':sha(OUT/'audio01/manifest.json'),'graphic_sha256':sha(OUT/'graphics02/manuscript.ass'),'paper_sha256':sha(OUT/'graphics01/aged-paper.png'),'deliveries':{p.name:sha(p) for p in [clean,captioned]},'encoded_levels':measure(clean),'publication':False}
    (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')

def remux():
    from finish246_music import video_hash
    d=OUT/'delivery02'; d.mkdir(exist_ok=False)
    rows=[]
    for name in ['pashtun-B-refined.mp4','pashtun-B-refined-captioned.mp4']:
        old=OUT/'delivery01'/name; new=d/name
        subprocess.run(['ffmpeg','-v','error','-i',str(old),'-i',str(OUT/AUDIO/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','22.5','-movflags','+faststart',str(new)],check=True)
        assert video_hash(old)==video_hash(new)
        subprocess.run(['ffmpeg','-v','error','-i',str(new),'-f','null','-'],check=True)
        rows.append({'file':name,'sha256':sha(new),'identical_video_hash':video_hash(new),'encoded_levels':measure(new)})
    (d/'manifest.json').write_text(json.dumps({'deliveries':rows,'audio_manifest_sha256':sha(OUT/AUDIO/'manifest.json'),'visual_evidence':'qc01 belongs to byte-identical delivery01 video; no visual changes in delivery02','direct_listening':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':
    {'audio':audio,'graphics':graphics,'deliver':deliver,'remux':remux}[sys.argv[1]]()
