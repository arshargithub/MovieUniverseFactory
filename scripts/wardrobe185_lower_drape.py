"""Clean lower-tunic dressing before a free-cloth performance solve."""
import json
from pathlib import Path
import numpy as np

SOURCE_SHA='20b06605833f46561db93ba3c25ef27e934b96abe39854958e8f1b101a284d0e'
CONTACT_SHA='577b9e0ee50a0350424d64aecf25b4965637c2bf23d6b8e9e6b9f878a377e0b5'
SCALE=.12292759120464325


def triangle_weights(point,triangle):
    """Double-precision closest convex coordinates, including edge hits."""
    t=np.asarray(triangle,dtype=float);p=np.asarray(point,dtype=float)
    basis=np.stack([t[1]-t[0],t[2]-t[0]],axis=1)
    uv=np.linalg.lstsq(basis,p-t[0],rcond=None)[0]
    w=np.array([1-uv.sum(),uv[0],uv[1]])
    candidates=[]
    if np.min(w)>=0:candidates.append(w)
    for a,b in ((0,1),(1,2),(2,0)):
        delta=t[b]-t[a];den=float(delta@delta)
        u=np.clip((p-t[a])@delta/den,0,1) if den else 0.
        edge=np.zeros(3);edge[a]=1-u;edge[b]=u;candidates.append(edge)
    return min(candidates,key=lambda v:np.linalg.norm(v@t-p))


def mapped_guides(rest,source,faces,matrices):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    tree=BVHTree.FromPolygons(source[0].tolist(),faces.tolist(),all_triangles=True)
    indices=[];weights=[];offsets=[]
    for point in rest:
        hit,normal,index,distance=tree.find_nearest(Vector(point));tri=faces[index]
        w=triangle_weights(hit,source[0,tri])
        indices.append(tri);weights.append(w);offsets.append(point-w@source[0,tri])
    weights=np.array(weights);indices=np.array(indices);offsets=np.array(offsets)
    if not np.isfinite(weights).all() or np.min(weights)<-1e-4 or np.max(abs(weights.sum(1)-1))>1e-5:
        raise ValueError('Invalid lower guide barycentric mapping')
    guided=np.einsum('fnjk,nj->fnk',source[:,indices],weights)
    guided+=np.einsum('fij,nj->fni',matrices[:,:3,:3],offsets)
    if np.max(abs(guided[0]-rest))>2e-5:raise ValueError('Lower neutral mapping changed rest')
    return guided


def contact_union(data,frame,standing):
    import bpy,bmesh
    from wardrobe185_lower import world_points
    contacts=[];arrays=[]
    for name in ('pelvis','thighL','thighR') if standing else ('pelvis','thighL','thighR','seat'):
        p=world_points(data[name+'_points'],data[name+'_matrices'][frame-1]);f=data[name+'_faces'];arrays.append((p,f))
        mesh=bpy.data.meshes.new('Lower '+name);mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
        ob=bpy.data.objects.new('MF185_lower_contact_'+name,mesh);bpy.context.scene.collection.objects.link(ob);contacts.append(ob)
    union=contacts[0].copy();union.data=union.data.copy();bpy.context.scene.collection.objects.link(union)
    union.name='MF185_lower_initial_union';bpy.context.view_layer.objects.active=union
    for ob in contacts[1:]:
        mod=union.modifiers.new('Initial lower union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(union.data);bad=sum(not e.is_manifold for e in bm.edges)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(union.data);bm.free()
    for ob in contacts:bpy.data.objects.remove(ob,do_unlink=True)
    if bad:raise ValueError('Lower dressing union is not closed')
    union.hide_render=True
    return union,arrays


def condition(points,faces,union,volumes,pins):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe185_convex import convex_outside
    q=np.array(points,copy=True);mesh=union.data
    tree=BVHTree.FromPolygons([v.co[:] for v in mesh.vertices],[p.vertices[:] for p in mesh.polygons])
    inside=np.zeros(len(q),dtype=bool)
    for p,f in volumes:inside|=~convex_outside(q,p,f,tolerance=1e-7)
    moves=[]
    for i,point in enumerate(np.array(q,copy=True)):
        hit,normal,_,distance=tree.find_nearest(Vector(point))
        if inside[i] or distance<.004/SCALE:
            q[i]=np.array(hit+normal*(.005/SCALE))
        moves.append(float(np.linalg.norm(q[i]-point)*SCALE))
    outside=np.ones(len(q),dtype=bool)
    for p,f in volumes:outside&=convex_outside(q,p,f,tolerance=1e-7)
    edges=np.unique(np.sort(np.concatenate([faces[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    lengths=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)*SCALE
    cloth_tree=BVHTree.FromPolygons(q.tolist(),faces.tolist())
    crossings=[(a,b) for a,b in cloth_tree.overlap(cloth_tree) if a<b and not set(faces[a])&set(faces[b])]
    actor_crossings=cloth_tree.overlap(tree)
    report={'max_initial_move_m':max(moves),'max_waist_move_m':max(moves[i] for i in pins),
        'remaining_inside_vertices':int((~outside).sum()),'min_edge_m':float(lengths.min()),
        'nonadjacent_crossings':crossings,'actor_crossing_pairs':len(actor_crossings),
        'actor_crossing_cloth_faces':sorted(set(a for a,b in actor_crossings))}
    return q,report


def dress(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import WORKING_SHA
    from wardrobe185_lower_pattern import pattern
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    motion=BASE/'wardrobe185-lowercapture02/moving-source.npz';contact=BASE/'wardrobe185-lowercontact01/contact.npz'
    for p,h in ((source,WORKING_SHA),(motion,SOURCE_SHA),(contact,CONTACT_SHA)):
        if digest(p)!=h:raise ValueError('Unbound lower dressing input')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    rest,faces,pins=pattern()
    with np.load(motion,allow_pickle=False) as data:
        guided=mapped_guides(rest,data['guide'],data['guide_faces'],data['pelvis_matrices'])
    with np.load(contact,allow_pickle=False) as data:contacts={k:data[k] for k in data.files}
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;old=bpy.data.objects['MF_fit_tunic_173_visible'];old.hide_render=True
    # Retired tunic toggles were fitted to the replaced old tunic, not this
    # upper shirt. Record them; do not confuse them with the functional buckle.
    retired=[]
    for ob in scene.objects:
        if ob.name.startswith('MF_173_tunic_toggle_'):
            retired.append({'name':ob.name,'was_visible':not ob.hide_render,'materials':[m.name for m in ob.data.materials]})
            ob.hide_render=True
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.use_persistent_data=True
    records={};layouts={};failures=[]
    for frame,label in ((1,'standing'),(169,'mounted')):
        scene.frame_set(frame);bpy.context.view_layer.update();union,volumes=contact_union(contacts,frame,frame==1)
        p,report=condition(guided[frame-1],faces,union,volumes,pins);records[label]=report;layouts[label]=p
        np.savez_compressed(out/(label+'-contact.npz'),points=np.array([v.co[:] for v in union.data.vertices]),
            **{'volume_'+str(i)+'_points':v[0] for i,v in enumerate(volumes)},
            **{'volume_'+str(i)+'_faces':v[1] for i,v in enumerate(volumes)})
        np.savez_compressed(out/'initial-layout.npz',rest=rest,faces=faces,guided=guided,
            pin_indices=np.array(list(pins)),pin_weights=np.array(list(pins.values())),**layouts)
        (out/'admission.json').write_text(json.dumps(records,indent=2)+'\n')
        if report['remaining_inside_vertices'] or report['nonadjacent_crossings'] or report['actor_crossing_pairs'] or report['min_edge_m']<.001:
            failures.append(label+': lower starting cut not admissible')
        if report['max_initial_move_m']>.10 or report['max_waist_move_m']>.015:
            failures.append(label+': lower cut requires construction or proxy reconsideration')
        mesh=bpy.data.meshes.new('185 coarse vented tunic');mesh.from_pydata(p.tolist(),[],faces.tolist());mesh.update()
        ob=bpy.data.objects.new('MF185_lower_dressing',mesh);scene.collection.objects.link(ob)
        for mat in old.data.materials:mesh.materials.append(mat)
        attr=mesh.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',rest.astype(np.float32).ravel())
        for poly in mesh.polygons:poly.use_smooth=True
        solid=ob.modifiers.new('Diagnostic cloth thickness','SOLIDIFY');solid.thickness=.006
        for horse in scene.objects:
            if horse.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):horse.hide_render=frame==1
        for angle,view in ((0,'front'),(90,'left'),(180,'rear')):
            fit_render(out,label+'-'+view,angle,(0,-.2,-6.5),7.,(640,640))
        ob.hide_render=True;bpy.data.objects.remove(union,do_unlink=True)
    check_protected()
    (out/'result.json').write_text(json.dumps({'working_sha256':WORKING_SHA,'motion_sha256':SOURCE_SHA,'contact_sha256':CONTACT_SHA,
        'layout_sha256':digest(out/'initial-layout.npz'),'retired_unattached_old_tunic_toggles':retired,
        'protected_exact':True,'visual_gate':'NOT_RUN','admission':'FAIL' if failures else 'PASS',
        'failures':failures,'scope':'Initial cloth dressing, no dynamic or final-looking garment claim'},indent=2)+'\n')
    if failures:raise ValueError('; '.join(failures))
