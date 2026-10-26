import numpy as np,json
m=np.load('.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz');b=np.load('.runtime/factory-native/sikh375-appearance-c129-inspect/horse-deform375.npz');names=list(b['names']);w=m['weights'];gi=list(m['group_names']);base=m['shape'][0];raw=m['mesh'];mask=(base[:,1]<-.2)&(base[:,2]>.9)&(base[:,2]<1.9)
print('segments of affecting bones:',[(n,int(b['segments'][names.index(n)])) for n in gi if n in names and b['deform'][names.index(n)] and w[mask,gi.index(n)].max()>.1])
for f in [283,333,339,346,367]:
 T=b['pose_'+str(f)]@np.linalg.inv(b['rest']);out=np.zeros_like(base,dtype=float);outRaw=np.zeros_like(base,dtype=float);total=np.zeros(len(base))
 for i,n in enumerate(gi):
  if n not in names or not b['deform'][names.index(n)]:continue
  a=T[names.index(n)];out+=w[:,i,None]*(base@a[:3,:3].T+a[:3,3]);outRaw+=w[:,i,None]*(raw@a[:3,:3].T+a[:3,3]);total+=w[:,i]
 use=total>1e-6;out[use]/=total[use,None];out[~use]=base[~use];outRaw[use]/=total[use,None];outRaw[~use]=raw[~use]
 err=np.linalg.norm(out-m['posed_'+str(f)],axis=1);print(f,'lbs err chest',np.quantile(err[mask],[.5,.9,1]),'raw restored max',np.linalg.norm(outRaw-out,axis=1).max())
 np.savez_compressed('/tmp/horse380-'+str(f)+'.npz',basis=base,raw=raw,source=m['posed_'+str(f)],restored=m['posed_'+str(f)]+outRaw-out,triangles=m['triangles'])
