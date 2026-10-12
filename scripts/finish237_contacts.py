"""Extract approximate hoof landing onsets from current native cache geometry."""
import json,sys
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_groom import read_mdd
from finish237_clock import clocks
def main():
    out=ROOT/'.runtime/art-direction/series01-finish237';inspection=json.loads((out/'inspection.json').read_text())
    arrays={k:read_mdd(next(o for o in v['objects'] if o['name']=='MF185_gait_horse')['caches'][0]['path']) for k,v in inspection.items()}
    first_cycle=np.asarray(arrays['opening'][:24]);rest=np.median(first_cycle,axis=0);low_cycle=first_cycle[:,:,2].min(0);groups=[]
    for front in (True,False):
        for left in (True,False):
            mask=((rest[:,1]<0)==front)&((rest[:,0]<0)==left)
            low=low_cycle[mask].min();groups.append(np.flatnonzero(mask&(low_cycle<low+.20)))
    heights=[]
    for kind,count,offset in [('opening',198,217),('route',306,361)]:
        a=arrays[kind]
        for i in range(count):
            t=clocks(kind,i)[0]-offset;j=int(t);u=t-j
            p=np.asarray(a[j])*(1-u)+np.asarray(a[min(j+1,len(a)-1)])*u
            heights.append([float(p[g,2].min()) for g in groups])
    heights=np.array(heights);events=[]
    for leg in range(4):
        peaks,props=find_peaks(-heights[:,leg],distance=6,prominence=.3)
        for j in peaks:
            # Earliest near-floor point before that supported stance trough.
            onset=j
            while onset>max(0,j-4) and heights[onset-1,leg]<heights[j,leg]+.15:onset-=1
            events.append(dict(time=float(onset/24),frame=int(onset),leg=leg,minimum_frame=int(j),height=float(heights[j,leg])))
    events.sort(key=lambda x:x['time'])
    (out/'hoof-contacts.json').write_text(json.dumps(dict(events=events,groups=[len(g) for g in groups],method='Lowest stable hoof-patch vertices, local vertical trough and first near-floor sample. Approximate image-sync cue, not physical force measurement.',limitations='24fps onset precision; tilted terrain/contact phase requires actual-shot spot checks.'),indent=2)+'\n')
    np.savez_compressed(out/'hoof-height-traces.npz',heights=heights)
    print('Extracted',len(events),'candidate contacts')
if __name__=='__main__':main()
