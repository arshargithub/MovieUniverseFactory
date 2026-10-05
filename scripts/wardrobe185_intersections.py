"""Layer-pair intersection audit; no source geometry changes."""
import json
from pathlib import Path
import numpy as np


def run(out):
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    path=base.BASE/'wardrobe185-cut05/trajectory.npz'
    if base.digest(path)!='b58d4b35d26c686014565630ed7debdd18a5ed77fb095e6436901cadc405ba3a':raise ValueError('Audit source changed')
    with np.load(path,allow_pickle=False) as d:p=d['points'];f=d['faces'];q=d['frames'][-1];counts=d['counts']
    report={}
    # Tiny separated/crossing control validates the installed overlap query.
    a=BVHTree.FromPolygons([(0,0,0),(1,0,0),(0,1,0)],[(0,1,2)])
    b=BVHTree.FromPolygons([(0,0,1),(1,0,1),(0,1,1)],[(0,1,2)])
    c=BVHTree.FromPolygons([(.2,.2,-1),(.2,.2,1),(.8,.2,0)],[(0,1,2)])
    if a.overlap(b) or not a.overlap(c):raise ValueError('Intersection query control failed')
    for label,points in (('initial',p),('settled',q)):
        trees=[];offset=0;faces=[]
        for count in counts:
            g=f[(f[:,0]>=offset)&(f[:,0]<offset+count)]
            trees.append(BVHTree.FromPolygons(points.tolist(),g.tolist()));faces.append(g);offset+=count
        record={}
        for i,j in ((0,1),(0,2),(1,2)):
            pairs=trees[i].overlap(trees[j])
            record[str((i,j))]={'face_pair_count':len(pairs),'examples':[{'faces':[int(x),int(y)],'point':points[faces[i][x]].mean(0).tolist()} for x,y in pairs[:20]]}
        report[label]=record
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
