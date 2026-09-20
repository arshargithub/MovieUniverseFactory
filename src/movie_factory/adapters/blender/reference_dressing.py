"""Reviewed static portrait dressing operations; fixed sources and bounded variants.

Preserve accepted face. Reuse the donor hood; author shoulder panels and hair
locks against the approved portrait. No executable job data or paid services.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
HEAD = BASE/'bilateral-04/head-bilateral.blend'
HEAD_SHA = 'c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322'
DONOR = ROOT/'.runtime/assets/series01-dressing-source/lam-m-zack-hijab/hijab.glb'
DONOR_SHA = 'c209b25a85a8dad1def97880ee400af23d38ded876e578968004bee59203700a'
REFERENCE=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png'
REFERENCE_SHA='7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75'
HAIR_TEXTURE=ROOT/'.runtime/assets/series01-dressing-source/o4saken-long01/o4saken_long01.png'
HAIR_SHA='436f34ddbd3d27275ecbfb7ea3e3159dc16ff8039313c003fdea30bcbdcefb10'
SIDE_REFERENCE=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01/portrait-v07-individualized.png'
SIDE_SHA='e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation','variant'}:
        raise ValueError('Invalid keys')
    if job['operation'] not in ('portrait_dressing','verify_portrait_dressing','inspect_portrait_dressing','render_portrait_dressing'):
        raise ValueError('Invalid operation')
    if type(job['variant']) is not int or job['variant'] not in tuple(range(1,19)):
        raise ValueError('Invalid variant')
    for path, digest in ((HEAD,HEAD_SHA),(DONOR,DONOR_SHA)):
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Changed source')
    if job['variant']>=4:
        for path,digest in ((REFERENCE,REFERENCE_SHA),(HAIR_TEXTURE,HAIR_SHA),(SIDE_REFERENCE,SIDE_SHA)):
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                raise ValueError('Changed reference/texture')
    name={'portrait_dressing':'reference-dress-','verify_portrait_dressing':'reference-verify-',
          'inspect_portrait_dressing':'reference-inspect-', 'render_portrait_dressing':'reference-portraits-'}[job['operation']]
    out = BASE/f'{name}{job["variant"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Output exists or disk low')
    return out


def hood_point(point,variant=1):
    x,y,z = point
    low = max(0., min(1., (1.55-z)/1.2))
    x *= 1.10+.35*low
    y = y*.86-.22 + .18*low
    z = z*.90-.70-.15*low
    if variant>=2:
        y += .19*low+.05
        x *= 1+.10*low
    if variant>=3:
        angle=math.atan2(x,z+.65)
        fold=.035*math.sin(angle*13+y*3)+.015*math.sin(angle*25-y*4)
        x+=fold*math.sin(angle)
        z+=fold*math.cos(angle)
    if variant>=4:
        y+=.65*low
    if variant>=6:
        weight=max(0.,min(1.,(1.30-z)/.55))*max(0.,min(1.,(abs(x)-.45)/.35))
        y+=(max(y,.48)-y)*weight
    if variant>=15:
        # The revised locks now begin behind the ears: return the upper hood lip
        # over the scalp transition, while leaving the lower jaw/neck open.
        base_x,base_y,base_z=hood_point(point,3)
        upper=max(0.,min(1.,(z-.10)/.45))
        forward=max(0.,min(1.,(.10-point[1])/.70))
        blend=upper*forward
        y=y*(1-blend)+(base_y-.05)*blend
    if variant>=16:
        upper=max(0.,min(1.,(z-.10)/.45))
        near=max(0.,min(1.,(1.5-y)/.6))
        target=-.20+.65*max(0.,abs(x)-.8)
        y-=max(0.,y-target)*upper*near
    return x,y,z


def panel_point(u,v,layer=0,variant=1):
    """Art-directed diagonal cloth pattern, not the prior circular collar."""
    if variant>=2:
        a=-2.05+4.10*u
        x=(2.20-.17*v)*math.sin(a)
        top=-1.48+.36*math.sin(a)+.16*abs(math.sin(a))
        z=top-(1.50 if layer==0 else .65)*v-(.10 if layer==0 else 0)
        phase=v*(11 if layer==0 else 5)+1.2*a+.65*math.sin(a*2+v*3)
        amplitude=.055+.040*math.sin(a*2+v*5)**2
        fold=amplitude*math.sin(phase)+.025*math.sin(phase*2.3)
        y=-(.94+fold)*math.cos(a)+.12
        x+=fold*math.sin(a)
        y-=.11 if layer else 0
        z+=.028*math.sin(a*5+v*8)
        if variant>=3:
            z-=.14*max(0.,math.sin(a))
            y-=.04*math.sin(phase)
        return x,y,z
    x = -2.5 + 5*u
    top = -1.47 + .23*x + .12*(x/2.5)**2
    z = top - (1.7 if layer==0 else .66)*v - (.02 if layer else .23)
    phase = v*(21 if layer==0 else 11)+x*1.5+.5*math.sin(x*1.8)
    fold = .09*math.sin(phase)+.035*math.sin(phase*2.17+.4)
    y = -.90*math.sqrt(max(.03,1-(x/2.72)**2))-.08-fold
    y -= .16 if layer else 0
    z += .025*math.sin(phase+1)
    return x,y,z


def lock_point(side,lock,t,strand=0,variant=1):
    """Swept, tapered side locks; roots sit outside the protected face region."""
    phase = lock*.91
    if variant>=2:
        keys=[(.32+.025*(lock%4),-.23,1.20-.022*(lock%4)),
              (.73+.025*(lock%4),-.43,.69),
              (.96+.025*(lock%4),-.29,.05),
              (1.10+.025*(lock%4),.0,-.53),
              (1.02+.035*(lock%4),.30,-1.32-.035*(lock%3))]
        q=t*4;k=min(3,int(q));f=q-k
        # Smooth Catmull-Rom interpolation: no exposed straight root edges.
        p0=keys[max(0,k-1)];p1=keys[k];p2=keys[k+1];p3=keys[min(4,k+2)]
        p=[.5*((2*p1[c])+(-p0[c]+p2[c])*f+(2*p0[c]-5*p1[c]+4*p2[c]-p3[c])*f*f+(-p0[c]+3*p1[c]-3*p2[c]+p3[c])*f*f*f) for c in range(3)]
        wave=math.sin(math.pi*t)**1.5
        p[0]+=.065*math.sin(t*11+phase)*wave
        p[1]+=.11*(lock//4)+.035*math.sin(t*9+phase)*wave
        width=(.05+.008*(lock%3))*math.sin(math.pi*(.06+.92*t))
        p[0]+=strand*width
        if variant>=3:
            keys=[(.57+.035*(lock%4),.10,1.03-.04*(lock%3)),
                  (.88+.03*(lock%4),-.07,.48-.035*(lock%3)),
                  (.97+.035*(lock%4),.03,-.10),
                  (1.12+.04*(lock%4),.20,-.60),
                  (.98+.045*(lock%4),.50,-1.40+.09*(lock%4))]
            p0=keys[max(0,k-1)];p1=keys[k];p2=keys[k+1];p3=keys[min(4,k+2)]
            p=[.5*((2*p1[c])+(-p0[c]+p2[c])*f+(2*p0[c]-5*p1[c]+4*p2[c]-p3[c])*f*f+(-p0[c]+3*p1[c]-3*p2[c]+p3[c])*f*f*f) for c in range(3)]
            p[0]+=.14*math.sin(t*12+phase)*wave+strand*width
            p[1]+=.14*(lock//4)+.085*math.sin(t*10+phase)*wave
        return side*p[0],p[1],p[2]
    root_z = .82-.095*(lock%5)
    x = .84+.037*(lock%4)+.11*math.sin(t*5.8+phase)*math.sin(math.pi*t)
    x += .19*t+.07*math.sin(t*9+phase)*t
    y = -.30+.10*(lock//4)+.56*t+.07*math.sin(t*7+phase)
    z = root_z-(1.7+.12*(lock%3))*t
    width = (.042+.012*(lock%3))*(.65+.35*math.sin(math.pi*t))*(1-t**5)
    x += strand*width
    y += .016*math.sin(strand*2.5+t*6)
    return side*x,y,z


def mesh_object(name,vertices,faces,mat,subdivision=1):
    import bpy
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    for poly in mesh.polygons: poly.use_smooth=True
    if subdivision:
        mod=obj.modifiers.new('Surface continuity','SUBSURF');mod.levels=subdivision
    return obj


def fabric_material(variant=1):
    import bpy
    mat=bpy.data.materials.new('MF_illustrated_indigo_fabric');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links
    p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.93
    coord=n.new('ShaderNodeTexCoord')
    scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(2,5,1)
    l.new(coord.outputs['Object'],scale.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=2.5;noise.inputs['Roughness'].default_value=.75
    l.new(scale.outputs[0],noise.inputs['Vector'])
    if variant>=2:
        scale.inputs[1].default_value=(1.3,1.3,4)
        noise.inputs['Scale'].default_value=7
    if variant>=3:
        rotate=n.new('ShaderNodeVectorRotate');rotate.rotation_type='AXIS_ANGLE'
        rotate.inputs['Axis'].default_value=(0,1,0);rotate.inputs['Angle'].default_value=.5
        l.new(coord.outputs['Object'],rotate.inputs['Vector']);l.new(rotate.outputs['Vector'],scale.inputs[0])
        scale.inputs[1].default_value=(3,4,18);noise.inputs['Scale'].default_value=2.5
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    colors=[(.25,(.006,.015,.040,1)),(.40,(.015,.038,.088,1)),(.55,(.028,.066,.14,1)),(.70,(.052,.10,.19,1))]
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    ramp.color_ramp.elements[0].position=colors[0][0];ramp.color_ramp.elements[0].color=colors[0][1]
    for pos,color in colors[1:]:ramp.color_ramp.elements.new(pos).color=color
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=220;grain.inputs['Detail'].default_value=1
    l.new(coord.outputs['Object'],grain.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.004
    l.new(grain.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    if variant>=4:
        # Use the existing accepted illustration directly as native material data.
        # Blue-dominance masking excludes skin/hair/background from cloth transfer.
        texture=n.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(REFERENCE));texture.image.pack();texture.extension='EXTEND'
        separate=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],separate.inputs[0])
        u=n.new('ShaderNodeMath');u.operation='MULTIPLY_ADD';u.inputs[1].default_value=.238;u.inputs[2].default_value=.5
        v=n.new('ShaderNodeMath');v.operation='MULTIPLY_ADD';v.inputs[1].default_value=.156;v.inputs[2].default_value=.677
        l.new(separate.outputs['X'],u.inputs[0]);l.new(separate.outputs['Z'],v.inputs[0])
        combine=n.new('ShaderNodeCombineXYZ');l.new(u.outputs[0],combine.inputs[0]);l.new(v.outputs[0],combine.inputs[1]);l.new(combine.outputs[0],texture.inputs['Vector'])
        rgb=n.new('ShaderNodeSeparateColor');l.new(texture.outputs['Color'],rgb.inputs[0])
        red=n.new('ShaderNodeMath');red.operation='MULTIPLY';red.inputs[1].default_value=1.12;l.new(rgb.outputs['Red'],red.inputs[0])
        blue=n.new('ShaderNodeMath');blue.operation='GREATER_THAN';l.new(rgb.outputs['Blue'],blue.inputs[0]);l.new(red.outputs[0],blue.inputs[1])
        mix=n.new('ShaderNodeMixRGB');l.new(blue.outputs[0],mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);l.new(texture.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        if variant>=5:
            # Avoid stretched edge pixels outside the reference's image coverage.
            left=n.new('ShaderNodeMath');left.operation='GREATER_THAN';left.inputs[1].default_value=.025;l.new(u.outputs[0],left.inputs[0])
            right=n.new('ShaderNodeMath');right.operation='LESS_THAN';right.inputs[1].default_value=.975;l.new(u.outputs[0],right.inputs[0])
            both=n.new('ShaderNodeMath');both.operation='MULTIPLY';l.new(left.outputs[0],both.inputs[0]);l.new(right.outputs[0],both.inputs[1])
            admitted=n.new('ShaderNodeMath');admitted.operation='MULTIPLY';l.new(both.outputs[0],admitted.inputs[0]);l.new(blue.outputs[0],admitted.inputs[1]);l.new(admitted.outputs[0],mix.inputs[0])
        if variant>=7:
            side_tex=n.new('ShaderNodeTexImage');side_tex.image=bpy.data.images.load(str(SIDE_REFERENCE));side_tex.image.pack();side_tex.extension='EXTEND'
            absx=n.new('ShaderNodeMath');absx.operation='ABSOLUTE';l.new(separate.outputs['X'],absx.inputs[0])
            sumxy=n.new('ShaderNodeMath');sumxy.operation='ADD';l.new(absx.outputs[0],sumxy.inputs[0]);l.new(separate.outputs['Y'],sumxy.inputs[1])
            su=n.new('ShaderNodeMath');su.operation='MULTIPLY_ADD';su.inputs[1].default_value=-.1414;su.inputs[2].default_value=.50;l.new(sumxy.outputs[0],su.inputs[0])
            sv=n.new('ShaderNodeMath');sv.operation='MULTIPLY_ADD';sv.inputs[1].default_value=.15;sv.inputs[2].default_value=.61;l.new(separate.outputs['Z'],sv.inputs[0])
            suv=n.new('ShaderNodeCombineXYZ');l.new(su.outputs[0],suv.inputs[0]);l.new(sv.outputs[0],suv.inputs[1]);l.new(suv.outputs[0],side_tex.inputs['Vector'])
            srgb=n.new('ShaderNodeSeparateColor');l.new(side_tex.outputs['Color'],srgb.inputs[0])
            sr=n.new('ShaderNodeMath');sr.operation='MULTIPLY';sr.inputs[1].default_value=1.12;l.new(srgb.outputs['Red'],sr.inputs[0])
            sb=n.new('ShaderNodeMath');sb.operation='GREATER_THAN';l.new(srgb.outputs['Blue'],sb.inputs[0]);l.new(sr.outputs[0],sb.inputs[1])
            smix=n.new('ShaderNodeMixRGB');l.new(sb.outputs[0],smix.inputs[0]);l.new(ramp.outputs[0],smix.inputs[1]);l.new(side_tex.outputs['Color'],smix.inputs[2])
            if variant>=9:
                # Conservative upper-cloth coverage; blue sky is not cloth.
                delta=n.new('ShaderNodeMath');delta.operation='SUBTRACT';delta.inputs[1].default_value=.50;l.new(su.outputs[0],delta.inputs[0])
                absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(delta.outputs[0],absolute.inputs[0])
                roof=n.new('ShaderNodeMath');roof.operation='MULTIPLY_ADD';roof.inputs[1].default_value=-.15;roof.inputs[2].default_value=.80;l.new(absolute.outputs[0],roof.inputs[0])
                below=n.new('ShaderNodeMath');below.operation='LESS_THAN';l.new(sv.outputs[0],below.inputs[0]);l.new(roof.outputs[0],below.inputs[1])
                mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(below.outputs[0],mask.inputs[0]);l.new(sb.outputs[0],mask.inputs[1]);l.new(mask.outputs[0],smix.inputs[0])
            geo=n.new('ShaderNodeNewGeometry');normal=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],normal.inputs[0])
            nx=n.new('ShaderNodeMath');nx.operation='ABSOLUTE';l.new(normal.outputs['X'],nx.inputs[0])
            blend=n.new('ShaderNodeMapRange');blend.clamp=True;blend.inputs['From Min'].default_value=.25;blend.inputs['From Max'].default_value=.8;l.new(nx.outputs[0],blend.inputs['Value'])
            output=n.new('ShaderNodeMixRGB');l.new(blend.outputs['Result'],output.inputs[0]);l.new(mix.outputs[0],output.inputs[1]);l.new(smix.outputs[0],output.inputs[2]);l.new(output.outputs[0],p.inputs['Base Color'])
    return mat


def make_hood(mat,variant=1):
    import bpy,bmesh
    from hijab_donor import connected_groups,inspect_glb
    inspect_glb(DONOR.read_bytes())
    prior=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(DONOR),import_pack_images=True)
    objs=[o for o in bpy.context.scene.objects if o not in prior and o.type=='MESH']
    if len(objs)!=1:raise ValueError('Unexpected source')
    obj=objs[0];points=[obj.matrix_world@v.co for v in obj.data.vertices]
    obj.parent=None;obj.matrix_world.identity()
    for v,p in zip(obj.data.vertices,points):v.co=p
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    groups=connected_groups(bm)
    if [len(g) for g in groups] != [2481,412]:raise ValueError('Donor groups changed')
    bmesh.ops.delete(bm,geom=groups[1],context='VERTS')
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                          plane_co=(0,0,.34),plane_no=(0,0,1),clear_inner=True,dist=.000001)
    cut_edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.z-.34)<.0001 for v in e.verts)]
    for v in bm.verts:v.co=hood_point(v.co,variant)
    # Extend the donor's cut lower edge as a loose continuous curtain, behind hair.
    if variant>=10:
        rows={v:[v] for edge in cut_edges for v in edge.verts}
        for v,row in rows.items():
            x,y,z=v.co
            for j in range(1,9):
                t=j/8
                row.append(bm.verts.new((x*(1+.45*t)+.04*math.sin(t*9+x*5)*t,
                    y+.35*t+.08*math.sin(x*8+t*5)*math.sin(math.pi*t),
                    z*(1-t)+(-3.25+.15*abs(x))*t)))
        for edge in cut_edges:
            a,b=edge.verts
            for j in range(8):bm.faces.new((rows[a][j],rows[b][j],rows[b][j+1],rows[a][j+1]))
    else:
        extended={}
        for edge in cut_edges:
            for v in edge.verts:
                if v not in extended:
                    x,y,z=v.co
                    extended[v]=bm.verts.new((x*1.32,y+.18,-1.95+.18*abs(x)))
            a,b=edge.verts
            bm.faces.new((a,b,extended[b],extended[a]))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free();obj.name='MF_adapted_donor_hood'
    obj.data.materials.clear();obj.data.materials.append(mat)
    for p in obj.data.polygons:p.use_smooth=True
    sub=obj.modifiers.new('Soft donor folds','SUBSURF');sub.levels=2
    if variant>=17:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=64,location=(0,.23,.15))
        envelope=bpy.context.object;envelope.name='MF_hidden_scalp_clearance_envelope'
        envelope.scale=(1.095,1.095,1.295);envelope.hide_render=True
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        group=obj.vertex_groups.new(name='Upper hood clearance only')
        for vertex in obj.data.vertices:
            weight=max(0.,min(1.,(vertex.co.z+.10)/.55))
            if weight:group.add([vertex.index],weight,'REPLACE')
        shrink=obj.modifiers.new('Outside scalp clearance','SHRINKWRAP')
        shrink.target=envelope;shrink.wrap_method='NEAREST_SURFACEPOINT'
        shrink.wrap_mode='OUTSIDE';shrink.offset=.035;shrink.vertex_group=group.name
    solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.009
    return obj


def make_shoulders(mat,variant=1):
    import bpy
    # Covered upper-body support: geometry only, no new visible costume detail.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=(0,.15,-2.4))
    body=bpy.context.object;body.name='MF_clothed_bust_support';body.scale=(2.35,.90,1.10)
    body.data.materials.append(mat)
    for p in body.data.polygons:p.use_smooth=True
    cloth_objects=[]
    if variant>=2:
        body.location.z=-2.65;body.scale=(2.20,.84,1.10)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        body.modifiers.new('Cloth support collision','COLLISION')
    if variant>=3:
        bpy.data.objects.remove(body,do_unlink=True)
        rings=[(-1.22,.48,.43),(-1.32,.70,.50),(-1.49,1.80,.65),
               (-1.75,2.14,.78),(-2.25,2.15,.83),(-3.30,1.9,.75),(-3.7,1.75,.67)]
        vertices=[(rx*math.sin(k*2*math.pi/64),.16-ry*math.cos(k*2*math.pi/64),z)
                  for z,rx,ry in rings for k in range(64)]
        faces=[(j*64+k,j*64+(k+1)%64,(j+1)*64+(k+1)%64,(j+1)*64+k)
               for j in range(len(rings)-1) for k in range(64)]
        body=mesh_object('MF_clothed_bust_support',vertices,faces,mat,subdivision=2)
        body.modifiers.new('Cloth support collision','COLLISION')
    if variant>=4:
        # Keep the fitting form behind the source garment, not in front of it.
        body.scale=(.88,.78,1);body.hide_render=variant<5
        if variant>=6:
            for v in body.data.vertices:
                if v.co.z>-1.45 and abs(v.co.x)<.8:v.co.z-=.40
        return make_donor_wrap(mat,variant)
    for layer in (0,1):
        nu,nv=(100,60) if variant==1 else (64,32)
        vertices=[panel_point(i/nu,j/nv,layer,variant) for i in range(nu+1) for j in range(nv+1)]
        faces=[(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1)
               for i in range(nu) for j in range(nv)]
        obj=mesh_object('MF_diagonal_shawl_'+str(layer),vertices,faces,mat,subdivision=0)
        if variant>=2:
            group=obj.vertex_groups.new(name='MF_drape_anchors')
            for i in range(nu+1):
                # Upper border follows the composed silhouette; fabric below settles.
                anchor=1.0 if variant==2 or abs(math.sin(-2.05+4.10*i/nu))>.94 else .12
                group.add([i*(nv+1)],anchor,'REPLACE')
                if i in (0,nu):group.add([i*(nv+1)+j for j in range(nv+1)],1.0,'REPLACE')
            cloth=obj.modifiers.new('Native cloth settling','CLOTH')
            cloth.settings.quality=6;cloth.settings.mass=.22
            cloth.settings.vertex_group_mass=group.name
            cloth.settings.tension_stiffness=20;cloth.settings.compression_stiffness=20
            cloth.settings.shear_stiffness=12;cloth.settings.bending_stiffness=.35
            if variant>=3:cloth.settings.bending_stiffness=.04
            cloth.collision_settings.use_self_collision=True
            cloth.collision_settings.self_distance_min=.012
            cloth.collision_settings.distance_min=.015
            cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=24
            cloth_objects.append((obj,cloth))
        sub=obj.modifiers.new('Smooth settled fabric','SUBSURF');sub.levels=2 if variant>=2 else 1
        solid=obj.modifiers.new('Fabric hem','SOLIDIFY');solid.thickness=.009
    if variant>=2:
        scene=bpy.context.scene;scene.gravity=(0,0,-.60)
        for frame in range(1,25):scene.frame_set(frame)
        for obj,cloth in cloth_objects:
            bpy.context.view_layer.objects.active=obj
            bpy.ops.object.modifier_apply(modifier=cloth.name)
        scene.frame_set(1)


def donor_wrap_point(point,variant=4):
    x,y,z=point
    x*=1.45
    zz=(z-.34)*.63-1.36+.25*x
    if variant>=5:
        zz-=.20*max(0.,min(1.,(z+.1)/.75))*max(0.,min(1.,(abs(x)-1)/1.2))
    if variant>=6:
        tail=max(0.,min(1.,(x-.3)/.8))*max(0.,min(1.,(-z-.6)/1.6))
        x-=.85*tail
        y+=.20*tail
    if variant>=12:
        neckline=-1.50+.20*x+.30*(abs(x)/2)**2
        zz=min(zz,neckline)
    if variant>=18:
        # Lower the donor's high outside shoulder lip, not the exposed neck.
        zz-=.25*max(0.,min(1.,(abs(x)-1.65)/.85))
    return x,y*.76-.60,zz


def make_donor_wrap(mat,variant):
    import bpy,bmesh
    from hijab_donor import connected_groups
    prior=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(DONOR),import_pack_images=True)
    obj=next(o for o in bpy.context.scene.objects if o not in prior and o.type=='MESH')
    points=[obj.matrix_world@v.co for v in obj.data.vertices];obj.parent=None;obj.matrix_world.identity()
    for v,p in zip(obj.data.vertices,points):v.co=p
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    groups=connected_groups(bm)
    if [len(g) for g in groups]!=[2481,412]:raise ValueError('Donor changed')
    bmesh.ops.delete(bm,geom=groups[1],context='VERTS')
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,.65),plane_no=(0,0,1),clear_outer=True,dist=.000001)
    for v in bm.verts:v.co=donor_wrap_point(v.co,variant)
    if variant>=5:
        bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=8)
        boundary=[v for v in bm.verts if v.is_boundary]
        for _ in range(4):
            bmesh.ops.smooth_vert(bm,verts=boundary,factor=.25,use_axis_x=True,use_axis_y=True,use_axis_z=True)
    if variant>=7:
        edges=set(e for e in bm.edges if e.is_boundary)
        while edges:
            edge=edges.pop();group={edge};stack=[edge];verts=set(edge.verts)
            while stack:
                for v in stack.pop().verts:
                    for e in v.link_edges:
                        if e in edges:edges.remove(e);group.add(e);stack.append(e);verts.update(e.verts)
            if len(group)<=32 and all(sum(e in group for e in v.link_edges)==2 for v in verts):
                from mathutils import Vector
                center=bm.verts.new(sum((v.co for v in verts),Vector())/len(verts))
                for e in group:bm.faces.new((e.verts[1],e.verts[0],center))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    obj.name='MF_diagonal_donor_wrap';obj.data.materials.clear();obj.data.materials.append(mat)
    for p in obj.data.polygons:p.use_smooth=True
    sub=obj.modifiers.new('Retain authored cloth folds','SUBSURF');sub.levels=2
    solid=obj.modifiers.new('Thin cloth','SOLIDIFY');solid.thickness=.009
    if variant>=8:
        # A static cloth shell with a small rounded edge, not paper-like cut sheets.
        solid.thickness=.055 if variant>=15 else .040
        remesh=obj.modifiers.new('Close and round cloth shell','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.023;remesh.use_smooth_shade=True
        smooth=obj.modifiers.new('Soften exposed hems','SMOOTH');smooth.factor=.65;smooth.iterations=4
        texture=bpy.data.textures.new('Secondary cloth creases','CLOUDS');texture.noise_scale=.18;texture.noise_depth=1
        displacement=obj.modifiers.new('Small cloth irregularity','DISPLACE');displacement.texture=texture;displacement.strength=.018;displacement.mid_level=.5;displacement.texture_coords='GLOBAL'


def make_hair(variant=1):
    import bpy
    if variant>=6:return make_fiber_locks(variant)
    if variant>=5:return make_textured_locks(variant)
    mats=[]
    for i,color in enumerate(((.017,.006,.0025,1),(.040,.016,.006,1),(.085,.037,.013,1),(.14,.071,.028,1))):
        mat=bpy.data.materials.new('MF_chestnut_lock_'+str(i));mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color
        p.inputs['Roughness'].default_value=.48;mats.append(mat)
        if variant>=3:
            p.inputs['Base Color'].default_value=tuple(c*.45 for c in color[:3])+(1,)
    for side in (-1,1):
        for lock in range(12 if variant<3 else 20):
            # Flattened dark lock core avoids transparent card silhouettes.
            vertices=[];faces=[];steps=48
            for j in range(steps+1):
                t=j/steps;x,y,z=lock_point(side,lock,t,variant=variant)
                taper=max(.025,(1-t**5));width=(.06+.01*(lock%3))*taper
                if variant>=3:width*=.8
                for k in range(8):
                    a=2*math.pi*k/8;vertices.append((x+width*math.cos(a),y+.035*taper*math.sin(a),z))
            for j in range(steps):
                for k in range(8):faces.append((j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k))
            mesh_object(f'MF_hair_lock_{side}_{lock}',vertices,faces,mats[0])
            for strand in range(17):
                curve=bpy.data.curves.new('MF_hair_strand','CURVE');curve.dimensions='3D'
                curve.resolution_u=1;curve.bevel_depth=.0035 if strand%4 else .005;curve.bevel_resolution=1
                spline=curve.splines.new('POLY');spline.points.add(steps)
                for j,p in enumerate(spline.points):
                    t=j/steps;x,y,z=lock_point(side,lock,t,(strand-8)/8,variant)
                    p.co=(x,y-.037,z,1);p.radius=max(.03,(1-t**4))
                ob=bpy.data.objects.new('MF_hair_strand',curve);bpy.context.scene.collection.objects.link(ob)
                curve.materials.append(mats[1+strand%3])


def make_textured_locks(variant):
    import bpy
    mat=bpy.data.materials.new('MF_04saken_textured_waves');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(HAIR_TEXTURE));tex.image.pack()
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.012,.004,.0015,1);ramp.color_ramp.elements[1].position=.35;ramp.color_ramp.elements[1].color=(.14,.065,.025,1)
    l.new(tex.outputs['Color'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color']);l.new(tex.outputs['Alpha'],p.inputs['Alpha']);p.inputs['Roughness'].default_value=.50
    for side in (-1,1):
        for lock in range(28):
            vertices=[];faces=[];uvs=[];nt,nw=60,6
            strip=lock%4;u0=.666+strip*.077;u1=u0+.072
            for j in range(nt+1):
                t=j/nt
                x,y,z=lock_point(side,lock,t,variant=3)
                # Offset cohorts into a fuller layered mass, rather than one ribbon.
                y+=.055*(lock//7)-.08
                width=(.11+.018*(lock%4))*(.30+.70*math.sin(math.pi*t)**.5)
                for k in range(nw+1):
                    across=(k/nw-.5)*2
                    angle=(lock%3-1)*.55
                    vertices.append((x+side*across*width*math.cos(angle),y+across*width*math.sin(angle)-.035*math.cos(across*math.pi/2),z))
                    uvs.append((u0+(u1-u0)*k/nw,1-t))
            for j in range(nt):
                for k in range(nw):faces.append((j*(nw+1)+k,j*(nw+1)+k+1,(j+1)*(nw+1)+k+1,(j+1)*(nw+1)+k))
            obj=mesh_object(f'MF_textured_wave_{side}_{lock}',vertices,faces,mat,subdivision=1)
            uv=obj.data.uv_layers.new(name='DonorHairUV')
            for poly in obj.data.polygons:
                for li in poly.loop_indices:uv.data[li].uv=uvs[obj.data.loops[li].vertex_index]
    bpy.context.scene.cycles.transparent_max_bounces=32


def make_fiber_locks(variant):
    import bpy
    import random
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    rng=random.Random(83)
    hood_tree=None;adjusted=0
    if variant>=8:
        bpy.context.view_layer.update()
        hood_tree=BVHTree.FromObject(bpy.data.objects['MF_adapted_donor_hood'],bpy.context.evaluated_depsgraph_get())
    mats=[]
    for color in ((.009,.0028,.0009,1),(.025,.008,.0025,1),(.055,.021,.007,1),(.10,.045,.016,1)):
        mat=bpy.data.materials.new('MF_warm_chestnut_fiber');mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color
        p.inputs['Roughness'].default_value=.50;p.inputs['Specular IOR Level'].default_value=.18
        mats.append(mat)
    if variant==11:
        # Reuse the accepted scalp's existing UV/material data on a separate shell.
        # The source head remains untouched; no generic comb-textured cap.
        import bmesh
        head=bpy.data.objects['FBHead'];dg=bpy.context.evaluated_depsgraph_get()
        mesh=bpy.data.meshes.new_from_object(head.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
        bm=bmesh.new();bm.from_mesh(mesh)
        removed=[]
        for f in bm.faces:
            center=f.calc_center_median()
            keep=(center.z>.92) or (center.z>.35 and center.y>-.18) or (center.z>-.10 and center.y>.35)
            if not keep:removed.append(f)
        bmesh.ops.delete(bm,geom=removed,context='FACES')
        bm.normal_update()
        for vertex in bm.verts:
            vertex.co+=vertex.normal*.06
            vertex.co.x*=1.035
        bm.to_mesh(mesh);bm.free()
        scalp=bpy.data.objects.new('MF_separate_side_back_hair_base',mesh);bpy.context.scene.collection.objects.link(scalp)
        scalp.matrix_world=head.matrix_world.copy()
        mesh.materials.clear()
        for material in head.data.materials:mesh.materials.append(material)
    elif variant>=10:
        # Separate side/back scalp volume; never modify or replace the face mesh.
        nu,nv=80,48
        vertices=[]
        for i in range(nu+1):
            phi=(-2.15+4.30*i/nu) if variant>=13 else (-1.85+3.7*i/nu)
            for j in range(nv+1):
                theta=.025+1.78*j/nv
                vertices.append((1.04*math.sin(theta)*math.sin(phi),
                                 .23+1.04*math.sin(theta)*math.cos(phi),
                                 .15+1.24*math.cos(theta)))
        faces=[(i*(nv+1)+j,(i+1)*(nv+1)+j,(i+1)*(nv+1)+j+1,i*(nv+1)+j+1)
               for i in range(nu) for j in range(nv)]
        capmat=mats[0]
        if variant>=12:
            capmat=bpy.data.materials.new('MF_portrait_chestnut_scalp');capmat.use_nodes=True
            n,l=capmat.node_tree.nodes,capmat.node_tree.links;p=n.get('Principled BSDF')
            p.inputs['Roughness'].default_value=.7;p.inputs['Specular IOR Level'].default_value=.12
            coords=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coords.outputs['Object'],sep.inputs[0])
            ax=n.new('ShaderNodeMath');ax.operation='ABSOLUTE';l.new(sep.outputs['X'],ax.inputs[0])
            xy=n.new('ShaderNodeMath');xy.operation='ADD';l.new(ax.outputs[0],xy.inputs[0]);l.new(sep.outputs['Y'],xy.inputs[1])
            u=n.new('ShaderNodeMath');u.operation='MULTIPLY_ADD';u.inputs[1].default_value=-.1414;u.inputs[2].default_value=.50;l.new(xy.outputs[0],u.inputs[0])
            v=n.new('ShaderNodeMath');v.operation='MULTIPLY_ADD';v.inputs[1].default_value=.15;v.inputs[2].default_value=.61;l.new(sep.outputs['Z'],v.inputs[0])
            uv=n.new('ShaderNodeCombineXYZ');l.new(u.outputs[0],uv.inputs[0]);l.new(v.outputs[0],uv.inputs[1])
            tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(SIDE_REFERENCE));tex.image.pack();l.new(uv.outputs[0],tex.inputs['Vector'])
            rgb=n.new('ShaderNodeSeparateColor');l.new(tex.outputs[0],rgb.inputs[0])
            blue=n.new('ShaderNodeMath');blue.operation='MULTIPLY';blue.inputs[1].default_value=1.2;l.new(rgb.outputs['Blue'],blue.inputs[0])
            brown=n.new('ShaderNodeMath');brown.operation='GREATER_THAN';l.new(rgb.outputs['Red'],brown.inputs[0]);l.new(blue.outputs[0],brown.inputs[1])
            dark=n.new('ShaderNodeMath');dark.operation='LESS_THAN';dark.inputs[1].default_value=.30;l.new(rgb.outputs['Red'],dark.inputs[0])
            mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(brown.outputs[0],mask.inputs[0]);l.new(dark.outputs[0],mask.inputs[1])
            mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.018,.006,.002,1);l.new(mask.outputs[0],mix.inputs[0]);l.new(tex.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
            if variant>=13:
                # Explicit hair-only patch, not a broad side projection that can
                # accidentally repeat an ear or skin in the scalp volume.
                tex.image=bpy.data.images.load(str(REFERENCE));tex.image.pack()
                u.inputs[1].default_value=0;u.inputs[2].default_value=.35
                l.new(ax.outputs[0],u.inputs[0]);u.inputs[1].default_value=.035;u.inputs[2].default_value=.314
                v.inputs[1].default_value=.04;v.inputs[2].default_value=.780
                l.new(tex.outputs[0],p.inputs['Base Color'])
            if variant>=14:
                # Blend the front edge into the accepted scalp, with actual swept
                # fibers supplying detail instead of a magnified texture patch.
                for link in list(p.inputs['Base Color'].links):l.remove(link)
                p.inputs['Base Color'].default_value=(.012,.0038,.0013,1)
                fade=n.new('ShaderNodeMapRange');fade.clamp=True
                fade.inputs['From Min'].default_value=-.32;fade.inputs['From Max'].default_value=.10
                l.new(sep.outputs['Y'],fade.inputs['Value']);l.new(fade.outputs['Result'],p.inputs['Alpha'])
        cap=mesh_object('MF_separate_side_back_hair_base',vertices,faces,capmat,subdivision=1)
        if variant>=16:cap.hide_render=True
        if variant>=14:
            for side in (-1,1):
                curve=bpy.data.curves.new('MF_swept_scalp_fibers','CURVE');curve.dimensions='3D'
                curve.bevel_depth=.0026;curve.bevel_resolution=1
                for mat in mats:curve.materials.append(mat)
                for i in range(350):
                    family=i/349;strand=curve.splines.new('POLY');strand.points.add(64)
                    strand.material_index=rng.choices([0,1,2,3],[.3,.43,.23,.04])[0]
                    for j,p in enumerate(strand.points):
                        t=j/64;theta=.32+1.45*t
                        phi=side*(2.28-.58*t-.65*family+.045*math.sin(t*7+family*13))
                        radius=1.049
                        if variant>=16:
                            phi+=side*.10*math.sin(t*8+family*9)*math.sin(math.pi*t)
                            radius+=.018*math.sin(t*11+family*6)*math.sin(math.pi*t)
                        p.co=(radius*math.sin(theta)*math.sin(phi),.23+radius*math.sin(theta)*math.cos(phi),.15+(radius+.2)*math.cos(theta),1)
                        p.radius=max(.02,math.sin(math.pi*t)**.5)*max(.05,min(1,(2.15-abs(phi))/.16))
                ob=bpy.data.objects.new('MF_swept_scalp_fibers',curve);bpy.context.scene.collection.objects.link(ob)
            bpy.context.scene.cycles.transparent_max_bounces=32
        for i in range(0 if variant>=12 else 180):
            phi=-1.85+3.7*i/179
            curve=bpy.data.curves.new('MF_scalp_fiber','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=1
            spline=curve.splines.new('POLY');spline.points.add(48)
            for j,p in enumerate(spline.points):
                theta=.035+1.77*j/48;angle=phi+.06*math.sin(theta*4+phi)
                p.co=(1.048*math.sin(theta)*math.sin(angle),.23+1.048*math.sin(theta)*math.cos(angle),.15+1.248*math.cos(theta),1)
                p.radius=math.sin(math.pi*(.03+.94*j/48))
            curve.materials.append(mats[1+i%3]);ob=bpy.data.objects.new('MF_scalp_fiber',curve);bpy.context.scene.collection.objects.link(ob)
    for side in (-1,1):
        for lock in range(28):
            curve=bpy.data.curves.new('MF_fiber_lock','CURVE');curve.dimensions='3D'
            curve.bevel_depth=.0028;curve.bevel_resolution=1;curve.resolution_u=1
            for mat in mats:curve.materials.append(mat)
            for strand in range(55):
                a=rng.uniform(0,2*math.pi);r=math.sqrt(rng.random())
                dx=.065*r*math.cos(a);dy=.044*r*math.sin(a)
                end=rng.uniform(.85,1);phase=rng.uniform(-.3,.3)
                spline=curve.splines.new('POLY');spline.points.add(64)
                spline.material_index=rng.choices([0,1,2,3],[.30,.43,.23,.04])[0]
                for j,p in enumerate(spline.points):
                    t=j/64*end;x,y,z=lock_point(side,lock,t,variant=3)
                    envelope=math.sin(math.pi*t)**.6
                    if variant>=7:
                        # Bury roots in the scalp; depth cohorts fan out only later.
                        opening=max(0.,min(1.,t/.40));opening=opening*opening*(3-2*opening)
                        y-=.14*(lock//4)*(1-opening)
                    x+=side*(dx*envelope+.008*math.sin(t*20+phase))
                    y+=dy*envelope+.06*(lock//7)*(envelope if variant>=7 else 1)-.05
                    if variant>=9:
                        # Retain the approved painted temple hair; new physical
                        # locks emerge behind the ears, rather than through the hood.
                        z-=.52*(1-t)**2
                    if variant>=18:
                        # Bring the deep cohorts inside the veil instead of
                        # allowing their waves to emerge through its rear wall.
                        y-=.105*(lock//4)*envelope
                    if hood_tree is not None and variant<9 and .10<t<.70:
                        origin=Vector((0,.30,z));point=Vector((x,y,z));direction=point-origin
                        distance=direction.length;direction.normalize()
                        hit,normal,index,hit_distance=hood_tree.ray_cast(origin,direction,3.5)
                        if hit is not None and distance>hit_distance-.035:
                            point=origin+direction*max(.10,hit_distance-.040)
                            x,y,z=point;adjusted+=1
                    p.co=(x,y,z,1);p.radius=max(.03,min(1,t*15)*(1-(t/end)**7))
            ob=bpy.data.objects.new('MF_fiber_lock',curve);bpy.context.scene.collection.objects.link(ob)
    bpy.context.scene['MF_hair_hood_radial_adjustments']=adjusted


def run(job):
    out=validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from hijab_donor import material_signature,review
    from likeness_cleanup import geometry_digest
    bpy.ops.wm.open_mainfile(filepath=str(HEAD),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead'];geometry=geometry_digest(head);material=material_signature(head.data.materials[0])
    values={k.name:k.value for k in head.data.shape_keys.key_blocks}
    if job['operation'] in ('verify_portrait_dressing','inspect_portrait_dressing','render_portrait_dressing'):
        folder=BASE/f'reference-dress-{job["variant"]:02}'
        record=json.loads((folder/'result.json').read_text())
        assert hashlib.sha256((folder/'dressed.blend').read_bytes()).hexdigest()==record['native_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(folder/'dressed.blend'),load_ui=False,use_scripts=False)
        if job['operation']=='render_portrait_dressing':
            out.mkdir()
            review(bpy.context.scene,out,(0,-.1,-.60),5.6,[('front',0),('left',-45),('right',45)],portrait=True)
        if job['operation']=='inspect_portrait_dressing':
            import bmesh
            report={}
            for name in ('MF_adapted_donor_hood','MF_diagonal_donor_wrap'):
                obj=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(obj.data)
                todo=set(e for e in bm.edges if e.is_boundary);groups=[]
                while todo:
                    edge=todo.pop();edges={edge};stack=[edge];vertices=set(edge.verts)
                    while stack:
                        for v in stack.pop().verts:
                            for e in v.link_edges:
                                if e in todo:
                                    todo.remove(e);edges.add(e);stack.append(e);vertices.update(e.verts)
                    groups.append({'edges':len(edges),'perimeter':sum(e.calc_length() for e in edges),
                                   'bounds':[[min(v.co[c] for v in vertices) for c in range(3)],
                                             [max(v.co[c] for v in vertices) for c in range(3)]]})
                report[name]=groups;bm.free()
            out.mkdir();(out/'boundaries.json').write_text(json.dumps(report,indent=2))
    else:
        for obj in list(bpy.context.scene.objects):
            if obj.type=='MESH' and obj!=head:obj.hide_render=True
        variant=job['variant']
        mat=fabric_material(variant);make_hood(mat,variant);make_shoulders(mat,variant);make_hair(variant)
        out.mkdir()
        review(bpy.context.scene,out,(0,-.1,-.60),5.6,[('front',0),('left',-45),('right',45)])
        bpy.context.scene.camera.location=(0,-10,-.60)
        bpy.context.scene.camera.rotation_euler=(math.pi/2,0,0)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed.blend'))
    head=bpy.data.objects['FBHead']
    assert geometry_digest(head)==geometry
    assert material_signature(head.data.materials[0])==material
    assert values=={k.name:k.value for k in head.data.shape_keys.key_blocks}
    assert hashlib.sha256(HEAD.read_bytes()).hexdigest()==HEAD_SHA
    if not out.exists():out.mkdir()
    result={'face_geometry_digest':geometry,'face_material_signature':material,'shape_values':values,
            'head_sha256':HEAD_SHA,'donor_sha256':DONOR_SHA,'operation':job['operation'],'variant':job['variant'],
            'limitations':'Static portrait fit only; no Director acceptance, animation, full-body or all-angle qualification.',
            'reference_sha256':REFERENCE_SHA,'side_reference_sha256':SIDE_SHA,
            'credit':'Hijab by lam_m_zack, CC BY 4.0, https://sketchfab.com/3d-models/hijab-ee50e01adc864ccc880caed9b5eb3bcb; hood/wrap cropped, extended, deformed, recolored. Hair geometry authored locally; variant 5 uses 04saken CC BY 4.0 hair texture; other variants use procedural fibers. Cloth projects approved project portraits.'}
    if job['operation']=='portrait_dressing':result['native_sha256']=hashlib.sha256((out/'dressed.blend').read_bytes()).hexdigest()
    else:
        result['fresh_reopen_verified']=True
        result['verified_native_sha256']=record['native_sha256']
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
