"""Clean lower-tunic dressing before a free-cloth performance solve."""
import json
from pathlib import Path
import numpy as np

SOURCE_SHA='20b06605833f46561db93ba3c25ef27e934b96abe39854958e8f1b101a284d0e'
CONTACT_SHA='577b9e0ee50a0350424d64aecf25b4965637c2bf23d6b8e9e6b9f878a377e0b5'
SURFACE_SHA='03c1143677e97891fecb66bc09a3ac9212db98c7fee63a557bc64b0b280124e8'
WAIST_SURFACE_SHA='45a5bb64fac88d648b212e112518554601d231b8c6cbd94c77d974fddf86651f'
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


def mounted_dressing(rest,guided):
    """Smooth initial layout over lap/back, never a prescribed animation."""
    t=np.clip((-5.35-rest[:,2])/2.10,0,1)
    theta=np.arctan2(rest[:,0]/(1.42+.57*t),(rest[:,1]-.085-.025*t)/(1.14+.25*t))
    cosine=np.cos(theta);p=np.array(rest,copy=True)
    p[:,0]=(1.42+1.20*t)*np.sin(theta)
    p[:,1]=.085+(1.14+1.40*t)*cosine
    p[:,2]=-5.35-2.10*t*(1-.72*abs(cosine))
    blend=np.clip((t-.10)/.20,0,1);blend=blend*blend*(3-2*blend)
    return guided*(1-blend[:,None])+p*blend[:,None]


def standing_dressing(rest):
    """Small initial air gap below the fixed waist; gravity will settle it."""
    p=np.array(rest,copy=True);t=np.clip((-5.35-rest[:,2])/2.10,0,1)
    ease=np.clip((t-.05)/.15,0,1);ease=ease*ease*(3-2*ease)
    p[:,0]*=1+.09*ease
    center=.085+.025*t;p[:,1]=center+(p[:,1]-center)*(1+.09*ease)
    return p


def attachment_targets(points,indices,weights,clearance,local_offsets=None):
    tri=np.asarray(points)[:,np.asarray(indices)];w=np.asarray(weights)
    normal=np.cross(tri[:,:,1]-tri[:,:,0],tri[:,:,2]-tri[:,:,0]);norm=np.linalg.norm(normal,axis=2)
    if norm.min()<1e-10:raise ValueError('Degenerate moving waist support face')
    normal=normal/norm[:,:,None]
    position=np.einsum('fnjk,nj->fnk',tri,w)
    if local_offsets is None:return position+normal*clearance
    tangent=tri[:,:,1]-tri[:,:,0];tangent/=np.linalg.norm(tangent,axis=2)[:,:,None]
    across=np.cross(normal,tangent);offset=np.asarray(local_offsets)
    return position+tangent*offset[None,:,0,None]+across*offset[None,:,1,None]+normal*offset[None,:,2,None]


def supported_edge(rest,pins,contacts):
    """Sew the small supported band to fixed actual-body correspondence.

    Free cloth does not use this mapping. No framewise nearest-point clamp.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    points=contacts['waist_frames'];faces=contacts['waist_faces'];indices=[];weights=[];offsets=[]
    tree=BVHTree.FromPolygons(points[0].tolist(),faces.tolist(),all_triangles=True)
    for i in pins:
        hit,_,index,_=tree.find_nearest(Vector(rest[i]));tri=faces[index]
        w=triangle_weights(hit,points[0,tri]);triangle=points[0,tri]
        tangent=triangle[1]-triangle[0];tangent/=np.linalg.norm(tangent)
        normal=np.cross(tangent,triangle[2]-triangle[0]);normal/=np.linalg.norm(normal)
        across=np.cross(normal,tangent);delta=rest[i]-w@triangle
        offsets.append([float(delta@tangent),float(delta@across),max(float(delta@normal),.004/SCALE)])
        indices.append(tri);weights.append(w)
    targets=attachment_targets(points,indices,weights,.004/SCALE,offsets)
    max_move=float(np.linalg.norm(targets[0]-rest[list(pins)],axis=1).max()*SCALE)
    if max_move>.02:raise ValueError('Body-bound waist support requires more than 20mm initial refit: '+str(max_move))
    return targets,{'method':'Fixed actual-waist triangle correspondence; preserve designed garment offset in rotating local frame, minimum 4mm normal clearance',
        'max_neutral_refit_m':max_move,'free_vertices_mapped':False}


def support_preflight(targets,contacts,out):
    from wardrobe185_lower_surface import winding_numbers
    failures=[]
    for j,frame in enumerate(contacts['frame_ids']):
        for name in ('waist','pants'):
            w=winding_numbers(targets[j],contacts[name+'_frames'][j],contacts[name+'_faces'])
            count=int(np.sum(abs(w)>.5));ambiguous=int(np.sum(abs(w-np.rint(w))>1e-3))
            if count or ambiguous:failures.append({'frame':int(frame),'contact':name,'inside':count,'ambiguous':ambiguous})
    (out/'support-admission.json').write_text(json.dumps({'source_frames':len(targets),'failures':failures,
        'gate':'FAIL' if failures else 'PASS','scope':'Supported band vs actual waist and pants, not free-cloth or visual qualification'},indent=2)+'\n')
    if failures:raise ValueError('Moving lower support targets fail actual contact preflight')


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
    surface='frame_ids' in data
    names=(('pants',) if standing else ('pants','horse','saddle','pad')) if surface else (('pelvis','thighL','thighR') if standing else ('pelvis','thighL','thighR','seat'))
    if 'waist_frames' in data:names=names+('waist',)
    for name in names:
        p=data[name+'_frames'][list(data['frame_ids']).index(frame)] if surface else world_points(data[name+'_points'],data[name+'_matrices'][frame-1])
        f=data[name+'_faces'];arrays.append((p,f))
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


def condition(points,faces,union,volumes,pins,convex=True):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe185_convex import convex_outside
    from wardrobe185_lower_surface import winding_numbers
    q=np.array(points,copy=True);mesh=union.data
    tree=BVHTree.FromPolygons([v.co[:] for v in mesh.vertices],[p.vertices[:] for p in mesh.polygons])
    mesh.calc_loop_triangles();vp=np.array([v.co[:] for v in mesh.vertices]);vf=np.array([t.vertices[:] for t in mesh.loop_triangles])
    def contained(points):
        w=winding_numbers(points,vp,vf)
        if np.max(abs(w-np.rint(w)))>1e-3:raise ValueError('Nonintegral lower contact winding requires review')
        return abs(w)>.5
    inside=np.zeros(len(q),dtype=bool)
    if convex:
        for p,f in volumes:inside|=~convex_outside(q,p,f,tolerance=1e-7)
    else:inside=contained(q)
    moves=[]
    for i,point in enumerate(np.array(q,copy=True)):
        hit,normal,_,distance=tree.find_nearest(Vector(point))
        if inside[i] or distance<.004/SCALE:
            q[i]=np.array(hit+normal*(.005/SCALE))
        moves.append(float(np.linalg.norm(q[i]-point)*SCALE))
    outside=np.ones(len(q),dtype=bool)
    if convex:
        for p,f in volumes:outside&=convex_outside(q,p,f,tolerance=1e-7)
    else:outside=~contained(q)
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
    waist=out.name.endswith(('lowerdress08','lowerdress09'))
    surface=waist or out.name.endswith(('lowerdress05','lowerdress06','lowerdress07'))
    if surface:contact=BASE/'wardrobe185-lowersurface02/surfaces.npz'
    contact_sha=SURFACE_SHA if surface else CONTACT_SHA
    if waist:contact=BASE/'wardrobe185-waistcontact01/contact.npz';contact_sha=WAIST_SURFACE_SHA
    for p,h in ((source,WORKING_SHA),(motion,SOURCE_SHA),(contact,contact_sha)):
        if digest(p)!=h:raise ValueError('Unbound lower dressing input')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    rest,faces,pins=pattern()
    with np.load(motion,allow_pickle=False) as data:
        guided=mapped_guides(rest,data['guide'],data['guide_faces'],data['pelvis_matrices'])
    with np.load(contact,allow_pickle=False) as data:contacts={k:data[k] for k in data.files}
    support=None
    if waist:
        support,support_record=supported_edge(rest,pins,contacts)
        (out/'support-binding.json').write_text(json.dumps(support_record,indent=2)+'\n')
        support_preflight(support,contacts,out)
        for j,frame in enumerate(contacts['frame_ids']):guided[frame-1,list(pins)]=support[j]
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
        initial=mounted_dressing(rest,guided[frame-1]) if surface and frame!=1 else guided[frame-1]
        if out.name.endswith(('lowerdress07','lowerdress08','lowerdress09')) and frame==1:initial=standing_dressing(rest)
        if waist:initial[list(pins)]=guided[frame-1,list(pins)]
        p,report=condition(initial,faces,union,volumes,pins,convex=not surface);records[label]=report;layouts[label]=p
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
    (out/'result.json').write_text(json.dumps({'working_sha256':WORKING_SHA,'motion_sha256':SOURCE_SHA,'contact_sha256':contact_sha,
        'layout_sha256':digest(out/'initial-layout.npz'),'retired_unattached_old_tunic_toggles':retired,
        'protected_exact':True,'visual_gate':'NOT_RUN','admission':'FAIL' if failures else 'PASS',
        'failures':failures,'scope':'Initial cloth dressing, no dynamic or final-looking garment claim'},indent=2)+'\n')
    if failures:raise ValueError('; '.join(failures))
