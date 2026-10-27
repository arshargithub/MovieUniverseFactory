"""Inert OBJ body-only parser for a source-bound CC0 anatomical reference."""
from pathlib import Path
import json,hashlib
import numpy as np

def parse(path):
 vertices=[];faces=[];group='';text=path.read_text()
 for line in text.splitlines():
  row=line.split()
  if not row:continue
  if row[0]=='v':vertices.append([float(x) for x in row[1:4]])
  elif row[0] in {'g','o'}:group=' '.join(row[1:])
  elif row[0]=='f' and group=='Plane':
   indices=[int(x.split('/')[0])-1 for x in row[1:]]
   if not all(0<=x<len(vertices) for x in indices):raise ValueError('REFERENCE_OBJ_INDEX')
   for i in range(1,len(indices)-1):faces.append([indices[0],indices[i],indices[i+1]])
 v=np.array(vertices);f=np.array(faces,dtype=np.int32)
 if not len(f) or not np.isfinite(v).all():raise ValueError('REFERENCE_OBJ_POINTS')
 used=np.unique(f);index=np.full(len(v),-1,dtype=np.int32);index[used]=np.arange(len(used));f=index[f];v=v[used]
 # OBJ Y-up, positiveZforward. Uniform scale preserves anatomy; translation
 # frames the chest beside known originalhorse landmarks, not exact retargeting.
 v=np.column_stack([v[:,0]*.2,-v[:,2]*.2,(v[:,1]+5.008283)*.2+.2])
 return v,f

if __name__=='__main__':
 root=Path(__file__).resolve().parents[1];base=root/'.runtime/art-direction/anatomy386-references';src=base/'LD_HorseRtime02.obj';v,f=parse(src)
 dest=base/'lyndon-body-reference.npz';np.savez_compressed(dest,vertices=v.astype(np.float32),faces=f)
 report=dict(input=dict(path=str(src.relative_to(root)),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),output=dict(path=str(dest.relative_to(root)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),vertices=len(v),triangles=len(f),uniform_scale=.2,reference_only=True,scope='Anatomy guide body geometry only, no texture/rig/material/pose/style adoption. Native shape still unqualified.')
 (root/'results/sikh386/reference-normalized.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
