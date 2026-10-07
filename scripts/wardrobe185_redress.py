"""Re-cut headfall and contact-supported seams for the retained two courses.

Initial dressing only. Simulation, not a posed-frame projection, determines
the final surface. This is a scoped construction experiment, not acceptance.
"""
import json
from pathlib import Path
import numpy as np

SEWN_SHA='d8050e135938134ffb43a5a183703d461e0f8ff6f1e921e84b9938388c389c09'


def shoulder_targets(points,faces):
    """Translate each small support patch onto its supporting cloth.

    Only pre-roll support positions change; do not project free solved cloth.
    Preserve spacing inside each patch instead of collapsing its vertices.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    p=np.asarray(points);target=p.copy();scale=.12292759120464325;record=[]
    for offset in (2501,4853):
        lower=faces[faces[:,0]<offset]
        tree=BVHTree.FromPolygons(p.tolist(),lower.tolist())
        for row in (28,84):
            center=offset+row*21+12;q=Vector(p[center]);hit,normal,_,distance=tree.find_nearest(q)
            outward=q-hit
            if outward.length<1e-7:outward=normal
            destination=hit+outward.normalized()*(.005/scale)
            delta=np.array(destination)-p[center]
            if np.linalg.norm(delta)*scale>.065:raise ValueError('Shoulder fit requires recutting')
            indices=[offset+i*21+j for i in (row-1,row,row+1) for j in (11,12,13)]
            target[indices]+=delta
            record.append({'center':center,'initial_distance_m':distance*scale,'travel_m':float(np.linalg.norm(delta)*scale)})
    return target,record


def rear_targets(points,faces):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe185_convex import rear_support_indices
    p=np.asarray(points);target=p.copy();scale=.12292759120464325
    tree=BVHTree.FromPolygons(p.tolist(),faces[faces[:,0]<2501].tolist())
    for index in rear_support_indices(2501):
        layer=int(index>=4853);q=Vector(p[index]);origin=Vector((0,.3,q.z));direction=q-origin
        radius=direction.length;direction.normalize();ray=origin.copy();outer=0.
        for _ in range(64):
            hit,_,_,_=tree.ray_cast(ray,direction,5.)
            if hit is None:break
            outer=max(outer,(hit-origin).dot(direction));ray=hit+direction*1e-4
        else:raise ValueError('Rear headfall ray did not terminate')
        if outer<=0:raise ValueError('No headfall under rear return')
        target[index]=origin+direction*min(radius,outer+(.007+.008*layer)/scale)
    return target


def clean_head_contacts(points,faces,protected):
    """Local authoring-mesh relaxation before dressing, never solved motion."""
    from mathutils.bvhtree import BVHTree
    p=points.copy();original=p.copy();neighbors=[set() for _ in p]
    for face in faces:
        for a,b in zip(face,np.roll(face,-1)):neighbors[a].add(int(b));neighbors[b].add(int(a))
    history=[]
    for iteration in range(33):
        tree=BVHTree.FromPolygons(p.tolist(),faces.tolist())
        pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(faces[a])&set(faces[b])]
        history.append(len(pairs))
        if not pairs:return p,history
        if iteration==32:break
        mask=set(np.concatenate([faces[i] for pair in pairs for i in pair]).tolist())
        mask.update(n for i in list(mask) for n in neighbors[i]);mask.difference_update(map(int,protected))
        q=p.copy()
        for i in mask:q[i]=.8*p[i]+.2*p[list(neighbors[i])].mean(0)
        p=q
        if np.linalg.norm(p-original,axis=1).max()*.12292759120464325>.02:
            raise ValueError('Head cleanup requires recutting, not large distortion')
    raise ValueError('Head self-contact did not resolve during initial cleanup: '+str(history))


def prepare(out,faces,rest):
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_head_dress import HEAD07_SHA
    from wardrobe185_cut import separate_layers,front_tail_stitches,closed_course,radial_actor_fit
    from wardrobe185_support_relax import shoulder_stitches
    head=BASE/'wardrobe185-headdress07/trajectory.npz'
    sewn=BASE/'wardrobe185-supportrelax03/sewn.npz'
    if digest(head)!=HEAD07_SHA or digest(sewn)!=SEWN_SHA:raise ValueError('Unbound re-cut inputs')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(sewn,allow_pickle=False) as data:p=data['frames'][-1].copy()
    with np.load(head,allow_pickle=False) as data:
        p[:2501]=data['frames'][-1];rest=rest.copy();rest[:2501]=data['rest'];ids=data['pin_indices'];weights=data['pin_weights']
    clean=out.name.endswith(('redress02','redress03','redress04'));cleanup=None
    if clean:
        p[:2501],cleanup=clean_head_contacts(p[:2501],faces[faces[:,0]<2501],ids)
        for layer,offset in enumerate((2501,4853)):
            q,_,r,_=closed_course(layer,tailored=True,fitted=True,tucked=True)
            p[offset:offset+2352]=q;rest[offset:offset+2352]=r+np.array([20+20*layer,0,0])
        from wardrobe185_convex import CONTACT_SHA
        path=BASE/'wardrobe185-convexcontact04/contact.npz'
        if digest(path)!=CONTACT_SHA:raise ValueError('Changed construction contacts')
        cp=[];cf=[]
        with np.load(path,allow_pickle=False) as data:
            for key in ('torso','armL','armR','head','groom'):
                cf.extend((data[key+'_faces']+len(cp)).tolist());cp.extend(data[key+'_points'].tolist())
        scale=.12292759120464325
        tree=BVHTree.FromPolygons((np.array(cp)*scale).tolist(),cf)
        p,_=radial_actor_fit(p,tree,2501,scale)
    original=p.copy()
    p,conditioning=separate_layers(p,faces,[2501,2352,2352],margin=.055,periodic=True,subsample=True)
    displacement=float(np.linalg.norm(p-original,axis=1).max()*.12292759120464325)
    record={'head_sha256':HEAD07_SHA,'course_sha256':None if clean else SEWN_SHA,'courses':'Fresh smooth authored cut' if clean else 'Previously settled fabric',
            'head_initial_self_cleanup':cleanup,'initial_layer_conditioning':conditioning,'max_initial_dressing_m':displacement}
    (out/'initial-dressing.json').write_text(json.dumps(record,indent=2)+'\n')
    if displacement>.08 or any(row['initial_layer_crossings'] for row in conditioning):raise ValueError('Re-cut needs a different initial dressing')
    fitted_holds=out.name.endswith('redress04')
    joins=front_tail_stitches(p)+( [] if fitted_holds else shoulder_stitches(p))
    if fitted_holds:
        for layer,offset in enumerate((2501,4853)):
            _,_,_,pins=closed_course(layer,tailored=True,fitted=True,tucked=True)
            shoulder={i:w for i,w in pins.items() if i//21 in (27,28,29,83,84,85)}
            ids=np.r_[ids,np.array(list(shoulder),dtype=int)+offset];weights=np.r_[weights,list(shoulder.values())]
    # Concealed rear return seams connect to the underlying fabric; no
    # body/head-following pins hold the outer wraps suspended in space.
    rear_held=out.name.endswith(('redress03','redress04'))
    if rear_held:
        from wardrobe185_convex import rear_support_indices
        rear=np.array(rear_support_indices(2501));ids=np.r_[ids,rear];weights=np.r_[weights,np.full(len(rear),.85)]
    else:
        used=set()
        for layer,offset in enumerate((2501,4853)):
            for row in (111,0,1):
                index=offset+row*21+10
                candidates=range(2501) if layer==0 else range(2501,4853)
                pool=[j for j in candidates if j not in used and p[j,1]>1.]
                target=min(pool,key=lambda j:np.linalg.norm(p[j]-p[index]))
                if np.linalg.norm(p[index]-p[target])*.12292759120464325>.08:raise ValueError('Rear return cannot reach support')
                joins.append((index,target));used.add(target)
    trees=[];self_counts=[]
    for a,b in ((0,2501),(2501,4853),(4853,7205)):
        f=faces[(faces[:,0]>=a)&(faces[:,0]<b)];tree=BVHTree.FromPolygons(p.tolist(),f.tolist())
        pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i])&set(f[j])]
        self_counts.append(len(pairs));trees.append(tree)
    record.update(self_crossing_pairs=self_counts,joins=joins,pin_count=len(ids),rear_return_support='Hybrid held rear return' if rear_held else 'Free cloth-to-cloth join',
                  joins_initial_distance_m=[float(np.linalg.norm(p[a]-p[b])*.12292759120464325) for a,b in joins])
    (out/'construction.json').write_text(json.dumps(record,indent=2)+'\n')
    np.savez_compressed(out/'construction.npz',points=p,faces=faces,rest=rest,pin_indices=ids,pin_weights=weights,stitches=joins)
    if any(self_counts):raise ValueError('Re-cut initially self-intersects')
    return p,rest,ids,weights,joins
