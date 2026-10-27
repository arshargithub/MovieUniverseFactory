"""Build an inert isosurface of244's unqualified volume goal for native review.

This is a modeling study, not a new reference authority or adopted horse.
"""
from pathlib import Path
import json
import numpy as np
from skimage.measure import marching_cubes
from anatomy386_envelope387 import field

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);i=list(q['times']).index(339);lo=np.array([-.5,-1.30,.70]);hi=np.array([.5,.85,2.03]);spacing=.025
    axes=[np.arange(a,b+spacing/2,spacing) for a,b in zip(lo,hi)];grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);values=field(grid.reshape(-1,3),q['bones'][i]).reshape(grid.shape[:-1]);v,f,n,val=marching_cubes(values,level=0,spacing=(spacing,)*3,allow_degenerate=False);v+=lo
    if len(v)>10000 or len(f)>20000 or not np.isfinite(v).all():raise ValueError('PROXY387_CAPACITY')
    out=root/'.runtime/art-direction/anatomy386-references/envelope387-245.npz';np.savez_compressed(out,vertices=v.astype(np.float32),faces=f.astype(np.int32))
    report=dict(frame=339,vertices=len(v),triangles=len(f),grid=list(values.shape),spacing=spacing,field_residual_p50_p95_max=np.percentile(abs(field(v,q['bones'][i])),[50,95,100]).tolist(),scope='Unqualified positive-volume modeling study for original-horse forequarter. Missing head/distallegs are excluded by scope; cap is a study boundary. Not physical reference authority, newactor, motion or topology solution.')
    (root/'results/sikh387/numeric245.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
