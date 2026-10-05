"""Closed collision-only envelope from retained evaluated actor surfaces.

Union winding fills nested small solids. Morphological closing removes narrow
garment crevices; the visible actor is never loaded or changed by this handler.
"""
import json
from pathlib import Path
import numpy as np


def neighborhood(a,dilate):
    pad=np.pad(a,1,constant_values=False)
    views=[pad[x:x+a.shape[0],y:y+a.shape[1],z:z+a.shape[2]] for x in range(3) for y in range(3) for z in range(3)]
    result=np.zeros_like(a) if dilate else np.ones_like(a)
    for view in views:
        if dilate:result|=view
        else:result&=view
    return result


def surface(cells,origin,step):
    points=[];faces=[];mapping={}
    # Quad winding faces away from each occupied cell.
    corners=(((0,0,0),(0,0,1),(0,1,1),(0,1,0)),
             ((1,0,0),(1,1,0),(1,1,1),(1,0,1)),
             ((0,0,0),(1,0,0),(1,0,1),(0,0,1)),
             ((0,1,0),(0,1,1),(1,1,1),(1,1,0)),
             ((0,0,0),(0,1,0),(1,1,0),(1,0,0)),
             ((0,0,1),(1,0,1),(1,1,1),(0,1,1)))
    for axis in range(3):
        for side in (-1,1):
            mask=cells & ~np.roll(cells,-side,axis=axis)
            for cell in np.argwhere(mask):
                face=[]
                for corner in corners[axis*2+(side==1)]:
                    key=tuple(cell+corner)
                    if key not in mapping:
                        mapping[key]=len(points);points.append(origin+step*np.array(key))
                    face.append(mapping[key])
                faces.append(face)
    return np.array(points),np.array(faces)


def run(out):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    path=base.BASE/'wardrobe185-settle03/conditioning.npz'
    if base.digest(path)!='88a2705bf0b5e5ba2ff76d25a664936f11e1b4c9cc98836744158344a1715860':raise ValueError('Envelope input changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(path,allow_pickle=False) as d:p=d['contact_points'];f=d['contact_faces']
    tree=BVHTree.FromPolygons(p.tolist(),f.tolist());step=.06
    origin=p.min(0)-step*4;shape=np.ceil((p.max(0)-origin)/step).astype(int)+4
    cells=np.zeros(shape,dtype=bool);zs=origin[2]+step*(np.arange(shape[2])+.5)
    direction=Vector((0,0,-1));max_hits=0;unbalanced=0
    for i in range(shape[0]):
        for j in range(shape[1]):
            x,y=origin[:2]+step*(np.array([i,j])+.5)
            ray=Vector((x,y,zs[-1]+1));winding=0;upper=ray.z;hits=0
            for _ in range(256):
                h,n,_,_=tree.ray_cast(ray,direction,20.)
                if h is None:break
                if winding>0:cells[i,j]|=(zs<upper)&(zs>h.z)
                winding+=1 if n.z>0 else -1
                upper=h.z;ray=h+direction*1e-4;hits+=1
            else:raise ValueError('Unbounded envelope intersections')
            max_hits=max(max_hits,hits)
            unbalanced+=int(winding!=0)
        if i%20==0:print('185 contact envelope',i,'/',shape[0],flush=True)
    original=cells.copy()
    for _ in range(2):cells=neighborhood(cells,True)
    for _ in range(2):cells=neighborhood(cells,False)
    q,g=surface(cells,origin,step)
    mesh=bpy.data.meshes.new('185 exterior');mesh.from_pydata(q.tolist(),[],g.tolist());mesh.update()
    ob=bpy.data.objects.new('185 exterior',mesh);bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob
    smooth=ob.modifiers.new('Contact envelope fairing','SMOOTH');smooth.factor=.6;smooth.iterations=5
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    if out.name.endswith('proxy02'):
        # Resolve ambiguous voxel edge-only contacts through an isosurface,
        # rather than treating touching cube edges as a manifold surface.
        remesh=ob.modifiers.new('Closed exterior isosurface','REMESH');remesh.mode='VOXEL';remesh.voxel_size=step*.7
        bpy.ops.object.modifier_apply(modifier=remesh.name)
        smooth=ob.modifiers.new('Isosurface fairing','SMOOTH');smooth.factor=.5;smooth.iterations=2
        bpy.ops.object.modifier_apply(modifier=smooth.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data)
    report={'step_native':step,'closing_radius_native':step*2,'grid_shape':shape.tolist(),
        'filled_cells':int(cells.sum()),'changed_cells':int(np.count_nonzero(cells!=original)),
        'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_native':bm.calc_volume(),
        'maximum_ray_hits':max_hits,'unbalanced_rays':unbalanced,'visible_actor_changed':False,'visual_gate':'NOT_RUN'}
    bm.free()
    np.savez_compressed(out/'proxy.npz',points=np.array([v.co[:] for v in ob.data.vertices]),faces=np.array([v.vertices[:] for v in ob.data.polygons]))
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
