"""Fixed character integration diagnostics; accepted masters remain untouched."""
import json
from pathlib import Path


def head_weights(z):
    from wardrobe_motion178_controls import smooth
    neck=smooth((z+1.72)/.34)
    head=smooth((z+1.38)/.38)
    return {'chest':1-neck,'MF185_neck':neck*(1-head),'MF185_head':neck*head}


def head_control(rig):
    """Two-joint derivative, neutral parity, rigid face with a lower-neck blend."""
    import bpy
    from mathutils import Vector
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe_refinement import neutral
    neutral(rig)
    roots=[bpy.data.objects[n] for n in ('MF_aimable_eye_Left','MF_aimable_eye_Right',
        'MF_natural147_hair_temples','MF_natural147_hair_retarget')]
    original={ob.name:ob.matrix_world.copy() for ob in roots}
    with render_geometry_paused():
        rig.data=rig.data.copy()
        bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
        bpy.ops.object.mode_set(mode='EDIT')
        for name,z0,z1,parent in (('MF185_neck',-1.55,-.75,'chest'),('MF185_head',-.75,.45,'MF185_neck')):
            bone=rig.data.edit_bones.new(name);bone.head=(0,.22,z0);bone.tail=(0,.22,z1)
            bone.parent=rig.data.edit_bones[parent];bone.use_connect=False
        bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
        body=bpy.data.objects['MF_studio_adult_body'];body.data=body.data.copy()
        groups={n:body.vertex_groups.get(n) or body.vertex_groups.new(name=n) for n in ('MF185_neck','MF185_head')}
        bone_groups={g.index:g for g in body.vertex_groups if g.name in rig.data.bones}
        changed=0
        for v in body.data.vertices:
            z=(body.matrix_world@v.co).z
            if z<=-1.72:continue
            weights=head_weights(z)
            # This sector is the central neck, not shoulders/upper arms.
            for index in [old.group for old in v.groups]:
                if index in bone_groups:bone_groups[index].remove([v.index])
            for name,w in weights.items():
                if w:body.vertex_groups[name].add([v.index],w,'REPLACE')
            changed+=1
        for ob in roots:
            matches=[c for c in ob.constraints if c.type=='CHILD_OF' and c.target==rig and c.subtarget=='chest']
            if len(matches)!=1:raise ValueError('Expected one chest attachment: '+ob.name)
            c=matches[0];c.subtarget='MF185_head'
            c.inverse_matrix=(rig.matrix_world@rig.pose.bones[c.subtarget].matrix).inverted()
        bpy.context.view_layer.update()
        parity=max(abs(ob.matrix_world[i][j]-original[ob.name][i][j]) for ob in roots for i in range(4) for j in range(4))
        if parity>1e-5:raise ValueError('Neutral eye/groom attachment drift')
    return {'weights_changed':changed,'neutral_root_matrix_error':parity,
        'scope':'Reversible derivative weights/rig; accepted coordinates, textures and expression keys unchanged'}


def boots(rig,mats):
    """Reconstruct at rest, then deform once with shin/foot rather than double pose.

    The source footwear contains baked pose coordinates. A later CHILD_OF is
    therefore not a neutral binding. Regenerate the existing authored last;
    keep the rigid footbed and blend only the ankle/shaft transition.
    """
    import bpy
    from wardrobe_finish import finishing
    from wardrobe_studio import smoothstep
    from wardrobe_motion178_controls import bind
    from wardrobe_refinement import neutral
    neutral(rig)
    names=('MF_173_work_boot_','MF_173_boot_')
    for ob in list(bpy.context.scene.objects):
        if ob.name.startswith(names):bpy.data.objects.remove(ob,do_unlink=True)
    finishing(mats,boots_only=True)
    attached=[]
    for ob in list(bpy.context.scene.objects):
        if not ob.name.startswith(names):continue
        side='L' if '_L' in ob.name else 'R' if '_R' in ob.name else None
        if side is None:raise ValueError('Unknown boot side')
        if ob.type=='CURVE':
            bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
            bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
            ob=bpy.context.view_layer.objects.active
        def weights(point):
            w=smoothstep((-12.05-point.z)/.65)
            return {'shin.'+side:1-w,'foot.'+side:w}
        bind(ob,rig,weights);attached.append(ob.name)
    return attached


def upper_garment(rig,mats):
    """One continuous torso/sleeve shell; retain the separate skirt below belt.

    Replace the failed overlapping shoulder cuts, not the accepted anatomy.
    Construct at neutral, trim real mesh boundaries, then bind to the body
    surface carrying its existing anatomical pose corrections.
    """
    import bpy
    from wardrobe_motion178_controls import render_surface_target,bind_render_surface,smooth
    body=bpy.data.objects['MF_studio_adult_body']
    flags=[(m,m.show_viewport) for m in body.modifiers if m.type=='SUBSURF']
    for m,_ in flags:m.show_viewport=False
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    ev=body.evaluated_get(deps);source=ev.to_mesh()
    data=bpy.data.meshes.new('Clean tailored upper topology')
    data.from_pydata([v.co[:] for v in source.vertices],[],[p.vertices[:] for p in source.polygons]);data.update();ev.to_mesh_clear()
    for m,state in flags:m.show_viewport=state
    import bmesh
    bm=bmesh.new();bm.from_mesh(data);deform=bm.verts.layers.deform.active
    if deform:
        for v in bm.verts:v[deform].clear()
    bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new('MF185_fitted_upper_tunic',data);bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world=body.matrix_world.copy();data.materials.clear();data.materials.append(mats['cloth'])
    for f in data.polygons:f.material_index=0;f.use_smooth=True
    coords=data.attributes.get('MF_173_material_coords') or data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
    group=ob.vertex_groups.new(name='Continuous upper garment cut')
    for v,item in zip(data.vertices,coords.data):
        p=ob.matrix_world@v.co;item.vector=p
        # Rounded modest V at front, shallow rear neckline. Rest x distinguishes
        # lowered arms from the torso, while distal forearm planes remove hands.
        front=smooth((.2-p.y)/.5)
        neckline=-1.83-.37*front*max(0.,1-abs(p.x)/1.1)
        w=smooth((neckline-p.z)/.12)
        if abs(p.x)<1.8:w*=smooth((p.z+5.42)/.12)
        else:
            side='L' if p.x>0 else 'R';bone=rig.data.bones['forearm.'+side]
            a=rig.matrix_world@bone.head_local;b=rig.matrix_world@bone.tail_local
            axis=(b-a).normalized();w*=smooth(((b-p).dot(axis)+.10)/.20)
        if w:group.add([v.index],w,'REPLACE')
    mask=ob.modifiers.new('Actual neckline waist and cuff boundaries','MASK');mask.vertex_group=group.name;mask.threshold=.5;mask.use_smooth=True
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mask.name)
    # A clipped anatomical tessellation is not a tailored neckline. Fair its
    # actual boundary loops and cloth surface before binding, rather than
    # carrying scalloped vertex-cut edges into animation.
    bm=bmesh.new();bm.from_mesh(ob.data)
    for _ in range(12):
        updates={}
        for v in bm.verts:
            adjacent=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(adjacent)==2:updates[v]=v.co*.5+(adjacent[0].co+adjacent[1].co)*.25
        for v,p in updates.items():v.co=p
    bm.to_mesh(ob.data);bm.free()
    fair=ob.modifiers.new('Rest garment ease fairing','SMOOTH');fair.factor=.5;fair.iterations=6
    bpy.ops.object.modifier_apply(modifier=fair.name)
    # Real construction ease, before fitting; a separate skin remains beneath.
    data=ob.data;data.update()
    # Read a single coherent normal field BEFORE changing any coordinates.
    # Compare with the previous incremental query rather than assume shading.
    points=[v.co.copy() for v in data.vertices];normals=[v.normal.copy() for v in data.vertices]
    legacy=data.copy()
    for v in legacy.vertices:v.co+=v.normal*.055
    for v,p,n in zip(data.vertices,points,normals):v.co=p+n*.055
    ob['incremental_offset_difference_native']=max((v.co-legacy.vertices[v.index].co).length for v in data.vertices)
    bpy.data.meshes.remove(legacy)
    data.update();target=render_surface_target();bind_render_surface(ob,target)
    bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());check=ev.to_mesh()
    error=max((v.co-data.vertices[v.index].co).length for v in check.vertices);ev.to_mesh_clear()
    ob['neutral_surface_bind_error_native']=error
    if error>1e-4:raise ValueError('Neutral garment surface bind changes its authored shape')
    sub=ob.modifiers.new('Tailored surface finish','SUBSURF');sub.levels=2;sub.render_levels=2
    shell=ob.modifiers.new('Woven fabric thickness','SOLIDIFY');shell.thickness=.012;shell.offset=0
    for name in ('MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible','MF178_render_underarm_gusset'):
        bpy.data.objects[name].hide_render=True
    skirt=bpy.data.objects['MF_fit_tunic_173_visible'];rest=skirt.data.attributes['MF_173_material_coords'].data
    cut=skirt.vertex_groups.new(name='Retained skirt below waistband')
    for v,item in zip(skirt.data.vertices,rest):
        w=smooth((-5.20-item.vector.z)/.12)
        if w:cut.add([v.index],w,'REPLACE')
    mask=skirt.modifiers.new('Upper section replaced by continuous garment','MASK');mask.vertex_group=cut.name;mask.use_smooth=True;mask.threshold=.5
    # Keep topology-changing clipping AFTER the existing surface bind. Moving
    # it ahead invalidates the admitted 10388-vertex deformation cache.
    return ob


def harness_shoulders(rig,upper):
    """Seat a continuous leather band on the corrected superior garment."""
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    from wardrobe_motion178_controls import bind_render_surface,render_surface_target,smooth
    tree=tree_for(upper);target=render_surface_target();record={}
    for sign in (-1,1):
        ob=bpy.data.objects['MF_173_tension_harness_'+str(sign)]
        for m in list(ob.modifiers):
            if m.type in ('SURFACE_DEFORM','ARMATURE'):ob.modifiers.remove(m)
        old=[ob.matrix_world@v.co for v in ob.data.vertices];centers=[(a+b)/2 for a,b in zip(old[::2],old[1::2])]
        normals=[];factors=[]
        for i,p in enumerate(centers):
            w=smooth((p.z+3.0)/.60);factors.append(w)
            hit,n,_,_=tree.find_nearest(p)
            root=Vector((0,.14,-3.3 if p.z>-2.6 else p.z))
            if n.dot(hit-root)<0:n=-n
            centers[i]=p.lerp(hit+n*.035,w);normals.append(n)
        for _ in range(6):
            oldcenters=centers
            centers=[p if i in (0,len(centers)-1) else p.lerp((oldcenters[i-1]+oldcenters[i+1])/2,.35*factors[i]) for i,p in enumerate(oldcenters)]
        for i,p in enumerate(centers):
            if not factors[i]:continue
            tangent=(centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
            width=tangent.cross(normals[i]).normalized()*.125
            if width.dot(old[2*i+1]-old[2*i])<0:width=-width
            # Move the band centre, not each edge independently, if either
            # edge would penetrate the garment; preserve a coherent width.
            for _ in range(3):
                shifts=[]
                for q in (p-width,p+width):
                    h,n,_,_=tree.find_nearest(q)
                    if n.dot(normals[i])<0:n=-n
                    shifts.append(max(0,.025-(q-h).dot(n)))
                p+=normals[i]*max(shifts)
            for k,q in enumerate((p-width,p+width)):
                ob.data.vertices[2*i+k].co=ob.matrix_world.inverted()@old[2*i+k].lerp(q,factors[i])
        ob.data.update();bind_render_surface(ob,target)
        record[str(sign)]={'max_rest_change_native':max((ob.matrix_world@v.co-old[v.index]).length for v in ob.data.vertices)}
    return record


def harness_routes(rig):
    """Rebuild crossed load paths from measured skin anchors, not old edges."""
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    from wardrobe_tension import open_curve
    from wardrobe_motion178_controls import bind_render_surface,render_surface_target
    tree=tree_for(bpy.data.objects['MF_studio_adult_body']);target=render_surface_target();record={}
    for sign in (-1,1):
        anchors=[]
        for front in (True,False):
            samples=[(-1.08,-5.28),(-.6,-4.6),(.15,-3.7),(.85,-2.8),(1.24,-2.1)]
            if not front:samples=samples[::-1]
            for x,z in samples:
                origin=Vector((sign*x,-4 if front else 4,z));direction=Vector((0,1 if front else -1,0))
                h,n,_,_=tree.ray_cast(origin,direction,8)
                if h is None:raise ValueError('Missing measured strap anchor')
                anchors.append(h+n*(.11 if sign==1 else .08))
            if front:
                for y in (-.28,.10,.46):
                    h,n,_,_=tree.ray_cast(Vector((sign*1.24,y,2)),Vector((0,0,-1)),6)
                    if h is None:raise ValueError('Missing superior shoulder')
                    anchors.append(h+n*.09)
        path=open_curve(anchors,steps=14);centers=[];normals=[]
        for p in path:
            h,n,_,_=tree.find_nearest(p)
            root=Vector((0,.14,min(-2.9,p.z)))
            if n.dot(h-root)<0:n=-n
            centers.append(h+n*(.11 if sign==1 else .08));normals.append(n)
        # Continuous frames on the measured body surface avoid the folded
        # thin-cloth boundary normals that turned the prior bands into spikes.
        vertices=[];previous=None
        for i,p in enumerate(centers):
            tangent=(centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
            width=tangent.cross(normals[i]).normalized()*.12
            if previous is not None and width.dot(previous)<0:width=-width
            previous=width;vertices.extend([p-width,p+width])
        faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(centers)-1)]
        ob=bpy.data.objects['MF_173_tension_harness_'+str(sign)]
        for m in list(ob.modifiers):
            if m.type in ('SURFACE_DEFORM','ARMATURE'):ob.modifiers.remove(m)
        materials=list(ob.data.materials);data=bpy.data.meshes.new('Measured continuous harness '+str(sign))
        data.from_pydata([tuple(p) for p in vertices],[],faces);data.update()
        for mat in materials:data.materials.append(mat)
        for p in data.polygons:p.use_smooth=True
        attr=data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
        for v,item in zip(data.vertices,attr.data):item.vector=v.co
        ob.data=data;ob.matrix_world=__import__('mathutils').Matrix.Identity(4)
        bind_render_surface(ob,target)
        record[str(sign)]={'vertices':len(vertices),'anchors':[list(p) for p in anchors]}
    # The old adjuster is fitted to the superseded band. Refit its original
    # functional detail after the continuous route passes, not floating here.
    bpy.data.objects['MF_173_strap_adjuster_1'].hide_render=True
    return record


def garment_screen(out):
    import bpy
    import wardrobe_motion178 as base
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe185_motion import animate
    from wardrobe_riding_fit import fit_render
    from mathutils import Vector
    import wardrobe_studio as studio
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation();record=head_control(rig)
    dress_actor(rig);repair(rig,'repair04');upper=upper_garment(rig,mats)
    record['harness']=harness_routes(rig) if out.name.endswith(('upper03','upper04')) else harness_shoulders(rig,upper)
    record['incremental_offset_difference_native']=upper['incremental_offset_difference_native']
    record['neutral_surface_bind_error_native']=upper['neutral_surface_bind_error_native']
    boots(rig,mats);animate(rig)
    scene=bpy.context.scene;scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for frame in ((169,217) if out.name.endswith(('upper03','upper04')) else (169,193,217)):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=studio.torso_matrix(-2.7)@Vector((0,.15,-2.4))
        for angle,label in ((0,'front'),(90,'side'),(270,'other'),(180,'rear')):
            fit_render(out,'upper-'+label+'-%03d'%frame,angle,tuple(center),7.2,(600,660))
    if out.name.endswith(('upper03','upper04')):
        clay=bpy.data.materials.new('185 diagnostic no-bump clay');clay.diffuse_color=(.35,.35,.35,1)
        clay.use_nodes=True;clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.35,.35,.35,1)
        upper.data.materials[0]=clay
        fit_render(out,'upper-clay-217',90,tuple(center),7.2,(600,660))
        if out.name.endswith('upper04'):
            upper.hide_render=True
            for sign in (-1,1):bpy.data.objects['MF_173_tension_harness_'+str(sign)].hide_render=True
            bpy.context.view_layer.material_override=clay
            fit_render(out,'body-clay-217',90,tuple(center),7.2,(600,660))
            bpy.context.view_layer.material_override=None
    base.check_protected();record.update({'protected_local_data_exact':True,'visual_gate':'NOT_RUN','new_upper_vertices':len(upper.data.vertices)})
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')


def audit(out):
    import bpy
    import numpy as np
    from mathutils import Vector
    import wardrobe_motion178 as base
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe185_motion import animate
    from wardrobe_riding_fit import fit_render
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation();dress_actor(rig)
    attached=boots(rig,mats);repair(rig,'repair04')
    names=('MF_continuous_head_neck','MF_aimable_eye_Left','MF_aimable_eye_Right',
           'MF_natural147_hair_temples','MF_natural147_hair_retarget','MF_studio_adult_body')
    inventory={}
    for name in names:
        ob=bpy.data.objects[name]
        bounds=[ob.matrix_world@Vector(p) for p in ob.bound_box]
        inventory[name]={'parent':ob.parent.name if ob.parent else None,
            'matrix_world':[list(r) for r in ob.matrix_world],
            'bounds':[[min(p[k] for p in bounds) for k in range(3)],[max(p[k] for p in bounds) for k in range(3)]],
            'constraints':[{'type':c.type,'target':c.target.name if getattr(c,'target',None) else None,
                            'bone':getattr(c,'subtarget',None)} for c in ob.constraints],
            'modifiers':[(m.name,m.type) for m in ob.modifiers]}
    head=bpy.data.objects[names[0]]
    np.savez_compressed(out/'head-basis.npz',points=np.array([head.matrix_world@v.co for v in head.data.vertices]))
    animate(rig);scene=bpy.context.scene;scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for frame in (1,193,217):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for angle,label in ((0,'front'),(90,'side')):
            fit_render(out,'body-'+label+'-%03d'%frame,angle,(0,.1,-5.2),15.8,(600,900))
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'inventory':inventory,'boots':attached,
        'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones},
        'protected_local_data_exact':True,'visual_gate':'NOT_RUN'},indent=2)+'\n')


def gaze_screen(out):
    import bpy
    import numpy as np
    import wardrobe_motion178 as base
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe185_motion import animate
    from wardrobe_riding_fit import fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    import wardrobe_studio as studio
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();rig,mats,_=base.clean_foundation()
    body=bpy.data.objects['MF_studio_adult_body']
    def points():
        bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        p=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear();return p
    before=points();record=head_control(rig);after=points()
    record['neutral_evaluated_body_error']=float(np.max(abs(after-before)))
    if record['neutral_evaluated_body_error']>2e-5:raise ValueError('Neutral body/head changed')
    dress_actor(rig);repair(rig,'repair04');animate(rig)
    scene=bpy.context.scene;scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for frame in (169,193,217):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=studio.torso_matrix(-2.7)@__import__('mathutils').Vector((0,.15,-1.1))
        for angle,label in ((0,'front'),(90,'side'),(270,'other'),(180,'rear')):
            fit_render(out,'neck-'+label+'-%03d'%frame,angle,tuple(center),5.8,(600,660))
    base.check_protected();record.update({'protected_local_data_exact':True,'visual_gate':'NOT_RUN','cloth_replay':'NOT_RUN'})
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
