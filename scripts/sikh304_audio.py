"""Non-destructive 42s edit; accepted Pashtun picture reused, no native render."""
import hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy import signal
from movie_factory import production_knowledge as pk
from movie_factory.sikh304_motion import RATE as CLOCK,travel
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh304'
OUT=BASE/'audio-01'
MUSIC=ROOT/'artifacts/imports/suno-theme-01/original/Harmonic Release.wav'
PASHTUN=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
JOIN=ROOT/'.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav'
SR=48000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    b=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar',str(SR),'-ac','2','-'])
    return np.frombuffer(b,dtype='<f4').reshape(-1,2).astype(float)
def write(name,data):wavfile.write(OUT/(name+'.wav'),SR,data.astype(np.float32))
def prepare():
    paths=[Path(__file__),ROOT/'results/sikh304/STRATEGY.md',ROOT/'results/sikh304/STRATEGY.md',ROOT/'src/movie_factory/sikh304_motion.py',PASHTUN,JOIN,MUSIC,ROOT/'.runtime/art-direction/series01-finish245/audio02/manifest.json',ROOT/'.runtime/art-direction/series01-finish248/audio02/manifest.json']
    task={'id':'sikh304-joined-audio','operation':'audio','entities':['music_reference','officer'],'query':'accepted Pashtun reuse music edit sound timing Sikh engine no new narration','intent':'Director304 two-stage skid picture requires corresponding local tire-dirt effect timing; same selected music, narration and accepted Pashtun picture; no provider calls','phase':'execution','inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths},'open_decisions':[],'execution_authority':{'source':'results/sikh304/STRATEGY.md','scope':'Scoped local effect timing for authorized scene derivative; no new narration, paid generation or publication'},'max_context_characters':42000}
    task['preserve_accepted_artifact']='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    authority='docs/knowledge/CURRENT_PRODUCTION_STATE.md';task['inputs'][authority]=sha(ROOT/authority)
    p=pk.task_packet(ROOT,task);dest=ROOT/'results/sikh304/audio';dest.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',p)]: (dest/(name+'.json')).write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
    return p
def audio():
    prepare()
    assert sha(PASHTUN)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    assert sha(JOIN)=='e991f5fecf4d2805b10c6a9857e08104984d31036c05f7cd2996a40abbbd76c8'
    OUT.mkdir(exist_ok=False)
    song=load(MUSIC);accepted=load(JOIN);master=json.loads((ROOT/'.runtime/art-direction/series01-finish245/audio02/manifest.json').read_text())['master_gain']
    n=22*SR;t=np.arange(n)/SR;source=np.arange(n)+round(60.18*SR)
    # First integration deliberately preserves a continuous source phrase; no
    # guessed jump to88s before the Director hears the joined sequence.
    music=song[source]*.66*master
    st=t*CLOCK;speed=np.array([abs(travel(float(s)+.005)-travel(float(s)-.005))/.01*CLOCK for s in st[::240]])
    speed=np.interp(t,t[::240],speed)
    rpm=np.interp(t,[0,3.7,5.2,6.3,14.9,15.7,17.9,18.7,22],[3700,3900,2500,950,950,1700,2300,4300,3900])
    # Four-stroke single: one exhaust pulse per two crank revolutions, with
    # resonant low-mid body; original synthesis, not an authentic recording.
    phase=np.cumsum(rpm/120)/SR;cycle=np.mod(phase,1)
    pulse=np.exp(-cycle*18)*(np.sin(cycle*2*np.pi*3.4)+.47*np.sin(cycle*2*np.pi*7.2))
    rng=np.random.default_rng(292);noise=rng.normal(0,1,n)
    noise=signal.sosfilt(signal.butter(2,[180,2500],fs=SR,btype='bandpass',output='sos'),noise)
    motor=signal.sosfilt(signal.butter(2,90,fs=SR,btype='highpass',output='sos'),pulse)+.08*noise*np.exp(-cycle*12)
    motor/=max(abs(motor));gain=np.interp(t,[0,1.2,3.7,6.2,7,14.7,15.3,17.8,18.5,20,22],[.22,.20,.13,.14,.055,.05,.07,.11,.25,.17,.045])
    motor*=gain*np.minimum(1,t/.025)
    effects=np.column_stack([motor,motor])
    def event(start,length,gain,frequency):
        a=round(start*SR);count=round(length*SR);q=np.arange(count)/SR
        grit=signal.sosfilt(signal.butter(2,[100,3300],fs=SR,btype='bandpass',output='sos'),rng.normal(0,1,count))
        body=np.sin(2*np.pi*(frequency*q-18*q*q))*np.exp(-q*8)
        x=(.22*grit+.7*body)*np.minimum(1,q/.012)*(1-np.clip(q/length,0,1))**1.4*gain
        end=min(n,a+count);effects[a:end]+=x[:end-a,None]
    event(5.55/CLOCK,.60/CLOCK,.35,125)
    event(6.70/CLOCK,.80/CLOCK,.31,118)
    event(15.47/CLOCK,.25,.38,135)
    event(17/CLOCK,.38,.28,105)
    event(21.4/CLOCK,.80,.4,150)
    combined=music+effects
    # Preserve music level; constrain only added FX when combined peaks demand it.
    limit=.90;allowed=np.ones_like(combined);pos=effects>1e-10;neg=effects< -1e-10
    allowed[pos]=(limit-music[pos])/effects[pos];allowed[neg]=(-limit-music[neg])/effects[neg]
    g=np.clip(allowed.min(1),0,1);g=__import__('scipy').ndimage.minimum_filter1d(g,241)
    effects*=g[:,None];mix=music+effects
    tail=np.clip((22-t)/.35,0,1);mix*=tail[:,None]
    joined=np.concatenate([accepted,mix]);assert len(joined)==42*SR;assert np.max(abs(joined))<.99
    for name,data in [('sikh-music',music),('sikh-effects',effects),('sikh-mix',mix),('joined-mix',joined)]:write(name,data)
    _,check=wavfile.read(OUT/'joined-mix.wav');assert np.array_equal(check[:20*SR],accepted.astype(np.float32))
    manifest={'accepted_picture_sha256':sha(PASHTUN),'accepted_join_audio_sha256':sha(JOIN),'music_source_sha256':sha(MUSIC),'music_source_interval_sikh':[60.18,82.18],'music_gain':.66*master,'new_voice':False,'new_provider_calls':0,'effects':'original local synthesis single-cylinder exhaust/dirt/spear/landing; temporary sound design not a recorded Enfield','pashtun_pcm_max_difference':float(np.max(abs(check[:20*SR]-accepted))),'peak':float(np.max(abs(joined))),'direct_listening':'NOT_RUN','music_mapping':'continuous first assembly, no new composition or guessed phrase splice','files':{p.name:sha(p) for p in OUT.glob('*.wav')}}
    (OUT/'audio-manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':
    {'prepare':prepare,'audio':audio}[sys.argv[1]]()



