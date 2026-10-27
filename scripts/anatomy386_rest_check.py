"""Read-only actual rest-target interface audit, never artistic approval."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from movie_factory.adapters.blender.anatomy_rest386 import load
r=Path(__file__).resolve().parents[1];cy=int(sys.argv[1]);p=r/f'.runtime/art-direction/anatomy386-targets/rest{cy}.npz';b=dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());q=load(r,b,depth_only="--form" not in sys.argv)
f=np.load(r/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz')['triangles'];f=f[np.any(q['mask'][f]>0,axis=1)];p0=q['rest'][f];t=q['target'][f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n0=np.cross(p0[:,1]-p0[:,0],p0[:,2]-p0[:,0]);a=np.linalg.norm(n,axis=1);a0=np.linalg.norm(n0,axis=1);valid=a0>1e-8;c=(n*n0).sum(1)/np.maximum(a*a0,1e-20);ratio=a/np.maximum(a0,1e-20)
x=dict(loader='PASS',binding=b,bad_triangles=int(np.sum(valid&((c<.05)|(ratio<.1)|(ratio>8)))),min_normal_cos=float(c[valid].min()),area_range=[float(ratio[valid].min()),float(ratio[valid].max())],scope='Restinterface numericaldiagnostic only, not posed or artisticacceptance.')
(r/f'results/sikh386/rest{cy}-interface.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x));raise SystemExit(2 if x['bad_triangles'] else 0)
