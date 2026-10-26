import numpy as np
from movie_factory.horse_shape379 import smooth
m=np.load('.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz');b=np.load('.runtime/factory-native/sikh375-appearance-c129-inspect/horse-deform375.npz');bn=list(b['names']);gn=list(m['group_names']);w=m['weights'].astype(float);base=m['shape'][0];raw=m['mesh'];p=raw
# Central pectoral tissue participates too; no abs(x) lateral gate or prior sculpt-delta mask.
mask=smooth((1.60-p[:,2])/.45)*smooth((p[:,2]-.88)/.12)*smooth((-.25-p[:,1])/.25)
w2=w.copy()
for side in ('L','R'):
 i=gn.index('DEF-breast.'+side);j=gn.index('DEF-upper_arm.'+side);take=w[:,i]*mask;w2[:,i]-=take;w2[:,j]+=take
for f in [283,333,339,346,367]:
 T=b['pose_'+str(f)]@np.linalg.inv(b['rest'])
 def lbs(p,w):
  out=np.zeros_like(p,dtype=float);total=np.zeros(len(p))
  for i,n in enumerate(gn):
   if n not in bn or not b['deform'][bn.index(n)]:continue
   a=T[bn.index(n)];out+=w[:,i,None]*(p@a[:3,:3].T+a[:3,3]);total+=w[:,i]
  use=total>1e-6;out[use]/=total[use,None];out[~use]=p[~use];return out
 source=m['posed_'+str(f)];restored=source+lbs(raw,w)-lbs(base,w);new=source+lbs(raw,w2)-lbs(base,w)
 np.savez_compressed('/tmp/control380-'+str(f)+'.npz',basis=base,raw=raw,source=source,restored=new,triangles=m['triangles'])
 print(f,'delta',np.linalg.norm(new-source,axis=1).max())
