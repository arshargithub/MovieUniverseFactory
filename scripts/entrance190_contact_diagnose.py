"""Locate lower-contact self intersections before changing cloth settings."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    from mathutils.bvhtree import BVHTree
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'contactdiagnose15'}:raise ValueError('Fixed contact diagnosis required')
    out=base.BASE/'entrance190-contactdiagnose15';source=base.BASE/'entrance190-fitted12/lower-contacts.npz'
    if out.exists() or base.digest(source)!='eff571c7b6fce6762fc0cd59bc74c5ae15f29a2d60370db46dd997b48d721624':raise ValueError('Changed contacts or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as z:data={k:z[k] for k in z.files}
    with np.load(base.BASE/'wardrobe185-lowerrecontact02/surfaces.npz',allow_pickle=False) as z:old={k:z[k] for k in z.files}
    rows=[]
    for frame in (360,361,385,409,433,453,489,529,553):
        for name in ('pants','upper','horse'):
            p=old[name+'_frames'][-1] if frame==360 else data[name+'_frames'][frame-361];f=data[name+'_faces'];tree=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
            pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(f[a])&set(f[b])]
            ids=np.unique(f[np.unique(np.array(pairs).ravel())]) if pairs else np.array([],int)
            local=[(a,b) for a,b in pairs if p[f[a],2].max()>-9.5 and p[f[b],2].max()>-9.5]
            rows.append({'frame':frame,'part':name,'pairs':len(pairs),'near_skirt_pairs':len(local),
                         'bounds':None if not len(ids) else [p[ids].min(0).tolist(),p[ids].max(0).tolist()]})
    (out/'result.json').write_text(json.dumps({'rows':rows},indent=2)+'\n');print(json.dumps(rows),flush=True)

if __name__=='__main__':main()
