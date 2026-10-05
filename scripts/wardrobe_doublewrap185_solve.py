"""Reviewed static drape proof on fixed section-authored double courses.

Uses the conventional computational cloth profile verified by contact05.
This is not a physical textile calibration or a final production asset.
"""
import json
from pathlib import Path

import numpy as np


def inside(tree, point):
    """Parity, rather than a nearest polygon normal at concave corners."""
    from mathutils import Vector
    votes=[]
    for axis in ((1,.231,.117),(-.173,1,.319),(.271,-.133,1)):
        direction=Vector(axis).normalized();start=point.copy();hits=0
        for _ in range(128):
            hit,_,_,_=tree.ray_cast(start,direction,30.)
            if hit is None:break
            hits+=1;start=hit+direction*1e-4
        else:raise ValueError('Unresolved closed-contact parity')
        votes.append(hits%2)
    if len(set(votes))!=1:raise ValueError('Ambiguous initial closed-contact interior')
    return bool(votes[0])


def volumecheck(out):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    path=base.BASE/'wardrobe185-fitcheck01/conditioning.npz'
    if base.digest(path)!='87f3c985a976733212b2967cb0603d0181402e49320c620e3bdd03318fcf1205':raise ValueError('Contact source mismatch')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(path,allow_pickle=False) as d:p=d['contact_points'];f=d['contact_faces'];raw=d['raw']
    mesh=bpy.data.meshes.new('audit');mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    report={'vertices':len(p),'faces':len(f),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
        'boundary_edges':sum(e.is_boundary for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)}
    bm.free()
    tree=BVHTree.FromPolygons(p.tolist(),f.tolist());ambiguous=[];buried=[]
    for i,point in enumerate(raw):
        q=Vector(point);h,n,_,dist=tree.find_nearest(q)
        try:within=inside(tree,q)
        except ValueError:
            ambiguous.append({'index':i,'point':point.tolist(),'nearest_distance':dist,'nearest_normal':list(n)});continue
        if within:buried.append({'index':i,'point':point.tolist(),'distance':dist})
    report.update({'ambiguous':ambiguous,'interior':buried})
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items()}),flush=True)


def settle(out):
    import bpy
    from mathutils import Matrix,Vector
    import wardrobe_doublewrap185 as recipe
    import wardrobe_motion178 as base
    import wardrobe_motion178_controls as controls
    import wardrobe_studio as studio
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl180_dynamics import collision_snapshot
    from wardrobe_shawl180_assembly import union_contact
    from wardrobe_shawl179 import screens
    from wardrobe_refinement import tree_for
    from wardrobe_shawl180 import measures
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected()
    rig,mats,_=base.clean_foundation();dress_actor(rig);repair(rig,'repair04')
    scale=bpy.context.scene.unit_settings.scale_length
    with np.load(recipe.HEAD,allow_pickle=False) as d:hp=d['frames'][-1].copy();hf=d['faces'].copy()
    points=[hp];faces=[hf];counts=[len(hp)];offset=len(hp)
    for layer in (0,1):
        p,f=recipe.course(layer,revised=3)
        points.append(p);faces.append(f+offset);counts.append(len(p));offset+=len(p)
    p=np.concatenate(points);f=np.concatenate(faces)
    raw=p.copy()
    contacts=collision_snapshot(separate=True,closed=True)
    # Do not inflate a fine voxel surface beyond its cell width: that can
    # fold nearby surfaces through one another. Solver thickness is separate.
    contact=union_contact(contacts,margin=0 if out.name.endswith(('settle02','settle03')) else .055)
    tree=tree_for(contact)
    # Initial conditioning against a closed OUTER contact volume only. This
    # is bounded, recorded, and never applied after the simulation.
    distances=[];interior=[]
    for i,point in enumerate(p):
        q=Vector(point)
        if out.name.endswith(('fitcheck02','settle02','settle03')):
            h,n,_,distance=tree.find_nearest(q)
            within=inside(tree,q);interior.append(within)
            if within or distance<.035:
                direction=(h-q) if within else (q-h)
                if direction.length<1e-7:direction=n
                direction.normalize();q=h+direction*.035
        else:
            for _ in range(5):
                h,n,_,_=tree.find_nearest(q)
                signed=(q-h).dot(n)
                if signed>=.035:break
                q+=n*(.035-signed)
        distances.append((q-Vector(point)).length);p[i]=q[:]
    order=np.argsort(distances)[-24:][::-1]
    conditioning={'maximum':max(distances),'interior_count':sum(interior),'quantiles':np.quantile(distances,[0,.5,.9,.99,1]).tolist(),
        'worst':[{'index':int(i),'raw':raw[i].tolist(),'corrected':p[i].tolist(),'distance':distances[i]} for i in order]}
    (out/'conditioning.json').write_text(json.dumps(conditioning,indent=2)+'\n')
    np.savez_compressed(out/'conditioning.npz',raw=raw,corrected=p,faces=f,
        contact_points=np.array([v.co[:] for v in contact.data.vertices]),
        contact_faces=np.array([poly.vertices[:] for poly in contact.data.polygons]))
    if out.name.endswith(('fitcheck01','fitcheck02')):
        print(json.dumps(conditioning),flush=True)
        return
    if max(distances)>.30:raise ValueError('Construction enters outer support by more than 3.7cm')
    print('185 initial conditioning',max(distances),sum(d>1e-5 for d in distances),flush=True)
    mesh=bpy.data.meshes.new('MF185_drape');mesh.from_pydata((p*scale).tolist(),[],f.tolist());mesh.update()
    cloth=bpy.data.objects.new('MF178_live_solver185',mesh);bpy.context.scene.collection.objects.link(cloth);cloth.hide_render=True
    pin=cloth.vertex_groups.new(name='support');pins={}
    # Small crown contact patch. Headfall lower sides/hem stay free.
    for i,q in enumerate(p[:counts[0]]):
        if q[2]>.96 and .25<q[1]<.85 and abs(q[0])<.5:pins[i]=1.
    for layer in (0,1):
        start=counts[0]+layer*counts[1]
        for row in (23,24,25,71,72,73):
            for col in (4,5,6,7,8):pins[start+row*17+col]=1. if col==6 else .6
    for i,w in pins.items():pin.add([i],w,'REPLACE')
    # Decimated single closed collision volume; original visible surfaces
    # are untouched and absent from this solver's explicit collection.
    bpy.context.view_layer.objects.active=contact
    dec=contact.modifiers.new('Contact-only reduction','DECIMATE');dec.ratio=min(1,12000/len(contact.data.polygons))
    bpy.ops.object.modifier_apply(modifier=dec.name)
    for v in contact.data.vertices:v.co*=scale
    contact.data.update();contact.modifiers.new('Metric collision','COLLISION')
    contact.collision.thickness_outer=.0015;contact.collision.cloth_friction=15
    domain=bpy.data.collections.new('MF185_explicit_contacts');bpy.context.scene.collection.children.link(domain);domain.objects.link(contact)
    mod=recipe.cloth_settings(cloth,1,domain)
    mod.settings.mass=.3;mod.settings.air_damping=.2
    mod.settings.bending_stiffness=.05;mod.settings.quality=12
    if out.name.endswith('settle03'):
        mod.settings.tension_stiffness=200
        mod.settings.compression_stiffness=200
        mod.settings.shear_stiffness=100
        mod.settings.quality=24
    mod.point_cache.frame_end=96
    bpy.context.scene.gravity=(0,0,-9.81);bpy.context.scene.render.fps=24
    frames=[]
    with controls.render_geometry_paused():
        for frame in range(1,97):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices])/scale;ev.to_mesh_clear()
            if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>50:raise ValueError('Invalid drape')
            frames.append(q)
            if frame%12==0:print('185 whole drape',frame,flush=True)
    frames=np.array(frames)
    np.savez_compressed(out/'trajectory.npz',points=p,raw_points=raw,faces=f,frames=frames,
                        counts=np.array(counts),pin_indices=np.array(list(pins)),pin_weights=np.array(list(pins.values())))
    # Colour-separated construction screen, no cloth texture polish.
    offset=0
    for k,(count,rgb) in enumerate(zip(counts,((.06,.10,.18),(.16,.30,.27),(.27,.17,.08)))):
        fs=f[(f[:,0]>=offset)&(f[:,0]<offset+count)]-offset
        studio.panel('MF185_draped_'+str(k),frames[-1,offset:offset+count].tolist(),fs.tolist(),recipe.color('stage'+str(k),rgb),.012,1)
        offset+=count
    screens(out,(96,))
    base.check_protected()
    report=measures(p,f,{1:frames[0],48:frames[47],96:frames[-1]},scale)
    report.update({'protected_exact':True,'visual_gate':'NOT_RUN','moving_gate':'NOT_RUN',
        'computational_vertex_mass':.3,'mass_is_physical_calibration':False,'self_collision':True,
        'tension_stiffness':mod.settings.tension_stiffness,'compression_stiffness':mod.settings.compression_stiffness,
        'shear_stiffness':mod.settings.shear_stiffness,'substeps':mod.settings.quality,
        'pin_count':len(pins),'vertex_count':len(p),'max_initial_conditioning_native':max(distances),
        'post_solve_projection':False,'source_sha256':base.SOURCE_SHA,'head_input_sha256':recipe.HEAD_SHA})
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
