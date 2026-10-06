"""Collision-only lower trunk exterior plus separate anatomical thighs.

Ray-sample the actual outer clothing at fixed pelvis-local sections. This
changes no rendered garment and does not project free simulated cloth.
"""
import json
from pathlib import Path
import numpy as np


def section_faces(around,rows):
    if around<3 or rows<2:raise ValueError('Invalid section grid')
    faces=[]
    for j in range(rows-1):
        for i in range(around):
            n=(i+1)%around;a=j*around+i;b=j*around+n;c=(j+1)*around+n;d=(j+1)*around+i
            faces.extend(((a,b,c),(a,c,d)))
    for i in range(around):
        n=(i+1)%around
        faces.append((around*rows,n,i))
        faces.append((around*rows+1,(rows-1)*around+i,(rows-1)*around+n))
    return np.array(faces)


def trunk_faces(name,rest,faces):
    """Classify in neutral, not by a posed height that admits knees/hands."""
    p=np.asarray(rest);keep=p[:,2]>-6.65
    if name=='upper':keep&=abs(p[:,0])<1.7
    elif name!='pants':raise ValueError('Unknown trunk source')
    return faces[np.all(keep[faces],axis=1)]


def run(out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_lower_hold import SURFACE_SHA
    from wardrobe185_lower_drape import SOURCE_SHA
    sources=[(BASE/'wardrobe185-lowersurface07/surfaces.npz',SURFACE_SHA),
        (BASE/'wardrobe185-lowerregions02/surfaces.npz','f77cf4a90feac89235f3b298677df341604978dd99ef733e6a31797c70ba53e6'),
        (BASE/'wardrobe185-lowercapture02/moving-source.npz',SOURCE_SHA)]
    for p,h in sources:
        if digest(p)!=h:raise ValueError('Radial contact source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(sources[0][0],allow_pickle=False) as d:actual={k:d[k] for k in d.files}
    with np.load(sources[1][0],allow_pickle=False) as d:
        payload={k:d[k] for k in d.files if k.split('_')[0] in ('horse','saddle','pad','thighL','thighR')}
    with np.load(sources[2][0],allow_pickle=False) as d:matrices=d['pelvis_matrices'][actual['frame_ids']-1]
    payload['frame_ids']=actual['frame_ids'];frames=[];source_local=[];record={}
    semantic=out.name.endswith('lowerradial02')
    selected={name:(trunk_faces(name,actual[name+'_frames'][0],actual[name+'_faces']) if semantic
        else actual[name+'_faces']) for name in ('pants','upper')}
    n=64;z=np.linspace(-4.65,-6.65,25);faces=section_faces(n,len(z))
    theta=2*np.pi*np.arange(n)/n;directions=np.stack((np.sin(theta),np.cos(theta),np.zeros(n)),axis=1)
    for k,(frame,m) in enumerate(zip(actual['frame_ids'],matrices)):
        inv=np.linalg.inv(m);trees=[];sources_in_frame=[]
        for name in ('pants','upper'):
            p=actual[name+'_frames'][k]@inv[:3,:3].T+inv[:3,3]
            trees.append(BVHTree.FromPolygons(p.tolist(),selected[name].tolist(),all_triangles=True))
            sources_in_frame.append(p[np.unique(selected[name])])
        points=[]
        for height in z:
            center=np.array([0.,0.,height])
            for direction in directions:
                hits=[]
                for tree in trees:
                    hit,normal,_,distance=tree.ray_cast(Vector(center+direction*5),Vector(-direction),5.)
                    if hit is not None:hits.append(float((np.array(hit)-center)@direction))
                if not hits or max(hits)<=.2:raise ValueError('Outer clothing is not star-shaped at required trunk section')
                points.append(center+direction*max(hits))
        points.extend(((0,0,z[0]),(0,0,z[-1])))
        q=np.array(points);world=q@m[:3,:3].T+m[:3,3];frames.append(world)
        if frame in (1,169,193,217,223,326,360):
            tree=BVHTree.FromPolygons(q.tolist(),faces.tolist(),all_triangles=True)
            source=np.concatenate(sources_in_frame);source=source[(source[:,2]<z[0]-.05)&(source[:,2]>z[-1]+.05)]
            signed=[]
            for p in source:
                hit,normal,_,distance=tree.find_nearest(Vector(p));signed.append(float((Vector(p)-hit).dot(normal)))
            overlaps=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(faces[a])&set(faces[b])]
            record[str(frame)]={'source_outer_signed_distance_native_quantiles':np.quantile(signed,[0,.5,.99,1]).tolist(),
                'nonadjacent_self_pairs':len(overlaps)}
        if frame%48==0:print('Trunk exterior',int(frame),flush=True)
    np.savez_compressed(out/'surfaces.npz',**payload,trunk_frames=np.array(frames),trunk_faces=faces)
    (out/'result.json').write_text(json.dumps({'sources':{str(p):h for p,h in sources},
        'surfaces_sha256':digest(out/'surfaces.npz'),'frames':record,'sections':len(z),'around':n,
        'admission':'NOT_RUN','visual_gate':'NOT_RUN','rendered_actor_unchanged':True,
        'neutral_semantic_face_selection':semantic,'source_face_counts':{name:len(f) for name,f in selected.items()},
        'scope':'Collision-only mounted candidate; trunk actual outer rays and trousers-only thigh hulls. No free-cloth projection or source acceptance.'},indent=2)+'\n')
