"""Actual-output negative control for bilateral versus single prep forehoof lifts.

No Blender call, universal gait detector or artistic verdict. Three finite
thresholds on a fixed interval calibrate against Director-rejected49.
"""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
reports={k:json.loads((r/p).read_text())['frames'] for k,p in {'rejected49':'.runtime/factory-native/sikh367-motion-c49-prepare/prep367.json','candidate50':'.runtime/factory-native/sikh368-motion-c50-prepare/prep367.json'}.items()}
result={}
for name,rows in reports.items():
    pre=[x for x in rows if x['frame']<=309];table={}
    for threshold in (.02,.04,.06):
        events=[]
        for side in ('L','R'):
            z0=next(q for q in pre[0]['support'] if q['side']==side)['fore_visible_hoof'][2]
            raised=[x['frame'] for x in pre if next(q for q in x['support'] if q['side']==side)['fore_visible_hoof'][2]>z0+threshold]
            groups=[]
            for frame in raised:
                if not groups or frame>groups[-1][-1]+1:groups.append([frame])
                else:groups[-1].append(frame)
            events += [dict(side=side,start=g[0],end=g[-1]) for g in groups]
        table[str(threshold)]=events
    result[name]=table
assert all(len(v)==2 for v in result['rejected49'].values())
assert all(len(v)==1 and v[0]['side']=='L' for v in result['candidate50'].values())
record=json.loads((r/'results/sikh368/BRACE_EVENT_CONTROL.json').read_text())
assert record['results']==result
print('Rejected49 two episodes; candidate50 one left brace at all three diagnostic thresholds. Existing exact result reproduced; no motion PASS.')
