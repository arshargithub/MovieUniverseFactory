"""Fixed wardrobe170 tailoring operations on an immutable static assembly.

No external paths, arbitrary expressions or executable job payloads admitted.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wardrobe_riding_fit import BASE, BODY, BODY_SHA, HORSE, HORSE_SHA, digest

SOURCE = BASE / 'wardrobe169-seal01/dressed-fit.blend'
SOURCE_SHA = '07d1989584dc44e2d1253364147dbd830ee67f7e7ad05c5ce4ed6ebff88c67ab'
OPERATIONS = ('inspect01', 'inspect02', 'preview01', 'preview02', 'preview03', 'preview04', 'preview05', 'preview06', 'preview07', 'preview08', 'preview09', 'preview10', 'preview11', 'preview12', 'preview13', 'preview14', 'preview15', 'preview16', 'preview17', 'seal01', 'verify01', 'seal02', 'verify02', 'seal03', 'verify03')


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Only fixed reviewed wardrobe operations admitted')
    for path, expected in ((SOURCE, SOURCE_SHA), (BODY, BODY_SHA), (HORSE, HORSE_SHA)):
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError('Pinned wardrobe input mismatch')
    out = BASE / ('wardrobe170-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite wardrobe evidence')
    if job['operation'].startswith('verify'):
        selected = BASE / ('wardrobe170-seal'+job['operation'][-2:])
        result = json.loads((selected / 'result.json').read_text())
        path = selected / 'dressed-fit.blend'
        if path.is_symlink() or digest(path) != result['native_sha256']:
            raise ValueError('Selected wardrobe hash mismatch')
    return out


def neutral(rig):
    from mathutils import Matrix
    import bpy
    for bone in rig.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def inspect(out):
    import bpy
    import bmesh
    from wardrobe_riding_fit import neutral_surface
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    body = bpy.data.objects['MF_studio_adult_body']
    rig = bpy.data.objects['MF_body156_fit_rig']
    neutral(rig)
    rows = []
    for ob in bpy.context.scene.objects:
        if not ob.hide_render and ob.type == 'MESH':
            ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            me = ev.to_mesh()
            pts = [ob.matrix_world @ v.co for v in me.vertices]
            row = {'name': ob.name, 'vertices': len(pts), 'bounds': [[min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]],
                   'modifiers': [(m.name, m.type) for m in ob.modifiers]}
            if 'horse' in ob.name.lower() or 'tail' in ob.name.lower() or 'headscarf' in ob.name:
                bm = bmesh.new(); bm.from_mesh(me)
                pending = set(bm.verts); components = []
                while pending:
                    group = {pending.pop()}; front = set(group)
                    while front:
                        adjacent = {e.other_vert(v) for v in front for e in v.link_edges if e.other_vert(v) in pending}
                        pending -= adjacent; group |= adjacent; front = adjacent
                    points = [ob.matrix_world @ v.co for v in group]
                    components.append({'count': len(group), 'bounds': [[min(p[k] for p in points) for k in range(3)], [max(p[k] for p in points) for k in range(3)]]})
                bm.free(); row['components'] = sorted(components, key=lambda c: -c['count'])[:15]
            ev.to_mesh_clear(); rows.append(row)
    surface = neutral_surface(body)
    result = {'visible_meshes': rows, 'body_neutral_bounds': [[min(p[k] for p, _ in surface) for k in range(3)], [max(p[k] for p, _ in surface) for k in range(3)]],
              'scene_units': {'system': bpy.context.scene.unit_settings.system, 'scale_length': bpy.context.scene.unit_settings.scale_length},
              'source_pins_unchanged': all(digest(p) == h for p, h in ((SOURCE,SOURCE_SHA),(BODY,BODY_SHA),(HORSE,HORSE_SHA)))}
    (out / 'inspection.json').write_text(json.dumps(result, indent=2) + '\n')


def tree_for(ob):
    import bpy
    from mathutils.bvhtree import BVHTree
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    tree = BVHTree.FromPolygons([ob.matrix_world @ v.co for v in me.vertices], [tuple(f.vertices) for f in me.polygons])
    ev.to_mesh_clear()
    return tree


def tailor(body, rig):
    """Reduce garment ease, never the accepted underlying anatomy."""
    import bpy
    from mathutils import Vector
    tunic = bpy.data.objects['MF_fit_tunic']
    tree = tree_for(body)
    follow = tunic.modifiers['Accepted evaluated-body surface support']
    bpy.context.view_layer.objects.active = tunic
    tunic.hide_set(False); tunic.select_set(True)
    bpy.ops.object.surfacedeform_bind(modifier=follow.name)
    assert not follow.is_bound
    changed = 0
    for v in tunic.data.vertices:
        p = tunic.matrix_world @ v.co
        hit, normal, _, distance = tree.find_nearest(p)
        if hit is None: continue
        # Upper sleeves/waist follow skin with modest practical ease. Retain
        # lower tunic shape and vents rather than shrink-wrapping the crotch.
        blend = min(1., max(0., (p.z + 6.65) / 1.0))
        if abs(p.x) > 2.1: blend = 1.
        ease = .10 if abs(p.x) > 1.8 else .085
        target = hit + normal * ease
        if distance < .95 and blend > 0:
            v.co = tunic.matrix_world.inverted() @ p.lerp(target, .92 * blend)
            changed += 1
    tunic.data.update(); bpy.context.view_layer.update()
    bpy.ops.object.surfacedeform_bind(modifier=follow.name)
    assert follow.is_bound
    tunic.modifiers['Static tailoring seam fairing'].iterations = 35
    tunic.modifiers['Explicit static posed body clearance'].offset = .13
    fair=tunic.modifiers.new('Posed fabric surface fairing','SMOOTH');fair.factor=.7;fair.iterations=8
    clearance=tunic.modifiers.new('Final posed fabric coverage','SHRINKWRAP')
    clearance.target=body;clearance.wrap_method='NEAREST_SURFACEPOINT';clearance.wrap_mode='OUTSIDE_SURFACE';clearance.offset=.11
    pants = bpy.data.objects['MF_fit_trousers']
    # Shell was offset .18; remove .12 of ease using the matching neutral skin.
    for v in pants.data.vertices:
        p = pants.matrix_world @ v.co; hit, normal, _, distance = tree.find_nearest(p)
        if hit is not None and distance < .7:
            v.co = pants.matrix_world.inverted() @ (hit + normal * .07)
    pants.data.update()
    armature=next(m for m in pants.modifiers if m.type=='ARMATURE');pants.modifiers.remove(armature)
    follower=pants.modifiers.new('Trousers evaluated-body pose support','SURFACE_DEFORM');follower.target=bpy.data.objects['MF_fit_pose_skin_support']
    bpy.context.view_layer.objects.active=pants;pants.hide_set(False);pants.select_set(True)
    while list(pants.modifiers).index(follower)>0:bpy.ops.object.modifier_move_up(modifier=follower.name)
    bpy.context.view_layer.update();bpy.ops.object.surfacedeform_bind(modifier=follower.name);assert follower.is_bound
    return {'tunic_vertices_refitted': changed, 'tunic_clearance_scene_units': .13,
            'trouser_ease_scene_units': .07, 'body_geometry_changed': False}


def cloth_character():
    """Major material/panel character, no new cultural insignia or jewelry."""
    import bpy
    from character_assembly import material
    tunic = bpy.data.objects['MF_fit_tunic']
    base = material('MF_170_indigo_woven', (.018,.043,.078))
    trim = material('MF_170_muted_indigo_bound_edges', (.043,.09,.12))
    panel = material('MF_170_deep_indigo_tailored_panel', (.011,.025,.042))
    scarf = material('MF_170_soft_indigo_scarf', (.027,.063,.095))
    for mat in (base, trim, panel, scarf):
        nodes = mat.node_tree.nodes; links = mat.node_tree.links
        bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        bsdf.inputs['Roughness'].default_value = .82
        bsdf.inputs['Sheen Weight'].default_value = .14
        noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 35
        noise.inputs['Detail'].default_value = 2
        bump = nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .12; bump.inputs['Distance'].default_value = .018
        links.new(noise.outputs['Fac'], bump.inputs['Height']); links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    tunic.data.materials.clear()
    for mat in (base, trim, panel): tunic.data.materials.append(mat)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(tunic.data); bm.verts.ensure_lookup_table(); bm.verts.index_update()
    rim = {v.index for e in bm.edges if e.is_boundary for v in e.verts}
    bm.free()
    for face in tunic.data.polygons:
        p = face.center
        if any(i in rim for i in face.vertices): face.material_index = 1
        elif p.y < -.55 and abs(p.x) < .55 and p.z > -5.8: face.material_index = 2
        else: face.material_index = 0
    hood = bpy.data.objects['MF_fit_indigo_headscarf']
    hood.data.materials.clear(); hood.data.materials.append(scarf)
    bpy.data.objects['MF_fit_diagonal_scarf'].data.materials.clear()
    bpy.data.objects['MF_fit_diagonal_scarf'].data.materials.append(scarf)
    # The original thick neckline roll competed with the open drape. Retain
    # its native diagnostic history, hide only this derivative's redundant roll.
    bpy.data.objects['MF_fit_bound_neckline'].hide_render = True
    return {'vocabulary': 'tonal indigo center panel, bound edges, soft scarf and functional brown harness', 'new_insignia_or_jewelry': False}


def fit_scarf():
    """Adapt actual donor topology to the groom/shoulders; keep open forehead."""
    import bpy, bmesh
    from mathutils.bvhtree import BVHTree
    hood = bpy.data.objects['MF_fit_indigo_headscarf']
    # Actual groom envelope, not the head's painted hair or a generic sphere.
    hull = bmesh.new()
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        ob = bpy.data.objects[name]; ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        stride = max(1, len(ev.data.points)//2000)
        for p in list(ev.data.points)[::stride]: hull.verts.new(ob.matrix_world @ p.position)
    bmesh.ops.convex_hull(hull, input=list(hull.verts), use_existing_faces=False)
    hull.verts.ensure_lookup_table(); hull.verts.index_update()
    top=max(v.co.z for v in hull.verts)
    vertices=[tuple(v.co) for v in hull.verts];faces=[tuple(v.index for v in f.verts) for f in hull.faces]
    tree = BVHTree.FromPolygons(vertices,faces); hull.free()
    from character_assembly import mesh
    proxy=mesh('MF_170_temporary_groom_collision',vertices,faces,hood.data.materials[0]);proxy.hide_render=True
    proxy.modifiers.new('Static drape groom collision','COLLISION');proxy.collision.thickness_outer=.035
    cloth_tree = tree_for(bpy.data.objects['MF_fit_tunic'])
    # Donor lower folds remain unsuitable after depth-only fitting. Do not
    # repeat another nearest-point patch. Author one continuous lightweight
    # open veil from measured hair/garment envelopes and broad vertical folds.
    hood.hide_render=True
    authored_open_hood(tree,cloth_tree,hood.data.materials[0],top)
    bpy.data.objects.remove(proxy,do_unlink=True)
    # Front donor wrap is separate from the hood. Refitting its single
    # surface avoids a thick collar/plate and preserves shoulder coverage.
    shawl=bpy.data.objects['MF_fit_diagonal_scarf'];shawl.hide_render=True
    authored_wrap(hood.data.materials[0])
    return {'donor_vertices_adapted':0,'hair_geometry_changed':False,'hair_clearance_scene_units':.14,'scope':'Authored open veil with scoped neutral static cloth settling, frozen before posing; not dynamic cloth qualification; rejected donor retained hidden'}


def authored_open_hood(hair_tree,cloth_tree,mat,top):
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    rig=bpy.data.objects['MF_body156_fit_rig']
    points=[];faces=[];nu=65;nv=17
    for j in range(nv):
        v=j/(nv-1)
        for i in range(nu):
            theta=-2.8+5.6*i/(nu-1);a=abs(theta);sign=-1 if theta<0 else 1
            # A loose crown-to-shoulder scarf strip, not a closed hood/bag.
            # It leaves the rear hair visible and cannot form the rejected
            # circumferential nape roll. Side ends settle onto the shoulders.
            if a<=math.pi/2:
                x=1.35*math.sin(theta);z=.1+(top+.02)*math.cos(theta)
            else:
                x=sign*(1.35+.34*(a-math.pi/2));z=.1-2.1*(a-math.pi/2)
            p=Vector((x,.32+v*(.65+.18*min(1,a)),z))
            if z>-.9:
                hit,normal,_,distance=hair_tree.find_nearest(p)
                if hit is not None and distance<.7:p=hit+normal*.12
            p.z+=.025*math.sin(4*theta+3*v)
            points.append(tuple(p))
    for j in range(nv-1):
        for i in range(nu-1):
            a=j*nu+i;faces.append((a,a+1,a+nu+1,a+nu))
    ob=mesh('MF_170_authored_open_scarf',points,faces,mat)
    settle_open_veil(ob,nu,nv)
    smooth=ob.modifiers.new('Continuous major scarf drape','SMOOTH');smooth.factor=.6;smooth.iterations=5
    ob.modifiers.new('Soft scarf surface','SUBSURF').levels=2
    ob.modifiers.new('Thin cloth edge','SOLIDIFY').thickness=.02
    rest=rig.matrix_world@rig.data.bones['chest'].matrix_local
    attach=ob.constraints.new('CHILD_OF');attach.target=rig;attach.subtarget='chest';attach.inverse_matrix=rest.inverted()


def settle_open_veil(ob,nu,nv):
    """Construction-only low-resolution settling; no production physics rig."""
    import bpy
    source=bpy.data.objects['MF_fit_tunic']
    proxy=source.copy();proxy.data=source.data.copy();proxy.name='MF_170_temporary_tunic_collision'
    bpy.context.scene.collection.objects.link(proxy);proxy.hide_render=True
    decimate=proxy.modifiers.new('Static drape inexpensive collision envelope','DECIMATE');decimate.ratio=.10
    proxy.modifiers.new('Static drape body collision','COLLISION');proxy.collision.thickness_outer=.035
    pin=ob.vertex_groups.new(name='Static crown attachment')
    pin.add([j*nu+i for j in range(nv) for i in range(nu//2-2,nu//2+3)],1.,'REPLACE')
    cloth=ob.modifiers.new('Construction-only neutral veil settling','CLOTH')
    cloth.settings.quality=5;cloth.settings.mass=.25
    cloth.settings.tension_stiffness=12;cloth.settings.compression_stiffness=12
    cloth.settings.shear_stiffness=6;cloth.settings.bending_stiffness=.08
    cloth.settings.vertex_group_mass=pin.name
    cloth.collision_settings.distance_min=.035
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=36
    original_frame=bpy.context.scene.frame_current
    for frame in range(1,37):
        bpy.context.scene.frame_set(frame)
        evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        temporary=evaluated.to_mesh();evaluated.to_mesh_clear()
    evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());temporary=evaluated.to_mesh()
    coords=[v.co.copy() for v in temporary.vertices];evaluated.to_mesh_clear()
    assert len(coords)==len(ob.data.vertices)
    ob.modifiers.remove(cloth)
    for vertex,co in zip(ob.data.vertices,coords):vertex.co=co
    ob.data.update();bpy.data.objects.remove(proxy,do_unlink=True)
    bpy.context.scene.frame_set(original_frame)


def authored_wrap(mat):
    """One draped, asymmetric scarf end; no concentric collar-ring plates."""
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    from wardrobe_riding_fit import bind_torso
    tunic=bpy.data.objects['MF_fit_tunic'];tree=tree_for(tunic)
    anchors=[Vector(p) for p in [(-1.28,.15,-1.45),(-1.67,-.35,-2.0),(-1.05,-1.0,-2.45),(-.25,-1.30,-2.90),(.65,-1.15,-3.40),(1.37,-.60,-3.85)]]
    points=[];faces=[];n=8
    for i in range(len(anchors)-1):
        p0=anchors[max(0,i-1)];p1=anchors[i];p2=anchors[i+1];p3=anchors[min(len(anchors)-1,i+2)]
        for j in range(12):
            t=j/12.;s=(i+t)/(len(anchors)-1)
            center=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
            tangent=(p2-p1).normalized();normal=Vector((center.x,center.y-.18,0)).normalized()
            across=tangent.cross(normal).normalized();width=.40+.23*math.sin(math.pi*s)
            for k in range(n):
                v=k/(n-1);p=center+across*(v-.5)*width
                hit,norm,_,distance=tree.find_nearest(p)
                if hit is not None and distance<.8:
                    p=hit+norm*(.065+.035*math.sin(math.pi*v)*math.sin(3*math.pi*s+.6)**2)
                points.append(tuple(p))
    rows=len(points)//n
    for i in range(rows-1):
        for j in range(n-1):
            a=i*n+j;faces.append((a,a+n,a+n+1,a+1))
    ob=mesh('MF_170_asymmetric_scarf_end',points,faces,mat)
    # Garment support owns the moving cloth surface, not a rigid chest plate.
    support=ob.modifiers.new('Static scarf evaluated-body support','SURFACE_DEFORM')
    support.target=bpy.data.objects['MF_fit_pose_skin_support']
    bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.context.view_layer.update()
    bpy.ops.object.surfacedeform_bind(modifier=support.name);assert support.is_bound
    ob.modifiers.new('Soft major scarf folds','SUBSURF').levels=2
    ob.modifiers.new('Scarf fabric thickness','SOLIDIFY').thickness=.025


def repair_tail(out, inspect_only=False):
    """Single static tail: source pins remain immutable; no gait claim."""
    import bpy
    from mathutils import Vector
    horse=bpy.data.objects['MF_fit_horse']; tail=bpy.data.objects['MF_fit_Full Bushy Flowing Horse Tail']
    points=[horse.matrix_world@v.co for v in horse.data.vertices]
    bins=[]
    for y in (4.,5.,6.,7.,8.,9.):
        pts=[p for p in points if y<=p.y<y+1 and abs(p.x)<.7]
        bins.append({'y_min':y,'count':len(pts),'z_range':[min(p.z for p in pts),max(p.z for p in pts)] if pts else None})
    result={'horse_rear_slices':bins,'horse_materials':[m.name if m else None for m in horse.data.materials],
            'horse_groups':[g.name for g in horse.vertex_groups],
            'baked_group_samples':[(v.index,[(g.group,g.weight) for g in v.groups]) for v in horse.data.vertices if v.groups][:3]}
    tail_groups={g.index:g.name for g in horse.vertex_groups if 'tail' in g.name.lower()}
    result['source_tail_groups']=tail_groups
    (out/'tail-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
    if inspect_only:return result
    # The evaluated native retains the author's component-selection group.
    # Remove exactly its tagged tail vertices in this private derivative,
    # never a guessed coordinate strip of the connected rump.
    import bmesh
    selection=horse.vertex_groups['tail'].index
    distal={g.index for g in horse.vertex_groups if g.name in ('DEF-tail.002','DEF-tail.003','DEF-tail.004','DEF-tail.005')}
    ids={v.index for v in horse.data.vertices if any((g.group==selection and g.weight>.5) or (g.group in distal and g.weight>.2) for g in v.groups)}
    assert ids and len(ids)<len(horse.data.vertices)*.1
    dock_points=[horse.matrix_world@horse.data.vertices[i].co for i in ids]
    root=min(dock_points,key=lambda p:p.y)
    bm=bmesh.new();bm.from_mesh(horse.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in ids],context='VERTS')
    boundaries=[e for e in bm.edges if e.is_boundary and all((horse.matrix_world@v.co-root).length<2. for v in e.verts)]
    assert boundaries, 'Inspect actual new tail aperture, never cap arbitrary horse holes'
    boundary_points=[horse.matrix_world@v.co for e in boundaries for v in e.verts]
    root=sum(boundary_points,Vector())/len(boundary_points)
    bmesh.ops.holes_fill(bm,edges=boundaries,sides=0)
    from static_tail_dock import soften_dock_surface,root_fibers
    soften_dock_surface(bm,horse.matrix_world,root)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(horse.data);bm.free()
    result['removed_original_tail_vertices']=len(ids);result['measured_original_dock_root']=list(root)
    inv=tail.matrix_world.inverted()
    for v in tail.data.vertices:
        p=tail.matrix_world@v.co
        s=min(1.,max(0.,(p.y-6.)/9.4))
        spread=.12+.70*math.sin(math.pi*s*.75)
        center=Vector((root.x,root.y+4.0*s,root.z-5.4*s**.80))
        residual=p.z-(-10.+3.9*s)
        new=Vector((center.x+(p.x-.10)*spread,center.y,center.z+residual*spread*.6))
        v.co=inv@new
    tail.data.update()
    # Small coherent dark dock core closes the groom's card roots. The
    # longitudinal hair geometry remains source-derived and separately named.
    from character_assembly import tube
    core=tube('MF_170_tail_dock',[(root.x,root.y-.08,root.z,.28,.28),
                                 (root.x,root.y+.25,root.z-.59,.24,.22),
                                 (root.x,root.y+.6,root.z-1.18,.10,.10)],tail.data.materials[0],detail=24)
    bm=bmesh.new();bm.from_mesh(core.data)
    bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(core.data);bm.free()
    result['dock_core']=core.name
    result['static_dock_fibers']=root_fibers(root)
    result['separate_flowing_tail_refitted']=True
    result['visible_tail']='Agent-authored volumetric native curve groom; refitted card groom/core retained hidden after flat-root failure; static only'
    return result


def render_views(out, full=False, rear_only=False):
    import bpy
    from wardrobe_riding_fit import fit_render, riding_pose, fit_static_contacts
    rig=bpy.data.objects['MF_body156_fit_rig']
    horse=[o for o in bpy.context.scene.objects if o.get('source_object')]
    horse_visible=[o for o in bpy.context.scene.objects if o.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_'))]
    states={o.name:o.hide_render for o in horse_visible}
    neutral(rig)
    for ob in horse_visible:ob.hide_render=True
    angles=[('rear',180),('side',90)] if rear_only else [('front',0),('side',90),('rear',180)] if full else [('front',0)]
    for label,angle in angles:fit_render(out,'standing-'+label,angle)
    fit_render(out,'head-scarf-quarter',-40,(0,.15,-.75),5.7,(720,800))
    if rear_only:return
    for ob in horse_visible:ob.hide_render=states[ob.name]
    riding_pose(rig);bpy.context.view_layer.update()
    leather=bpy.data.objects['MF_fit_waist_belt'].data.materials[0]
    fit_static_contacts(horse,rig,leather)
    fit_render(out,'mounted-side',90,(0,-1,-10),29,(1000,700))
    fit_render(out,'mounted-front-quarter',-40,(0,-1,-10),29,(540,900))
    if full:
        fit_render(out,'mounted-opposite-side',-90,(0,-1,-10),29,(1000,700))
        fit_render(out,'mounted-rear-quarter',140,(0,-1,-10),29,(540,900))
        fit_render(out,'tail-rear-quarter',140,(0,7.,-10.0),12,(850,750))
        riding_pose(rig,.75);bpy.context.view_layer.update();fit_static_contacts(horse,rig,leather)
        fit_render(out,'mounted-partial-lean',90,(0,-1,-10),29,(1000,700))
        riding_pose(rig);bpy.context.view_layer.update();fit_static_contacts(horse,rig,leather)


def build(out, operation):
    import bpy
    from wardrobe_riding_fit import accepted_signature, neutral_surface, evaluated_surfaces, fit_straps
    from body_studio_fit import coordinates_digest
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    prior=json.loads((SOURCE.parent/'result.json').read_text())
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    before=accepted_signature(prior['protected_signatures']); basis=coordinates_digest(tuple(v.co) for v in body.data.vertices)
    assert before==prior['protected_signatures'] and basis==prior['body_basis_digest']
    neutral(rig)
    if operation=='inspect02':repair_tail(out,True);return
    surface=neutral_surface(body);height=max(p.z for p,_ in surface)-min(p.z for p,_ in surface)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.7526/height
    bpy.context.scene['MF_pashtun_stature_m']=1.7526
    tailoring=tailor(body,rig);look=cloth_character();scarf=fit_scarf();tail=repair_tail(out)
    straps=[o for o in bpy.context.scene.objects if o.name.startswith(('MF_fit_shoulder_harness','MF_fit_waist_belt'))]
    fit_straps(straps,[bpy.data.objects['MF_fit_tunic']])
    for strap in straps:
        contact=strap.modifiers['Static strap-to-garment registration'];contact.offset=.10
        rounded=strap.modifiers.new('Soft continuous leather shoulder return','SUBSURF');rounded.levels=2
        bpy.context.view_layer.objects.active=strap
        while list(strap.modifiers).index(rounded)>1:
            bpy.ops.object.modifier_move_up(modifier=rounded.name)
    bpy.context.scene.cycles.samples=16
    if operation in ('preview14','preview15','preview16','preview17'):
        from wardrobe_riding_fit import fit_render
        for label,angle in [('rear-quarter',140),('side',90),('opposite-side',-90)]:
            fit_render(out,'tail-'+label,angle,(0,7,-10),12,(850,750))
    else:
        render_views(out,operation.startswith('seal'),operation in ('preview06','preview07','preview08','preview09','preview10','preview11','preview12','preview13'))
    assert accepted_signature(before)==before and coordinates_digest(tuple(v.co) for v in body.data.vertices)==basis
    result={'operation':operation,'parent_sha256':SOURCE_SHA,'protected_signatures':before,'body_basis_digest':basis,
            'protected_data_exact':True,'body_basis_exact':True,'source_pins_unchanged':all(digest(p)==h for p,h in ((SOURCE,SOURCE_SHA),(BODY,BODY_SHA),(HORSE,HORSE_SHA))),
            'stature_m':1.7526,'neutral_body_height_scene_units':height,'metric_scale_length':bpy.context.scene.unit_settings.scale_length,
            'tailoring':tailoring,'look':look,'scarf':scarf,'tail':tail,'handler_sha256':digest(Path(__file__)),
            'visual_gate':'NOT_RUN','Director_acceptance':'PENDING','limits':['Static pose only','No gait, cloth physics, continuous grasp, rights or release qualification']}
    from static_tail_dock import data_signature
    result['static_tail_curve_digest']=data_signature(bpy.data.objects['MF_170_tail_fibers'])
    if operation.startswith('seal'):
        import numpy as np
        names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type=='MESH']
        np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
        for block in bpy.data.texts:block.use_module=False
        bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True)
        result['native_sha256']=digest(out/'dressed-fit.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def verify(out, operation):
    import bpy
    import numpy as np
    from wardrobe_riding_fit import accepted_signature, evaluated_surfaces, fit_render, riding_pose, fit_static_contacts
    from body_studio_fit import coordinates_digest
    selected=BASE/('wardrobe170-seal'+operation[-2:])
    result=json.loads((selected/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(selected/'dressed-fit.blend'),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    exact=accepted_signature(result['protected_signatures'])==result['protected_signatures']
    basis=coordinates_digest(tuple(v.co) for v in body.data.vertices)==result['body_basis_digest']
    from static_tail_dock import data_signature
    tail_exact=data_signature(bpy.data.objects['MF_170_tail_fibers'])==result['static_tail_curve_digest']
    reference=np.load(selected/'evaluated-surfaces.npz',allow_pickle=False)
    actual=evaluated_surfaces(reference.files)
    errors={name:float(np.max(np.abs(actual[name]-reference[name]))) if actual[name].shape==reference[name].shape else None for name in reference.files}
    assert exact and basis and tail_exact and all(v is not None and v<2e-5 for v in errors.values())
    tunic=bpy.data.objects['MF_fit_tunic'];contact=tunic.modifiers['Final posed fabric coverage'];offset=contact.offset
    contact.offset=offset+.025;bpy.context.view_layer.update()
    revised=evaluated_surfaces([tunic.name])[tunic.name]
    revision_delta=float(np.max(np.abs(revised-actual[tunic.name])))
    assert revision_delta>1e-5
    contact.offset=offset;bpy.context.view_layer.update()
    rollback=float(np.max(np.abs(evaluated_surfaces([tunic.name])[tunic.name]-actual[tunic.name])))
    assert rollback<2e-5
    fit_render(out,'reopened-mounted-side',90,(0,-1,-10),29,(1000,700))
    neutral(rig)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):ob.hide_render=True
    bpy.context.view_layer.update();fit_render(out,'reopened-standing-front',0)
    verification={'reopened':True,'protected_signatures_exact':exact,'body_basis_exact':basis,'static_tail_curve_data_exact':tail_exact,
                  'evaluated_local_surface_max_errors':errors,'surface_tolerance':2e-5,
                  'stature_m':bpy.context.scene['MF_pashtun_stature_m'],
                  'controlled_garment_clearance_revision_max_delta':revision_delta,'revision_rollback_max_delta':rollback,
                  'neutral_rollback':True,'source_pins_unchanged':all(digest(p)==h for p,h in ((SOURCE,SOURCE_SHA),(BODY,BODY_SHA),(HORSE,HORSE_SHA))),
                  'limits':['Local evaluated positions and tested control only; no gait, topology, dynamics or appearance approval']}
    (out/'result.json').write_text(json.dumps(verification,indent=2)+'\n')


def main():
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job); out.mkdir()
    if job['operation'] == 'inspect01':
        inspect(out)
    elif job['operation'].startswith('verify'):
        verify(out,job['operation'])
    else:
        build(out,job['operation'])


if __name__ == '__main__':
    main()
