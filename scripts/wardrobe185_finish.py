"""Render-surface finishing on a hash-bound simulated garment.

Retain approved indigo brush/weave shader; map it in fabric coordinates so it
does not swim. No simulation displacement, painted shadow baking or actor edit.
"""
import json
from pathlib import Path
import numpy as np


def fabric_coordinates(rest,counts=(2501,2352,2352)):
    r=np.asarray(rest);counts=tuple(int(c) for c in counts)
    if counts!=(2501,2352,2352) or r.shape!=(sum(counts),3) or not np.isfinite(r).all():raise ValueError('Unexpected fabric topology')
    uv=np.zeros_like(r);wear=np.zeros(len(r));head=r[:2501].reshape(41,61,3)
    uv[:2501,0]=head[:,:,1].reshape(-1);uv[:2501,2]=head[:,:,0].reshape(-1)
    hg=wear[:2501].reshape(41,61);hg[[0,-1],:]=.10;hg[:,[0,-1]]=.10
    for k in (0,1):
        offset=2501+k*2352;g=r[offset:offset+2352].reshape(112,21,3)
        lengths=np.linalg.norm(np.roll(g,-1,axis=0)-g,axis=2).sum(0)
        arc=float(np.median(lengths));width=float(np.ptp(g[:,:,2]))
        grid=uv[offset:offset+2352].reshape(112,21,3)
        grid[:,:,0]=np.arange(112)[:,None]*arc/112;grid[:,:,2]=np.linspace(0,width,21)[None,:]
        wear[offset:offset+2352].reshape(112,21)[:,[0,-1]]=.10
    return uv,wear


def apply(ob,rest,counts,out):
    import bpy
    uv,wear=fabric_coordinates(rest,counts)
    coord=ob.data.attributes.get('MF_173_material_coords') or ob.data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
    edge=ob.data.attributes.get('MF_173_contact_wear') or ob.data.attributes.new('MF_173_contact_wear','FLOAT','POINT')
    for item,p in zip(coord.data,uv):item.vector=p
    for item,value in zip(edge.data,wear):item.value=float(value)
    if len(ob.data.materials)!=1:raise ValueError('Unexpected scarf material assembly')
    material=ob.data.materials[0].copy();material.name='MF185_indigo_fabric_finish';ob.data.materials[0]=material
    bsdf=material.node_tree.nodes.get('Principled BSDF');paint=bsdf.inputs['Base Color'].links[0].from_node
    if paint.bl_idname!='ShaderNodeMixRGB' or paint.blend_type!='MULTIPLY' or not material.get('art_direction_source'):raise ValueError('Approved brush-value shader missing')
    paint.inputs[0].default_value=.45
    record=[]
    for mod in ob.modifiers:
        if mod.type=='SUBSURF':mod.levels=2;mod.render_levels=2
        if mod.type=='SOLIDIFY':mod.thickness=.006
        record.append({'name':mod.name,'type':mod.type})
    # Preserve per-component material labels for exact evaluated intersection
    # diagnostics; all three slots reference the same visual material.
    ob.data.materials.append(material);ob.data.materials.append(material)
    for poly in ob.data.polygons:
        first=min(poly.vertices);poly.material_index=0 if first<2501 else 1 if first<4853 else 2
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    (out/'finish-contract.json').write_text(json.dumps({'material':material.name,'brush_value_mix':.45,
        'render_thickness_m':.006*.12292759120464325,'subdivision':2,'fabric_coordinates':'Rest cut, not posed world positions',
        'edge_wear_max':float(wear.max()),'simulation_points_unchanged':True,'modifiers':record,'visual_gate':'NOT_RUN'},indent=2)+'\n')


def intersections(ob,frames,out):
    import bpy
    from mathutils.bvhtree import BVHTree
    states=[(m,m.show_viewport) for m in ob.modifiers if m.type=='SOLIDIFY']
    for m,_ in states:m.show_viewport=False
    records=[]
    for frame in frames:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
        points=[list(ob.matrix_world@v.co) for v in mesh.vertices];polygons=[[] for _ in range(3)]
        for tri in mesh.loop_triangles:polygons[mesh.polygons[tri.polygon_index].material_index].append(tuple(tri.vertices))
        trees=[BVHTree.FromPolygons(points,faces,all_triangles=True) for faces in polygons]
        records.append({'frame':frame,'midsurface_crossing_pairs':{str((a,b)):len(trees[a].overlap(trees[b])) for a in range(3) for b in range(a+1,3)}})
        ev.to_mesh_clear()
    for m,state in states:m.show_viewport=state
    (out/'finished-layer-intersections.json').write_text(json.dumps({'samples':records,'scope':'Exact evaluated midsurface pairs, not visibility or thickness acceptance'},indent=2)+'\n')
