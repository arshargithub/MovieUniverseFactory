"""Original procedural temp sound: contact-timed hoofbeats, wind and signal bell."""
from pathlib import Path
import json,wave,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
RATE=44100;SECONDS=24
rng=np.random.default_rng(20260912)
a=np.zeros((RATE*SECONDS,2),dtype=np.float64)
wind=rng.normal(0,1,len(a));wind=np.convolve(wind,np.ones(70)/70,mode='same');time=np.arange(len(a))/RATE
wind*=.07*(.65+.2*np.sin(time*.8)+.15*np.sin(time*1.73));a[:]=wind[:,None]
events=json.loads((ROOT/'runs/demonstrator-01/cut-motion/motion.json').read_text())['contact_events']
for e in events:
 start=round(e['time']*RATE)
 if not 0<=start<len(a):continue
 n=min(int(.18*RATE),len(a)-start);t=np.arange(n)/RATE
 grit=rng.normal(size=n);grit=np.convolve(grit,np.ones(5)/5,mode='same')
 body=np.sin(2*np.pi*(92-100*t)*t)*np.exp(-t*32)
 tap=(body*.17+grit*.14*np.exp(-t*65))*(1-np.exp(-t*1700))
 pan=.10 if e['leg'].startswith('R') else -.10
 a[start:start+n,0]+=tap*(1-pan);a[start:start+n,1]+=tap*(1+pan)
# A quiet original bell coincides with the signal flag being raised.
start=int(15.4*RATE);n=int(2*RATE);t=np.arange(n)/RATE
bell=sum(g*np.sin(2*np.pi*f*t)*np.exp(-t*d) for f,g,d in ((660,.045,2.5),(1821,.018,4),(3564,.008,6)))
bell*=1-np.exp(-t*2000);a[start:start+n]+=bell[:,None]
peak=float(np.max(np.abs(a)));scale=min(1,.85/max(peak,1e-9));pcm=(a*scale*32767).astype('<i2')
out=ROOT/'runs/demonstrator-01/cut-review';out.mkdir(exist_ok=True)
with wave.open(str(out/'temp-sound.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
(ROOT/'results/demonstrator-01/rough-cut/audio.json').write_text(json.dumps({'origin':'original deterministic synthesis; no sampled media or provider generation','status':'PROVISIONAL','duration_seconds':24,'sample_rate':RATE,'channels':2,'contact_event_count':len(events),'signal_bell_seconds':15.4,'peak_before_scaling':peak,'scale':scale,'seed':20260912,'sha256':hashlib.sha256((out/'temp-sound.wav').read_bytes()).hexdigest()},indent=2)+'\n')
