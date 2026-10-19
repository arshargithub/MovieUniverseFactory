"""Local synchronization of previously cleared effects; no external calls."""
import sys,json
from pathlib import Path
import numpy as np
from scipy import signal,ndimage
from scipy.io import wavfile
from movie_factory import sikh315_motion as m
import sikh305_recorded_audio as old
ROOT=old.ROOT;SR=48000;BASE=ROOT/'.runtime/art-direction/series01-sikh315'
def main():
    v=int(sys.argv[1]);assert 1<=v<=16
    from sikh315_run import source_for
    native=source_for('movie',v).parent;out=BASE/f'audio-{v:02d}';out.mkdir(exist_ok=False)
    source=ROOT/'.runtime/art-direction/series01-sikh305/audio-04';manifest=json.loads((source/'manifest.json').read_text())
    for name,h in manifest['files'].items():assert old.p.sha(source/name)==h
    music=old.p.load(source/'sikh-music.wav');engine=old.p.load(source/'engine-stem.wav');friction=old.p.load(source/'friction-stem.wav');horse=np.zeros_like(music);events=[]
    # Preserve both established brakes. Replace only the launch friction window.
    friction[round(21.3/m.RATE*SR):]=0
    def place(dest,x,start,gain,label):
        a=round(start*SR);end=min(len(dest),a+len(x));dest[a:end]+=x[:end-a]*gain
        events.append({'event':label,'start':start,'end':end/SR,'gain':gain})
    tire=old.norm(old.filt(old.p.load(old.SRC/'tire-skid.mp3')[round(.07*SR):round(.70*SR)],180,4300))
    count=round(1.35/m.RATE*SR);x=signal.resample(tire,count,axis=0)
    place(friction,old.fade(x,.015,.09),21.4/m.RATE,.20,'low-traction launch friction')
    hoof=old.filt(old.p.load(old.SRC/'hoof-foley.mp3'),65,6500)
    impacts=json.loads((native/'impact-events.json').read_text())['events']
    for j,e in enumerate(impacts):
        peak=[8.05,9.45,10.06][j%3];x=old.norm(old.fade(hoof[round((peak-.018)*SR):round((peak+.22)*SR)],.002,.035));q=np.arange(len(x))/SR
        body=np.sin(2*np.pi*(88*q-26*q*q))*np.exp(-q*17)*(1-np.exp(-q*800));x=old.norm(x*.65+body[:,None]*.65)
        gain=.15 if e['event']=='spear' else .10 if 'grip' in e['event'] else .13 if 'drive' in e['event'] else .34*e['power']
        place(horse,x,e['edit_seconds'],gain,e['event'])
    neigh=old.fade(old.norm(old.filt(old.p.load(old.SRC/'horse-neigh.wav'),110,7500)),.008,.07)
    place(horse,neigh,14.82/m.RATE,.31,'rear neigh')
    effects=engine+friction+horse;pre=music+effects
    peak=ndimage.maximum_filter1d(np.max(np.abs(pre),axis=1),481);gain=ndimage.minimum_filter1d(np.minimum(1,.94/np.maximum(peak,1e-9)),241)
    t=np.arange(len(pre))/SR;mix=pre*gain[:,None]*np.clip((29-t)/.35,0,1)[:,None]
    accepted=old.p.load(old.p.JOIN);assert old.p.sha(old.p.JOIN)=='e991f5fecf4d2805b10c6a9857e08104984d31036c05f7cd2996a40abbbd76c8'
    joined=np.concatenate((accepted,mix));assert np.max(abs(joined))<.99
    for name,data in [('sikh-music',music),('sikh-effects',effects),('sikh-mix',mix),('joined-mix',joined),('horse-stem',horse),('engine-stem',engine),('friction-stem',friction)]:wavfile.write(out/(name+'.wav'),SR,data.astype(np.float32))
    assert np.array_equal(wavfile.read(out/'joined-mix.wav')[1][:20*SR],accepted.astype(np.float32))
    (out/'manifest.json').write_text(json.dumps({'source_manifest_sha':old.p.sha(source/'manifest.json'),'rights':manifest['source_rights'],'events':events,'peak':float(np.max(abs(joined))),'pashtun_pcm_exact':True,'new_paid_calls':0,'direct_listening':'NOT_RUN_DIRECTOR313','files':{p.name:old.p.sha(p) for p in out.glob('*.wav')}},indent=2))
if __name__=='__main__':main()
