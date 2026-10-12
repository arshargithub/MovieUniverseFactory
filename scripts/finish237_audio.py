"""Reproducible music-free21s stems from bounded provider sources.

Timing/levels are measurable. This does not claim human listening or final
pronunciation approval; keep the provider originals and all editable cues.
"""
import json,subprocess,hashlib,sys
from pathlib import Path
import numpy as np
from scipy import signal
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-finish237/audio'
SRC=ROOT/'.runtime/art-direction/series01-audio223/provider'
RATE=48000
def read(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar',str(RATE),'-ac','1','-'])
    return np.frombuffer(raw,dtype='<f4').astype(float)
def wav(path,x):
    subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(RATE),'-ac','1' if x.ndim==1 else '2','-i','pipe:0','-c:a','pcm_s24le',str(path)],input=x.astype('<f4').tobytes(),check=True)
def put(target,x,start,gain=1.,pan=0.):
    i=int(start*RATE);j=min(len(target),i+len(x));x=x[:j-i]*gain
    if i<0:raise ValueError('Negative cue')
    target[i:j,0]+=x*np.sqrt((1-pan)/2);target[i:j,1]+=x*np.sqrt((1+pan)/2)
def main(contact=False):
    global OUT
    if contact:OUT=OUT.with_name('audio02')
    if OUT.exists():raise ValueError('Preserve mix')
    OUT.mkdir(parents=True)
    paths={k:SRC/v for k,v in dict(voice='finish237-voice-1.mp3',hoof='finish237-hoof-1.mp3',wind='finish237-wind-1.mp3',turn='turn-1.mp3').items()}
    inputs={k:read(p) for k,p in paths.items()}
    # Remove only measured silence interiors; retain meaningful pauses and all
    # speech samples at original rate, including the 'impeccable' hesitation.
    gaps=[(1.858662,2.637528,.38),(4.304694,4.872766,.42),(5.651905,6.958481,.28),(7.807279,8.405828,.18),(9.943537,10.595170,.32)]
    keep=[];last=0;cuts=[]
    for a,b,retain in gaps:
        left=a+retain/2;right=b-retain/2
        keep.append(inputs['voice'][int(last*RATE):int(left*RATE)]);cuts.append([left,right]);last=right
    keep.append(inputs['voice'][int(last*RATE):]);voice=np.concatenate(keep)
    voice/=max(np.max(abs(voice)),1e-5);voice*=.63
    n=21*RATE;v=np.zeros((n,2));put(v,voice,.15)
    wind=signal.sosfilt(signal.butter(2,[100,5000],fs=RATE,btype='bandpass',output='sos'),inputs['wind'])
    wind/=max(np.max(abs(wind)),1e-5)
    ambience=np.zeros((n,2))
    for start in (0,10):
        w=wind.copy();fade=int(RATE*1.2);w[:fade]*=np.linspace(0,1,fade);w[-fade:]*=np.linspace(1,0,fade)
        put(ambience,w,start,.12)
    # A low, dry transient with the actual grit retained. No synthesized music.
    hoof=inputs['hoof'];energy=np.convolve(hoof*hoof,np.ones(480)/480,mode='same');peak=int(np.argmax(energy))
    onset=max(0,peak-int(.025*RATE));h=hoof[onset:min(len(hoof),onset+int(.32*RATE))].copy()
    h=signal.sosfilt(signal.butter(2,[55,4200],fs=RATE,btype='bandpass',output='sos'),h)
    h/=max(np.max(abs(h)),1e-5);h[:240]*=np.linspace(0,1,240);h[-960:]*=np.linspace(1,0,min(960,len(h)))
    foley=np.zeros((n,2));rng=np.random.default_rng(237);cues=[]
    # Initial cadence scaffold. Replace with extracted native landing events
    # before sound synchronization can PASS; no metronome-as-physics claim.
    t=0.
    while t<21 and not contact:
        hz=2.2 if t<9.0 else (1.8 if t<12 else 2.0)
        period=1/hz
        for leg,phase in enumerate((0.,.15,.47,.63)):
            at=t+phase*period
            if at>=21:continue
            gain=(.19 if at<9.6 else .30)*[.9,.85,1.15,1][leg]*rng.uniform(.9,1.1)
            put(foley,h,at,gain,[-.1,.1,-.07,.07][leg]);cues.append(dict(time=at,kind='hoof',leg=leg,status='CADENCE_SCAFFOLD_PENDING_NATIVE_CONTACT_ALIGNMENT'))
        t+=period
    if contact:
        events=json.loads((OUT.parent/'hoof-contacts.json').read_text())['events']
        for event in events:
            at=event['time'];leg=event['leg'];gain=(.19 if at<9.6 else .30)*[1.15,1.0,.9,.85][leg]*rng.uniform(.91,1.08)
            sample=signal.resample(h,int(len(h)*rng.uniform(.96,1.045)))
            put(foley,sample,at,gain,[-.08,.08,-.1,.1][leg]);cues.append({**event,'kind':'hoof','status':'NATIVE_CACHE_DERIVED_ONSET_PENDING_TEMPORAL_SPOT_CHECK'})
    turn=signal.sosfilt(signal.butter(2,[80,6500],fs=RATE,btype='bandpass',output='sos'),inputs['turn'])
    turn/=max(np.max(abs(turn)),1e-5);put(foley,turn,10.35,.4)
    # Duck effects with a broad envelope, not abrupt narration-triggered pumping.
    time=np.arange(n)/RATE;gain=1-.30*np.clip((9.8-time)/.6,0,1)
    foley*=gain[:,None];mix=v+foley+ambience
    peak=float(np.max(abs(mix)));master_gain=min(1,.89/max(peak,1e-9));mix*=master_gain
    for name,x in [('voice',v),('physical-effects',foley),('wind',ambience),('music-free-mix',mix)]:wav(OUT/(name+'.wav'),x)
    report=dict(duration_seconds=21,speech_end=.15+len(voice)/RATE,speech_speed_changed=False,silence_cuts=cuts,
        sources={k:dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for k,p in paths.items()},
        cues=cues,master_peak=float(np.max(abs(mix))),master_gain=master_gain,auditory_review='NOT_RUN: technical listening request timed out; no music supplied or reviewed',
        contact_sync='NATIVE_CACHE_DERIVED; temporal spot checks pending' if contact else 'NOT_RUN: scaffold to be replaced using actual native contact evidence',music='NONE; Director composing in Suno')
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['duration_seconds','speech_end','master_peak','contact_sync']}))
if __name__=='__main__':
    if sys.argv[1:] not in ([],['contact']):raise ValueError('Closed mix operation')
    main(bool(sys.argv[1:]))
