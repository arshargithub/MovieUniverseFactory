"""Fixed saved-actor layer proof; binding follows the actual cloth surface.

No model code, paths, installations or new donor imports are accepted. This is
a reversible derivative of actor33, not a new accepted character.
"""
import math
import numpy as np


def cuff_fit(points,wrist,elbow,side):
    p=np.asarray(points,dtype=float).copy();w=np.asarray(wrist);e=np.asarray(elbow)
    axis=(w-e)/np.linalg.norm(w-e);q=p-w;along=q@axis
    radial=q-along[:,None]*axis;radius=np.linalg.norm(radial,axis=1)
    mask=(p[:,0]*side>.30)&(along>-.12)&(along<.03)
    weight=np.clip((along+.12)/.075,0,1)*mask
    scale=np.minimum(1,.044/np.maximum(radius,1e-8))
    p+=radial*((scale-1)*weight)[:,None]
    return p,mask


def coat_region(points,wrists,elbows):
    """Rest-body ownership, with wrist planes independent of hand spread."""
    p=np.asarray(points);keep=(p[:,2]>1.005)&(p[:,2]<1.635)
    for side in (-1,1):
        w=np.asarray(wrists[side]);e=np.asarray(elbows[side]);axis=(w-e)/np.linalg.norm(w-e)
        keep &= ~((p[:,0]*side>.28)&((p-w)@axis>-.038))
    return keep


def body_coat(bpy,body,coat,rig):
    """Construct the actual rest body shell, retaining each anatomical weight."""
    from mathutils.kdtree import KDTree
    states=[(m,m.show_viewport,m.show_render) for m in body.modifiers]
    for m,_,_ in states:m.show_viewport=False;m.show_render=False
    bpy.context.view_layer.update()
    raw=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    if len(raw.vertices)!=len(body.data.vertices):raise ValueError('REFIT_BODY_INDEX')
    kd=KDTree(len(raw.vertices))
    for v in raw.vertices:kd.insert(v.co,v.index)
    kd.balance()
    for m,v,r in states:
        if m.type=='MASK':m.show_viewport=v;m.show_render=r
    bpy.context.view_layer.update()
    surface=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    transform=coat.matrix_world.inverted()@body.matrix_world
    if max(abs(transform[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))>.0001:
        raise ValueError('REFIT_BODY_COAT_SPACE')
    wrists={s:np.array(rig.data.bones['wrist.'+('L' if s==1 else 'R')].head_local) for s in (-1,1)}
    elbows={s:np.array(rig.data.bones['lowerarm01.'+('L' if s==1 else 'R')].head_local) for s in (-1,1)}
    points=np.array([v.co[:] for v in surface.vertices]);keep=coat_region(points,wrists,elbows)
    faces=[tuple(p.vertices) for p in surface.polygons if all(keep[i] for i in p.vertices)]
    ids=sorted({i for f in faces for i in f});remap={v:i for i,v in enumerate(ids)}
    coords=[];weights=[]
    for i in ids:
        v=surface.vertices[i]
        # Waist compression fades out before the chest; bounded geometric folds,
        # not a global sine-wave displacement over anatomy.
        x,y,z=v.co;band=math.exp(-((z-1.14)/.085)**2)
        folds=.0045*band*math.sin(z*91+x*13+math.sin(x*17))
        coords.append(v.co+v.normal*(.024+folds))
        src=kd.find(v.co)[1]
        weights.append([(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[src].groups])
    mesh=bpy.data.meshes.new('MF body-fitted continuous chola35');mesh.from_pydata(coords,[],[tuple(remap[i] for i in f) for f in faces]);mesh.update()
    for mat in coat.data.materials:mesh.materials.append(mat)
    coat.data=mesh;coat.vertex_groups.clear()
    for i,row in enumerate(weights):
        for name,w in row:
            g=coat.vertex_groups.get(name) or coat.vertex_groups.new(name=name);g.add([i],w,'REPLACE')
    for p in mesh.polygons:p.use_smooth=True
    for m,v,r in states:m.show_viewport=v;m.show_render=r
    for d in (raw,surface):bpy.data.meshes.remove(d)
    bpy.context.view_layer.update()
    return dict(method='Actual evaluated rest body shell with inherited anatomical weights',vertices=len(coords),faces=len(faces),normal_clearance=.024)


def lower_garment_ownership(bpy):
    """Remove the rest-pose hand islands wrongly captured by the pants z-cut."""
    import bmesh
    pants=bpy.data.objects['MF coherent pants'];bm=bmesh.new();bm.from_mesh(pants.data)
    ids=[v for v in bm.verts if abs(v.co.x)>.34 and v.co.z>.9]
    removed=len(ids);bmesh.ops.delete(bm,geom=ids,context='VERTS');bm.to_mesh(pants.data);bm.free();pants.data.update()
    skirts=[o for o in bpy.data.objects if o.name.startswith('MF coherent split chola')]
    for obj in skirts:
        for v in obj.data.vertices:
            u=max(0,min(1,(1.06-v.co.z)/.45))
            v.co.z+=.035*(1-u)**2
        obj.data.update()
    return dict(pants_hand_vertices_removed=removed,skirt_roots_extended=len(skirts),overlap=.035)


def oppose_thumbs(bpy,rig,support):
    """Oppose each thumb across the actual index grip, retaining phalanx lengths."""
    from mathutils import Vector
    scene=bpy.context.scene;records=[]
    for frame in range(252,442):
        scene.frame_set(frame);bpy.context.view_layer.update()
        for side in ('L','R'):
            suffix='.'+side
            wrist=rig.pose.bones['wrist'+suffix]
            hand=wrist.matrix@wrist.bone.matrix_local.inverted()
            bones=[rig.pose.bones[f'finger1-{j}'+suffix] for j in (1,2,3)]
            index=rig.pose.bones['finger2-2'+suffix]
            middle=rig.pose.bones['finger3-1'+suffix]
            base=hand@bones[0].bone.head_local
            longitudinal=(middle.head-wrist.head).normalized()
            across=(rig.pose.bones['finger2-1'+suffix].head-rig.pose.bones['finger5-1'+suffix].head).normalized()
            normal=across.cross(longitudinal).normalized()
            # Same dorsal side on both hands. Thumb rests over the index, not
            # on the common cross-palm curling axis used by the four fingers.
            if side=='R':normal=-normal
            target=(index.head+index.tail)*.5+normal*.010
            first=base+(index.head-base).normalized()*bones[0].bone.length
            distance=(target-first).length;lengths=[p.bone.length for p in bones[1:]]
            if not abs(lengths[0]-lengths[1])+.0001<distance<sum(lengths)-.005:
                raise ValueError('REFIT_THUMB_TARGET_UNREACHABLE')
            joint=Vector(support.bend_joint(first,target,bones[1].bone.length,bones[2].bone.length,tuple(normal)))
            endpoints=[base,first,joint,target]
            for pb,a,b in zip(bones,endpoints,endpoints[1:]):
                rest=hand.to_3x3()@pb.bone.matrix_local.to_3x3()
                rotation=rest.col[1].normalized().rotation_difference((b-a).normalized()).to_matrix()@rest
                m=rotation.to_4x4();m.translation=a;pb.rotation_mode='QUATERNION';pb.matrix=m
                for path in ('location','rotation_quaternion','scale'):pb.keyframe_insert(path,frame=frame)
                bpy.context.view_layer.update()
            records.append(dict(frame=frame,side=side,target=list(target),error=(bones[-1].tail-target).length))
    scene.frame_set(283);bpy.context.view_layer.update()
    return dict(samples=len(records),maximum_tip_error=max(x['error'] for x in records),method='Thumb opposition to actual index grip; fixed anatomical lengths',samples_at_controls=[x for x in records if x['frame'] in (283,327,350)])


def surface_readability(bpy,body,coat):
    """Retain warm skin and indigo; introduce visible surface variation, not a new style."""
    mat=body.data.materials[0].copy();mat.name='MF leader warm weathered skin36';body.data.materials[0]=mat
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value=.67;bs.inputs['Specular IOR Level'].default_value=.25
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=47;noise.inputs['Detail'].default_value=3
    l.new(tc.outputs['Object'],noise.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.19,.076,.034,1)
    ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.32,.161,.079,1)
    l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=620;fine.inputs['Detail'].default_value=2
    l.new(tc.outputs['Object'],fine.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.20;bump.inputs['Distance'].default_value=.00045
    l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    for name in ('MF coherent weathered indigo','MF coherent ochre weave'):
        material=bpy.data.materials.get(name)
        if not material:continue
        for node in material.node_tree.nodes:
            if node.type=='BUMP':node.inputs['Strength'].default_value=.4;node.inputs['Distance'].default_value=.0007
            if node.type=='VALTORGB':
                for e in node.color_ramp.elements:
                    factor=.83 if e.position<.5 else 1.12
                    e.color=tuple(c*factor for c in e.color[:3])+(1,)


def run(bpy,out):
    import json
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from pathlib import Path
    import importlib.util
    spec=importlib.util.spec_from_file_location('mf_refit_support',Path(__file__).with_name('nihang_support.py'))
    support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
    scene=support.select_production_scene(bpy);scene.frame_set(283)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    body=bpy.data.objects['MF coherent Nihang body']
    if rig.get('layer_refit_proof'):raise ValueError('REFIT_ALREADY_APPLIED')
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    # An always-projecting post-deform wrap erased cloth volume and changed its
    # posed surface independently of the sash. Preserve the fitted cloth shell.
    removed=[]
    for mod in list(coat.modifiers):
        if mod.type=='SHRINKWRAP':removed.append(mod.name);coat.modifiers.remove(mod)
    shell=body_coat(bpy,body,coat,rig);cuffs=[]
    lower=lower_garment_ownership(bpy);surface_readability(bpy,body,coat)
    # Bind to a clean, open evaluated garment target (no opposing solid shell).
    cage=coat.copy();cage.data=coat.data.copy();scene.collection.objects.link(cage)
    cage.name='MF coherent layer support';cage.hide_render=True
    for mod in list(cage.modifiers):
        if mod.type=='SOLIDIFY':cage.modifiers.remove(mod)
    bpy.context.view_layer.update()
    evaluated=cage.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([v.co for v in evaluated.data.vertices],[tuple(p.vertices) for p in evaluated.data.polygons])
    layers=[]
    for name,offset in [('MF coherent waist wrap',.010),('MF coherent shoulder sash',.008)]:
        obj=bpy.data.objects[name]
        for mod in list(obj.modifiers):obj.modifiers.remove(mod)
        distances=[]
        for v in obj.data.vertices:
            p,n,_,distance=tree.find_nearest(v.co)
            if p is None or distance>.20:raise ValueError('REFIT_LAYER_SUPPORT_DISTANCE')
            v.co=p+n*offset;distances.append(distance)
        obj.data.update();bpy.context.view_layer.update()
        mod=obj.modifiers.new('Follow actual coat deformation','SURFACE_DEFORM');mod.target=cage;mod.falloff=4
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.ops.object.surfacedeform_bind(modifier=mod.name)
        if not mod.is_bound:raise ValueError('REFIT_SURFACE_BIND_FAILED')
        solid=obj.modifiers.new('Woven layer thickness','SOLIDIFY');solid.thickness=.002
        bevel=obj.modifiers.new('Soft woven edge','BEVEL');bevel.width=.0015;bevel.segments=2
        layers.append({'name':name,'bound':True,'maximum_rest_projection':max(distances),'offset':offset})
    rig.data.pose_position='POSE';rig['layer_refit_proof']=1
    thumbs=oppose_thumbs(bpy,rig,support)
    rows=[]
    for frame in (283,327,350):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=cage.evaluated_get(bpy.context.evaluated_depsgraph_get())
        tree=BVHTree.FromPolygons([v.co for v in ev.data.vertices],[tuple(p.vertices) for p in ev.data.polygons])
        for name,_ in [('MF coherent waist wrap',0),('MF coherent shoulder sash',0)]:
            obj=bpy.data.objects[name];mesh=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            signed=[]
            for v in mesh.vertices:
                p,n,_,_=tree.find_nearest(v.co)
                signed.append(float((v.co-p).dot(n)))
            rows.append({'frame':frame,'layer':name,'minimum_signed_distance':min(signed),
                         'penetrating_vertices':sum(x<-.001 for x in signed),'vertices':len(signed)})
    scene.frame_set(283);bpy.context.view_layer.update()
    bones={n:{'rest_head':list(b.head_local),'rest_tail':list(b.tail_local),
              'posed_head':list(rig.pose.bones[n].head),'posed_tail':list(rig.pose.bones[n].tail)}
           for n,b in rig.data.bones.items() if n.startswith(('wrist','finger','lowerarm'))}
    (out/'actor-hand-diagnostic.json').write_text(json.dumps(bones,indent=2)+'\n')
    return {'scope':'Actual layer binding and three mounted pose checks; not full actor or AV approval.',
            'removed_projection':removed,'body_shell':shell,'lower_ownership':lower,'thumb_opposition':thumbs,'cuffs':cuffs,'layers':layers,'pose_checks':rows}
