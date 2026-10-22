"""Fixed costume173 construction; input contains only an operation enum.

Private pose-specific authoring, not a runtime cloth or production-motion rig.
Accepted anatomy/groom are immutable. No external asset scripts are enabled.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wardrobe_refinement import BASE, neutral, tree_for
from wardrobe_riding_fit import digest
from wardrobe_balance import single_surface_mesh, outer_ray_radius

SOURCE = BASE / 'wardrobe172-seal01/dressed-fit.blend'
SOURCE_SHA = 'd003f791b3f0cc00cfac72957db7877ced45a66e43d274f198a0bb911fc3dfcd'
OPERATIONS = tuple('preview%02d'%i for i in range(1,51)) + ('inspect01','inspect02','inspect03','clothprobe01','seal01', 'verify01')


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Only fixed reviewed operations admitted')
    if SOURCE.is_symlink() or not SOURCE.is_file() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned source mismatch')
    out = BASE / ('wardrobe173-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite evidence')
    if job['operation'] == 'verify01':
        selected = BASE / 'wardrobe173-seal01'
        native = selected / 'dressed-fit.blend'
        result = json.loads((selected / 'result.json').read_text())
        if native.is_symlink() or digest(native) != result['native_sha256']:
            raise ValueError('Selected native mismatch')
    if job['operation'] in ('seal01','verify01'):source_binding()
    return out


def source_binding():
    """Validate a pre-dispatch source manifest with fixed admitted paths."""
    path=BASE/'wardrobe173-operating/source-binding.json'
    if path.is_symlink() or not path.is_file():raise ValueError('Freeze selected source binding before dispatch')
    binding=json.loads(path.read_text());root=Path(__file__).resolve().parents[4]
    expected={str(p.relative_to(root)) for p in Path(__file__).resolve().parent.glob('*.py')}
    expected.add('scripts/package_wardrobe_studio.py')
    rows=binding['source_files']
    if len(rows)!=len(expected) or {row['path'] for row in rows}!=expected:raise ValueError('Unexpected source manifest paths')
    for row in rows:
        source=root/row['path']
        if source.is_symlink() or digest(source)!=row['sha256']:raise ValueError('Frozen selected source changed')
    return binding


def smoothstep(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def wrinkle(z, phase=0.):
    """Unequal localized compression folds; never uniformly noisy anatomy."""
    return .5+.5*math.sin(13*z+phase+1.1*math.sin(3.7*z))


def torso_weights(z):
    chest=min(1.,max(0.,(z+4.8)/1.6));pelvis=min(1.,max(0.,(-z-4.8)/1.2))
    return {'chest':chest,'spine':1-chest-pelvis,'pelvis':pelvis}


def torso_matrix(z):
    import bpy
    from mathutils import Matrix
    rig=bpy.data.objects['MF_body156_fit_rig'];world=rig.matrix_world
    result=Matrix(((0.,)*4,)*4)
    for name,w in torso_weights(z).items():
        if w:
            delta=world@rig.pose.bones[name].matrix@rig.data.bones[name].matrix_local.inverted()@world.inverted()
            result+=delta*w
    return result


def torso_point(p):
    return torso_matrix(p.z)@p


def make_materials():
    import bpy
    from character_assembly import material
    result = {}
    colors = {'cloth':(.010,.023,.057), 'scarf':(.009,.023,.076),
              'panel':(.005,.011,.028), 'pants':(.014,.021,.032),
              'leather':(.105,.042,.018), 'boot':(.057,.028,.015),
              'seam':(.018,.038,.072), 'thread':(.20,.135,.064),
              'metal':(.19,.15,.095), 'sole':(.025,.020,.015)}
    for label, color in colors.items():
        mat = material('MF_173_'+label, color)
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        bsdf=nodes.get('Principled BSDF')
        bsdf.inputs['Roughness'].default_value = .87 if label not in ('leather','boot','metal') else .59
        bsdf.inputs['Sheen Weight'].default_value = .17 if label in ('cloth','scarf','pants') else 0.
        bsdf.inputs['Specular IOR Level'].default_value=.20 if label in ('cloth','scarf','panel','pants') else .35
        if label=='metal':bsdf.inputs['Metallic'].default_value=.75
        if label in ('cloth','scarf','panel','pants','leather','boot'):
            coords=nodes.new('ShaderNodeAttribute');coords.attribute_name='MF_173_material_coords'
            stretched=nodes.new('ShaderNodeVectorMath');stretched.operation='MULTIPLY';stretched.inputs[1].default_value=(2.2,2.2,.65)
            links.new(coords.outputs['Vector'],stretched.inputs[0])
            noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4.8
            noise.inputs['Detail'].default_value=3.;noise.inputs['Roughness'].default_value=.7
            links.new(stretched.outputs['Vector'],noise.inputs['Vector'])
            ramp=nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[0].color=(*[c*.57 for c in color],1)
            ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*[c*1.65 for c in color],1)
            links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
            grain=nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=78 if label in ('leather','boot') else 95
            grain.inputs['Detail'].default_value=2.
            links.new(coords.outputs['Vector'],grain.inputs['Vector'])
            bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.27;bump.inputs['Distance'].default_value=.012
            links.new(grain.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
            fleck=nodes.new('ShaderNodeValToRGB')
            fleck.color_ramp.elements[0].position=.30;fleck.color_ramp.elements[0].color=(.42,.45,.52,1)
            fleck.color_ramp.elements[1].position=.72;fleck.color_ramp.elements[1].color=(1.55,1.43,1.22,1)
            links.new(grain.outputs['Fac'],fleck.inputs[0])
            mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.58
            links.new(ramp.outputs['Color'],mix.inputs[1]);links.new(fleck.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],bsdf.inputs['Base Color'])
            if label in ('cloth','scarf','panel','pants'):
                warp=nodes.new('ShaderNodeTexWave');warp.wave_type='BANDS';warp.bands_direction='X';warp.inputs['Scale'].default_value=115;warp.inputs['Distortion'].default_value=2.2
                weft=nodes.new('ShaderNodeTexWave');weft.wave_type='BANDS';weft.bands_direction='Z';weft.inputs['Scale'].default_value=130;weft.inputs['Distortion'].default_value=1.5
                for wave in (warp,weft):links.new(coords.outputs['Vector'],wave.inputs['Vector'])
                weave=nodes.new('ShaderNodeMath');weave.operation='MULTIPLY';links.new(warp.outputs['Fac'],weave.inputs[0]);links.new(weft.outputs['Fac'],weave.inputs[1])
                fibre=nodes.new('ShaderNodeBump');fibre.inputs['Strength'].default_value=.18;fibre.inputs['Distance'].default_value=.007
                links.new(weave.outputs[0],fibre.inputs['Height']);links.new(bump.outputs['Normal'],fibre.inputs['Normal']);links.new(fibre.outputs['Normal'],bsdf.inputs['Normal'])
            wear=nodes.new('ShaderNodeAttribute');wear.attribute_name='MF_173_contact_wear'
            wear_mix=nodes.new('ShaderNodeMixRGB');wear_mix.blend_type='MIX';links.new(wear.outputs['Fac'],wear_mix.inputs[0]);links.new(mix.outputs[0],wear_mix.inputs[1]);wear_mix.inputs[2].default_value=(*[c*1.65 for c in color],1.)
            links.new(wear_mix.outputs[0],bsdf.inputs['Base Color'])
            rough=nodes.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.49 if label in ('leather','boot') else .76
            rough.inputs['To Max'].default_value=.82 if label in ('leather','boot') else .96
            links.new(noise.outputs['Fac'],rough.inputs['Value']);links.new(rough.outputs['Result'],bsdf.inputs['Roughness'])
        result[label]=mat
    from wardrobe_painterly import augment
    for label in ('cloth','scarf','panel','pants'):augment(result[label],.18 if label in ('cloth','scarf') else .10)
    return result


def border_seams(ob,mat):
    """Follow actual garment boundaries rather than guessed floating loops."""
    import bpy,bmesh
    flags=[(m,m.show_viewport) for m in ob.modifiers if m.type=='SOLIDIFY']
    for m,_ in flags:m.show_viewport=False
    bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
    bm=bmesh.new();bm.from_mesh(data);ev.to_mesh_clear()
    for m,state in flags:m.show_viewport=state
    bpy.context.view_layer.update();bm.verts.ensure_lookup_table();bm.verts.index_update()
    adjacency={}
    for e in bm.edges:
        if e.is_boundary:
            a,b=(v.index for v in e.verts)
            adjacency.setdefault(a,set()).add(b);adjacency.setdefault(b,set()).add(a)
    pending=set(adjacency);paths=[]
    while pending:
        first=min(pending);path=[first];pending.remove(first);previous=None;current=first
        while True:
            options=[i for i in adjacency[current] if i!=previous and (i in pending or i==first)]
            if not options:break
            next_=min(options)
            if next_==first:path.append(first);break
            pending.remove(next_);path.append(next_);previous,current=current,next_
        if len(path)>4:paths.append([tuple(ob.matrix_world@(bm.verts[i].co+bm.verts[i].normal*.008)) for i in path])
    bm.free()
    for i,path in enumerate(paths):line(ob.name+'_seam_'+str(i),path,mat,.0045 if 'scarf' in ob.name else .007)


def set_surface(name, data, thickness=.015):
    import bpy
    from mathutils import Matrix
    ob=bpy.data.objects.get(name)
    if ob is None:
        ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob)
    else:
        old=ob.data;ob.data=data
        if old.users==0:bpy.data.meshes.remove(old)
    ob.matrix_world=Matrix.Identity(4);ob.hide_render=False
    if not ob.modifiers and thickness:
        ob.modifiers.new('Thickness after single-surface construction','SOLIDIFY').thickness=thickness
    ob['qualification']='Prescribed static pose derivative; not continuously simulated cloth'
    return ob


def panel(name, points, faces, mat, thickness=.015, sub=1):
    import bpy
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],faces);data.update()
    old=bpy.data.objects.get(name)
    attr=data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
    prior=old.data.attributes.get('MF_173_material_coords') if old else None
    for i,item in enumerate(attr.data):item.vector=prior.data[i].vector if prior and len(prior.data)==len(attr.data) else data.vertices[i].co
    data.materials.append(mat)
    for f in data.polygons:f.use_smooth=True
    ob=set_surface(name,data,thickness)
    if sub and not any(m.type=='SUBSURF' for m in ob.modifiers):
        mod=ob.modifiers.new('Major-fold surface continuity','SUBSURF');mod.levels=sub
        bpy.context.view_layer.objects.active=ob
        while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    return ob


def line(name, points, mat, radius=.012):
    import bpy
    from mathutils import Matrix
    old=bpy.data.objects.get(name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=2
    data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1.)
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);data.materials.append(mat)
    ob.matrix_world=Matrix.Identity(4)
    return ob


def sculpt_fabric(mats):
    """Visible derivatives carry cloth folds; accepted skin is never edited."""
    import bpy
    for name, label in [('MF_fit_tunic','cloth'),('MF_171_fitted_sleeve_L','cloth'),
                        ('MF_171_fitted_sleeve_R','cloth'),('MF_fit_trousers','pants')]:
        source=bpy.data.objects[name];data=single_surface_mesh(source)
        disabled=[(m,m.show_viewport) for m in source.modifiers if m.type in ('SURFACE_DEFORM','ARMATURE','SHRINKWRAP')]
        for m,_ in disabled:m.show_viewport=False
        bpy.context.view_layer.update();rest=single_surface_mesh(source)
        for m,state in disabled:m.show_viewport=state
        bpy.context.view_layer.update();assert len(rest.vertices)==len(data.vertices)
        coords=data.attributes.get('MF_173_material_coords') or data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
        for v,item in zip(rest.vertices,coords.data):item.vector=v.co
        # Keep evaluated normals before changing the derivative coordinates.
        normals=[v.normal.copy() for v in data.vertices]
        for v,n,rv in zip(data.vertices,normals,rest.vertices):
            p=v.co;rp=rv.co
            if label=='pants':
                # Compression concentrates around knee and tucked boot cuff.
                z=rp.z;band=math.exp(-((z+9.4)/.65)**2)+.7*math.exp(-((z+11.2)/.40)**2)
                ease=.050+.066*band*wrinkle(z,4*rp.x+2*rp.y)
            elif 'sleeve' in name:
                ease=.018+.025*wrinkle(rp.z,5*rp.y)*math.exp(-((rp.z+4.1)/.85)**2)
            else:
                ease=.020+.048*math.exp(-((p.z+5.1)/.7)**2)*wrinkle(p.z,5*p.x)
                ease+=.030*math.exp(-((p.z+6.8)/1.1)**2)*(math.sin(5*p.x+2*p.z)**2)
            v.co=source.matrix_world@(p+n*ease)
        wear=data.attributes.new('MF_173_contact_wear','FLOAT','POINT')
        for rv,item in zip(rest.vertices,wear.data):
            z=rv.co.z
            contact=(math.exp(-((z+9.4)/.55)**2)+.6*math.exp(-((z+11.2)/.28)**2)) if label=='pants' else (math.exp(-((z+4.65)/.6)**2) if 'sleeve' in name else math.exp(-((z+6.85)/.38)**2))
            item.value=.28*contact*(.35+.65*wrinkle(z,7*rv.co.x))
        material_indices=[f.material_index for f in data.polygons]
        data.update();data.materials.clear();data.materials.append(mats[label])
        bpy.data.meshes.remove(rest)
        if name=='MF_fit_tunic':
            data.materials.append(mats['panel'])
            # Original center-panel indices retain the liked construction.
            for f,index in zip(data.polygons,material_indices):f.material_index=min(index,1)
        target=set_surface(name+'_173_visible',data,.018)
        source.hide_render=True
        target['source_control']=source.name
        border_seams(target,mats['seam'])
    bpy.context.view_layer.update()


def settle_scarf(ob,proxy,shirt):
    """Freeze an inexpensive neutral cloth settle; never claim riding physics."""
    import bpy
    source_frame=bpy.context.scene.frame_current;gravity=bpy.context.scene.gravity.copy()
    collisions=[]
    supports=(proxy,shirt,bpy.data.objects['MF_171_fitted_sleeve_L_173_visible'],bpy.data.objects['MF_171_fitted_sleeve_R_173_visible'])
    for source in supports:
        ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());data=bpy.data.meshes.new_from_object(ev,depsgraph=bpy.context.evaluated_depsgraph_get())
        collision=bpy.data.objects.new('MF_173_temporary_cloth_support',data);bpy.context.collection.objects.link(collision)
        collision.matrix_world=source.matrix_world;collision.hide_render=True
        decimate=collision.modifiers.new('Inexpensive construction collision','DECIMATE');decimate.ratio=1. if source==proxy else .18
        collision.modifiers.new('Construction collision','COLLISION');collision.collision.thickness_outer=.018
        collisions.append(collision)
    initial=[v.co.copy() for v in ob.data.vertices]
    pin=ob.vertex_groups.new(name='Construction crown and face opening hold')
    for vertex in ob.data.vertices:
        i,j=divmod(vertex.index,41)
        if j<4 and 37<=i<=43:pin.add([vertex.index],1.,'REPLACE')
    cloth=ob.modifiers.new('Neutral construction cloth settle','CLOTH')
    cloth.settings.quality=10;cloth.settings.mass=.12;cloth.settings.tension_stiffness=16
    cloth.settings.compression_stiffness=16;cloth.settings.shear_stiffness=8;cloth.settings.bending_stiffness=.030
    cloth.settings.tension_damping=8;cloth.settings.compression_damping=8;cloth.settings.shear_damping=8
    cloth.settings.vertex_group_mass=pin.name
    cloth.collision_settings.distance_min=.016;cloth.collision_settings.use_self_collision=True
    cloth.collision_settings.self_distance_min=.015
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=96
    bpy.context.view_layer.objects.active=ob
    while list(ob.modifiers).index(cloth)>0:bpy.ops.object.modifier_move_up(modifier=cloth.name)
    bpy.context.scene.gravity=(0,0,-9.81)
    for frame_number in range(1,97):
        bpy.context.scene.frame_set(frame_number)
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();ev.to_mesh_clear()
    # Extract only the simulated low-resolution surface before smoothing/thickness.
    states=[(m,m.show_viewport) for m in ob.modifiers if m!=cloth]
    for m,_ in states:m.show_viewport=False
    bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    coords=[v.co.copy() for v in me.vertices];ev.to_mesh_clear();assert len(coords)==len(ob.data.vertices)
    ob.modifiers.remove(cloth)
    for v,p in zip(ob.data.vertices,coords):v.co=p
    for m,state in states:m.show_viewport=state
    ob.data.update()
    for collision in collisions:bpy.data.objects.remove(collision,do_unlink=True)
    bpy.context.scene.gravity=gravity;bpy.context.scene.frame_set(source_frame)


def groom_support():
    """Height-local envelope of all hair points, not a whole-groom balloon."""
    import bpy,bmesh
    from wardrobe_groom_envelope import envelope
    points=[]
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        if len(ev.data.points)>2_000_000:raise ValueError('Groom collision complexity cap')
        points.extend(tuple(ob.matrix_world@point.position) for point in ev.data.points)
    vertices,faces=envelope(points)
    ob=bpy.data.objects.get('MF_173_static_groom_clearance')
    if ob is None:
        data=bpy.data.meshes.new('MF_173_static_groom_clearance');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob)
    ob.data.clear_geometry();ob.data.from_pydata(vertices,[],faces);ob.data.update()
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.hide_render=True;ob.hide_set(True)
    bpy.context.view_layer.update();return ob


def fall_wrap_weight(z):return smoothstep((-1.45-z)/1.4)


def wrap_tuck_indices(x,y,row):
    """An interior fold destination, never the exposed border of the wrap."""
    column=40+math.atan2(x,-(y-.14))*80/2.96
    return max(12,min(68,column)),12+10*max(0,min(40,row))/40


def grid_sample(points,i,j,nv=33):
    a,b=math.floor(i),math.floor(j);u,v=i-a,j-b
    return (points[a*nv+b]*(1-u)*(1-v)+points[(a+1)*nv+b]*u*(1-v)
            +points[a*nv+b+1]*(1-u)*v+points[(a+1)*nv+b+1]*u*v)


def wrap_tuck_weight(z):return smoothstep((-1.6-z)/.6)


def shawl_return(u,v):
    """One long chest-crossing end and one shorter underlapping end."""
    if u<.5:
        t=max(0.,min(1.,(.30-u)/.30))
        return 80*t,32*(1-v),1
    t=max(0.,min(1.,(u-.70)/.30))
    return 80-20*t,32*(1-v),-1


def shawl_blend(u):
    return smoothstep((.40-u)/.10) if u<.5 else smoothstep((u-.60)/.10)


def shawl_relief(s,v):
    folds=((.16+.04*math.sin(4*s),.09,.08),
           (.48+.07*math.sin(3*s+.5),.14,.13),
           (.82+.05*math.sin(5*s),.10,.075))
    return sum(a*math.exp(-((v-c)/width)**2) for c,width,a in folds)*(.55+.45*math.sin(math.pi*s))


def rear_ease_weight(u,y):
    return smoothstep((u-.25)/.08)*smoothstep((.75-u)/.08)*smoothstep((y-.25)/.30)


def arrange_scarf_falls(scarf,frame,shirt):
    """Static dressing: draw loose ends forward, under the chest wrap.

    Preserve the settled crown; this intentional garment arrangement is not
    a claim that gravity alone ties or wraps a scarf around its wearer.
    """
    from mathutils import Vector
    inverse=frame.inverted()
    for vertex in scarf.data.vertices:
        p=inverse@vertex.co;w=fall_wrap_weight(p.z)
        if not w:continue
        _,j=divmod(vertex.index,41);v=j/40
        p.x*=1-.48*w
        p.y=p.y*(1-w)+(-1.35+.11*math.sin(5*math.pi*v+.4*p.x))*w
        p.z-=.13*w*(.8+.2*v)
        target=frame@p;hit,n,_,distance=shirt.find_nearest(target)
        if hit is not None and distance<.9 and (target-hit).dot(n)<.055:target=hit+n*.055
        vertex.co=target
    scarf.data.update()


def tuck_scarf_ends(scarf,wrap,frame):
    """Fair the free falls and tuck their ends under the wrapped chest cloth."""
    import bpy
    # Fit the actually smoothed authoring surface. Later subdivision must not
    # pull a fitted return back through the visible wrap.
    data=single_surface_mesh(scarf)
    reference=data.attributes['MF_173_scarf_rest_position'].data
    parameters=data.attributes['MF_173_sheet_parameter'].data
    # This is an intentional overlapping return. Query the smooth single
    # authoring surface, never ambiguous front/back solidified cloth faces.
    from mathutils import Vector
    shirt=tree_for(bpy.data.objects['MF_fit_tunic_173_visible'])
    proxy=bpy.data.objects['MF_173_static_groom_clearance'];groom=tree_for(proxy)
    wrap_points=[wrap.matrix_world@v.co for v in wrap.data.vertices]
    for vertex in data.vertices:
        rest=reference[vertex.index].vector
        uv=parameters[vertex.index].vector;weight=shawl_blend(uv.x)
        if not weight:continue
        # Shorter/right folds must turn UP into the wrap: projecting a long
        # end straight onto the shirt leaves a dangling patch below its hem.
        i,j,layer=shawl_return(uv.x,uv.y)
        i=min(79.999,max(0.,i));j=min(31.999,max(0.,j))
        destination=grid_sample(wrap_points,i,j)
        support_frame=torso_matrix(-2.8);local=support_frame.inverted()@destination
        outward=(support_frame.to_3x3()@Vector((local.x,local.y-.14,0))).normalized()
        target=destination+outward*.035
        if layer==-1:
            hit,n,_,distance=shirt.find_nearest(destination)
            if hit is not None and distance<1.1:target=hit+n*.025
        vertex.co=vertex.co.lerp(target,weight)
        if weight<1:
            local=support_frame.inverted()@vertex.co
            local.x+=(-1 if layer==1 else 1)*.24*math.sin(math.pi*weight)
            vertex.co=support_frame@local
            root=torso_point(Vector((0,.14,local.z)))
            direction=(torso_matrix(local.z).to_3x3()@Vector((local.x,local.y-.14,0))).normalized()
            radius=(vertex.co-root).dot(direction)
            for tree,clearance in ((groom,.045),(shirt,.035)):
                hit,_,_,distance=tree.ray_cast(root,direction,3.)
                if hit is not None and radius<distance+clearance:
                    radius=distance+clearance;vertex.co=root+direction*radius
    data.update()
    for mod in list(scarf.modifiers):
        if mod.type=='SUBSURF':scarf.modifiers.remove(mod)
    set_surface(scarf.name,data,.012)


def construct_scarf(mats):
    """Soft open sheet resting on the groom, with unequal gravity falls."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_fold_transfer import relief
    source=bpy.data.objects['MF_172_folded_head_drape'];frame=source.matrix_world.copy();inv=frame.inverted()
    proxy=groom_support();ev=proxy.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    hair=BVHTree.FromPolygons([inv@proxy.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);ev.to_mesh_clear()
    shirt=tree_for(bpy.data.objects['MF_fit_tunic_173_visible']);skin=tree_for(bpy.data.objects['MF_studio_adult_body'])
    points=[];faces=[];nu=81;nv=41
    top=max((inv@proxy.matrix_world@v.co).z for v in proxy.data.vertices)
    for i in range(nu):
        x=10.6*(i/(nu-1)-.5)
        for j in range(nv):
            v=j/(nv-1);p=Vector((x,-.30+1.70*v-.85*abs(x)/5.3*(1-v),top+.055+.007*math.sin(1.7*i+.8*j)))
            if j<4 and 37<=i<=43:
                hit,n,_,_=hair.ray_cast(p+Vector((0,0,.3)),Vector((0,0,-1)),1.)
                if hit is not None:p=hit+n*.045
            points.append(tuple(frame@p))
    for i in range(nu-1):
        for j in range(nv-1):
            k=i*nv+j;faces.append((k,k+nv,k+nv+1,k+1))
    cache=bpy.data.objects.get('MF_173_neutral_scarf_pattern')
    if cache is None:
        scarf=panel('MF_173_open_scarf',points,faces,mats['scarf'],.012,2)
        for vertex,item in zip(scarf.data.vertices,scarf.data.attributes['MF_173_material_coords'].data):item.vector=(vertex.co.x,0,vertex.co.y)
        settle_scarf(scarf,proxy,bpy.data.objects['MF_fit_tunic_173_visible'])
        # Frozen contact recheck: simulation is not an automatic visual pass.
        for vertex in scarf.data.vertices:
            p=inv@vertex.co;hit,n,_,dist=hair.find_nearest(p)
            if hit is not None and dist<.25 and (p-hit).dot(n)<.025:vertex.co=frame@(hit+n*.040)
        scarf.data.update()
        # Fair only lower simulated gathers; preserve the opening/crown.
        import bmesh
        bm=bmesh.new();bm.from_mesh(scarf.data)
        lower=[v for v in bm.verts if v.co.z<-.8]
        for _ in range(4):bmesh.ops.smooth_vert(bm,verts=lower,factor=.28,use_axis_x=True,use_axis_y=True,use_axis_z=True)
        bm.to_mesh(scarf.data);bm.free()
        for vertex in scarf.data.vertices:
            p=inv@vertex.co;hit,n,_,dist=hair.find_nearest(p)
            if hit is not None and dist<.25 and (p-hit).dot(n)<.025:vertex.co=frame@(hit+n*.040)
        scarf.data.update()
        arrange_scarf_falls(scarf,frame,shirt)
        cache=bpy.data.objects.new('MF_173_neutral_scarf_pattern',scarf.data.copy());bpy.context.collection.objects.link(cache);cache.hide_render=True;cache.hide_set(True)
        cache['qualification']='Frozen neutral construction cloth, not a dynamic cloth cache'
    else:
        coords=[tuple(torso_point(v.co)) for v in cache.data.vertices]
        scarf=panel('MF_173_open_scarf',coords,[tuple(f.vertices) for f in cache.data.polygons],mats['scarf'],.012,2)
    rest=scarf.data.attributes.get('MF_173_scarf_rest_position') or scarf.data.attributes.new('MF_173_scarf_rest_position','FLOAT_VECTOR','POINT')
    uv=scarf.data.attributes.get('MF_173_sheet_parameter') or scarf.data.attributes.new('MF_173_sheet_parameter','FLOAT_VECTOR','POINT')
    for idx,v in enumerate(cache.data.vertices):
        rest.data[idx].vector=v.co
        i,j=divmod(idx,41);uv.data[idx].vector=(i/80,j/40,0)
        scarf.data.attributes['MF_173_material_coords'].data[idx].vector=cache.data.attributes['MF_173_material_coords'].data[idx].vector
    border_seams(scarf,mats['seam'])
    # A folded diagonal fall with unequal gathered crests, not a bib patch.
    points=[];faces=[];nu=81;nv=33
    for i in range(nu):
        s=i/(nu-1);theta=-1.48+3.68*s
        direction=Vector((math.sin(theta),-math.cos(theta),0))
        for j in range(nv):
            v=j/(nv-1)
            top_z=-2.90+1.20*s+.18*abs(math.sin(theta))
            bottom_z=top_z-.90-.24*math.sin(math.pi*s)
            z=bottom_z*(1-v)+top_z*v
            support_frame=torso_matrix(z);center=support_frame@Vector((0,.14,z));ray=support_frame.to_3x3()@direction
            hit,normal,_,_=shirt.ray_cast(center,ray,3.)
            if hit is None:
                hit,normal,_,_=skin.ray_cast(center,ray,2.15)
            if hit is None:hit=support_frame@Vector((1.65*math.sin(theta),.14-1.04*math.cos(theta),z));normal=ray
            # Unequal fold valleys all follow the long diagonal fabric path.
            scan=relief(Vector((1.3*math.sin(theta),.25-.85*math.cos(theta),-.60-1.10*v)))
            fold=.065+shawl_relief(s,v)+.007*math.sin(9*math.pi*v+2*s)**2+scan*.10
            p=hit+ray*fold;p.z-=.26*math.sin(math.pi*s)*(.65+.35*v)
            points.append(tuple(p))
    for i in range(nu-1):
        for j in range(nv-1):
            k=i*nv+j;faces.append((k,k+nv,k+nv+1,k+1))
    wrap=panel('MF_173_diagonal_scarf_fall',points,faces,mats['scarf'],.012,2)
    line('MF_173_scarf_bound_edge',[points[i*nv] for i in range(nu)],mats['seam'],.0045)
    bpy.context.view_layer.update()
    return frame


def catmull(anchors, steps=10):
    result=[]
    for i in range(len(anchors)):
        p0,p1,p2,p3=[anchors[k%len(anchors)] for k in (i-1,i,i+1,i+2)]
        for j in range(steps):
            t=j/steps
            result.append(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    return result


def compression_weight(distance):return smoothstep(1-distance/.32)


def compress_cloth(mats):
    """Static tailoring pressure under actual shoulder-to-belt load paths."""
    import bpy
    from mathutils.kdtree import KDTree
    shirt=tree_for(bpy.data.objects['MF_fit_tunic_173_visible']);supports=[]
    for sign in (-1,1):
        source=bpy.data.objects['MF_fit_shoulder_harness_'+str(sign)]
        disabled=[(m,m.show_viewport) for m in source.modifiers if m.type in ('SUBSURF','SHRINKWRAP','SOLIDIFY')]
        for m,_ in disabled:m.show_viewport=False
        bpy.context.view_layer.update();ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        points=[source.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
        for m,state in disabled:m.show_viewport=state
        bpy.context.view_layer.update()
        for i in range(0,len(points),2):
            p=(points[i]+points[i+1])/2;hit,n,_,dist=shirt.find_nearest(p)
            if hit is not None and dist<1.3:supports.append((hit,n))
    kd=KDTree(len(supports))
    for i,(p,_) in enumerate(supports):kd.insert(p,i)
    kd.balance()
    for name in ('MF_173_open_scarf','MF_173_diagonal_scarf_fall'):
        ob=bpy.data.objects[name]
        for vertex in ob.data.vertices:
            _,i,distance=kd.find(vertex.co)
            if distance>.80:continue
            point,n=supports[i];delta=vertex.co-point;outward=delta.dot(n);tangent=(delta-n*outward).length
            if outward>.075:vertex.co-=n*(outward-.075)*compression_weight(tangent)
        ob.data.update();border_seams(ob,mats['seam'])
    bpy.context.view_layer.update()


def leather_paths(frame,mats):
    """Continuous belt and authored envelope-supported leather load paths."""
    import bpy
    from mathutils import Vector
    shirt=tree_for(bpy.data.objects['MF_fit_tunic_173_visible'])
    # Waist band follows a fair continuous waist contour, not small folds.
    source=bpy.data.objects['MF_fit_waist_belt'];data=single_surface_mesh(source)
    for vertex in data.vertices:
        p=source.matrix_world@vertex.co;hit,n,_,dist=shirt.find_nearest(p)
        if hit is not None and dist<.15:p=hit+n*.040
        vertex.co=p
    data.update();data.materials.clear();data.materials.append(mats['leather'])
    belt=set_surface('MF_173_waist_belt',data,.026);border_seams(belt,mats['thread'])
    # Simple worn functional buckle, not jewellery or invented insignia.
    center,n,_,_=tree_for(belt).find_nearest(torso_point(Vector((0,-1.28,-5.18))));center+=n*.045
    side=torso_matrix(-5.18).to_3x3()@Vector((1,0,0));up=torso_matrix(-5.18).to_3x3()@Vector((0,0,1))
    buckle=[tuple(center+side*a+up*b) for a,b in [(-.27,.20),(.27,.20),(.27,-.20),(-.27,-.20),(-.27,.20)]]
    line('MF_173_belt_buckle',buckle,mats['metal'],.027)
    line('MF_173_buckle_tongue',[tuple(center+up*.20),tuple(center-up*.09)],mats['metal'],.015)
    from wardrobe_tension import harness
    harness(mats)


def boots(mats):
    import bpy
    for source in [o for o in bpy.context.scene.objects if o.name in ('MF_fit_boots','MF_fit_closed_boot_L','MF_fit_closed_boot_R')]:
        ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
        for v in data.vertices:v.co=source.matrix_world@v.co
        data.materials.clear();data.materials.append(mats['boot']);data.update()
        target=set_surface(source.name+'_173_visible',data,0)
        if 'closed' in source.name and not target.modifiers:
            bevel=target.modifiers.new('Softened boot last edges','BEVEL');bevel.width=.035;bevel.segments=3
        source.hide_render=True


def pose_wardrobe(mats):
    import bpy
    for ob in bpy.context.scene.objects:
        if ob.name.startswith('MF_172_') or '_172_pose_surface' in ob.name:ob.hide_render=True
    for name in ('MF_fit_shoulder_harness_-1','MF_fit_shoulder_harness_1','MF_fit_waist_belt'):
        bpy.data.objects[name].hide_render=True
    sculpt_fabric(mats);frame=construct_scarf(mats);compress_cloth(mats)
    # Tuck against the FINAL pressured layer, not the pre-compression wrap.
    tuck_scarf_ends(bpy.data.objects['MF_173_open_scarf'],bpy.data.objects['MF_173_diagonal_scarf_fall'],frame)
    # The long end is now the visible chest drape of the same cloth sheet.
    # Keep its clean support pattern editable/hidden, not as a competing layer.
    bpy.data.objects['MF_173_diagonal_scarf_fall'].hide_render=True
    bpy.data.objects['MF_173_scarf_bound_edge'].hide_render=True
    border_seams(bpy.data.objects['MF_173_open_scarf'],mats['seam'])
    leather_paths(frame,mats)
    from wardrobe_tension import press_visible_scarf
    press_visible_scarf();border_seams(bpy.data.objects['MF_173_open_scarf'],mats['seam'])
    boots(mats)
    from wardrobe_finish import finishing
    finishing(mats)
    bpy.context.view_layer.update()


def render_set(out,full=False):
    import bpy
    from wardrobe_riding_fit import fit_render,riding_pose
    from wardrobe_studio_contacts import fit_contacts as fit_static_contacts
    rig=bpy.data.objects['MF_body156_fit_rig'];neutral(rig);mats=make_materials();pose_wardrobe(mats)
    horse=[o for o in bpy.context.scene.objects if o.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_'))]
    state={o.name:o.hide_render for o in horse}
    for o in horse:o.hide_render=True
    bpy.context.scene.cycles.samples=24
    for label,angle in ([('front',0),('left',-40),('right',40),('rear',180),('profile',90)] if full else [('front',0),('right',40),('rear',180),('profile',90)]):
        fit_render(out,'upper-'+label,angle,(0,.15,-1.7),7.,(800,850))
    if full or out.name.endswith(('preview30','preview31','preview32','preview33','preview34','preview35','preview36','preview37','preview38','preview40','preview41','preview42','preview43','preview44','preview45','preview46','preview47','preview48')):
        for label,angle in [('left',-40),('right',40)]:fit_render(out,'chest-'+label,angle,(0,-.3,-3.2),4.,(750,750))
    for label,angle in ([('front',0),('side',90),('rear',180)] if full else [('front',0)]):fit_render(out,'standing-'+label,angle)
    if full:fit_render(out,'standing-boot',90,(1.,-.2,-12.40),3.8,(750,650))
    for o in horse:o.hide_render=state[o.name]
    riding_pose(rig);bpy.context.view_layer.update();pose_wardrobe(mats)
    contacts=[o for o in bpy.context.scene.objects if o.get('source_object')]
    fit_static_contacts(contacts,rig,mats['leather'])
    for label,angle in ([('left',-40),('right',40),('rear',140)] if full else [('left',-40),('right',40)]):fit_render(out,'mounted-upper-'+label,angle,(-.1,-2.5,-6),11.,(800,850))
    if full:
        for label,angle in [('side',90),('opposite-side',-90)]:fit_render(out,'mounted-'+label,angle,(0,-1,-10),29.,(1000,700))
        for ob in horse:ob.hide_render=True
        for ob in bpy.context.scene.objects:
            if ob.name.startswith(('MF_fit_rein_','MF_fit_stirrup_leather_')):ob.hide_render=True
        center=rig.matrix_world@rig.pose.bones['foot.L'].head
        fit_render(out,'mounted-boot-isolated',90,tuple(center),4.5,(750,650))
        for ob in horse:ob.hide_render=state[ob.name]
        for ob in bpy.context.scene.objects:
            if ob.name.startswith(('MF_fit_rein_','MF_fit_stirrup_leather_')):ob.hide_render=False
        riding_pose(rig,.75);bpy.context.view_layer.update();pose_wardrobe(mats);fit_static_contacts(contacts,rig,mats['leather'])
        fit_render(out,'mounted-partial',90,(0,-1,-10),29.,(1000,700))
        riding_pose(rig);bpy.context.view_layer.update();pose_wardrobe(mats);fit_static_contacts(contacts,rig,mats['leather'])


def build(out,operation):
    import bpy
    from wardrobe_riding_fit import accepted_signature,evaluated_surfaces
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    prior=json.loads((SOURCE.parent/'result.json').read_text())
    protected=accepted_signature(prior['protected_signatures']);body=bpy.data.objects['MF_studio_adult_body']
    basis=coordinates_digest(tuple(v.co) for v in body.data.vertices)
    assert protected==prior['protected_signatures'] and basis==prior['body_basis_digest']
    render_set(out,operation in ('preview17','preview18','preview20','preview21','preview22','preview23','preview24','preview28','preview39','preview49','seal01'))
    assert accepted_signature(protected)==protected and coordinates_digest(tuple(v.co) for v in body.data.vertices)==basis
    tail=data_signature(bpy.data.objects['MF_170_tail_fibers']);assert tail==prior['static_tail_curve_digest']
    result={'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),'protected_signatures':protected,'body_basis_digest':basis,
            'static_tail_curve_digest':tail,'head_scale_changed':False,'visual_gate':'NOT_RUN','Director_acceptance':'PENDING',
            'blender_version':str(bpy.app.version_string),'blender_build_hash':str(bpy.app.build_hash),
            'limits':['Prescribed static surfaces, not cloth dynamics','Appearance not motion/rights qualification']}
    if operation=='seal01':
        import numpy as np
        binding=source_binding();binding_hash=digest(BASE/'wardrobe173-operating/source-binding.json')
        bpy.context.scene['MF_173_source_commit']=binding['source_commit']
        bpy.context.scene['MF_173_source_binding_sha256']=binding_hash
        bpy.context.scene['MF_173_asset_status']='Static appearance pending; motion and upstream rights not qualified'
        result.update({'source_commit':binding['source_commit'],'source_git_tree':binding['source_git_tree'],'source_binding_sha256':binding_hash})
        names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type=='MESH']
        np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
        for text in bpy.data.texts:text.use_module=False
        bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True)
        result['native_sha256']=digest(out/'dressed-fit.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def cloth_probe(out):
    """Small deterministic readout of rest-key versus frozen surface semantics."""
    import bpy
    points=[((i-5)*.15,j*.15,1.+.3*math.cos((i-5)*.2)) for i in range(11) for j in range(11)]
    faces=[(i*11+j,(i+1)*11+j,(i+1)*11+j+1,i*11+j+1) for i in range(10) for j in range(10)]
    data=bpy.data.meshes.new('MF_173_probe');data.from_pydata(points,[],faces);data.update()
    ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob)
    basis=ob.shape_key_add(name='Draped');flat=ob.shape_key_add(name='Flat rest')
    for index,v in enumerate(flat.data):
        i,j=divmod(index,11);v.co=((i-5)*.16,j*.16,1.)
    flat.value=0.;ob.active_shape_key_index=0;ob.show_only_shape_key=False
    pin=ob.vertex_groups.new(name='Pins');pin.add([5*11,5*11+1],1.,'REPLACE')
    cloth=ob.modifiers.new('Probe cloth','CLOTH');cloth.settings.rest_shape_key=flat;cloth.settings.vertex_group_mass=pin.name;cloth.settings.quality=5
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=12
    rows={}
    def sample():
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();coords=[v.co.copy() for v in me.vertices];ev.to_mesh_clear();return coords
    for frame in range(1,13):
        bpy.context.scene.frame_set(frame);coords=sample()
        if frame in (1,2,12):rows[str(frame)]=[tuple(coords[i]) for i in (0,55,120)]
    cloth_saved=[tuple(p) for p in coords]
    ob.modifiers.remove(cloth);ob.shape_key_clear()
    for v,p in zip(ob.data.vertices,cloth_saved):v.co=p
    bpy.context.view_layer.update();rows['after_clear']=[tuple(sample()[i]) for i in (0,55,120)]
    rows['flat_key_value']=flat.value if flat.id_data is not None else None
    (out/'result.json').write_text(json.dumps(rows,indent=2)+'\n')


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());out=validate(job);out.mkdir()
    if job['operation']=='clothprobe01':cloth_probe(out);return
    if job['operation']=='verify01':
        from wardrobe_studio_verify import verify
        verify(out);return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    if job['operation']=='inspect02':
        from wardrobe_layer_probe import run
        run(out);return
    if job['operation']=='inspect03':
        from wardrobe_profile_probe import run
        run(out);return
    if job['operation']=='inspect01':
        neutral(bpy.data.objects['MF_body156_fit_rig'])
        source=bpy.data.objects['MF_172_folded_head_drape'];body=bpy.data.objects['MF_studio_adult_body']
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        rows={'scarf_frame':[list(row) for row in source.matrix_world],'frame_scale':list(source.matrix_world.to_scale()),'body_modifiers':[(m.name,m.type) for m in body.modifiers]}
        def bounds(points):return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
        for sign in (-1,1):
            rows[str(sign)]={'raw':bounds([body.matrix_world@v.co for v in body.data.vertices if v.co.z<-12.1 and v.co.x*sign>0]),'evaluated':bounds([body.matrix_world@v.co for v in me.vertices if v.co.z<-12.1 and v.co.x*sign>0])}
        ev.to_mesh_clear();(out/'result.json').write_text(json.dumps(rows,indent=2)+'\n');return
    neutral(bpy.data.objects['MF_body156_fit_rig']);build(out,job['operation'])


if __name__=='__main__':main()
