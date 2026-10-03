"""Fixed private exchange171 correction jobs; no executable payloads admitted."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wardrobe_refinement import BASE, neutral, tree_for
from wardrobe_riding_fit import digest

SOURCE = BASE / 'wardrobe170-seal03/dressed-fit.blend'
SOURCE_SHA = 'f146fc11bada5c1bb47c4880f5d615d8a4896fa8009ad09535425e11734f0280'
OPERATIONS = ('inspect01', 'inspect02', 'diagnosis01', 'diagnosis02', 'diagnosis03', 'diagnosis04', 'diagnosis05', 'preview01', 'preview02', 'preview03', 'preview04', 'preview05', 'preview06', 'preview07', 'preview08', 'preview09', 'seal01', 'verify01')


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Only fixed reviewed correction operations admitted')
    if SOURCE.is_symlink() or not SOURCE.is_file() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned source mismatch')
    out = BASE / ('wardrobe171-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite evidence')
    if job['operation'].startswith('verify'):
        selected = BASE / 'wardrobe171-seal01'
        result = json.loads((selected/'result.json').read_text())
        path = selected/'dressed-fit.blend'
        if path.is_symlink() or digest(path) != result['native_sha256']:
            raise ValueError('Selected native mismatch')
    return out


def inspect(out):
    import bpy
    from wardrobe_riding_fit import neutral_surface
    body = bpy.data.objects['MF_studio_adult_body']
    surface = neutral_surface(body)
    rows = []
    for z in (-1., -1.6, -2., -2.5, -3., -4., -5., -6., -7.):
        pts = [p for p, _ in surface if abs(p.z-z)<.12 and abs(p.x)<2.]
        rows.append({'z':z,'bounds':[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)] if pts else None})
    materials = []
    for index, mat in enumerate(body.data.materials):
        faces=[p for p in body.data.polygons if p.material_index==index]
        materials.append({'index':index,'name':mat.name,'faces':len(faces),
                         'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in mat.node_tree.nodes] if mat.use_nodes else []})
    rig=bpy.data.objects['MF_body156_fit_rig']
    bones={n:{'head':list(rig.matrix_world@rig.data.bones[n].head_local),'tail':list(rig.matrix_world@rig.data.bones[n].tail_local)} for n in rig.data.bones.keys() if any(s in n.lower() for s in ('arm','shoulder','chest'))}
    (out/'inspection.json').write_text(json.dumps({'body_slices':rows,'materials':materials,'attributes':[(a.name,a.data_type,a.domain) for a in body.data.attributes],'bones':bones},indent=2)+'\n')


def follow_body(ob):
    import bpy
    follow=ob.modifiers.new('Static evaluated-body cloth support','SURFACE_DEFORM')
    follow.target=bpy.data.objects['MF_fit_pose_skin_support']
    bpy.context.view_layer.objects.active=ob;ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.update();bpy.ops.object.surfacedeform_bind(modifier=follow.name)
    assert follow.is_bound
    sub=ob.modifiers.new('Continuous fabric surface','SUBSURF');sub.levels=2


def cloth_thickness(ob):
    # Fit the ONE fabric surface before constructing its two sides. Fitting
    # both solidified layers to one offset collapses them into z-fighting.
    thick=ob.modifiers.new('Cloth edge thickness','SOLIDIFY');thick.thickness=.018


def body_skin_blend(z):
    t=max(0.,min(1.,(-.35-z)/.85))
    return t*t*(3-2*t)


def continuous_waist_belt():
    """A vertical leather band, not a nearest-projected horizontal rim."""
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    old=bpy.data.objects['MF_fit_waist_belt'];mat=old.data.materials[0]
    old.hide_render=True;old.name='MF_171_rejected_waist_belt'
    tree=tree_for(bpy.data.objects['MF_studio_adult_body']);points=[];faces=[];n=64
    for z in (-4.98,-5.08,-5.28,-5.38):
        for i in range(n):
            a=math.tau*i/n;direction=Vector((math.sin(a),-math.cos(a),0));center=Vector((0,.12,z))
            hit,_,_,_=tree.ray_cast(center,direction,3.)
            assert hit is not None
            points.append(tuple(hit+direction*.24))
    for j in range(3):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
    from wardrobe_riding_fit import bind_torso
    belt=mesh('MF_fit_waist_belt',points,faces,mat);bind_torso(belt,bpy.data.objects['MF_body156_fit_rig'])
    belt.modifiers.new('Continuous vertical leather surface','SUBSURF').levels=2
    contact=belt.modifiers.new('Vertical band posed garment clearance','SHRINKWRAP');contact.target=bpy.data.objects['MF_fit_tunic'];contact.wrap_method='NEAREST_SURFACEPOINT';contact.wrap_mode='OUTSIDE_SURFACE';contact.offset=.10
    belt.modifiers.new('Leather thickness after fitting','SOLIDIFY').thickness=.035
    return 'Continuous vertical body-supported waist band; no collapsed horizontal rim'


def garment_pattern():
    """Independent sewn sleeves, torso and vented flare, not axilla bridges."""
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    body=bpy.data.objects['MF_studio_adult_body'];tree=tree_for(body)
    old=bpy.data.objects['MF_fit_tunic'];mats=list(old.data.materials)
    old.hide_render=True;old.name='MF_171_rejected_flap_tunic'
    # The upper pattern is fitted; ease grows below the belt. A short side
    # vent opens the hem rather than sewing a skirt across astride legs.
    rings=[(-2.02,1.88,.83),(-2.40,1.78,1.00),(-2.9,1.59,1.16),(-3.4,1.48,1.16),(-4.,1.38,1.07),(-4.7,1.31,.96),(-5.25,1.38,1.07),(-5.8,1.60,1.28),(-6.4,1.77,1.32),(-7.,1.87,1.29),(-7.45,1.94,1.22)]
    points=[];faces=[];n=64
    for j,(z,rx,ry) in enumerate(rings):
        for i in range(n):
            a=2*math.pi*i/n;p=Vector((rx*math.sin(a),.12-ry*math.cos(a),z))
            if j<7:
                hit,normal,_,_=tree.ray_cast(Vector((0,.12,z)),Vector((math.sin(a),-math.cos(a),0)),3.)
                if hit is not None and abs(hit.x)<1.9:
                    p=hit+normal*(.11 if j<5 else .16)
            if j==0:p.z+=.55*abs(math.sin(a))+.12*max(0.,-math.cos(a))
            if j>=7:
                fold=.075*math.sin(6*a+.4)*((j-6)/4)
                p.x+=fold*math.sin(a);p.y-=fold*math.cos(a)
            points.append(tuple(p))
    for j in range(len(rings)-1):
        for i in range(n):
            if j>=8 and i in (15,16,47,48):continue
            a=j*n+i;b=j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
    ob=mesh('MF_fit_tunic',points,faces,mats[0]);ob.data.materials.append(mats[2])
    for p in ob.data.polygons:
        column=p.vertices[0]%n
        if column<3 or column>=61:p.material_index=1
    follow_body(ob)
    cover=ob.modifiers.new('Upper tunic actual skin coverage','SHRINKWRAP');cover.target=body;cover.wrap_method='NEAREST_SURFACEPOINT';cover.wrap_mode='OUTSIDE_SURFACE';cover.offset=.10
    group=ob.vertex_groups.new(name='Upper pattern coverage only')
    for vertex in ob.data.vertices:
        w=max(0.,min(1.,(vertex.co.z+5.5)/.7))
        if w:group.add([vertex.index],w,'REPLACE')
    cover.vertex_group=group.name
    cloth_thickness(ob)
    rig=bpy.data.objects['MF_body156_fit_rig'];sleeves=[]
    for side in ('L','R'):
        upper=rig.data.bones['upperarm.'+side];fore=rig.data.bones['forearm.'+side]
        start=rig.matrix_world@upper.head_local;elbow=rig.matrix_world@upper.tail_local;end=rig.matrix_world@fore.tail_local
        points=[];faces=[];n=32;rows=25
        for j in range(rows):
            t=j/(rows-1);s=-.14+t*1.84
            if s<=1:center=start.lerp(elbow,s);axis=(elbow-start).normalized()
            else:center=elbow.lerp(end,s-1);axis=(end-elbow).normalized()
            across=axis.cross(Vector((0,1,0))).normalized();depth=axis.cross(across).normalized()
            radius=(.30+.28*math.sin(min(1.,max(0.,(s+.14)/.24))*math.pi/2)) if s<.10 else .58-.17*max(0.,(s-.1)/1.6)
            for i in range(n):
                a=2*math.pi*i/n;direction=across*math.cos(a)+depth*math.sin(a)
                p=center+direction*radius
                # Smooth sewn sleeve, not the nearest-point jumps of a skin
                # copy. The short rounded shoulder cap overlaps the torso.
                points.append(tuple(p))
        for j in range(rows-1):
            for i in range(n):
                a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
        sleeve=mesh('MF_171_fitted_sleeve_'+side,points,faces,mats[0]);follow_body(sleeve)
        # A bone-axis radial fit avoids medial nearest-point jumps at the
        # axilla. Surface deformation follows the evaluated pose; do not
        # reproject the whole sleeve onto a different nearby body region.
        cloth_thickness(sleeve)
        sleeves.append(sleeve)
    return {'method':'Separate coherent sewn sleeve patterns, body-following torso and softly flared vented lower tunic','anatomy_changed':False,'new_sleeves':[o.name for o in sleeves]}


def rugged_fabric():
    import bpy
    for name in ('MF_170_indigo_woven','MF_170_deep_indigo_tailored_panel','MF_170_soft_indigo_scarf'):
        mat=bpy.data.materials[name];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=tuple(bsdf.inputs['Base Color'].default_value)
        bsdf.inputs['Roughness'].default_value=.94;bsdf.inputs['Sheen Weight'].default_value=.07
        coords=nodes.new('ShaderNodeTexCoord')
        broad=nodes.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=2.2;broad.inputs['Detail'].default_value=3.;broad.inputs['Roughness'].default_value=.75
        links.new(coords.outputs['Object'],broad.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=tuple(c*.65 for c in base[:3])+(1.,)
        ramp.color_ramp.elements[1].position=.80;ramp.color_ramp.elements[1].color=tuple(c*1.8+.007 for c in base[:3])+(1.,)
        links.new(broad.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],bsdf.inputs['Base Color'])
        warp=nodes.new('ShaderNodeTexWave');warp.bands_direction='X';warp.inputs['Scale'].default_value=34;warp.inputs['Distortion'].default_value=2.8
        weft=nodes.new('ShaderNodeTexWave');weft.bands_direction='Z';weft.inputs['Scale'].default_value=39;weft.inputs['Distortion'].default_value=1.9
        for field in (warp,weft):links.new(coords.outputs['Object'],field.inputs['Vector'])
        multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';links.new(warp.outputs['Fac'],multiply.inputs[0]);links.new(weft.outputs['Fac'],multiply.inputs[1])
        bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.065;bump.inputs['Distance'].default_value=.006
        links.new(multiply.outputs[0],bump.inputs['Height']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    return 'Worn uneven indigo dye, rough broken warp/weft and restrained sheen; not dirt or cultural ornament'


def skin_continuity():
    """Reuse skin-only atlas regions; never project eyes/lips onto the body."""
    import bpy
    from character_assembly import material
    body=bpy.data.objects['MF_studio_adult_body'];source=body.data.materials[0]
    atlas=next(n.image for n in source.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name=='skin-authored.png')
    skin=material('MF_171_exposed_painterly_skin',(.42,.23,.135))
    def atlas_nodes(mat):
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        coords=nodes.new('ShaderNodeAttribute');coords.attribute_name='MF_fit_source_skin_coordinates'
        xyz=nodes.new('ShaderNodeSeparateXYZ');links.new(coords.outputs['Vector'],xyz.inputs[0])
        uv=nodes.new('ShaderNodeCombineXYZ')
        for k,key in enumerate(('X','Z')):
            scale=nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=.15;links.new(xyz.outputs[key],scale.inputs[0])
            wrap=nodes.new('ShaderNodeMath');wrap.operation='PINGPONG';wrap.inputs[1].default_value=.23;links.new(scale.outputs[0],wrap.inputs[0])
            add=nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=.015;links.new(wrap.outputs[0],add.inputs[0]);links.new(add.outputs[0],uv.inputs[k])
        tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.extension='EXTEND';links.new(uv.outputs[0],tex.inputs['Vector'])
        tint=nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1.;tint.inputs[2].default_value=(.90,.90,.90,1);links.new(tex.outputs['Color'],tint.inputs[1])
        return tint.outputs[0]
    color=atlas_nodes(skin);bsdf=skin.node_tree.nodes.get('Principled BSDF');skin.node_tree.links.new(color,bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.78
    body.data.materials[3]=skin;body.data.materials[4]=skin
    # Blend the new body material into the derivative lower-neck shader;
    # face/groom/source materials stay untouched. The same detail enters
    # both slots rather than keeping a hard flat donor patch at the neckline.
    copied=source.copy();copied.name='MF_171_lower_neck_continuity';body.data.materials[0]=copied
    p=next(n for n in copied.node_tree.nodes if n.type=='BSDF_PRINCIPLED');original=p.inputs['Base Color'].links[0].from_socket
    attr=body.data.attributes.new('MF_171_body_skin_blend','FLOAT','POINT')
    for v,item in zip(body.data.vertices,attr.data):
        z=(body.matrix_world@v.co).z;item.value=body_skin_blend(z)
    mask=copied.node_tree.nodes.new('ShaderNodeAttribute');mask.attribute_name=attr.name
    mix=copied.node_tree.nodes.new('ShaderNodeMixRGB');copied.node_tree.links.new(mask.outputs['Fac'],mix.inputs[0]);copied.node_tree.links.new(original,mix.inputs[1]);copied.node_tree.links.new(atlas_nodes(copied),mix.inputs[2]);copied.node_tree.links.new(mix.outputs[0],p.inputs['Base Color'])
    return {'atlas':'Existing accepted atlas02 skin-only lower-left region','face_blend_zero_above_z':-.35,'body_basis_changed':False,'protected_source_material_changed':False}


def full_scarf():
    """Open front, continuous broad rear drape; not a crown ribbon."""
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from character_assembly import mesh
    for name in ('MF_170_authored_open_scarf','MF_170_asymmetric_scarf_end'):bpy.data.objects[name].hide_render=True
    hull=bmesh.new()
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for p in list(ev.data.points)[::max(1,len(ev.data.points)//1600)]:hull.verts.new(o.matrix_world@p.position)
    bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False);hull.verts.ensure_lookup_table();hull.verts.index_update()
    verts=[v.co.copy() for v in hull.verts];faces=[tuple(v.index for v in f.verts) for f in hull.faces]
    hair=BVHTree.FromPolygons(verts,faces);top=max(v.z for v in verts);hull.free()
    cloth=tree_for(bpy.data.objects['MF_fit_tunic']);points=[];faces=[];nu=65;nv=35
    # Open-backed cylindrical hood: continuous crown and broad falling
    # back, no independently expanded corner plates behind the ears.
    for j in range(nv):
        v=j/(nv-1)
        for i in range(nu):
            theta=-1.90+3.80*i/(nu-1)
            radius=.12+1.42*math.sin(min(1.,v/.60)*math.pi/2)+.12*max(0.,(v-.6)/.4)
            z=top+.16-(top+3.35)*v
            x=radius*math.sin(theta);y=.40+(radius*.92)*math.cos(theta)
            p=Vector((x,y,z))
            hit,normal,_,distance=hair.find_nearest(p)
            if hit is not None and z> -2.1 and distance<.7:p=hit+normal*.17
            # The lower veil falls around the groom, not onto the back's
            # nearest triangle. That projection made a horizontal rear spike.
            radial=Vector((math.sin(theta),math.cos(theta),0))
            p+=radial*((.12*math.sin(7*theta+.7*v)+.045*math.sin(11*theta-2*v))*v)
            p.z+=.10*v**4*math.cos(3*theta+.4)
            points.append(tuple(p))
    for j in range(nv-1):
        for i in range(nu-1):
            a=j*nu+i;faces.append((a,a+1,a+nu+1,a+nu))
    mat=bpy.data.materials['MF_170_soft_indigo_scarf'];o=mesh('MF_171_full_open_scarf',points,faces,mat)
    fair=o.modifiers.new('Connected scarf edge fairing','SMOOTH');fair.factor=.5;fair.iterations=8
    o.modifiers.new('Soft broad drape','SUBSURF').levels=2;o.modifiers.new('Scarf edge','SOLIDIFY').thickness=.02
    rig=bpy.data.objects['MF_body156_fit_rig'];attach=o.constraints.new('CHILD_OF');attach.target=rig;attach.subtarget='chest';attach.inverse_matrix=(rig.matrix_world@rig.data.bones['chest'].matrix_local).inverted()
    # Retain the approved asymmetric chest vocabulary but widen the end;
    # this is a connected-looking shoulder wrap, not a new cultural ornament.
    from wardrobe_refinement import authored_wrap
    authored_wrap(mat);end=bpy.data.objects['MF_170_asymmetric_scarf_end.001']
    end.name='MF_171_front_scarf_drape'
    return {'method':'Broad continuous crown-to-back-and-shoulder drape with open front','forehead_hair_preserved':True,'dynamic_cloth_qualified':False}


def build(out,operation):
    import bpy
    from wardrobe_riding_fit import accepted_signature,evaluated_surfaces,fit_straps,fit_render,riding_pose,fit_static_contacts
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    prior=json.loads((SOURCE.parent/'result.json').read_text());protected=accepted_signature(prior['protected_signatures']);basis=coordinates_digest(tuple(v.co) for v in body.data.vertices)
    assert protected==prior['protected_signatures'] and basis==prior['body_basis_digest']
    result={'garment':garment_pattern(),'fabric':rugged_fabric(),'skin':skin_continuity(),'scarf':full_scarf(),'belt':continuous_waist_belt()}
    straps=[o for o in bpy.context.scene.objects if o.name.startswith('MF_fit_shoulder_harness')]
    fit_straps(straps,[bpy.data.objects['MF_fit_tunic']])
    for o in straps:
        m=o.modifiers.get('Static strap-to-garment registration')
        if m:
            m.target=bpy.data.objects['MF_fit_tunic']
        # Fitting may make a band follow tiny local cloth facets. Fair the
        # SINGLE leather surface before its thickness, not both layers.
        fair=o.modifiers.new('Continuous fitted leather band','SMOOTH');fair.factor=.75;fair.iterations=10
        bpy.context.view_layer.objects.active=o
        while list(o.modifiers).index(fair)>list(o.modifiers).index(next(m for m in o.modifiers if m.type=='SOLIDIFY')):
            bpy.ops.object.modifier_move_up(modifier=fair.name)
    bpy.context.scene.cycles.samples=20
    horse=[o for o in bpy.context.scene.objects if o.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_'))]
    contacts=[o for o in bpy.context.scene.objects if o.get('source_object')]
    states={o.name:o.hide_render for o in horse}
    for o in horse:o.hide_render=True
    if operation.startswith('diagnosis'):
        from character_assembly import material
        visible=[{'name':o.name,'materials':[m.name if m else None for m in o.data.materials]} for o in bpy.context.scene.objects if not o.hide_render and o.type=='MESH']
        bpy.context.scene.view_layers[0].material_override=material('MF_171_geometry_diagnosis',(.3,.3,.3))
        fit_render(out,'clay-upper',-40,(0,.15,-1.7),7.,(800,850))
        if operation in ('diagnosis02','diagnosis03'):fit_render(out,'clay-rear',140,(0,.15,-3.4),11.,(800,850))
        if operation in ('diagnosis04','diagnosis05'):
            riding_pose(rig);bpy.context.view_layer.update()
            fit_render(out,'clay-reach',-40,(-.1,-2.5,-6),11.,(800,850))
        (out/'diagnosis.json').write_text(json.dumps({'visible_meshes':visible,'scope':'Untextured geometry control, not new acceptance'},indent=2)+'\n')
        return
    targeted=operation in ('preview08','preview09')
    for label,angle in ([('front',0)] if targeted else [('front',0),('side',90),('rear',180)]):fit_render(out,'standing-'+label,angle)
    if not targeted:
        for label,angle in [('left',-40),('right',40)]:fit_render(out,'upper-'+label,angle,(0,.15,-1.7),7.,(800,850))
    if operation in ('preview05','preview06','preview07','seal01'):fit_render(out,'upper-front',0,(0,.15,-1.7),7.,(800,850))
    for o in horse:o.hide_render=states[o.name]
    leather=bpy.data.objects['MF_fit_waist_belt'].data.materials[0]
    riding_pose(rig);bpy.context.view_layer.update();fit_static_contacts(contacts,rig,leather)
    if not targeted:
        for label,angle in [('side',90),('front-quarter',-40),('rear-quarter',140)]:fit_render(out,'mounted-'+label,angle,(0,-1,-10),29,(1000,700) if label=='side' else (540,900))
    if operation in ('preview05','preview06','preview07','preview08','preview09','seal01'):
        if not targeted:fit_render(out,'mounted-opposite-side',-90,(0,-1,-10),29,(1000,700))
        fit_render(out,'mounted-sleeve-interface',-40,(-.1,-2.5,-6),11.,(800,850))
        fit_render(out,'mounted-sleeve-opposite',40,(-.1,-2.5,-6),11.,(800,850))
        riding_pose(rig,.75);bpy.context.view_layer.update();fit_static_contacts(contacts,rig,leather)
        fit_render(out,'mounted-partial-lean',90,(0,-1,-10),29,(1000,700))
        riding_pose(rig);bpy.context.view_layer.update();fit_static_contacts(contacts,rig,leather)
    assert accepted_signature(protected)==protected and coordinates_digest(tuple(v.co) for v in body.data.vertices)==basis
    assert digest(SOURCE)==SOURCE_SHA
    garments=[bpy.data.objects[n] for n in ('MF_fit_tunic','MF_171_fitted_sleeve_L','MF_171_fitted_sleeve_R')]
    assert all(o.modifiers[-1].type=='SOLIDIFY' for o in garments)
    result.update({'operation':operation,'parent_sha256':SOURCE_SHA,'protected_signatures':protected,'body_basis_digest':basis,'protected_data_exact':True,'body_basis_exact':True,'source_unchanged':True,'cloth_thickness_after_fitting':True,'static_tail_curve_digest':data_signature(bpy.data.objects['MF_170_tail_fibers']),'handler_sha256':digest(Path(__file__)),'visual_gate':'NOT_RUN','Director_acceptance':'PENDING'})
    if operation.startswith('seal'):
        import numpy as np
        names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type=='MESH'];np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
        for block in bpy.data.texts:block.use_module=False
        bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True);result['native_sha256']=digest(out/'dressed-fit.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def verify(out):
    import bpy,numpy as np
    from wardrobe_riding_fit import accepted_signature,evaluated_surfaces,fit_render
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    selected=BASE/'wardrobe171-seal01';result=json.loads((selected/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(selected/'dressed-fit.blend'),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    reference=np.load(selected/'evaluated-surfaces.npz',allow_pickle=False);actual=evaluated_surfaces(reference.files)
    errors={n:float(np.max(np.abs(actual[n]-reference[n]))) if actual[n].shape==reference[n].shape else None for n in reference.files}
    protected=accepted_signature(result['protected_signatures'])==result['protected_signatures']
    basis=coordinates_digest(tuple(v.co) for v in body.data.vertices)==result['body_basis_digest']
    tail=data_signature(bpy.data.objects['MF_170_tail_fibers'])==result['static_tail_curve_digest']
    assert protected and basis and tail and all(v is not None and v<2e-5 for v in errors.values())
    tunic=bpy.data.objects['MF_fit_tunic'];cover=tunic.modifiers['Upper tunic actual skin coverage'];old=cover.offset
    cover.offset=old+.025;bpy.context.view_layer.update();delta=float(np.max(np.abs(evaluated_surfaces([tunic.name])[tunic.name]-actual[tunic.name])))
    cover.offset=old;bpy.context.view_layer.update();rollback=float(np.max(np.abs(evaluated_surfaces([tunic.name])[tunic.name]-actual[tunic.name])))
    assert delta>1e-5 and rollback<2e-5
    fit_render(out,'reopened-mounted-side',90,(0,-1,-10),29,(1000,700))
    neutral(rig)
    for o in bpy.context.scene.objects:
        if o.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):o.hide_render=True
    fit_render(out,'reopened-upper-front',0,(0,.15,-1.7),7.,(800,850))
    (out/'result.json').write_text(json.dumps({'reopened':True,'protected_signatures_exact':protected,'body_basis_exact':basis,'static_tail_curve_data_exact':tail,'evaluated_local_surface_max_errors':errors,'surface_tolerance':2e-5,'controlled_garment_revision_max_delta':delta,'revision_rollback_max_delta':rollback,'source_unchanged':digest(SOURCE)==SOURCE_SHA,'appearance_acceptance':'PENDING'},indent=2)+'\n')


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir()
    if job['operation']=='verify01':
        verify(out)
        return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    neutral(bpy.data.objects['MF_body156_fit_rig'])
    if job['operation'].startswith('inspect'):inspect(out)
    else:build(out,job['operation'])


if __name__=='__main__':main()
