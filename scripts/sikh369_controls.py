"""Finite actual-source controls for current52; no Blender calls or art verdict."""
import json,math,sys
from pathlib import Path
cycle=int(sys.argv[1]);assert 52<=cycle<=57
r=Path(__file__).resolve().parents[1];o=r/'results/sikh369'
old=json.loads((r/'.runtime/factory-native/sikh367-motion-c49-prepare/prep367.json').read_text())
now=json.loads((r/f'.runtime/factory-native/sikh369-motion-c{cycle}-prepare/prep367.json').read_text())
def write(name,value):
 p=o/name;t=json.dumps(value,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,name
 else:p.write_text(t)
def foot(x,side):return next(q for q in x['support'] if q['side']==side)['fore_visible_hoof']
def distance(a,b):return math.dist(a,b)
a=now['frames'];pre=[x for x in a if x['frame']<=309];planted=[x for x in a if 300<=x['frame']<=309]
v=dict(opposite_forehoof_max_3d_displacement_m=max(distance(foot(x,'R'),foot(pre[0],'R')) for x in pre),brace_forehoof_max_3d_displacement_while_planted_m=max(distance(foot(x,'L'),foot(planted[0],'L')) for x in planted),geometry_unchanged=now['geometry_unchanged'],scope='Actual deform-hoof landmark controls, not physical force, complete surface contact or perceptual motion.')
assert v['opposite_forehoof_max_3d_displacement_m']<.001 and v['brace_forehoof_max_3d_displacement_while_planted_m']<.001
write(f'SOURCE_CONTROLS{cycle}.json',v)
events={}
for label,report in [('rejected49',old),('candidate52',now)]:
 rows=[x for x in report['frames'] if x['frame']<=309];table={}
 for threshold in [.02,.04,.06]:
  found=[]
  for side in ['L','R']:
   z0=foot(rows[0],side)[2];groups=[]
   for f in [x['frame'] for x in rows if foot(x,side)[2]>z0+threshold]:
    if not groups or f>groups[-1][-1]+1:groups.append([f])
    else:groups[-1].append(f)
   found += [dict(side=side,start=g[0],end=g[-1]) for g in groups]
  table[str(threshold)]=found
 events[label]=table
assert all(len(x)==2 for x in events['rejected49'].values()) and all(len(x)==1 and x[0]['side']=='L' for x in events['candidate52'].values())
write(f'BRACE_EVENT_CONTROL{cycle}.json',dict(results=events,scope='Finite2/4/6cm landmark-elevation control through309 detects oldtwo versus newone; not a universal gait detector or visual acceptance.'))
boundaries={}
for name,i,j in [('entry',0,1),('firstlift_exit',-2,-1)]:
 x,y=a[i],a[j];dt=(y['frame']-x['frame'])/24;vel=lambda u,v:[(b-a)/dt for a,b in zip(u,v)]
 boundaries[name]=dict(frames=[x['frame'],y['frame']],pose=y['phase'],horse_world=y['horse_world'],horse_root_velocity_m_s=vel([q[3] for q in x['horse_world'][:3]],[q[3] for q in y['horse_world'][:3]]),body_pitch_velocity_rad_s=(y['phase']['pitch']-x['phase']['pitch'])/dt,feet={q['side']:dict(hind=q['visible_hoof'],fore=q['fore_visible_hoof'],hind_velocity_m_s=vel(x['support'][k]['visible_hoof'],q['visible_hoof']),fore_velocity_m_s=vel(x['support'][k]['fore_visible_hoof'],q['fore_visible_hoof'])) for k,q in enumerate(y['support'])},rider_sagittal=y['rider_sagittal'])
boundaries['scope']=f'Actual{cycle} pose/finite24fps velocity/contact handoff; no zero-velocity hold. Director368 keeps scope prep; later action invalidated, not accepted.'
write(f'PHASE_BOUNDARIES{cycle}.json',boundaries)
print(f'Actual{cycle} singlebrace/plant controls and outgoing state verified; biological fluidity remains Director AV.')
