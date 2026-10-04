"""Reviewed fixed static outer-shawl correction; no executable job payload."""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import wardrobe_construction174 as prior
studio = prior.studio
BASE = studio.BASE
SOURCE = BASE/'wardrobe174-seal01/dressed-fit.blend'
SOURCE_SHA = '65d19c99bc7232b62146df0fb866412e2431f2e8e12deb29caaa17f7e14331cd'
OPERATIONS = tuple('preview%02d'%i for i in range(1,27)) + ('seal01','verify01')


def route_point(column, across):
    """Two offset exterior courses; length direction never collapses to a tuck."""
    course = studio.smoothstep((column-78)/16)
    theta = column/90*2*math.pi
    front = max(0., -math.cos(theta))
    rear = max(0., math.cos(theta))
    side = math.sin(theta)**4
    norm=math.hypot(side,1-side)
    roll,hang=side/norm,(1-side)/norm
    width = .62 + .48*front + .18*rear
    center = -1.28-1.42*front-.30*course*front
    center+=rear*(-.88+.32*course)
    center+=(.55-.90*course)*math.sin(theta)*front
    center+=.065*course*side
    z = center + width*(across-.5)*hang
    # Sparse unequal longitudinal fold ridges, not periodic transverse waves.
    fold = sum(a*math.exp(-((across-c-.065*math.sin(theta*.7+course))/w)**2)
               for c,w,a in ((.18,.12,.080),(.58,.17,.160),(.91,.07,.055)))
    fold*=.55+.45*front
    rx = 1.36+.35*side+.38*front+.22*rear-.08*across*(1-front)*(1-side)+.05*course
    ry = 1.39+.09*course if math.cos(theta)<0 else 1.66+.07*course
    # Across-sheet width rolls onto the shoulder top, perpendicular to the
    # front-to-rear centerline. A vertical ribbon here creates rigid fins.
    return (math.sin(theta)*(rx+fold*(1-side)+width*(across-.5)*roll),
            .14+math.cos(theta)*(ry+fold), z+fold*side)


def rear_drop(lean,y,z):
    """Bounded prescribed-pose drape, not dynamic cloth qualification."""
    return min(.65,1.10*abs(math.sin(lean)))*studio.smoothstep((y-.35)/.70)*studio.smoothstep((-z-.60)/.70)


def cloth_point(p):
    result=studio.torso_point(p)
    lean=abs(studio.torso_matrix(-2.7).to_quaternion().angle)
    result.z-=rear_drop(lean,p.y,p.z)
    return result


def construct(mats):
    import bpy
    import numpy as np
    from mathutils import Vector
    frame = prior.ORIGINAL_CONSTRUCT(mats)
    for old in list(bpy.data.objects):
        if old.name.startswith(('MF_173_open_scarf_seam_','MF_173_diagonal_scarf_fall_seam_')):
            bpy.data.objects.remove(old,do_unlink=True)
    if prior.digest(prior.PHYSICS_INPUT)!=prior.PHYSICS_INPUT_SHA:
        raise ValueError('Frozen pattern input changed')
    with np.load(prior.PHYSICS_INPUT,allow_pickle=False) as record:
        a = record['points']
        if a.shape!=(243*41,3) or not np.isfinite(a).all():
            raise ValueError('Invalid frozen pattern')
        rest = [Vector(p) for p in a]
    for i in range(181):
        for j in range(41):
            p=Vector(route_point(i,j/40))
            if i<9:
                t=1-studio.smoothstep(i/8)
                p.z=p.z*(1-t)+(-1.92+.50*(j/40-.5))*t
            if i>170:
                target=Vector((0.,1.54,-1.92+.48*(j/40-.5)))
                p=p.lerp(target,studio.smoothstep((i-170)/10))
            rest[i*41+j]=p
    for i in range(181,189):
        for j in range(41):
            target=Vector((0.,1.54,-1.92+.48*(j/40-.5)))
            rest[i*41+j]=rest[i*41+j].lerp(target,1-studio.smoothstep((i-180)/9))
    # Broad end under rear overlap, not a point-tuck or dangling jagged tab.
    for i in range(227,243):
        t=studio.smoothstep((i-226)/16)
        for j in range(41):
            v=j/40
            target=Vector((.15+.95*(v-.5),1.60+.12*math.sin(math.pi*v),
                           -2.06-.28*math.sin(math.pi*v)))
            rest[i*41+j]=rest[i*41+j].lerp(target,t)
    faces = prior.sheet_faces(243)
    # Preserve the sloped rounded shoulder crossing instead of flattening
    # all columns to a superior-surface shelf.
    ob = studio.panel('MF_173_open_scarf', [tuple(cloth_point(p)) for p in rest],
                      faces,mats['scarf'],.012,1)
    for p,item in zip(rest,ob.data.attributes['MF_173_material_coords'].data):item.vector=p
    layer = ob.data.attributes.new('MF_174_wrap_under_harness','FLOAT','POINT')
    for item in layer.data:item.value=0.
    course_attr=ob.data.attributes.new('MF_175_course','FLOAT','POINT')
    across_attr=ob.data.attributes.new('MF_175_across','FLOAT','POINT')
    tuck_attr=ob.data.attributes.new('MF_175_tuck','FLOAT','POINT')
    for i,item in enumerate(course_attr.data):
        col=i//41
        item.value=2. if col>180 else studio.smoothstep((col-78)/16)
        across_attr.data[i].value=(i%41)/40
        tuck_attr.data[i].value=(1-studio.smoothstep(col/9) if col<9 else
            studio.smoothstep((col-170)/10) if 170<col<=180 else
            1-studio.smoothstep((col-180)/9) if 180<col<189 else
            studio.smoothstep((col-226)/16) if col>226 else 0.)
    # Resolve whole-sheet folds through the actual contact geometry at the
    # low-resolution authoring surface, before subdivision. This is a frozen
    # construction settle for each prescribed pose, not moving cloth approval.
    # The normal pipeline rebuilds leather AFTER cloth. A construction solve
    # must instead see the current pose's leather, never yesterday's surfaces.
    prior.leather(frame,mats)
    from body_studio_fit import coordinates_digest
    ob['MF_175_harness_before_solve']=json.dumps({str(sign):coordinates_digest(
        tuple(v.co for v in bpy.data.objects['MF_173_tension_harness_'+str(sign)].data.vertices)) for sign in (-1,1)})
    ob['MF_175_construction_settled']=False
    outer_clearance()
    collision_mods=[]
    try:
        for sign in (-1,1):
            support=bpy.data.objects['MF_173_tension_harness_'+str(sign)]
            mod=support.modifiers.new('175 outer-shawl construction support','COLLISION')
            support.collision.thickness_outer=.016
            collision_mods.append((support,mod))
        settle_shoulders(ob)
    finally:
        for support,mod in collision_mods:support.modifiers.remove(mod)
    ob['MF_175_construction_settled']=True
    data = studio.single_surface_mesh(ob)
    for mod in list(ob.modifiers):
        if mod.type=='SUBSURF':ob.modifiers.remove(mod)
    studio.set_surface(ob.name,data,.012)
    bpy.data.objects['MF_173_diagonal_scarf_fall'].hide_render=True
    ob['MF_175_layer_order']='tunic / harness / shawl; rear wrap over headfall'
    return frame


def shoulder_freedom(column):
    if column>180 or column<9 or column>170:return 0.
    return studio.smoothstep((abs(math.sin(column/90*2*math.pi))-.55)/.25)


def settle_shoulders(ob):
    """Frozen local contact solve; preserve established chest/rear/head layout."""
    import bpy
    scene=bpy.context.scene;old_frame=scene.frame_current;old_gravity=scene.gravity.copy()
    supports=('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
              'MF_171_fitted_sleeve_R_173_visible','MF_studio_adult_body',
              'MF_173_static_groom_clearance')
    temporary=[];states=[];cloth=None;group=None;group_name=None
    assert len(ob.data.vertices)==243*41
    try:
        for name in supports:
            source=bpy.data.objects[name]
            if any(m.type=='SOLIDIFY' for m in source.modifiers):data=studio.single_surface_mesh(source)
            else:data=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get()),
                       depsgraph=bpy.context.evaluated_depsgraph_get())
            collider=bpy.data.objects.new('MF175 local cloth support',data)
            bpy.context.collection.objects.link(collider);collider.matrix_world=source.matrix_world.copy()
            collider.hide_render=True;temporary.append(collider)
            if len(data.polygons)>15000:
                mod=collider.modifiers.new('Construction support simplification','DECIMATE');mod.ratio=.22
            collider.modifiers.new('Static construction collision','COLLISION');collider.collision.thickness_outer=.018
        group=ob.vertex_groups.new(name='MF175 preserve layout outside shoulder turns')
        group_name=group.name
        for i in range(243):
            weight=1-shoulder_freedom(i)
            if weight:group.add(list(range(i*41,(i+1)*41)),weight,'REPLACE')
        for mod in ob.modifiers:
            if mod.type in ('SOLIDIFY','SUBSURF'):
                states.append((mod,mod.show_viewport));mod.show_viewport=False
        cloth=ob.modifiers.new('MF175 local frozen contact solve','CLOTH')
        s=cloth.settings;s.quality=6;s.mass=.14;s.tension_stiffness=28;s.compression_stiffness=12
        s.shear_stiffness=12;s.bending_stiffness=2.;s.vertex_group_mass=group.name;s.pin_stiffness=1
        cloth.collision_settings.use_collision=True;cloth.collision_settings.distance_min=.016
        cloth.collision_settings.use_self_collision=True;cloth.collision_settings.self_distance_min=.014
        cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=32;scene.gravity=(0,0,-9.81)
        for frame in range(1,33):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());ev.to_mesh();ev.to_mesh_clear()
            if frame%8==0:print('175 local construction settle frame',frame,flush=True)
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
        ob.modifiers.remove(cloth);cloth=None;studio.set_surface(ob.name,data,.012)
    finally:
        if cloth is not None:ob.modifiers.remove(cloth)
        # Replacing the baked mesh can invalidate Blender's group handle.
        # Resolve the name on the current object, never use a stale RNA ref.
        current=ob.vertex_groups.get(group_name) if group_name else None
        if current is not None:ob.vertex_groups.remove(current)
        for mod,state in states:mod.show_viewport=state
        for collider in temporary:
            data=collider.data;bpy.data.objects.remove(collider,do_unlink=True)
            if not data.users:bpy.data.meshes.remove(data)
        scene.gravity=old_gravity;scene.frame_set(old_frame);bpy.context.view_layer.update()


def outer_clearance(fair=True):
    """Fit only nearby intended supports; outer cloth never pressed under leather."""
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    from mathutils.bvhtree import BVHTree
    import bmesh
    ob = bpy.data.objects['MF_173_open_scarf']
    if ob.get('MF_175_construction_settled'):
        from body_studio_fit import coordinates_digest
        after={str(sign):coordinates_digest(tuple(v.co for v in
            bpy.data.objects['MF_173_tension_harness_'+str(sign)].data.vertices)) for sign in (-1,1)}
        ob['MF_175_harness_after_solve']=json.dumps(after)
        ob['MF_175_harness_same_support']=json.loads(ob['MF_175_harness_before_solve'])==after
        print('175 harness support unchanged:',ob['MF_175_harness_same_support'],flush=True)
        return
    courses=ob.data.attributes['MF_175_course'].data
    tucks=ob.data.attributes['MF_175_tuck'].data
    head_tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],
        [tuple(f.vertices) for f in ob.data.polygons
         if all(courses[i].value>1.5 and tucks[i].value<.1 for i in f.vertices)])
    # A woven shawl bridges the narrow harness, not every edge triangle.
    # Build one temporary convex torso/strap support in the intended corridor.
    frame=studio.torso_matrix(-2.7);inverse=frame.inverted()
    cloud=[]
    for name in ('MF_fit_tunic_173_visible','MF_studio_adult_body','MF_173_tension_harness_-1',
                 'MF_173_tension_harness_1','MF_173_strap_adjuster_1'):
        source=bpy.data.objects[name];ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        for v in list(mesh.vertices)[::3]:
            p=source.matrix_world@v.co;local=inverse@p
            if name=='MF_studio_adult_body' and local.z<-1.7:continue
            if -3.9<local.z<-.85 and abs(local.x)<1.65 and -.1<abs(local.y)<2.1:cloud.append(p)
        ev.to_mesh_clear()
    bm=bmesh.new()
    for p in cloud:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    bm.verts.index_update()
    bridge=BVHTree.FromPolygons([v.co.copy() for v in bm.verts],
                               [tuple(v.index for v in f.verts) for f in bm.faces])
    bm.free();supports=[bridge]
    shoulder_supports=[tree_for(bpy.data.objects[name]) for name in
        ('MF_studio_adult_body','MF_fit_tunic_173_visible',
         'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
         'MF_173_tension_harness_-1','MF_173_tension_harness_1')]
    for vertex,item in zip(ob.data.vertices,ob.data.attributes['MF_173_material_coords'].data):
        rest = item.vector
        course=courses[vertex.index].value
        tuck=ob.data.attributes['MF_175_tuck'].data[vertex.index].value
        p = ob.matrix_world@vertex.co
        if course>1.5:
            continue
        if rest.z>-.7:continue
        root = studio.torso_point(Vector((0,.14,rest.z)))
        direction = p-root
        if direction.length<.2:continue
        direction.normalize()
        shoulder=studio.smoothstep((abs(rest.x)-1.25)/.3)*studio.smoothstep((rest.z+2.25)/.55)
        up=(studio.torso_matrix(rest.z).to_3x3()@Vector((0,0,1))).normalized()
        direction=(direction+up*shoulder*.9).normalized()
        # Bounded inward rays from the exterior find the outer boundary;
        # nearest-face normals on thin band edges produced contact spikes.
        for tree in supports:
            hit,_,_,_=tree.ray_cast(root,direction,4.)
            if hit is None:continue
            clearance=.050+.085*min(course,1.)
            signed=(p-hit).dot(direction)
            if signed<clearance:p+=direction*(clearance-signed)*(1-tuck)
        if course<1.5 and rest.y>.55:
            back=(studio.torso_matrix(rest.z).to_3x3()@Vector((0,1,0))).normalized()
            # A smooth exterior rear envelope bridges the folded headfall.
            # Do not copy the sheet's individual concave/back-facing folds.
            v=ob.data.attributes['MF_175_across'].data[vertex.index].value
            ridge=(.10*math.exp(-((v-.34-.065*math.sin(rest.x))/ .14)**2)
                   +.045*math.exp(-((v-.78+.04*math.cos(rest.x))/ .09)**2))
            y=1.91-.12*rest.x**2+.09*course+ridge
            target=cloth_point(Vector((rest.x,y,rest.z)))
            weight=studio.smoothstep((rest.y-.55)/.60)*(1-tuck)
            p+=back*(target-p).dot(back)*weight
            # Absolute target, not an accumulated displacement on each refit.
            # Rear height remains continuous with the shoulder/headfall.
            # A separate accumulated world-Z shift tore this interface.
        cap=studio.smoothstep((abs(rest.x)-.8)/.3)*(1-studio.smoothstep((abs(rest.y-.14)-.25)/.65))
        cap*=studio.smoothstep((rest.z+2.15)/.5)
        if cap and tuck<.1:
            hits=[tree.ray_cast(p+up*1.,-up,2.4)[0] for tree in shoulder_supports]
            hits=[hit for hit in hits if hit is not None]
            if hits:
                hit=max(hits,key=lambda q:q.dot(up))
                target=hit+up*(.055+.090*min(course,1.))
                if fair or (p-target).dot(up)<0:
                    p=p.lerp(target,cap)
        # Establish winding outside the headfall BEFORE self-collision. A
        # solver cannot reliably untangle sheets that already pass through
        # each other, especially while their established layout is pinned.
        if abs(rest.x)>.85 and rest.z>-2.9 and tuck<.1:
            local=frame.inverted()@p
            root=frame@Vector((0,.14,local.z))
            direction=p-root
            if direction.length>.1:
                direction.normalize();hit,_,_,_=head_tree.ray_cast(root,direction,4.)
                if hit is not None:p+=direction*max(0.,(hit-p).dot(direction)+.075+.065*min(course,1.))
        vertex.co=ob.matrix_world.inverted()@p
    if not fair:
        ob.data.update();bpy.context.view_layer.update();return
    # Fair the real contact surface locally; frozen folds remain elsewhere.
    neighbors=[set() for _ in ob.data.vertices]
    weights=[]
    for index,item in enumerate(ob.data.attributes['MF_173_material_coords'].data):
        p=item.vector
        weights.append(studio.smoothstep((abs(p.x)-.85)/.55)
                       *studio.smoothstep((-.70-p.z)/.35)
                       *studio.smoothstep((p.z+3.8)/.75)*(courses[index].value<1.5))
    for f in ob.data.polygons:
        ids=list(f.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):neighbors[a].add(b);neighbors[b].add(a)
    # Vectorized local surface fairing permits a meaningful contact-radius
    # solve instead of tiny repeated high-poly cosmetic passes.
    import numpy as np
    points=np.array([tuple(v.co) for v in ob.data.vertices],dtype=np.float64)
    degree=max(len(ids) for ids in neighbors)
    indices=np.repeat(np.arange(len(points))[:,None],degree,axis=1)
    mask=np.zeros(indices.shape,dtype=np.float64)
    for i,ids in enumerate(neighbors):
        for j,n in enumerate(sorted(ids)):indices[i,j]=n;mask[i,j]=1
    counts=np.maximum(mask.sum(axis=1),1)[:,None]
    factors=np.array(weights)[:,None]*.44
    for _ in range(48):
        average=(points[indices]*mask[:,:,None]).sum(axis=1)/counts
        points+=(average-points)*factors
    for v,p in zip(ob.data.vertices,points):v.co=p
    ob.data.update();bpy.context.view_layer.update()
    outer_clearance(False)


def install():
    prior.install()
    studio.construct_scarf=construct
    import wardrobe_tension
    wardrobe_tension.support_cloud=tunic_support_cloud
    wardrobe_tension.press_visible_scarf=outer_clearance


def tunic_support_cloud():
    """Leather rests on tunic only; the outer shawl is not its support layer."""
    import bpy
    ob=bpy.data.objects['MF_fit_tunic_173_visible']
    coords=ob.data.attributes['MF_173_material_coords'].data
    return [(coords[i].vector.z,ob.matrix_world@v.co) for i,v in enumerate(ob.data.vertices)
            if -6.1<coords[i].vector.z<-.8 and abs(coords[i].vector.x)<2.35]


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed enum operation only')
    if SOURCE.is_symlink() or prior.digest(SOURCE)!=SOURCE_SHA:
        raise ValueError('Pinned source mismatch')
    out=BASE/('wardrobe175-'+job['operation'])
    if out.exists():raise ValueError('Never overwrite evidence')
    if job['operation'] in ('seal01','verify01'):
        from wardrobe_outer175_evidence import binding
        binding()
    return out


def preview(out):
    import bpy
    from wardrobe_riding_fit import fit_render,riding_pose
    rig=bpy.data.objects['MF_body156_fit_rig']
    studio.neutral(rig);mats=studio.make_materials();studio.pose_wardrobe(mats)
    diagnostic=out.name.endswith('preview23')
    if diagnostic:colour_routes()
    horse=[o for o in bpy.context.scene.objects if o.name.startswith(
        ('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus',
         'MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_'))]
    for o in horse:o.hide_render=True
    bpy.context.scene.cycles.samples=16
    for label,angle in (('front',0),('right',40),('rear',180),('profile',90)):
        fit_render(out,'upper-'+label,angle,(0,.15,-1.7),7.,(720,765))
    riding_pose(rig);bpy.context.view_layer.update();studio.pose_wardrobe(mats)
    if diagnostic:colour_routes()
    for label,angle in (('left',-40),('right',40)):
        fit_render(out,'mounted-'+label,angle,(0,-1.4,-3.4),9.,(720,765))
    # Cloth/body comparison diagnoses the upper-arm issue without anatomy edits.
    garments=[o for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE')
              and o.name!='MF_studio_adult_body' and ('MF_fit_' in o.name or 'MF_173_' in o.name
                   or 'MF_171_' in o.name)]
    for o in garments:o.hide_render=True
    fit_render(out,'mounted-body-control',-40,(0,-1.4,-3.4),9.,(720,765))


def colour_routes():
    """Read-only appearance diagnostic: red inner/blue outer/yellow head sheet."""
    import bpy
    ob=bpy.data.objects['MF_173_open_scarf']
    mat=bpy.data.materials.new('175 sheet section diagnostic');mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    shader=nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=1
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='MF_175_course'
    scale=nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=.5
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    ramp.color_ramp.elements[0].color=(.8,.04,.03,1)
    ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.8,.5,.02,1)
    mid=ramp.color_ramp.elements.new(.4);mid.color=(.02,.12,.8,1)
    links.new(attr.outputs['Fac'],scale.inputs[0]);links.new(scale.outputs[0],ramp.inputs[0])
    links.new(ramp.outputs[0],shader.inputs['Base Color'])
    ob.data.materials.clear();ob.data.materials.append(mat)


def isolate(out):
    """Cheap controls distinguish leather clipping from cloth self-overlap."""
    import bpy
    from wardrobe_riding_fit import fit_render
    studio.neutral(bpy.data.objects['MF_body156_fit_rig'])
    studio.pose_wardrobe(studio.make_materials())
    for o in bpy.context.scene.objects:
        if o.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus',
            'MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):o.hide_render=True
        if 'harness' in o.name or 'strap_adjuster' in o.name:o.hide_render=True
    bpy.context.scene.cycles.samples=16
    fit_render(out,'cloth-without-leather',0,(0,.15,-1.7),7.,(720,765))
    ob=bpy.data.objects['MF_173_open_scarf'];courses=ob.data.attributes['MF_175_course'].data
    info={'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),
          'modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport,'show_render':m.show_render} for m in ob.modifiers]}
    faces=[tuple(f.vertices) for f in ob.data.polygons if all(courses[i].value>.95 for i in f.vertices)]
    points=[tuple(v.co) for v in ob.data.vertices]
    data=bpy.data.meshes.new('Outer-course-only diagnostic');data.from_pydata(points,[],faces)
    for mat in ob.data.materials:data.materials.append(mat)
    for f in data.polygons:f.use_smooth=True
    studio.set_surface(ob.name,data,.012)
    for o in bpy.context.scene.objects:
        if o.name.startswith('MF_173_open_scarf_seam_'):o.hide_render=True
    fit_render(out,'outer-course-only',0,(0,.15,-1.7),7.,(720,765))
    (out/'isolation.json').write_text(json.dumps(info,indent=2)+'\n')


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    install()
    if job['operation']=='preview08':isolate(out)
    elif job['operation'].startswith('preview'):preview(out)
    elif job['operation']=='seal01':
        from wardrobe_outer175_evidence import seal
        seal(out);return
    elif job['operation']=='verify01':
        from wardrobe_outer175_evidence import verify
        verify(out);return
    from wardrobe_riding_fit import accepted_signature
    from body_studio_fit import coordinates_digest
    result=json.loads((SOURCE.parent/'result.json').read_text())
    assert accepted_signature(result['protected_signatures'])==result['protected_signatures']
    assert coordinates_digest(tuple(v.co for v in bpy.data.objects['MF_studio_adult_body'].data.vertices))==result['body_basis_digest']
    (out/'result.json').write_text(json.dumps({'protected_exact':True,'body_basis_exact':True,
        'handler_sha256':prior.digest(Path(__file__)),'visual_gate':'NOT_RUN',
        'source_sha256':SOURCE_SHA,'static_only':True,
        'harness_same_support':bool(bpy.data.objects['MF_173_open_scarf'].get('MF_175_harness_same_support',False))},indent=2)+'\n')


if __name__=='__main__':main()
