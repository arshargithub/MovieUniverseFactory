"""Cleared recorded effects and local processing. No provider calls."""
import json,sys
from pathlib import Path
import numpy as np
from scipy import signal,ndimage
from scipy.io import wavfile
from movie_factory import production_knowledge as pk
from movie_factory import sikh305_motion as m
import sikh304_audio as p
ROOT=p.ROOT;BASE=ROOT/'.runtime/art-direction/series01-sikh305';OUT=BASE/'audio-04';SRC=BASE/'sound-sources';SR=p.SR
SPECS=[
 ('enfield-350.mp3','350cc bike firing','rsn267','https://freesound.org/people/rsn267/sounds/274962/','https://cdn.freesound.org/previews/274/274962_2251150-hq.mp3','HQ MP3 preview; Royal Enfield350 recorded with ZoomH4n'),
 ('acceleration.mp3','Dirt motorcycle onboard take off','kyles','https://freesound.org/people/kyles/sounds/450019/','https://cdn.freesound.org/previews/450/450019_612689-hq.mp3','HQ MP3 preview; supporting acceleration layer, not exact historical motorcycle'),
 ('tire-skid.mp3','tire_skid_02','loganzsound','https://freesound.org/people/loganzsound/sounds/774265/','https://cdn.freesound.org/previews/774/774265_16682330-hq.mp3','HQ MP3 preview; bicycle tire on concrete, brief designed friction accent'),
 ('hoof-foley.mp3','Hooves Hard Muddy Surface Layer08','kalhan','https://freesound.org/people/kalhan/sounds/434809/','https://cdn.freesound.org/previews/434/434809_2161107-hq.mp3','HQ MP3 preview; coconut-shell foley on hard muddy surface'),
 ('horse-neigh.wav','Horse neighing4','Joseph SARDIN','https://bigsoundbank.com/horse-neighing-4-s1541.html','https://bigsoundbank.com/UPLOAD/bwf-en/1541.wav','Free WAV; outdoor horse recording, MixPre3 and ME66')]
def rights():
    return [dict(file=str((SRC/f).relative_to(ROOT)),sha256=p.sha(SRC/f),title=title,author=author,page=page,download=url,description=desc,license='CC0-1.0',license_url='https://creativecommons.org/publicdomain/zero/1.0/',verified_date='2026-10-18') for f,title,author,page,url,desc in SPECS]
def prepare():
    task=json.loads((ROOT/'results/sikh304/audio/task.json').read_text());task.update(id='sikh305-recorded-audio-4',intent='Replace shuffle-only effects with recorded engine, tire, hoof and neigh; synchronize revised action, preserve selected music and Pashtun PCM',execution_authority={'source':'results/sikh305/STRATEGY.md','scope':'Director-requested free-source local sound correction; no purchase, provider call or publication'})
    paths=[Path(__file__),ROOT/'scripts/sikh304_audio.py',ROOT/'src/movie_factory/sikh305_motion.py',ROOT/'results/sikh305/STRATEGY.md',p.PASHTUN,p.JOIN,p.MUSIC,BASE/'build-11/impact-events.json',ROOT/'.runtime/art-direction/series01-finish245/audio02/manifest.json',ROOT/'docs/knowledge/CURRENT_PRODUCTION_STATE.md']+[SRC/s[0] for s in SPECS]
    task['inputs']={str(f.relative_to(ROOT)):p.sha(f) for f in paths};packet=pk.task_packet(ROOT,task);dest=ROOT/'results/sikh305/audio-4';dest.mkdir(parents=True,exist_ok=True)
    for name,obj in [('task',task),('packet',packet),('source-rights',rights())]:(dest/(name+'.json')).write_text(json.dumps(obj,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
def filt(x,lo=45,hi=6000):return signal.sosfilt(signal.butter(2,[lo,hi],fs=SR,btype='bandpass',output='sos'),x,axis=0)
def norm(x):return x/max(float(np.max(np.abs(x))),1e-9)
def fade(x,a=.006,b=.035):
    q=np.arange(len(x))/SR;return x*np.minimum(1,q/a)[:,None]*np.minimum(1,(len(x)/SR-q)/b)[:,None]
def audio():
    prepare();OUT.mkdir(exist_ok=False)
    assert p.sha(p.PASHTUN)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    assert p.sha(p.JOIN)=='e991f5fecf4d2805b10c6a9857e08104984d31036c05f7cd2996a40abbbd76c8'
    seconds=m.FRAMES/m.FPS;n=round(seconds*SR);t=np.arange(n)/SR
    song=p.load(p.MUSIC);accepted=p.load(p.JOIN);master=json.loads((ROOT/'.runtime/art-direction/series01-finish245/audio02/manifest.json').read_text())['master_gain']
    music=song[round(60.18*SR):round(60.18*SR)+n]*.66*master;assert len(music)==n
    raw={f:p.load(SRC/f) for f,*_ in SPECS};stems={k:np.zeros((n,2)) for k in ('engine','friction','horse')};events=[]
    def place(stem,x,start,gain,label,source,edit):
        a=round(start*SR);end=min(n,a+len(x));assert a>=0 and end>a;stems[stem][a:end]+=x[:end-a]*gain
        events.append(dict(label=label,start=start,end=end/SR,stem=stem,gain=gain,source=source,edit=edit))
    # Real single-cylinder body; smooth source loops and perspective attenuation.
    loop=filt(raw['enfield-350.mp3'],45,4700)[round(2.3*SR):round(9.3*SR)];cross=round(.18*SR)
    extent=n*2;looped=np.zeros((extent+len(loop)*2,2));weights=np.zeros(len(looped));env=np.ones(len(loop));env[:cross]=np.linspace(0,1,cross);env[-cross:]=np.linspace(1,0,cross)
    for a in range(0,extent,len(loop)-cross):looped[a:a+len(loop)]+=loop*env[:,None];weights[a:a+len(loop)]+=env
    looped/=np.maximum(weights[:,None],1e-6)
    rate=np.interp(t,[0,4.65,5.2,5.65,6.35,14.8,16.7,18.0,18.5,19.5,22,29],[1.18,1.18,.85,.92,.68,.68,.78,.9,1.38,1.24,1.35,1.35])
    index=np.cumsum(rate)-rate[0];bed=norm(np.column_stack([np.interp(index,np.arange(len(looped)),looped[:,ch]) for ch in (0,1)]))
    levels=np.interp(t,[0,3.7,4.7,6.35,7,11.3,14.8,17.2,18,18.7,20,22,25,29],[.27,.24,.20,.09,.055,.025,.03,.07,.16,.28,.17,.08,.025,.003])
    stems['engine']+=bed*levels[:,None];events.append(dict(label='Enfield continuous body',start=0,end=seconds,source='enfield-350.mp3',edit='2.3-9.3s excerpt,180ms crossfades, perspective envelope, continuous playback rate follows braking/idle/launch',playback_rate_range=[float(rate.min()),float(rate.max())]))
    acc=fade(norm(filt(raw['acceleration.mp3'],55,4200)[round(17.8*SR):round(25.5*SR)]),.025,.30);q=np.arange(len(acc))/SR
    acc*=np.interp(q,[0,.35,1,2,4,7.7],[.4,1,.95,.75,.35,.03])[:,None]
    place('engine',acc,21.4/m.RATE-.18,.24,'traction launch throttle','acceleration.mp3','17.8-25.5s, lowpass4.2kHz, distance decay')
    rng=np.random.default_rng(305);tire=norm(filt(raw['tire-skid.mp3'][round(.07*SR):round(.70*SR)],180,4300))
    for k,(a,b,g) in enumerate([(5.55,6.15,.30),(6.70,7.50,.25),(21.4,22.22,.18)]):
        count=round((b-a)/m.RATE*SR);x=signal.resample(tire,count,axis=0)
        place('friction',fade(x,.015,.065),a/m.RATE,g,'wheel slip '+str(k+1),'tire-skid.mp3','brief raspy source accent fitted to lock interval, not long asphalt squeal')
        grit=norm(filt(rng.normal(0,1,(count,2)),90,2200))*np.sin(np.pi*np.arange(count)/(count-1))[:,None]
        place('friction',grit,a/m.RATE,.10,'earth scrape '+str(k+1),'original synthesis','supporting irregular low-mid grit, not primary sound')
    hoof=filt(raw['hoof-foley.mp3'],65,6500);impacts=json.loads((BASE/'build-11/impact-events.json').read_text())['events']
    for j,e in enumerate(impacts):
        peak=[8.05,9.45,10.06][j%3];x=norm(fade(hoof[round((peak-.018)*SR):round((peak+.22)*SR)],.002,.035));q=np.arange(len(x))/SR
        body=np.sin(2*np.pi*(88*q-26*q*q))*np.exp(-q*17)*(1-np.exp(-q*800));weighted=norm(x*.65+body[:,None]*.65)
        gain=.15 if e['event']=='spear' else .10 if 'grip' in e['event'] else .13 if 'drive' in e['event'] else .34*e['power']
        place('horse',weighted,e['edit_seconds'],gain,e['event'],'hoof-foley.mp3',dict(excerpt=[peak-.018,peak+.22],body='original88Hz decaying impact',native_frame=e['frame']))
    neigh=fade(norm(filt(raw['horse-neigh.wav'],110,7500)),.008,.07)
    place('horse',neigh,14.86/m.RATE,.31,'rear neigh','horse-neigh.wav','full1.105s vocalization; onset at rise')
    effects=sum(stems.values());pre=music+effects
    peak=ndimage.maximum_filter1d(np.max(np.abs(pre),axis=1),size=481);gain=np.minimum(1,.94/np.maximum(peak,1e-9));gain=ndimage.minimum_filter1d(gain,241)
    mix=pre*gain[:,None]*np.clip((seconds-t)/.35,0,1)[:,None];joined=np.concatenate([accepted,mix]);assert np.max(abs(joined))<.99
    for name,data in [('sikh-music',music),('sikh-effects',effects),('sikh-mix',mix),('joined-mix',joined),*[(k+'-stem',v) for k,v in stems.items()]]:wavfile.write(OUT/(name+'.wav'),SR,data.astype(np.float32))
    _,check=wavfile.read(OUT/'joined-mix.wav');assert np.array_equal(check[:20*SR],accepted.astype(np.float32))
    record=dict(duration=seconds,joined_duration=20+seconds,source_music_interval=[60.18,60.18+seconds],pashtun_picture_sha256=p.sha(p.PASHTUN),pashtun_pcm_exact=True,peak=float(np.max(abs(joined))),minimum_headroom_gain=float(gain.min()),new_paid_calls=0,direct_listening='NOT_RUN',events=events,source_rights=rights(),files={f.name:p.sha(f) for f in OUT.glob('*.wav')})
    (OUT/'manifest.json').write_text(json.dumps(record,indent=2))
if __name__=='__main__':{'prepare':prepare,'audio':audio}[sys.argv[1]]()
