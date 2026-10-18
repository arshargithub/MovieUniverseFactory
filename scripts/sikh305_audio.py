"""Local extension of the selected continuous music/edit; no provider calls."""
import json,sys
from pathlib import Path
import numpy as np
from scipy import signal,ndimage
from scipy.io import wavfile
from movie_factory import production_knowledge as pk
from movie_factory import sikh305_motion as motion
import sikh304_audio as prior
ROOT=prior.ROOT;OUT=ROOT/'.runtime/art-direction/series01-sikh305/audio-02';SR=prior.SR
def prepare():
    task=json.loads((ROOT/'results/sikh304/audio/task.json').read_text())
    task.update(id='sikh305-extended-audio',intent='Extend same selected musical treatment and synchronize local effects with corrected rear/launch; preserve accepted Pashtun PCM',execution_authority={'source':'results/sikh305/STRATEGY.md','scope':'Local authorized scene edit and effects timing; no new composition, voice or paid calls'})
    task['inputs']={str(p.relative_to(ROOT)):prior.sha(p) for p in (Path(__file__),ROOT/'scripts/sikh304_audio.py',ROOT/'src/movie_factory/sikh305_motion.py',ROOT/'results/sikh305/STRATEGY.md',prior.PASHTUN,prior.JOIN,prior.MUSIC,ROOT/'.runtime/art-direction/series01-finish245/audio02/manifest.json',ROOT/'docs/knowledge/CURRENT_PRODUCTION_STATE.md')}
    packet=pk.task_packet(ROOT,task);dest=ROOT/'results/sikh305/audio-2';dest.mkdir(parents=True,exist_ok=True)
    for n,d in [('task',task),('packet',packet)]:(dest/(n+'.json')).write_text(json.dumps(d,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    return packet
def audio():
    prepare();OUT.mkdir(exist_ok=False)
    assert prior.sha(prior.PASHTUN)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    assert prior.sha(prior.JOIN)=='e991f5fecf4d2805b10c6a9857e08104984d31036c05f7cd2996a40abbbd76c8'
    seconds=motion.FRAMES/motion.FPS;n=round(seconds*SR);t=np.arange(n)/SR
    song=prior.load(prior.MUSIC);accepted=prior.load(prior.JOIN)
    master=json.loads((ROOT/'.runtime/art-direction/series01-finish245/audio02/manifest.json').read_text())['master_gain']
    music=song[round(60.18*SR):round(60.18*SR)+n]*.66*master
    assert len(music)==n
    rpm=np.interp(t,[0,3.7,5.2,6.3,14.9,15.7,17.9,18.7,22,seconds],[3700,3900,2500,950,950,1700,2300,4300,3900,3900])
    phase=np.cumsum(rpm/120)/SR;cycle=np.mod(phase,1)
    pulse=np.exp(-cycle*18)*(np.sin(cycle*2*np.pi*3.4)+.47*np.sin(cycle*2*np.pi*7.2))
    rng=np.random.default_rng(292);noise=signal.sosfilt(signal.butter(2,[180,2500],fs=SR,btype='bandpass',output='sos'),rng.normal(0,1,n))
    motor=signal.sosfilt(signal.butter(2,90,fs=SR,btype='highpass',output='sos'),pulse)+.08*noise*np.exp(-cycle*12)
    motor/=max(abs(motor))
    gain=np.interp(t,[0,1.2,3.7,6.2,7,14.7,15.3,17.8,18.5,20,22,25,seconds],[.22,.20,.13,.14,.055,.05,.07,.11,.25,.17,.10,.035,.004])
    motor*=gain*np.minimum(1,t/.025);effects=np.column_stack([motor,motor])
    def event(start,length,gain,frequency):
        a=round(start*SR);count=round(length*SR);q=np.arange(count)/SR
        grit=signal.sosfilt(signal.butter(2,[100,3300],fs=SR,btype='bandpass',output='sos'),rng.normal(0,1,count))
        body=np.sin(2*np.pi*(frequency*q-18*q*q))*np.exp(-q*8)
        x=(.22*grit+.7*body)*np.minimum(1,q/.012)*(1-np.clip(q/length,0,1))**1.4*gain
        end=min(n,a+count);effects[a:end]+=x[:end-a,None]
    for start,length,gain,freq in [(5.55/motion.RATE,.60/motion.RATE,.35,125),(6.70/motion.RATE,.80/motion.RATE,.31,118),(15.47/motion.RATE,.25,.38,135),(16.38/motion.RATE,.38,.28,105),(21.4/motion.RATE,.82/motion.RATE,.40,150)]:event(start,length,gain,freq)
    limit=.90;allowed=np.ones_like(effects);pos=effects>1e-10;neg=effects< -1e-10
    allowed[pos]=(limit-music[pos])/effects[pos];allowed[neg]=(-limit-music[neg])/effects[neg]
    effects*=ndimage.minimum_filter1d(np.clip(allowed.min(1),0,1),241)[:,None]
    mix=(music+effects)*np.clip((seconds-t)/.35,0,1)[:,None];joined=np.concatenate([accepted,mix])
    assert np.max(abs(joined))<.99
    for name,data in [('sikh-music',music),('sikh-effects',effects),('sikh-mix',mix),('joined-mix',joined)]:wavfile.write(OUT/(name+'.wav'),SR,data.astype(np.float32))
    _,check=wavfile.read(OUT/'joined-mix.wav');assert np.array_equal(check[:20*SR],accepted.astype(np.float32))
    (OUT/'manifest.json').write_text(json.dumps({'duration':seconds,'joined_duration':20+seconds,'source_music_interval':[60.18,60.18+seconds],'pashtun_picture_sha256':prior.sha(prior.PASHTUN),'pashtun_pcm_exact':True,'peak':float(np.max(abs(joined))),'effects':'Original synthetic single-cylinder/dirt/hoof effects, not authentic field recordings','new_paid_calls':0,'direct_listening':'NOT_RUN','files':{p.name:prior.sha(p) for p in OUT.glob('*.wav')}},indent=2))
if __name__=='__main__':{'prepare':prepare,'audio':audio}[sys.argv[1]]()
