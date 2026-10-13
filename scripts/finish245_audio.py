"""Local editable sound finishing: original music, new short voice, native hoof cues."""
import json,subprocess
from pathlib import Path
import numpy as np
from scipy import signal,ndimage
from finish242_audition import ROOT,MUSIC,load,sha
from finish237_audio import RATE,put,wav
from finish245_clock import clocks
from entrance189_groom import read_mdd
OUT=ROOT/'.runtime/art-direction/series01-finish245/audio02'
SRC=ROOT/'.runtime/art-direction/series01-audio223/provider'
DURATION=22.5

def music_gain(t):
    # Smoothly rising perceived build. No speech-triggered gain drops.
    knots=[(0,0),(1.5,.012),(3.5,.028),(5.5,.055),(6.7,.080),(8,.24),(9.7,.45),(11.3,.66),(21.9,.66),(22.5,0)]
    return np.interp(t,*zip(*knots))

def contact_events():
    inspection=json.loads((ROOT/'.runtime/art-direction/series01-finish237/inspection.json').read_text())
    arrays={k:read_mdd(next(o for o in v['objects'] if o['name']=='MF185_gait_horse')['caches'][0]['path']) for k,v in inspection.items()}
    first=np.asarray(arrays['opening'][:24]);rest=np.median(first,axis=0);low=first[:,:,2].min(0);groups=[]
    for front in (True,False):
        for left in (True,False):
            mask=((rest[:,1]<0)==front)&((rest[:,0]<0)==left);groups.append(np.flatnonzero(mask&(low<low[mask].min()+.20)))
    heights=[]
    for kind,count,offset in [('opening',234,217),('route',306,361)]:
        a=arrays[kind]
        for i in range(count):
            t=clocks(kind,i)[0]-offset;j=int(t);u=t-j;p=np.asarray(a[j])*(1-u)+np.asarray(a[min(j+1,len(a)-1)])*u
            heights.append([float(p[g,2].min()) for g in groups])
    heights=np.array(heights);events=[]
    for leg in range(4):
        peaks,_=signal.find_peaks(-heights[:,leg],distance=6,prominence=.3)
        for j in peaks:
            onset=j
            while onset>max(0,j-4) and heights[onset-1,leg]<heights[j,leg]+.15:onset-=1
            events.append(dict(time=onset/24,leg=leg,frame=int(onset)))
    return sorted(events,key=lambda x:x['time'])

def shorten_voice(x):
    # Measured silence interiors only; no phoneme time stretch. Keep .45s
    # phrase pause and .45s thoughtful pause before impeccable.
    cuts=[(2.33,3.1187),(4.9832,5.4907)]
    result=[];last=0;checks=[]
    for a,b in cuts:
        ia,ib=round(a*RATE),round(b*RATE)
        for i in (ia,ib):
            peak=float(np.max(abs(x[i-120:i+120])));checks.append(peak)
            if peak>.004:raise ValueError('Not a safe silent splice')
        result.append(x[round(last*RATE):ia]);last=b
    result.append(x[round(last*RATE):]);return np.concatenate(result),checks

def finish_voice(x):
    x=signal.sosfilt(signal.butter(2,75,fs=RATE,btype='highpass',output='sos'),x)
    # Gentle speech-level rider prevents phrase tails from disappearing. Limit
    # gain to6dB and do not boost the measured silence/noise floor.
    rms=np.sqrt(ndimage.uniform_filter1d(x*x,round(.08*RATE)))
    gain=np.clip(.12/np.maximum(rms,.002),.75,2.0)
    active=np.clip((rms-.002)/.008,0,1);gain=1+(gain-1)*active
    x*=ndimage.uniform_filter1d(gain,round(.025*RATE))
    x*=.72/max(np.max(abs(x)),1e-9)
    return x

def measure(path):
    p=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])

def main():
    if OUT.exists():raise ValueError('Preserve245 audio')
    OUT.mkdir(parents=True);n=round(DURATION*RATE);t=np.arange(n)/RATE
    original=load(SRC/'finish245-voice-1.mp3',1);spoken,splices=shorten_voice(original);spoken=finish_voice(spoken)
    # The new take still has a quiet final word. Equalize whole phrase bodies,
    # not merely the track peak; protect the already-identified failure.
    phrase_gains=[]
    for a,b in [(0,2.1053),(2.555,3.970),(4.4195,len(spoken)/RATE)]:
        ia,ib=round(a*RATE),round(b*RATE);rms=float(np.sqrt(np.mean(spoken[ia:ib]**2)))
        gain=np.clip(.17/max(rms,1e-9),.8,4.0)
        lo=max(0,ia-2400);hi=min(len(spoken),ib+2400)
        env=np.ones(hi-lo)*gain
        if ia>lo:env[:ia-lo]=np.linspace(1,gain,ia-lo)
        if hi>ib:env[ib-lo:]=np.linspace(gain,1,hi-ib)
        spoken[lo:hi]*=env;phrase_gains.append(float(gain))
    voice=np.zeros((n,2));put(voice,spoken,1.5,1.25)
    music=load(MUSIC)[round(76.25*RATE):round(98.75*RATE)]*music_gain(t)[:,None]
    hoof=load(SRC/'finish237-hoof-1.mp3',1)
    energy=ndimage.uniform_filter1d(hoof*hoof,480);peaks,_=signal.find_peaks(energy,distance=round(.23*RATE),prominence=.0004)
    peaks=sorted(peaks,key=lambda i:energy[i],reverse=True)[:4]
    if not peaks:raise ValueError('No hoof source impacts')
    impacts=[]
    for peak in peaks:
        a=max(0,peak-round(.018*RATE));h=hoof[a:a+round(.24*RATE)].copy()
        h=signal.sosfilt(signal.butter(2,[70,3400],fs=RATE,btype='bandpass',output='sos'),h);h/=max(np.max(abs(h)),1e-9)
        q=np.arange(len(h))/RATE
        # Short contact knock plus longer low-mid chest impact. High transient
        # is retained for small speakers; not a sub-only synthetic kick.
        body=(np.sin(2*np.pi*(125*q-85*q*q))*np.exp(-q*27)+.45*np.sin(2*np.pi*235*q)*np.exp(-q*40))
        h=.65*h+.65*body;h/=max(np.max(abs(h)),1e-9)
        h[:96]*=np.linspace(0,1,96);h[-960:]*=np.linspace(1,0,960);impacts.append(h)
    physical=np.zeros((n,2));events=contact_events();rng=np.random.default_rng(245)
    end=1.5+len(spoken)/RATE
    for i,e in enumerate(events):
        at=e['time'];gain=np.interp(at,[0,1.2,1.5,end,end+.4,11.75,22.5],[.83,.83,.15,.15,.62,.76,.66])
        gain*=[1.12,1.,.8,.88][e['leg']]*rng.uniform(.94,1.06)
        put(physical,impacts[i%len(impacts)],at,gain,[-.10,.10,-.08,.08][e['leg']]);e['gain']=float(gain)
    turn=load(SRC/'turn-1.mp3',1);turn/=max(np.max(abs(turn)),1e-9);put(physical,turn,11.85,.54)
    wind=load(ROOT/'.runtime/art-direction/series01-finish242/audition01/wind.wav')*.65
    mix=voice+music+physical+wind;safety=min(1.,.89/max(np.max(abs(mix)),1e-9))
    for name,x in [('voice',voice),('music',music),('physical-effects',physical),('wind',wind),('mix-premaster',mix*safety)]:wav(OUT/(name+'.wav'),x)
    levels=measure(OUT/'mix-premaster.wav');trim=min(-16-float(levels['input_i']),-1.5-float(levels['input_tp']))
    master=safety*10**(trim/20);wav(OUT/'mix.wav',mix*master)
    # Evidence addresses masking potential, not a fabricated listening result.
    windows=[('first_line',1.5,3.65),('credentials',4.08,5.47),('impeccable',5.92,end)]
    margins=[]
    for label,a,b in windows:
        lo,hi=round(a*RATE),round(b*RATE);v=voice[lo:hi];other=(music+physical+wind)[lo:hi]
        vr=np.sqrt(np.mean(v*v));nr=np.sqrt(np.mean(other*other));margins.append(dict(window=label,start=a,end=b,voice_over_competing_rms_db=float(20*np.log10((vr+1e-12)/(nr+1e-12)))))
    manifest=dict(duration=DURATION,voice_start=1.5,voice_end=end,silence_cut_checks=splices,phrase_gains=phrase_gains,source_voice_sha256=sha(SRC/'finish245-voice-1.mp3'),music_source_sha256=sha(MUSIC),music_interval=[76.25,98.75],music_peak_time=11.3,turn_time=11.75,events=events,masking_margins=margins,master_gain=master,loudness=measure(OUT/'mix.wav'),listening='NOT_RUN; source/mix measurements do not establish intelligibility or performance acceptance',new_provider_reservation_usd=.05)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('voice_end','masking_margins','loudness')}))
if __name__=='__main__':main()
