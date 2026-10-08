"""Fixed surface transport of the selected mane/tail into the new route.

Authored attached response, not a claim of physical hair dynamics. No new
nearest-point projection in motion; roots and topology remain auditable.
"""
import json
from pathlib import Path
import numpy as np


def update(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from entrance188_groom import triangle_frames
    from wardrobe185_lower_drape import triangle_weights
    from entrance190_contacts import world_transform
    source=json.loads((BASE/'entrance189-performance14/result.json').read_text())
    paths={r['object']:(BASE/'entrance189-performance14'/r['path']).resolve() for r in source['caches']}
    for r in source['caches']:
        if digest(paths[r['object']])!=r['sha256']:raise ValueError('Changed selected groom source')
    oldhorse=read_mdd(paths['MF185_gait_horse']);newhorse=read_mdd(BASE/'entrance190-route-export08/horse.mdd')
    horse=bpy.data.objects['MF185_gait_horse'];horse.data.calc_loop_triangles()
    tris=np.array([tuple(t.vertices) for t in horse.data.loop_triangles if horse.data.polygons[t.polygon_index].material_index==0])
    p0=np.asarray(oldhorse[0],float)
    with np.load(BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    rotations=np.array([np.array(world_transform(route,361+i))[:3,:3] for i in range(193)])
    records={}
    for kind,name in (('mane','MF188_flowing_mane'),('tail','MF185_gait_Full Bushy Flowing Horse Tail')):
        ob=bpy.data.objects[name];old=read_mdd(paths[name]);rest=np.asarray(old[0],float)
        if kind=='mane':
            if rest.shape!=(226152,3):raise ValueError('Selected fine mane topology changed')
            points=rest.reshape(6282,12,3,3).mean(2).reshape(-1,3)
            region=tris[np.all(p0[tris,1]<1,axis=1)&np.all(p0[tris,2]>-11,axis=1)]
            progress=np.tile(np.linspace(0,1,12),6282)
        else:
            points=rest
            region=tris[np.all(p0[tris,1]>3,axis=1)&np.all(p0[tris,2]>-12,axis=1)]
            progress=np.clip((rest[:,1]-6.1)/9.2,0,1)
        if not len(region):raise ValueError('No semantic groom support')
        tree=BVHTree.FromPolygons(p0.tolist(),region.tolist(),all_triangles=True)
        ids=[];weights=[];offsets=[]
        # Tail root frame is shared along its length, preventing tail tips
        # from binding to a nearby moving leg instead of the rump.
        tailroot=rest[rest[:,1]<6.35].mean(0) if kind=='tail' else None
        for pt in points:
            hit,normal,index,_=tree.find_nearest(Vector(tailroot if kind=='tail' else pt))
            ids.append(region[index]);weights.append(triangle_weights(hit,p0[region[index]]));offsets.append(pt-np.array(hit))
        ids=np.array(ids);weights=np.array(weights);frames0=triangle_frames(p0[ids]);offsets=np.einsum('ni,nij->nj',offsets,frames0)
        root_errors=[]
        def frames():
            for i in range(193):
                tri=np.asarray(newhorse[i][ids],float);basis=triangle_frames(tri)
                placed=(tri*weights[:,:,None]).sum(1)+np.einsum('ni,nji->nj',offsets,basis)
                fixed=placed.copy()
                # Restrained orientation lag creates coherent turn response.
                # Translation at constant riding speed is not mistakenly
                # converted into metres-long trailing strand displacement.
                lag=max(0,i-3);lagrot=rotations[i].T@rotations[lag]
                if kind=='mane':
                    q=placed.reshape(6282,12,3);roots=q[:,:1].copy();rel=q-roots
                    q+=((rel@lagrot.T)-rel)*np.linspace(0,1,12)[None,:,None]**2*.55
                    phase=points[:,1]*3.7;amplitude=np.minimum(.06,np.maximum(0,offsets[:,2])*.10)*progress**2
                    q=q.reshape(-1,3)+basis[:,:,2]*(amplitude*(np.sin(phase+i/24*5)-np.sin(phase)))[:,None]
                    q=q.reshape(6282,12,3);root_errors.append(float(abs(q[:,0]-fixed.reshape(6282,12,3)[:,0]).max()))
                    # Transport the exact selected triangular strand section.
                    delta=rest.reshape(6282,12,3,3)-points.reshape(6282,12,1,3)
                    transport=np.einsum('nij,nkj->nik',basis,frames0).reshape(6282,12,3,3)
                    result=q[:,:,None,:]+np.einsum('nsij,nskj->nski',transport,delta)
                    yield result.reshape(-1,3).astype(np.float32)
                else:
                    root=placed[rest[:,1]<6.35].mean(0);relative=placed-root
                    placed+=(relative@lagrot.T-relative)*progress[:,None]**2*.7
                    # Less air support in the gathering, continuous return
                    # on the climb. Keep the accepted substantial volume.
                    speed=float(route['speed'][i*8]);placed[:,2]-=.65*(1-speed/12)*progress**1.5
                    placed[:,0]+=.09*np.sin(i/24*4.2+progress*4)*progress**2
                    roots=rest[:,1]<6.35;placed[roots]=fixed[roots];root_errors.append(float(abs(placed[roots]-fixed[roots]).max()))
                    yield placed.astype(np.float32)
        path=out/(kind+'.mdd');write_mdd(path,193,len(rest),frames());attach_cache(ob,path,361)
        np.savez_compressed(out/(kind+'-binding.npz'),triangles=ids,barycentric=weights,offsets=offsets)
        records[kind]={'cache_sha256':digest(path),'maximum_root_transport_error_native':max(root_errors),
            'method':'Fixed source-surface transport plus restrained authored turn lag; not a physical hair simulation','visual_gate':'NOT_RUN'}
    return records
