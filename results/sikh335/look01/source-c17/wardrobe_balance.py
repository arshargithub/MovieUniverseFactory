"""Reviewed fixed exchange172 assembly corrections; never execute job code."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wardrobe_refinement import BASE, neutral
from wardrobe_riding_fit import digest

SOURCE = BASE / 'wardrobe171-seal01/dressed-fit.blend'
SOURCE_SHA = 'ce5a05ab7405d097b7787cfce31d035cc9e5ce582e6f9b6fddf0db4b8e964d3d'
OPERATIONS = ('inspect01','inspect02','preview13','seal01','verify01')


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Only fixed reviewed operations admitted')
    if SOURCE.is_symlink() or not SOURCE.is_file() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned source mismatch')
    out = BASE / ('wardrobe172-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite evidence')
    if job['operation']=='verify01':
        selected=BASE/'wardrobe172-seal01'
        result=json.loads((selected/'result.json').read_text())
        native=selected/'dressed-fit.blend'
        if native.is_symlink() or not native.is_file() or digest(native)!=result['native_sha256']:raise ValueError('Selected native mismatch')
    return out


def inspect(out):
    import bpy
    from wardrobe_riding_fit import neutral_surface
    body = bpy.data.objects['MF_studio_adult_body']
    points = [p for p, _ in neutral_surface(body)]
    rows = []
    for z in [i*.15 for i in range(-20, 16)]:
        sample = [p for p in points if abs(p.z-z)<.065]
        rows.append({'z':z, 'bounds':[[min(p[k] for p in sample),max(p[k] for p in sample)] for k in range(3)] if sample else None})
    objects = []
    for ob in bpy.context.scene.objects:
        if not ob.hide_render and ob.type in ('MESH','CURVES'):
            objects.append({'name':ob.name, 'scale':list(ob.scale), 'location':list(ob.location),
                            'modifiers':[(m.name,m.type) for m in ob.modifiers], 'constraints':[(c.name,c.type) for c in ob.constraints]})
    result = {'body_bounds':[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)],
              'upper_body_slices':rows,'visible_objects':objects,'scene_scale_length':bpy.context.scene.unit_settings.scale_length,
              'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in bpy.data.objects['MF_body156_fit_rig'].data.bones},
              'source_unchanged':digest(SOURCE)==SOURCE_SHA}
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    chin_candidates=[p for p in points if abs(p.x)<.18 and p.y<-.78 and -1.15<p.z<0]
    chin=min(p.z for p in chin_candidates);crown=max(p.z for p in points);sole=min(p.z for p in points)
    result['anatomical_proportions']={'chin_landmark_z':chin,'chin_method':'Lowest central anterior chin surface: abs(x)<.18, y<-.78, -1.15<z<0; approximate landmark, not calibrated anthropometry',
        'crown_z':crown,'sole_z':sole,'anatomical_height':crown-sole,'head_height':crown-chin,'head_units_per_stature':(crown-sole)/(crown-chin),
        'hair_scarf_excluded':True,'projection':'World-space neutral evaluated surface; orthographic review cameras'}
    tree=tree_for(body);rig=bpy.data.objects['MF_body156_fit_rig'];ease=[]
    for side in ('L','R'):
        up=rig.data.bones['upperarm.'+side];fore=rig.data.bones['forearm.'+side]
        start=rig.matrix_world@up.head_local;elbow=rig.matrix_world@up.tail_local;end=rig.matrix_world@fore.tail_local
        for s in (.25,.6,.9,1.3,1.6):
            center=start.lerp(elbow,s) if s<=1 else elbow.lerp(end,s-1)
            axis=(elbow-start).normalized() if s<=1 else (end-elbow).normalized()
            across=axis.cross(Vector((0,1,0))).normalized();depth=axis.cross(across).normalized()
            radii=[]
            for direction in (across,-across,depth,-depth):
                hit,_,_,_=tree.ray_cast(center,direction,1.)
                if hit is not None:radii.append((hit-center).length)
            sleeve_radius=.58-.17*max(0.,(s-.1)/1.6)
            ease.append({'side':side,'along_arm':s,'skin_radii':radii,'sleeve_pattern_radius':sleeve_radius})
    result['sleeve_ease_samples']=ease
    (out/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')


def fitted_sleeves():
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    tree=tree_for(bpy.data.objects['MF_studio_adult_body']);rig=bpy.data.objects['MF_body156_fit_rig']
    changed=0
    for side in ('L','R'):
        ob=bpy.data.objects['MF_171_fitted_sleeve_'+side]
        follow=ob.modifiers['Static evaluated-body cloth support']
        bpy.context.view_layer.objects.active=ob;ob.hide_set(False);ob.select_set(True)
        bpy.ops.object.surfacedeform_bind(modifier=follow.name);assert not follow.is_bound
        up=rig.data.bones['upperarm.'+side];fore=rig.data.bones['forearm.'+side]
        start=rig.matrix_world@up.head_local;elbow=rig.matrix_world@up.tail_local;end=rig.matrix_world@fore.tail_local
        for j in range(25):
            s=-.14+j/24*1.84
            center=start.lerp(elbow,s) if s<=1 else elbow.lerp(end,s-1)
            axis=(elbow-start).normalized() if s<=1 else (end-elbow).normalized()
            for i in range(32):
                vert=ob.data.vertices[j*32+i];p=ob.matrix_world@vert.co;direction=(p-center).normalized()
                hit,_,_,_=tree.ray_cast(center,direction,.80)
                radius=(hit-center).length+.075 if hit is not None else (p-center).length*.80
                blend=max(0.,min(1.,(s+.02)/.25));blend=blend*blend*(3-2*blend)
                target=center+direction*radius
                vert.co=ob.matrix_world.inverted()@p.lerp(target,blend);changed+=int(blend>0)
        ob.data.update();bpy.context.view_layer.update();bpy.ops.object.surfacedeform_bind(modifier=follow.name);assert follow.is_bound
        fair=ob.modifiers.new('Tailored sleeve section continuity','SMOOTH');fair.factor=.45;fair.iterations=4
        while list(ob.modifiers).index(fair)>1:bpy.ops.object.modifier_move_up(modifier=fair.name)
    return {'vertices_refitted':changed,'radial_ease_scene_units':.075,'head_or_body_resculpted':False}


def rejected_folded_strip():
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from character_assembly import mesh
    from wardrobe_refinement import tree_for
    from wardrobe_riding_fit import bind_torso
    for name in ('MF_171_full_open_scarf','MF_171_front_scarf_drape'):bpy.data.objects[name].hide_render=True
    hull=bmesh.new()
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for p in list(ev.data.points)[::max(1,len(ev.data.points)//1600)]:hull.verts.new(ob.matrix_world@p.position)
    bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False);hull.verts.ensure_lookup_table();hull.verts.index_update()
    hair=BVHTree.FromPolygons([v.co.copy() for v in hull.verts],[tuple(v.index for v in f.verts) for f in hull.faces]);hull.free()
    anchors=[Vector(p) for p in [(-.75,-1.25,-4.3),(-1.38,-.95,-3.1),(-1.83,-.25,-1.75),(-1.35,.08,-.55),(-1.15,.12,.65),(-.65,.12,1.19),(0,.14,1.4),(.65,.12,1.19),(1.15,.12,.65),(1.37,.15,-.65),(1.85,.08,-1.75),(1.38,-.8,-2.55),(.70,-1.2,-3.05)]]
    points=[];faces=[];nv=21;steps=10;tree=tree_for(bpy.data.objects['MF_fit_tunic'])
    for segment in range(len(anchors)-1):
        p0=anchors[max(0,segment-1)];p1=anchors[segment];p2=anchors[segment+1];p3=anchors[min(len(anchors)-1,segment+2)]
        for step in range(steps):
            t=step/steps;s=(segment+t)/(len(anchors)-1)
            center=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
            tangent=(p2-p1).normalized()
            across=Vector((0,1,0)) if center.z>-.9 else tangent.cross(Vector((center.x,center.y-.15,0)).normalized()).normalized()
            if across.y<0:across=-across
            width=1.48 if center.z>-.9 else 1.10
            for j in range(nv):
                v=j/(nv-1);p=center+across*((v-.13)*width)
                fold=.06*math.sin(5*math.pi*v+.6*math.sin(6*s))+.025*math.sin(9*math.pi*v+2*s)
                if center.z>-.9:
                    hit,normal,_,distance=hair.find_nearest(p)
                    if hit is not None and distance<.8:p=hit+normal*(.14+fold)
                else:
                    hit,normal,_,distance=tree.find_nearest(p)
                    if hit is not None and distance<1.:p=hit+normal*(.12+fold)
                points.append(tuple(p))
    rows=len(points)//nv
    for i in range(rows-1):
        for j in range(nv-1):
            a=i*nv+j;faces.append((a,a+nv,a+nv+1,a+1))
    shawl=mesh('MF_172_folded_open_shawl',points,faces,bpy.data.materials['MF_170_soft_indigo_scarf'])
    bind_torso(shawl,bpy.data.objects['MF_body156_fit_rig'])
    shawl.modifiers.new('Soft major shawl folds','SUBSURF').levels=2
    group=shawl.vertex_groups.new(name='Shoulder and chest scarf clearance')
    for vertex in shawl.data.vertices:
        w=max(0.,min(1.,(-vertex.co.z-.9)/.55))
        if w:group.add([vertex.index],w,'REPLACE')
    cover=shawl.modifiers.new('Actual posed shirt clearance','SHRINKWRAP');cover.target=bpy.data.objects['MF_fit_tunic'];cover.wrap_method='NEAREST_SURFACEPOINT';cover.wrap_mode='OUTSIDE_SURFACE';cover.offset=.115;cover.vertex_group=group.name
    shawl.modifiers.new('Shawl thickness after fitting','SOLIDIFY').thickness=.018
    return {'method':'Continuous broad folded shawl from crown through asymmetric shoulder/chest ends, not a rear hood curtain','hair_forehead_open':True,'body_head_scale_changed':False,'dynamics_qualified':False}


def hair_clearance_proxy():
    """Static pose-derived groom envelope; never alter accepted hair data."""
    import bpy, bmesh
    hull=bmesh.new()
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        points=ev.data.points
        for p in list(points)[::max(1,len(points)//2200)]:hull.verts.new(ob.matrix_world@p.position)
    bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False)
    bmesh.ops.recalc_face_normals(hull,faces=list(hull.faces))
    ob=bpy.data.objects.get('MF_172_static_groom_clearance')
    if ob is None:
        data=bpy.data.meshes.new('MF_172_static_groom_clearance');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob)
    hull.to_mesh(ob.data);hull.free();ob.hide_render=True;ob.hide_set(True)
    ob['qualification']='Static current pose groom envelope; not a cloth simulation'
    bpy.context.view_layer.update()
    return ob


def folded_shawl():
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    from wardrobe_refinement import tree_for
    from wardrobe_riding_fit import bind_torso
    hood=bpy.data.objects['MF_171_full_open_scarf'];hood.name='MF_172_folded_head_drape'
    bpy.data.objects['MF_171_front_scarf_drape'].hide_render=True
    for vertex in hood.data.vertices:
        j,i=divmod(vertex.index,65);v=j/34;theta=-1.90+3.80*i/64
        p=vertex.co;p.z+=.35*v*v
        p.x*=1+.12*v**3;p.y+=.12*v*v
        # Unequal long diagonal folds, not a uniform vertical hood curtain.
        fold=(.065*math.sin(5*theta-5*v)+.03*math.sin(9*theta+3*v))*v
        p.x+=fold*math.sin(theta);p.y+=fold*math.cos(theta)
        if abs(theta)>1.4:p.y-=.35*v*v
        # Side returns stop on the torso, not as rectangular upper-arm tabs.
        edge=max(0.,min(1.,(abs(theta)-1.15)/.5))
        p.z+=(1.30 if theta>0 else .65)*v**3*edge
        p.x*=1-.12*v**3*edge
    hood.data.update()
    group=hood.vertex_groups.new(name='Lower head-drape shirt clearance')
    for vertex in hood.data.vertices:
        w=max(0.,min(1.,(-vertex.co.z-.9)/.5))
        if w:group.add([vertex.index],w,'REPLACE')
    tree=tree_for(bpy.data.objects['MF_fit_tunic']);mat=bpy.data.materials['MF_170_soft_indigo_scarf']
    points=[];faces=[];nv=25;rows=81
    for i in range(rows):
        s=i/(rows-1);theta=-1.40+2.80*s;direction=Vector((math.sin(theta),-math.cos(theta),0))
        for j in range(nv):
            v=j/(nv-1);z=-2.80+1.10*s-.25*math.sin(math.pi*s)+(v-.5)*(1.0+.40*math.sin(math.pi*s))
            center=Vector((0,.12,z));hit,_,_,_=tree.ray_cast(center,direction,3.)
            if hit is None:
                radius=1./math.sqrt((direction.x/1.5)**2+(direction.y/1.07)**2)
                hit=center+direction*radius
            # Radial sections preserve the intended cloth path: no nearest
            # jumps onto breast sides or rear-facing normals at the tail.
            fold=.080*math.sin(3*math.pi*v+.70*math.sin(4*s))**2+.015*math.sin(5*s)*v
            points.append(tuple(hit+direction*(.15+fold)))
    rows=len(points)//nv
    for i in range(rows-1):
        for j in range(nv-1):
            a=i*nv+j;faces.append((a,a+nv,a+nv+1,a+1))
    wrap=mesh('MF_172_folded_shoulder_wrap',points,faces,mat)
    bind_torso(wrap,bpy.data.objects['MF_body156_fit_rig'])
    wrap.modifiers.new('Soft torso-supported scarf folds','SUBSURF').levels=2
    wrap.modifiers.new('Wrap thickness after fitting','SOLIDIFY').thickness=.018
    return {'method':'Full folded head drape with short shoulder return and asymmetric folded chest/shoulder wrap','hair_forehead_open':True,'body_head_scale_changed':False,'dynamics_qualified':False}


def outer_ray_radius(tree,center,direction,maximum=8.):
    """Return the outermost bounded hit, not the entry into a sleeve shell."""
    distance=0.;outer=None
    for _ in range(16):
        hit,_,_,_=tree.ray_cast(center+direction*distance,direction,maximum-distance)
        if hit is None:break
        radius=(hit-center).length;outer=radius if outer is None else max(outer,radius)
        distance=radius+.003
        if distance>=maximum:break
    return outer


def harness_refit_weight(z):
    """Confine new scarf registration; preserve existing waist fit."""
    t=max(0.,min(1.,(z+4.50)/.70))
    return t*t*(3-2*t)


def single_surface_mesh(source,skip_old_clearance=False):
    """Evaluate the authoring surface with shell stages temporarily disabled."""
    import bpy
    shells=[m for m in source.modifiers if m.type=='SOLIDIFY'];assert len(shells)==1
    disabled=shells+[m for m in source.modifiers if skip_old_clearance and m.type=='SHRINKWRAP']
    old=[m.show_viewport for m in disabled]
    try:
        for m in disabled:m.show_viewport=False
        bpy.context.view_layer.update()
        ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
    finally:
        for m,state in zip(disabled,old):m.show_viewport=state
        bpy.context.view_layer.update()


def fit_scarf_static_pose():
    """Freeze fitted visible surfaces for this prescribed pose, not dynamics.

    Radial exclusion preserves the authored path rather than jumping to a
    neighbouring surface triangle. Source scarf objects remain editable and
    hidden; regenerated pose surfaces never modify accepted body/hair.
    """
    import bpy
    from mathutils import Vector, Matrix
    from mathutils.bvhtree import BVHTree
    proxy=hair_clearance_proxy();hood=bpy.data.objects['MF_172_folded_head_drape']
    frame=hood.matrix_world.copy();inverse=frame.inverted();trees=[]
    for ob in [proxy,*[bpy.data.objects[n] for n in ('MF_fit_tunic','MF_171_fitted_sleeve_L','MF_171_fitted_sleeve_R')]]:
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        trees.append(BVHTree.FromPolygons([inverse@ob.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]))
        ev.to_mesh_clear()
    for name in ('MF_172_folded_head_drape','MF_172_folded_shoulder_wrap'):
        source=bpy.data.objects[name]
        data=single_surface_mesh(source)
        for vertex in data.vertices:
            p=inverse@source.matrix_world@vertex.co
            center=Vector((0,.20,-.70)) if name.endswith('head_drape') and p.z>0 else Vector((0,.20,p.z))
            direction=p-center;radius=direction.length
            if radius<1e-6:continue
            direction.normalize();required=radius
            for index,tree in enumerate(trees):
                if name.endswith('shoulder_wrap') and index>=2:continue
                # A reaching forearm is a remote obstacle, not the torso
                # support for a scarf. Do not expand cloth to the wrists.
                radius_hit=outer_ray_radius(tree,center,direction,8. if index==0 else radius+.55)
                if radius_hit is not None:required=max(required,radius_hit+(.24 if index==0 else .08))
            vertex.co=frame@(center+direction*required)
        data.update()
        target=bpy.data.objects.get(name+'_pose_surface')
        if target is None:
            target=bpy.data.objects.new(name+'_pose_surface',data);bpy.context.collection.objects.link(target)
        else:target.data=data
        if not target.modifiers:
            target.modifiers.new('Thickness AFTER static surface fitting','SOLIDIFY').thickness=.018
        assert len(target.modifiers)==1 and target.modifiers[0].type=='SOLIDIFY'
        target.matrix_world=Matrix.Identity(4);target.hide_render=False
        target['qualification']='Current prescribed static pose only; regenerate from protected inputs, not cloth dynamics'
        source.hide_render=True
    bpy.context.view_layer.update()
    # Re-register the continuous shoulder leather OUTSIDE the new cloth.
    # Fitting to the shirt alone exposes disconnected brown fragments.
    points=[];faces=[]
    for name in ('MF_fit_tunic','MF_172_folded_head_drape_pose_surface','MF_172_folded_shoulder_wrap_pose_surface'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();offset=len(points)
        points.extend(inverse@ob.matrix_world@v.co for v in me.vertices)
        faces.extend(tuple(offset+i for i in f.vertices) for f in me.polygons if all(abs(points[offset+i].x)<1.95 for i in f.vertices))
        ev.to_mesh_clear()
    support=BVHTree.FromPolygons(points,faces)
    for name in ('MF_fit_shoulder_harness_-1','MF_fit_shoulder_harness_1'):
        source=bpy.data.objects[name];data=single_surface_mesh(source,skip_old_clearance=True)
        previous=single_surface_mesh(source);assert len(previous.vertices)==len(data.vertices)
        for vertex in data.vertices:
            p=inverse@source.matrix_world@vertex.co;center=Vector((0,.20,p.z));direction=p-center
            if direction.length<1e-6:continue
            original_radius=direction.length;direction.normalize();radius=outer_ray_radius(support,center,direction,original_radius+.65)
            corrected=frame@(center+direction*(radius+.065)) if radius is not None else source.matrix_world@vertex.co
            vertex.co=(source.matrix_world@previous.vertices[vertex.index].co).lerp(corrected,harness_refit_weight(p.z))
        data.update();target=bpy.data.objects.get(name+'_172_pose_surface')
        if target is None:
            target=bpy.data.objects.new(name+'_172_pose_surface',data);bpy.context.collection.objects.link(target)
            target.modifiers.new('Leather thickness AFTER static fitting','SOLIDIFY').thickness=.026
        else:target.data=data
        target.matrix_world=Matrix.Identity(4);target.hide_render=False;source.hide_render=True
        assert len(target.modifiers)==1 and target.modifiers[0].type=='SOLIDIFY'
    bpy.context.view_layer.update()


def build(out,operation):
    import bpy
    from wardrobe_riding_fit import accepted_signature,fit_render,riding_pose,evaluated_surfaces,fit_static_contacts
    from body_studio_fit import coordinates_digest
    prior=json.loads((SOURCE.parent/'result.json').read_text());protected=accepted_signature(prior['protected_signatures']);body=bpy.data.objects['MF_studio_adult_body']
    basis=coordinates_digest(tuple(v.co) for v in body.data.vertices);assert protected==prior['protected_signatures'] and basis==prior['body_basis_digest']
    result={'sleeves':fitted_sleeves(),'scarf':rejected_folded_strip() if operation=='preview01' else folded_shawl()}
    if operation!='preview01':fit_scarf_static_pose()
    bpy.context.scene.cycles.samples=16
    horse=[o for o in bpy.context.scene.objects if o.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_'))];states={o.name:o.hide_render for o in horse}
    for o in horse:o.hide_render=True
    targeted=operation.startswith('preview') and operation!='preview01'
    concise=operation=='preview13'
    if not concise:
        for label,angle in ([('front',0)] if targeted else [('front',0),('side',90),('rear',180)]):fit_render(out,'standing-'+label,angle)
    upper=[('front',0),('rear',180)] if concise else [('front',0),('left',-40),('right',40),('rear',180)]
    for label,angle in upper:fit_render(out,'upper-'+label,angle,(0,.15,-1.7),7.,(800,850))
    for o in horse:o.hide_render=states[o.name]
    rig=bpy.data.objects['MF_body156_fit_rig'];riding_pose(rig);bpy.context.view_layer.update();fit_scarf_static_pose()
    contacts=[o for o in bpy.context.scene.objects if o.get('source_object')];leather=bpy.data.objects['MF_fit_waist_belt'].data.materials[0]
    fit_static_contacts(contacts,rig,leather)
    if not targeted:
        for label,angle in [('side',90),('opposite-side',-90)]:fit_render(out,'mounted-'+label,angle,(0,-1,-10),29,(1000,700))
    mounted=[('left',-40),('right',40)] if concise else [('left',-40),('right',40),('rear',140)]
    for label,angle in mounted:fit_render(out,'mounted-upper-'+label,angle,(-.1,-2.5,-6),11.,(800,850))
    if not targeted:
        riding_pose(rig,.75);bpy.context.view_layer.update();fit_scarf_static_pose();fit_static_contacts(contacts,rig,leather);fit_render(out,'mounted-partial',90,(0,-1,-10),29,(1000,700))
    riding_pose(rig);bpy.context.view_layer.update();fit_scarf_static_pose();fit_static_contacts(contacts,rig,leather)
    assert accepted_signature(protected)==protected and coordinates_digest(tuple(v.co) for v in body.data.vertices)==basis
    from static_tail_dock import data_signature
    tail=data_signature(bpy.data.objects['MF_170_tail_fibers']);assert tail==prior['static_tail_curve_digest']
    result.update({'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),'protected_signatures':protected,'body_basis_digest':basis,'static_tail_curve_digest':tail,'head_scale_changed':False,'source_unchanged':digest(SOURCE)==SOURCE_SHA,'visual_gate':'NOT_RUN','Director_acceptance':'PENDING','static_scarf_limit':'Pose-specific regenerated surfaces and torso support; no continuous cloth/hair physics qualification'})
    if operation=='seal01':
        import numpy as np
        names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type=='MESH'];np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
        for text in bpy.data.texts:text.use_module=False
        bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True);result['native_sha256']=digest(out/'dressed-fit.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def verify(out):
    import bpy,numpy as np
    from wardrobe_riding_fit import accepted_signature,evaluated_surfaces,fit_render
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    selected=BASE/'wardrobe172-seal01';result=json.loads((selected/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(selected/'dressed-fit.blend'),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    reference=np.load(selected/'evaluated-surfaces.npz',allow_pickle=False);actual=evaluated_surfaces(reference.files)
    errors={n:float(np.max(np.abs(actual[n]-reference[n]))) if actual[n].shape==reference[n].shape else None for n in reference.files}
    protected=accepted_signature(result['protected_signatures'])==result['protected_signatures']
    basis=coordinates_digest(tuple(v.co) for v in body.data.vertices)==result['body_basis_digest']
    tail=data_signature(bpy.data.objects['MF_170_tail_fibers'])==result['static_tail_curve_digest']
    assert protected and basis and tail and all(v is not None and v<2e-5 for v in errors.values())
    tunic=bpy.data.objects['MF_fit_tunic'];cover=tunic.modifiers['Upper tunic actual skin coverage'];offset=cover.offset
    cover.offset=offset+.025;bpy.context.view_layer.update()
    delta=float(np.max(np.abs(evaluated_surfaces([tunic.name])[tunic.name]-actual[tunic.name])))
    cover.offset=offset;bpy.context.view_layer.update()
    rollback=float(np.max(np.abs(evaluated_surfaces([tunic.name])[tunic.name]-actual[tunic.name])))
    assert delta>1e-5 and rollback<2e-5
    fit_render(out,'reopened-mounted-side',90,(0,-1,-10),29,(1000,700))
    neutral(rig);fit_scarf_static_pose()
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):ob.hide_render=True
    bpy.context.view_layer.update();fit_render(out,'reopened-upper-front',0,(0,.15,-1.7),7.,(800,850))
    (out/'result.json').write_text(json.dumps({'reopened':True,'protected_signatures_exact':protected,'body_basis_exact':basis,'static_tail_curve_data_exact':tail,'surface_errors':errors,'surface_tolerance':2e-5,'controlled_garment_revision_max_delta':delta,'revision_rollback_max_delta':rollback,'neutral_pose_scarf_regenerated':True,'source_unchanged':digest(SOURCE)==SOURCE_SHA,'appearance_acceptance':'PENDING'},indent=2)+'\n')


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir()
    if job['operation']=='verify01':verify(out);return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    neutral(bpy.data.objects['MF_body156_fit_rig'])
    if job['operation'].startswith('inspect'):inspect(out)
    else:build(out,job['operation'])


if __name__=='__main__': main()
