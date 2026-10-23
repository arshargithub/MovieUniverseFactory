"""Offline numerical strategy probe; approximate vertical shaft, no native writes."""
import json,numpy as np
from movie_factory.adapters.blender.nihang_arm352 import solve
d=json.load(open('.runtime/factory-native/sikh344-look-c37-save/actor-hand-diagnostic.json'))
frames=json.load(open('.runtime/factory-native/sikh352-c58-anatomy_custom_front/frames.json'))
b=frames[0]['anatomy']['bones'];s0=np.array(b['upperarm01.L']['rest_head']);e0=np.array(d['lowerarm01.L']['rest_head']);w0=np.array(d['wrist.L']['rest_head'])
across=np.array(d['finger2-1.L']['rest_head'])-d['finger5-1.L']['rest_head'];long=np.mean([d[f'finger{i}-1.L']['rest_head'] for i in range(2,6)],axis=0)-w0
rest=(s0,e0,w0,across,long,long*.7);records=json.load(open('.runtime/factory-native/sikh352-c58-save/arm352.json'))['records']
poses={f['frame']:(np.array(f['anatomy']['bones']['upperarm01.L']['pose_matrix'])[:3,3],next(x for x in records if x['frame']==f['frame'])) for f in frames}
rank=[];individual={f:[] for f in poses}
for drop in np.arange(0,.41,.04):
 for yaw in np.radians(np.arange(-180,181,20)):
  for pole in [np.array((x,y,z)) for x in (.05,.15,.25,.35) for y in (-.25,-.1,.05) for z in (-.35,-.2,-.1)]:
   vals=[]
   try:
    for f,(s,record) in poses.items():
     v=solve(s,np.array(record['center'])+[0,0,.12],[0,0,1],rest,pole,drop,yaw)
     if v['elbow'][0]>s[0]+.05:individual[f].append((v['bend'],drop,float(np.degrees(yaw)),pole.tolist(),v['elbow'].tolist()))
     if v['elbow'][0]<s[0]+.05 or v['bend']>45:raise ValueError('invalid')
     vals.append(v)
   except ValueError:continue
   rank.append((max(v['bend'] for v in vals),drop,float(np.degrees(yaw)),pole.tolist(),max(v['twist'] for v in vals)))
print('feasible',len(rank));print(sorted(rank)[:10])
print({f:sorted(v)[:2] for f,v in individual.items()})
