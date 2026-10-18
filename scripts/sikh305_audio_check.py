"""Signal and provenance checks, explicitly not a listening verdict."""
import json,subprocess,re,sys
from pathlib import Path
import numpy as np
from scipy import signal
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sikh304_audio as p
BASE=p.ROOT/'.runtime/art-direction/series01-sikh305';OUT=BASE/'audio-04'
def main():
    manifest=json.loads((OUT/'manifest.json').read_text());metrics={}
    for name,h in manifest['files'].items():
        path=OUT/name;assert p.sha(path)==h
        x=p.load(path);assert np.isfinite(x).all()
        mono=np.mean(x,axis=1);stereo=float(np.mean(x*x));metrics[name]={'seconds':len(x)/p.SR,'peak':float(np.max(abs(x))),'rms_dbfs':float(10*np.log10(max(stereo,1e-15))),'mono_power_ratio':float(np.mean(mono*mono)/max(stereo,1e-15))}
    x=p.load(OUT/'joined-mix.wav');accepted=p.load(p.JOIN);assert np.array_equal(x[:20*p.SR],accepted)
    for s in manifest['source_rights']:assert p.sha(p.ROOT/s['file'])==s['sha256'] and s['license']=='CC0-1.0'
    events=manifest['events'];impacts=json.loads((BASE/'build-11/impact-events.json').read_text())['events']
    for e in impacts:
        a=next(x for x in events if x['label']==e['event']);assert abs(a['start']-e['edit_seconds'])<1/p.SR
    proc=subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-nostats','-i',str(OUT/'sikh-mix.wav'),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
    summary=proc.stderr.split('Summary:')[-1]
    effects=p.load(OUT/'sikh-effects.wav');music=p.load(OUT/'sikh-music.wav');windows=[]
    for label,a,b in [('brake1',4.696,5.204),('brake2',5.669,6.346),('rear',12.083,13.90),('launch',17.928,19.5)]:
        sl=slice(round(a*p.SR),round(b*p.SR));e=effects[sl];mu=music[sl]
        low=signal.sosfilt(signal.butter(3,[50,250],fs=p.SR,btype='bandpass',output='sos'),e,axis=0)
        windows.append(dict(label=label,seconds=[a,b],effects_rms_dbfs=float(10*np.log10(max(np.mean(e*e),1e-15))),music_rms_dbfs=float(10*np.log10(max(np.mean(mu*mu),1e-15))),effects_50_250hz_rms_dbfs=float(10*np.log10(max(np.mean(low*low),1e-15)))))
    result=dict(signal_provenance_and_sync='PASS',listening='NOT_RUN',auditory_quality='NOT_CERTIFIED_BY_SIGNAL_CHECKS',metrics=metrics,event_windows=windows,loudness_summary=summary,pashtun_pcm_exact=True,source_hashes_verified=len(manifest['source_rights']),contact_timing_verified=len(impacts),new_paid_calls=0)
    (p.ROOT/'results/sikh305/audio-4/verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
