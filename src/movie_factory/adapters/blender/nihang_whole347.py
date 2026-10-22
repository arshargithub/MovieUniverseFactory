"""Fixed whole-actor derivative of47; no external assets or recipe code.

Authored garment relaxation is not cloth simulation. Preserve skeleton actions,
hands and torso anatomy; evidence must qualify each posed interface separately.
"""
import math
import json
from pathlib import Path
import numpy as np


def relaxed_points(points, edges, strength, iterations=8):
    p=np.asarray(points,dtype=float).copy();w=np.asarray(strength,dtype=float)
    if p.ndim!=2 or p.shape[1]!=3 or w.shape!=(len(p),) or not np.isfinite(p).all():
        raise ValueError('WHOLE347_POINTS')
    if np.any(w<0) or np.any(w>1):raise ValueError('WHOLE347_WEIGHTS')
    e=np.asarray(edges,dtype=int)
    if e.ndim!=2 or e.shape[1]!=2 or e.min()<0 or e.max()>=len(p):raise ValueError('WHOLE347_EDGES')
    for _ in range(iterations):
        total=np.zeros_like(p);count=np.zeros(len(p))
        for a,b in ((e[:,0],e[:,1]),(e[:,1],e[:,0])):
            np.add.at(total,a,p[b]);np.add.at(count,a,1)
        delta=total/np.maximum(count[:,None],1)-p
        p+=delta*w[:,None]*.42
    return p


def fold_field(p):
    """Waist-origin fan folds fade at their anchors and across the chest."""
    x,y,z=np.asarray(p).T
    side=np.sign(y);waist=np.exp(-((z-1.26)/.13)**2)
    front=np.clip((np.abs(y)-.045)/.055,0,1)
    broad=.008*np.sin(44*x+18*(z-1.16)+.7*np.sin(17*x))
    fine=.0018*np.sin(93*x-21*z)*np.exp(-((z-1.20)/.09)**2)
    # Unequal tension ridges originate near the belted waist and die toward the
    # chest. Compact ridge/valley pairs are folds, not large cloudy shading.
    ridges=np.zeros(len(x))
    for h,slope,amp in ((1.27,.34,.009),(1.35,-.28,.007),(1.43,.23,.005)):
        d=z-h-slope*x
        ridges+=amp*(np.exp(-(d/.012)**2)-.45*np.exp(-((d+.016)/.013)**2))*np.exp(-(x/.26)**4)
    anchor=np.clip((z-1.23)/.05,0,1)
    return np.column_stack((np.zeros(len(x)),side*front*anchor*(waist*broad+fine+ridges),np.zeros(len(x))))


def finish_face(bpy,rig,body):
    """Root a continuous beard into the actual evaluated resting face.

    Replaces overlapping donor cards, not the face geometry or its identity.
    Carries the exact existing head attachment action; no independent head owner.
    """
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    rng=np.random.default_rng(347)
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mat=rig.matrix_world.inverted()@body.matrix_world
    tree=BVHTree.FromPolygons([mat@v.co for v in ev.data.vertices],[tuple(p.vertices) for p in ev.data.polygons])
    source=bpy.data.objects['beard donor-guided fiber detail']
    eye=rig.data.bones['eye.L'].head_local.z
    paths=[]
    for i in range(3700):
        x=float(rng.uniform(-.076,.076));z=eye-float(rng.uniform(.030,.130))
        # Diagonal upper cheek boundary and clear lips, not a rectangular sticker.
        if z>eye-.078+.48*abs(x):continue
        if abs(x)<.027 and eye-.097<z<eye-.055:continue
        hit=tree.ray_cast(Vector((x,-.6,z)),Vector((0,1,0)))[0]
        if hit is None or hit.y>-.04:continue
        root=hit+Vector((0,-.0014,0))
        length=float(rng.uniform(.058,.105))*(1-.24*abs(x)/.076)
        phase=float(rng.uniform(0,math.tau));points=[]
        for j in range(14):
            t=j/13;wave=math.sin(math.pi*t)
            points.append(root+Vector((.006*math.sin(phase+9*t)*wave,-.025*t+.003*math.sin(phase+12*t)*wave,-length*t)))
        paths.append(points)
    # Moustache fans from philtrum to corners with downward ends.
    for side in (-1,1):
        for i in range(310):
            u=float(rng.random());x=side*(.003+.038*u);z=eye-.061+float(rng.uniform(-.003,.002))-.005*u
            hit=tree.ray_cast(Vector((x,-.6,z)),Vector((0,1,0)))[0]
            if hit is None:continue
            root=hit+Vector((0,-.0015,0));points=[];length=float(rng.uniform(.012,.023))
            for j in range(10):
                t=j/9;points.append(root+Vector((side*length*t,-.004*math.sin(t*math.pi),-(.006+length*.3)*t-.003*t*t)))
            paths.append(points)
    if len(paths)<1500:raise ValueError('WHOLE347_BEARD_ROOT_COVERAGE')
    data=bpy.data.curves.new('347 skin rooted beard','CURVE');data.dimensions='3D';data.bevel_depth=.00025;data.bevel_resolution=1;data.resolution_u=1
    for points in paths:
        spline=data.splines.new('POLY');spline.points.add(len(points)-1)
        for j,(p,co) in enumerate(zip(spline.points,points)):
            p.co=(*co,1);p.radius=max(.05,(1-j/(len(points)-1))**.52)
    ob=bpy.data.objects.new('MF347 integrated beard and moustache',data);bpy.context.scene.collection.objects.link(ob)
    ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=source.matrix_basis.copy();ob.rotation_mode='QUATERNION'
    ob.animation_data_create();ob.animation_data.action=source.animation_data.action.copy()
    if ob.animation_data.action.slots:ob.animation_data.action_slot=ob.animation_data.action.slots[0]
    hairmat=source.data.materials[0].copy();hairmat.name='347 dark beard varied fibers';data.materials.append(hairmat)
    bs=next(n for n in hairmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for link in list(bs.inputs['Base Color'].links):hairmat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=(.016,.009,.005,1);bs.inputs['Roughness'].default_value=.57
    bs.inputs['Specular IOR Level'].default_value=.30
    info=hairmat.node_tree.nodes.new('ShaderNodeHairInfo');ramp=hairmat.node_tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.008,.005,.003,1);ramp.color_ramp.elements[-1].color=(.045,.025,.014,1)
    hairmat.node_tree.links.new(info.outputs['Random'],ramp.inputs['Fac']);hairmat.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    hidden=[]
    for old in rig.children:
        if old.name.startswith(('beard donor-guided','Sikh265 coherent MPFB male.rehmanpolanski_')):
            old.hide_render=True;hidden.append(old.name)
    for ob in rig.children:
        if ob.name.startswith(('eyeball.','iris.','pupil.')):
            for m in ob.data.materials:
                bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                if bs:bs.inputs['Roughness'].default_value=.24;bs.inputs['Specular IOR Level'].default_value=.40
    skin=body.data.materials[0];nodes=skin.node_tree.nodes
    for n in nodes:
        if n.type=='TEX_NOISE' and n.inputs['Scale'].default_value<100:n.inputs['Scale'].default_value=120
        if n.type=='VALTORGB':
            n.color_ramp.elements[0].color=(.16,.068,.032,1);n.color_ramp.elements[-1].color=(.32,.169,.084,1)
        if n.type=='BUMP':n.inputs['Strength'].default_value=.36;n.inputs['Distance'].default_value=.0007
    return dict(curves=len(paths),eye_height=eye,hidden=hidden,attachment='Existing source head action, actual resting skin roots')


SKIN_GRAIN='.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-02/skin-authored.png'


def skin_grain(bpy,body):
    """Reuse only featureless top-left pigment texture; no facial-image transfer."""
    image=bpy.data.images.load(str(Path(__file__).resolve().parents[4]/SKIN_GRAIN),check_existing=True)
    image.pack();mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    for socket in ('Base Color','Normal'):
        for link in list(bs.inputs[socket].links):l.remove(link)
    uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.23,.23,0)
    offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.01,.75,0)
    tex=n.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND'
    l.new(uv.outputs['UV'],scale.inputs[0]);l.new(scale.outputs['Vector'],offset.inputs[0]);l.new(offset.outputs['Vector'],tex.inputs['Vector'])
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.65,.70,.74,1)
    l.new(tex.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00035
    l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return dict(source=SKIN_GRAIN,uv_rectangle=[.01,.75,.24,.98],scope='Featureless pigment grain only, no eyes/nose/lips or identity mapping')


def saddle_finish(bpy):
    ob=bpy.data.objects.get('fitted saddle blanket292')
    if not ob:raise ValueError('WHOLE347_SADDLE')
    mat=ob.data.materials[0].copy();mat.name='347 woven saddle blanket';ob.data.materials[0]=mat
    material(bpy,mat,(.033,.046,.063),(.069,.083,.104),240)
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],sep.inputs[0])
    edge=n.new('ShaderNodeMath');edge.operation='PINGPONG';edge.inputs[1].default_value=.5;l.new(sep.outputs['X'],edge.inputs[0])
    band=n.new('ShaderNodeMath');band.operation='LESS_THAN';band.inputs[1].default_value=.05;l.new(edge.outputs[0],band.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.30,.15,.044,1)
    previous=bs.inputs['Base Color'].links[0].from_socket;l.new(previous,mix.inputs[1]);l.new(band.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    return dict(object=ob.name,scope='Actual existing fitted saddle blanket with woven border; geometry and horse ownership unchanged')


def garment_edges(bpy,coat,rig):
    """Visible sewn edges sharing the garment skeleton and actual rest surface."""
    from collections import Counter
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    mesh=coat.data;edges=Counter(tuple(sorted((a,b))) for f in mesh.polygons for a,b in zip(f.vertices,(*f.vertices[1:],f.vertices[0])))
    boundary=[e for e,count in edges.items() if count==1 and all(mesh.vertices[i].co.z>1.36 for i in e)]
    pts=[];faces=[];weights=[]
    for a,b in boundary:
        av,bv=mesh.vertices[a],mesh.vertices[b]
        # A narrow turned hem, not shoulder armor or decorative metallic piping.
        start=len(pts)
        for v in (av,bv):
            normal=v.normal.normalized();edge=(bv.co-av.co).normalized();across=normal.cross(edge).normalized()
            for sign in (-1,1):
                pts.append(v.co+normal*.002+across*(sign*.0025))
                weights.append([(coat.vertex_groups[g.group].name,g.weight) for g in v.groups if coat.vertex_groups[g.group].name in rig.data.bones])
        faces.append((start,start+1,start+3,start+2))
    tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
    for j in range(32):
        z=1.25+.33*j/31;x=.025+.012*math.sin((z-1.25)*5)
        for sign in (-1,1):
            hit,n,idx,_=tree.ray_cast(Vector((x+sign*.007,-.7,z)),Vector((0,1,0)))
            if hit is None:raise ValueError('WHOLE347_PLACKET_SUPPORT')
            pts.append(hit+n*.003)
            source=mesh.vertices[mesh.polygons[idx].vertices[0]]
            weights.append([(coat.vertex_groups[g.group].name,g.weight) for g in source.groups if coat.vertex_groups[g.group].name in rig.data.bones])
        if j:
            k=len(pts)-4;faces.append((k,k+1,k+3,k+2))
    data=bpy.data.meshes.new('347 turned chola hems');data.from_pydata(pts,[],faces);data.update()
    ob=bpy.data.objects.new('MF347 chola neckline cuff and placket',data);bpy.context.scene.collection.objects.link(ob)
    ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=coat.matrix_basis.copy()
    mat=coat.data.materials[0].copy();mat.name='347 darker indigo turned edges';material(bpy,mat,(.009,.018,.032),(.020,.035,.056));data.materials.append(mat)
    for i,row in enumerate(weights):
        total=sum(w for _,w in row)
        if total<.5:raise ValueError('WHOLE347_EDGE_WEIGHT')
        for name,w in row:
            g=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name);g.add([i],w/total,'REPLACE')
    arm=ob.modifiers.new('Same garment skeleton','ARMATURE');arm.object=rig
    shrink=ob.modifiers.new('Sewn to actual coat exterior','SHRINKWRAP');shrink.target=coat;shrink.wrap_method='NEAREST_SURFACEPOINT';shrink.wrap_mode='ABOVE_SURFACE';shrink.offset=.002
    solid=ob.modifiers.new('Turned cloth thickness','SOLIDIFY');solid.thickness=.001
    for p in data.polygons:p.use_smooth=True
    return dict(object=ob.name,vertices=len(pts),edges=len(boundary))


def material(bpy,mat,low,high,grain=190):
    n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    # Retain existing image alpha on cards; only change owned solid cloth shaders.
    for socket in ('Base Color','Normal','Roughness'):
        for link in list(bs.inputs[socket].links):l.remove(link)
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=65;noise.inputs['Detail'].default_value=3
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.16;ramp.color_ramp.elements[-1].position=.84
    ramp.color_ramp.elements[0].color=(*low,1);ramp.color_ramp.elements[-1].color=(*high,1)
    l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=grain;fine.inputs['Roughness'].default_value=.8
    l.new(tc.outputs['Object'],fine.inputs['Vector']);bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.00065
    l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value=.84;bs.inputs['Specular IOR Level'].default_value=.21
    bs.inputs['Sheen Weight'].default_value=.15


def run(bpy,out):
    import importlib.util
    spec=importlib.util.spec_from_file_location('whole_support',Path(__file__).with_name('nihang_support.py'))
    support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
    scene=support.select_production_scene(bpy);scene.frame_set(283)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if rig.get('whole347'):raise ValueError('WHOLE347_ALREADY_APPLIED')
    if not rig.get('finish345'):raise ValueError('WHOLE347_PARENT_NOT47')
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    old=np.array([v.co[:] for v in coat.data.vertices]);edges=[e.vertices[:] for e in coat.data.edges]
    # Freeze waist support and cuff boundaries; remove inflated rest shoulder form.
    w=np.clip((old[:,2]-1.24)/.15,0,1)*np.clip((.48-np.abs(old[:,0]))/.12,0,1)
    new=relaxed_points(old,edges,w)+fold_field(old)
    # Copy-on-write protects prior meshes. Hidden coat supports receive the same
    # coordinate mapping by nearest original point, not a second independent fit.
    from mathutils.kdtree import KDTree
    kd=KDTree(len(old))
    for i,p in enumerate(old):kd.insert(p,i)
    kd.balance();changed=[]
    for ob in [coat]+[o for o in bpy.data.objects if o.name in ('MF coherent layer support','MF346 waist-only coat support')]:
        ob.data=ob.data.copy()
        for v in ob.data.vertices:
            _,i,d=kd.find(v.co)
            if d<.0001:v.co+=__import__('mathutils').Vector(new[i]-old[i])
        ob.data.update()
        for mod in ob.modifiers:
            if mod.type=='ARMATURE':mod.use_deform_preserve_volume=False
        # Corrective smoothing works on post-armature geometry, before subdiv.
        smooth=ob.modifiers.new('347 garment joint relaxation','CORRECTIVE_SMOOTH')
        group=ob.vertex_groups.new(name='347 upper garment relaxation')
        for v in ob.data.vertices:
            weight=max(0,min(1,(v.co.z-1.29)/.11))
            if weight:group.add([v.index],weight,'REPLACE')
        smooth.factor=.5;smooth.iterations=8;smooth.use_pin_boundary=True
        smooth.vertex_group=group.name
        smooth.rest_source='ORCO'
        ob.modifiers.move(len(ob.modifiers)-1,1)
        changed.append(ob.name)
    for name,low,high in [('MF coherent weathered indigo',(.022,.041,.072),(.038,.062,.105)),
                           ('MF coherent ochre weave',(.25,.139,.043),(.34,.205,.072))]:
        mat=bpy.data.materials.get(name)
        if mat:material(bpy,mat,low,high)
    # Crown core and courses keep their exact animated head owner. Relief is
    # constrained to each existing surface, with irregular oblique compression.
    crown=[]
    for ob in rig.children:
        if not ob.name.startswith(('MF Nihang wrapped crown','MF Nihang overlapped cloth','MF Nihang gathered crown')):continue
        if ob.type!='MESH':continue
        ob.data=ob.data.copy()
        for v in ob.data.vertices:
            x,y,z=v.co;angle=math.atan2(x,y+.02)
            # Cloth coordinates are flattened head-rest coordinates (z~1.8).
            center=1.746 if z>1 else 0
            height=z-center
            relief=.0018*math.sin(angle*7+height*65)+.0009*math.sin(angle*13-height*83)
            radius=math.hypot(x,y+.02)
            if radius>.03:v.co.x+=relief*x/radius;v.co.y+=relief*(y+.02)/radius
        ob.data.update();crown.append(ob.name)
    # Keep imported beard silhouette but remove the exaggerated narrow hanging
    # point in both cards and curve strands using their shared local bounds.
    duplicates=[]
    for ob in rig.children:
        if ob.name.startswith('Sikh265 coherent MPFB male.rehmanpolanski_') and any(m.type=='ARMATURE' for m in ob.modifiers):
            ob.hide_render=True;duplicates.append(ob.name)
    hair=[o for o in rig.children if not o.hide_render and o.name.startswith(('beard donor-guided','Sikh265 coherent MPFB male.rehmanpolanski_beard'))]
    hair_report=[]
    for ob in hair:
        ob.data=ob.data.copy()
        blocks=([ob.data.vertices] if ob.type=='MESH' else [s.points for s in ob.data.splines])
        pts=[p for block in blocks for p in block]
        if not pts:continue
        zs=[p.co.z for p in pts];lo=min(zs);hi=max(zs);span=hi-lo
        for p in pts:
            u=max(0,min(1,(hi-p.co.z)/max(span,1e-6)))
            ease=u*u*(3-2*u);p.co.x*=1+.16*ease;p.co.z+=.018*ease
        hair_report.append(dict(name=ob.name,z=[lo,hi],type=ob.type))
    body=bpy.data.objects['MF coherent Nihang body']
    if not any(m.type=='SUBSURF' for m in body.modifiers):
        sub=body.modifiers.new('347 continuous facial curvature','SUBSURF');sub.levels=1;sub.render_levels=1
    bpy.context.view_layer.update()
    face=finish_face(bpy,rig,body);hems=garment_edges(bpy,coat,rig)
    pigment=skin_grain(bpy,body);saddle=saddle_finish(bpy)
    # Inventory makes the next decision use actual attachment spaces/materials.
    objects=[]
    for ob in rig.children:
        if ob.type in ('MESH','CURVE'):
            points=[v.co[:] for v in ob.data.vertices] if ob.type=='MESH' else [p.co[:3] for s in ob.data.splines for p in s.points]
            objects.append(dict(name=ob.name,type=ob.type,materials=[m.name for m in ob.data.materials],
                bounds=np.array(points).min(0).tolist()+np.array(points).max(0).tolist() if points else [],
                modifiers=[m.type for m in ob.modifiers],hidden=ob.hide_render))
    rig.data.pose_position='POSE';rig['whole347']=1;scene.frame_set(283);bpy.context.view_layer.update()
    report=dict(changed=changed,crown=crown,hair=hair_report,objects=objects,hidden_duplicate_cards=duplicates,face=face,hems=hems,pigment=pigment,saddle=saddle,
        maximum_rest_change=float(np.linalg.norm(new-old,axis=1).max()),
        scope='Whole appearance first proof, authored relaxation not simulation or artistic acceptance')
    (out/'whole347.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
