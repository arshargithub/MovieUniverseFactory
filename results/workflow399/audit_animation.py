"""Read-only GLB keyframe/FK inspection; no mesh posing/render or artistic verdict."""
import json,struct,math
from pathlib import Path
import numpy as np
p=Path('/Users/adisharma/Downloads/horse_riggedgame_ready.glb');raw=p.read_bytes();n,_=struct.unpack_from('<II',raw,12);d=json.loads(raw[20:20+n]);pos=20+n;length,kind=struct.unpack_from('<II',raw,pos);assert kind==0x004e4942;buf=raw[pos+8:pos+8+length]
width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def acc(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];assert a['componentType']==5126 and 'sparse' not in a
 stride=v.get('byteStride',4*width[a['type']]);return np.ndarray((a['count'],width[a['type']]),dtype='<f4',buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,4)).copy()
tracks={}
for ch in d['animations'][0]['channels']:
 s=d['animations'][0]['samplers'][ch['sampler']];assert s.get('interpolation','LINEAR')=='LINEAR';tracks[ch['target']['node'],ch['target']['path']]=(acc(s['input'])[:,0],acc(s['output']))
parents={j:i for i,node in enumerate(d['nodes']) for j in node.get('children',[])}
def value(i,key,t,default):
 if (i,key) not in tracks:return np.array(d['nodes'][i].get(key,default),dtype=float)
 times,vals=tracks[i,key];b=int(np.searchsorted(times,t));b=min(b,len(times)-1);a=max(0,b-1);w=0 if times[b]==times[a] else max(0,min(1,(t-times[a])/(times[b]-times[a])))
 va=vals[a];vb=vals[b]
 if key=='rotation' and np.dot(va,vb)<0:vb=-vb
 return va*(1-w)+vb*w

def matrix(i,t):
 node=d['nodes'][i]
 if 'matrix' in node:return np.array(node['matrix']).reshape((4,4),order='F')
 tr=value(i,'translation',t,[0,0,0]);q=value(i,'rotation',t,[0,0,0,1]);q=q/np.linalg.norm(q);x,y,z,w=q
 m=np.eye(4);m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]];m[:3,:3]*=value(i,'scale',t,[1,1,1]);m[:3,3]=tr;return m
samples=[]
for t in np.arange(0,60.34,1/30):
 world={}
 def at(i):
  if i not in world:world[i]=(at(parents[i]) if i in parents else np.eye(4))@matrix(i,float(t))
  return world[i]
 positions={name:at(i)[:3,3] for name,i in [('hip',11),('front_torso',13),('head',16),('frontL',25),('frontR',31),('hindL',37),('hindR',43)]}
 v=positions['front_torso']-positions['hip'];angle=math.degrees(math.atan2(v[1],np.linalg.norm(v[[0,2]])))
 samples.append(dict(t=round(float(t),3),torso_elevation_degrees=angle,front_minus_hind_height=float((positions['frontL'][1]+positions['frontR'][1]-positions['hindL'][1]-positions['hindR'][1])/2)))
intervals=[];start=None
for s in samples+[dict(t=60.4,torso_elevation_degrees=0)]:
 if s['torso_elevation_degrees']>35 and start is None:start=s['t']
 elif s['torso_elevation_degrees']<=35 and start is not None:intervals.append([start,s['t']]);start=None
out=dict(source='ABHAY_METADATA.json',sample_fps=30,method='Read original transforms and approximate quaternion interpolation; no skin evaluation or artistic/motion judgment.',torso_elevation_range=[min(s['torso_elevation_degrees'] for s in samples),max(s['torso_elevation_degrees'] for s in samples)],candidate_high_forequarter_intervals=intervals,limitations='Numerical intervals may be other actions; do not label them rear without visual inspection. Mesh deformation, contact, identity, speed and production suitability NOT_RUN.',samples=samples)
Path('results/workflow399/ANIMATION_STRUCTURE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='samples'},indent=2))
