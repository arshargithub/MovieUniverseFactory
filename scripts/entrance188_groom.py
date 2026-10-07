"""Source-rooted, deterministic horse groom. Native trajectory, not simulation."""
import numpy as np


def guides(samples, children=3):
    """Preserve source roots; author flow in a moving crest frame, not world axes."""
    a = np.asarray(samples, dtype=np.float64)
    if a.shape != (144, 1047, 6, 3) or not np.isfinite(a).all():
        raise ValueError('Bound source mane samples required')
    if children not in (1, 3):
        raise ValueError('Reviewed density only')
    root = a[:, :, 0]
    y = root[0, :, 1]
    # Stable neighborhoods on either side of each growth position.
    neighbors = []
    for value in y:
        neighbors.append((np.argsort(abs(y-(value-.30)))[:14],
                          np.argsort(abs(y-(value+.30)))[:14]))
    tangent = np.stack([root[:,hi].mean(1)-root[:,lo].mean(1) for lo,hi in neighbors], axis=1)
    tangent /= np.maximum(np.linalg.norm(tangent, axis=-1, keepdims=True), 1e-8)
    side = np.cross(tangent, [0.,0.,1.])
    side /= np.maximum(np.linalg.norm(side, axis=-1, keepdims=True), 1e-8)
    up = np.cross(side, tangent)
    up /= np.maximum(np.linalg.norm(up, axis=-1, keepdims=True), 1e-8)
    rng = np.random.default_rng(18801)
    n = len(y)*children
    roots = np.repeat(root, children, axis=1)
    side = np.repeat(side, children, axis=1)
    tangent = np.repeat(tangent, children, axis=1)
    up = np.repeat(up, children, axis=1)
    fy = np.repeat(y, children)
    t = np.linspace(0, 1, 12)[None,None,:,None]
    # Forelock separates at the poll; the crest flows down one side of the neck.
    fore = (fy < -6.8).astype(float)[None,:,None,None]
    length = rng.uniform(.82,1.15,n)[None,:,None,None]
    phase = (np.repeat(y,children)*3.7+rng.normal(0,.22,n))[None,:,None,None]
    time = np.arange(144)[:,None,None,None]/24
    curl = np.sin(t*6.5+phase+time*5)*t*t
    s = (-2.1*np.sin(t*np.pi/2) + .18*curl)*(1-fore) + (-.15*np.sin(t*np.pi/2)+.10*curl)*fore
    along = (2.65*t + .25*np.sin(t*4+phase)*t)*(1-fore) - .85*t*fore
    vertical = -1.20*t**1.4*(1-fore) - 1.05*t**1.4*fore + .16*curl
    length*=np.where(fy>-3.,.58,1.)[None,:,None,None]
    points = roots[:,:,None,:] + length*(side[:,:,None,:]*s + tangent[:,:,None,:]*along + up[:,:,None,:]*vertical)
    # Root-correlated inertial follow-through, not independent noisy strand motion.
    lag = np.maximum(0,np.arange(144)-3)
    inertia = (roots[lag]-roots)[:,:,None,:]
    points += inertia*(t*t)*.42
    return points.astype(np.float32), {'guides':n,'points_per_guide':12,
        'source_root_error':float(np.max(abs(points[:,:,0]-roots))),
        'motion':'Authored crest-relative flow with short root-motion lag; not physical hair simulation'}


def tube_frames(points):
    a = np.asarray(points, dtype=np.float32)
    tang = np.gradient(a,axis=2)
    tang /= np.maximum(np.linalg.norm(tang,axis=-1,keepdims=True),1e-8)
    u = np.cross(tang,[0.,1.,0.])
    u /= np.maximum(np.linalg.norm(u,axis=-1,keepdims=True),1e-8)
    v = np.cross(tang,u)
    rng=np.random.default_rng(18802)
    radii=(np.linspace(.026,.0012,a.shape[2])[None,None,:,None]
           *rng.uniform(.65,1.2,a.shape[1])[None,:,None,None])
    tubes=np.stack([a+u*radii,a+(-.5*u+.8660254*v)*radii,
                    a+(-.5*u-.8660254*v)*radii],axis=3).reshape(len(a),-1,3)
    faces=[]
    for strand in range(a.shape[1]):
        for k in range(a.shape[2]-1):
            first=(strand*a.shape[2]+k)*3
            for side in range(3):
                faces.append((first+side,first+(side+1)%3,first+3+(side+1)%3,first+3+side))
    return tubes.astype(np.float32), faces


def build(scene,out,source):
    import bpy
    from entrance_astra_world import mesh_object
    from wardrobe_shawl180_cache import cache
    curves,report=guides(np.load(source)['points'])
    report['surface_clearance']=clear_mane(curves,bpy.data.objects['MF185_gait_horse'])
    vertices,faces=tube_frames(curves)
    ob=mesh_object('MF188_flowing_mane',vertices[0].tolist(),faces,scene.collection)
    ob.location.z=-1.05
    colors=[(.028,.012,.005),(.045,.018,.007),(.075,.032,.012),(.105,.052,.022),(.16,.078,.027)]
    for i,c in enumerate(colors):
        mat=bpy.data.materials.new('MF188_mane_'+str(i));mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value=(*c,1)
        shader.inputs['Roughness'].default_value=.53
        shader.inputs['Specular IOR Level'].default_value=.25
        anisotropy=shader.inputs.get('Anisotropic') or shader.inputs.get('Anisotropic IOR Level')
        if anisotropy:anisotropy.default_value=.5
        ob.data.materials.append(mat)
    rng=np.random.default_rng(18803)
    labels=np.repeat(rng.choice(5,curves.shape[1],p=[.24,.38,.24,.10,.04]),33)
    ob.data.polygons.foreach_set('material_index',labels.astype(np.int32))
    for poly in ob.data.polygons:poly.use_smooth=True
    mod=cache(ob,vertices,out/'mane.mdd');mod.frame_start=217
    report['native_vertices']=len(vertices[0]);report['root_location_z']=-1.05
    return report


def clear_mane(curves,horse):
    """Keep authored hairs outside the actual cached neck/head, not a guessed ellipsoid."""
    import struct
    import bpy
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector
    from pathlib import Path
    path=Path(bpy.path.abspath(next(m.filepath for m in horse.modifiers if m.type=='MESH_CACHE')))
    with path.open('rb') as stream:nf,nv=struct.unpack('>ii',stream.read(8))
    if nf!=144 or nv!=len(horse.data.vertices):raise ValueError('Horse trajectory topology mismatch')
    samples=np.memmap(path,dtype='>f4',mode='r',offset=8+nf*4,shape=(nf,nv,3))
    p0=samples[0]
    polys=[tuple(p.vertices) for p in horse.data.polygons if p.material_index==0 and
           np.all(p0[list(p.vertices),1]<1) and np.all(p0[list(p.vertices),2]>-11)]
    forehead=[tuple(p.vertices) for p in horse.data.polygons if p.material_index==0 and
              np.all(p0[list(p.vertices),1]<-6.2) and np.all(p0[list(p.vertices),2]>-4.3) and
              np.all(abs(p0[list(p.vertices),0])<1.5)]
    if not forehead:raise ValueError('No semantic forehead support')
    fore=np.repeat(curves[0,:,0,1]<-6.8,11)
    count=0;worst=0.
    for f in range(nf):
        bvh=BVHTree.FromPolygons(np.asarray(samples[f],dtype=float).tolist(),polys)
        brow=BVHTree.FromPolygons(np.asarray(samples[f],dtype=float).tolist(),forehead)
        flat=curves[f,:,1:].reshape(-1,3).copy()
        for j,point in enumerate(flat):
            loc,normal,face,distance=(brow if fore[j] else bvh).find_nearest(Vector(point.tolist()))
            if face is not None:
                signed=(Vector(point.tolist())-loc).dot(normal)
                if signed<.025 or fore[j]:
                    offset=.035+.10*np.sin(np.pi*((j%11)+1)/12) if fore[j] else .025
                    worst=max(worst,-signed);flat[j]=np.array(loc)+np.array(normal)*offset;count+=1
        curves[f,:,1:]=flat.reshape(curves.shape[1],11,3)
        if f%36==0:print('188 groom surface clearance',f,flush=True)
    return {'corrected_control_points':count,'max_preprojection_penetration_native':worst,
            'method':'Nearest actual head/neck surface normal projection of interior guide controls; segment/visual checks separate'}


def coat(horse):
    """Keep source color ownership; add stable UV-attached short-coat response."""
    import bpy
    mat=horse.data.materials[0].copy();mat.name='MF188_bay_short_coat';horse.data.materials[0]=mat
    n,l=mat.node_tree.nodes,mat.node_tree.links
    bsdf=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    coord=n.new('ShaderNodeTexCoord')
    mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(150,24,1)
    l.new(coord.outputs['UV'],mapping.inputs[0])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=5;fine.inputs['Detail'].default_value=2;fine.inputs['Roughness'].default_value=.7
    l.new(mapping.outputs[0],fine.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.4;bump.inputs['Distance'].default_value=.028
    l.new(fine.outputs['Fac'],bump.inputs['Height'])
    if bsdf.inputs['Normal'].is_linked:l.new(bsdf.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(bump.outputs[0],bsdf.inputs['Normal'])
    rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.62;rough.inputs['To Max'].default_value=.82
    l.new(fine.outputs['Fac'],rough.inputs['Value']);l.new(rough.outputs[0],bsdf.inputs['Roughness'])
    bsdf.inputs['Sheen Weight'].default_value=.20
    bsdf.inputs['Specular IOR Level'].default_value=.3
    bsdf.inputs['Sheen Roughness'].default_value=.6
    anisotropy=bsdf.inputs.get('Anisotropic') or bsdf.inputs.get('Anisotropic IOR Level')
    if anisotropy:anisotropy.default_value=.32
    # Warm, irregular body color variation at coat scale, never screen-space noise.
    source_color=bsdf.inputs['Base Color'].links[0].from_socket if bsdf.inputs['Base Color'].is_linked else None
    if source_color:
        lum=n.new('ShaderNodeRGBToBW');l.new(source_color,lum.inputs[0])
        scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=2.5;l.new(lum.outputs[0],scale.inputs[0])
        bay=n.new('ShaderNodeValToRGB')
        bay.color_ramp.elements[0].color=(.09,.022,.005,1);bay.color_ramp.elements[1].color=(.30,.12,.038,1)
        mid=bay.color_ramp.elements.new(.45);mid.color=(.19,.059,.016,1)
        l.new(scale.outputs[0],bay.inputs[0])
        coarse=n.new('ShaderNodeTexNoise');coarse.inputs['Scale'].default_value=48;coarse.inputs['Detail'].default_value=3
        l.new(coord.outputs['UV'],coarse.inputs[0])
        cr=n.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(.46,.36,.27,1);cr.color_ramp.elements[1].color=(1,1,1,1)
        l.new(coarse.outputs['Fac'],cr.inputs[0])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.30
        l.new(bay.outputs[0],mix.inputs[1]);l.new(cr.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bsdf.inputs['Base Color'])
    from pathlib import Path
    image_path=Path(__file__).resolve().parents[1]/'.runtime/art-direction/series01-entrance-art188/horse-coat-v01.png'
    authored=n.new('ShaderNodeTexImage');authored.image=bpy.data.images.load(str(image_path),check_existing=True)
    scale_uv=n.new('ShaderNodeVectorMath');scale_uv.operation='SCALE';scale_uv.inputs[3].default_value=15
    l.new(coord.outputs['UV'],scale_uv.inputs[0]);l.new(scale_uv.outputs[0],authored.inputs[0])
    before=bsdf.inputs['Base Color'].links[0].from_socket
    coat_detail=n.new('ShaderNodeValToRGB');coat_detail.color_ramp.elements[0].color=(.45,.45,.45,1);coat_detail.color_ramp.elements[1].position=.45;coat_detail.color_ramp.elements[1].color=(1,1,1,1)
    l.new(authored.outputs['Color'],coat_detail.inputs[0])
    coat_mix=n.new('ShaderNodeMixRGB');coat_mix.blend_type='MULTIPLY';coat_mix.inputs[0].default_value=.65
    l.new(before,coat_mix.inputs[1]);l.new(coat_detail.outputs[0],coat_mix.inputs[2]);l.new(coat_mix.outputs[0],bsdf.inputs['Base Color'])
    authored_bump=n.new('ShaderNodeBump');authored_bump.inputs['Strength'].default_value=.22;authored_bump.inputs['Distance'].default_value=.008
    l.new(authored.outputs['Color'],authored_bump.inputs['Height']);l.new(bump.outputs[0],authored_bump.inputs['Normal']);l.new(authored_bump.outputs[0],bsdf.inputs['Normal'])
    return {'material':mat.name,'coordinates':'original UV, stable with cached deformation'}


def fuzz(scene,horse):
    """Barycentric attachment samples evaluated source triangles; no random reseeding in motion."""
    import bpy
    scene.frame_set(217);bpy.context.view_layer.update()
    evaluated=horse.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    p=np.array([v.co[:] for v in mesh.vertices])
    ids=np.array([t.vertices[:] for t in mesh.loop_triangles if mesh.polygons[t.polygon_index].material_index==0])
    tri=p[ids];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
    rng=np.random.default_rng(18804);count=22000
    chosen=rng.choice(len(ids),count,p=area/area.sum());indices=ids[chosen];tri=tri[chosen]
    uv=rng.random((count,2));uv[uv.sum(1)>1]=1-uv[uv.sum(1)>1]
    weights=np.column_stack([1-uv.sum(1),uv])
    root=(tri*weights[:,:,None]).sum(1)
    desired=np.tile([0.,1.,-.25],(count,1));desired[root[:,2]<-11]=[0,0,-1];desired[root[:,1]<-6]=[0,-1,-1]
    e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
    basis=np.stack([e1,e2],axis=2)
    coef=np.einsum('nij,nj->ni',np.linalg.pinv(basis),desired)
    evaluated.to_mesh_clear()
    data=bpy.data.meshes.new('MF188_fixed_fuzz_binding')
    data.from_pydata(np.repeat(root,3,axis=0).tolist(),[(3*i+k,3*i+k+1) for i in range(count) for k in range(2)],[]);data.update()
    ob=bpy.data.objects.new('MF188_short_coat_fuzz',data);scene.collection.objects.link(ob)
    def attr(name,kind,values):
        a=data.attributes.new(name,kind,'POINT');a.data.foreach_set('value',np.asarray(values).ravel())
    for i in range(3):
        attr('bind_index_'+str(i),'INT',np.repeat(indices[:,i],3))
        attr('bind_weight_'+str(i),'FLOAT',np.repeat(weights[:,i],3))
    for i in range(2):attr('flow_'+str(i),'FLOAT',np.repeat(coef[:,i],3))
    length=rng.uniform(.033,.055,count)
    length[root[:,1]<-6]*=.27
    attr('tip_offset','FLOAT',(length[:,None]*np.array([0,.25,.50])).ravel())
    attr('flow_offset','FLOAT',(length[:,None]*np.array([0,.6,1.])).ravel())
    attr('mf188_fuzz_radius','FLOAT',np.tile([.0015,.001,.0003],count))
    group=bpy.data.node_groups.new('MF188_fixed_surface_fuzz','GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    nodes,links=group.nodes,group.links
    inp=nodes.new('NodeGroupInput');out=nodes.new('NodeGroupOutput')
    info=nodes.new('GeometryNodeObjectInfo');info.transform_space='RELATIVE';info.inputs['Object'].default_value=horse
    position=nodes.new('GeometryNodeInputPosition')
    def named(name,kind='FLOAT'):
        n=nodes.new('GeometryNodeInputNamedAttribute');n.data_type=kind;n.inputs['Name'].default_value=name;return n.outputs['Attribute']
    def vector(op,a,b=None):
        n=nodes.new('ShaderNodeVectorMath');n.operation=op;links.new(a,n.inputs[0])
        if b is not None:links.new(b,n.inputs[3] if op=='SCALE' else n.inputs[1])
        return n.outputs['Vector']
    sampled=[];weighted=[]
    for i in range(3):
        s=nodes.new('GeometryNodeSampleIndex');s.data_type='FLOAT_VECTOR';s.domain='POINT'
        links.new(info.outputs['Geometry'],s.inputs['Geometry']);links.new(position.outputs[0],s.inputs['Value']);links.new(named('bind_index_'+str(i),'INT'),s.inputs['Index'])
        sampled.append(s.outputs['Value']);weighted.append(vector('SCALE',s.outputs['Value'],named('bind_weight_'+str(i))))
    base=vector('ADD',vector('ADD',weighted[0],weighted[1]),weighted[2])
    edge1=vector('SUBTRACT',sampled[1],sampled[0]);edge2=vector('SUBTRACT',sampled[2],sampled[0])
    normal=vector('NORMALIZE',vector('CROSS_PRODUCT',edge1,edge2))
    flow=vector('NORMALIZE',vector('ADD',vector('SCALE',edge1,named('flow_0')),vector('SCALE',edge2,named('flow_1'))))
    newpos=vector('ADD',base,vector('ADD',vector('SCALE',normal,named('tip_offset')),vector('SCALE',flow,named('flow_offset'))))
    setpos=nodes.new('GeometryNodeSetPosition');links.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);links.new(newpos,setpos.inputs['Position'])
    tocurve=nodes.new('GeometryNodeMeshToCurve');links.new(setpos.outputs['Geometry'],tocurve.inputs['Mesh'])
    radius=nodes.new('GeometryNodeSetCurveRadius');links.new(tocurve.outputs['Curve'],radius.inputs['Curve']);links.new(named('mf188_fuzz_radius'),radius.inputs['Radius'])
    circle=nodes.new('GeometryNodeCurvePrimitiveCircle');circle.inputs['Resolution'].default_value=3;circle.inputs['Radius'].default_value=1
    tube=nodes.new('GeometryNodeCurveToMesh');links.new(radius.outputs['Curve'],tube.inputs['Curve']);links.new(circle.outputs['Curve'],tube.inputs['Profile Curve'])
    # Blender5.2's explicit Scale may replace legacy radius consumption.
    if tube.inputs.get('Scale'):links.new(named('mf188_fuzz_radius'),tube.inputs['Scale'])
    mat=bpy.data.materials.new('MF188_fine_brown_fuzz');mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.065,.026,.011,1);bs.inputs['Roughness'].default_value=.66
    assign=nodes.new('GeometryNodeSetMaterial');assign.inputs['Material'].default_value=mat;links.new(tube.outputs['Mesh'],assign.inputs['Geometry']);links.new(assign.outputs['Geometry'],out.inputs['Geometry'])
    mod=ob.modifiers.new('Fixed barycentric coat attachment','NODES');mod.node_group=group
    return {'strands':count,'binding':'Fixed original triangle indices and barycentric weights; evaluated horse positions each frame',
            'length_native_range':[.033,.068],'weights_max_error':float(abs(weights.sum(1)-1).max()),'simulation':False}
