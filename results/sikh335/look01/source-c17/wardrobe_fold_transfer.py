"""Fixed relief transfer from the already licensed, hash-pinned scarf scan.

Keeps the clean recipient topology; does not cut/patch imported scan geometry.
CC BY4 credit travels with any derivative. This is static authoring, not physics.
"""
import json
import struct
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[4]/'.runtime/assets/series01-dressing-source/scarf-original.glb'
SHA='b34727d6d989d33cef5fb77c84bb34194bf8045e4d01ac4a4d7c48c93319e7c7'
_TREES=None


def validate_source():
    from wardrobe_riding_fit import digest
    if SOURCE.is_symlink() or not SOURCE.is_file() or digest(SOURCE)!=SHA:raise ValueError('Scarf donor changed')
    blob=SOURCE.read_bytes();size,_=struct.unpack_from('<II',blob,12);doc=json.loads(blob[20:20+size])
    if any('uri' in item for key in ('buffers','images') for item in doc.get(key,[])):raise ValueError('No external donor URIs')
    if sum(item.get('count',0) for item in doc['accessors'])>2_000_000:raise ValueError('Donor complexity cap')


def trees():
    global _TREES
    if _TREES is not None:return _TREES
    validate_source()
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    prior=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(SOURCE),import_pack_images=True)
    imported=[o for o in bpy.context.scene.objects if o not in prior]
    meshes=[o for o in imported if o.type=='MESH'];assert len(meshes)==1
    source=meshes[0];points=[source.matrix_world@v.co for v in source.data.vertices]
    low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
    scale=2.5/(high[0]-low[0])
    coords=[Vector(((p.x-(low[0]+high[0])/2)*scale,(p.y-(low[1]+high[1])/2)*scale+.25,(p.z-high[2])*scale+1.55)) for p in points]
    faces=[tuple(f.vertices) for f in source.data.polygons]
    smooth=source.data.copy()
    for vertex,p in zip(smooth.vertices,coords):vertex.co=p
    bm=bmesh.new();bm.from_mesh(smooth)
    for _ in range(28):bmesh.ops.smooth_vert(bm,verts=list(bm.verts),factor=.45,use_axis_x=True,use_axis_y=True,use_axis_z=True)
    bm.to_mesh(smooth);bm.free()
    _TREES=(BVHTree.FromPolygons(coords,faces),BVHTree.FromPolygons([v.co for v in smooth.vertices],faces))
    bpy.data.meshes.remove(smooth)
    for ob in imported:
        ob.name='MF_173_hidden_scan_relief_source_'+ob.name;ob.hide_render=True;ob.hide_set(True)
        ob['attribution']='Balaclava - scarf as a hood - 3D scan by Tijerín Art Studio; https://skfb.ly/oP7Yu; CC BY4.0; fold-relief derivative by MovieUniverseFactory'
    return _TREES


def relief(point):
    """Bounded signed raw-versus-faired relief, not donor shape substitution."""
    raw,fair=trees();hit,normal,_,distance=fair.find_nearest(point)
    if hit is None or distance>.9:return 0.
    rawhit,_,_,_=raw.find_nearest(hit)
    return max(-.075,min(.16,(rawhit-hit).dot(normal)*2.2))
