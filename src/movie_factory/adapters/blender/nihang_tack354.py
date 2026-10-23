"""Reconstruct local saddlecloth on actual horse; preserve keyed performance."""
import math,json,hashlib
import numpy as np

def blanket_probe(u,v,lo,hi):
    low=np.asarray(lo);high=np.asarray(hi);center=(low+high)/2
    a=(2*u-1)*1.40;edge=abs(math.sin(a))**5
    x=center[0]+(high[0]-low[0])*.50*math.sin(a)
    y=center[1]+(v-.5)*(high[1]-low[1])*(1-.14*edge)
    z=high[2]-.46*(1-math.cos(a))+.009*edge*math.sin(5*math.pi*v+.4)
    return np.array((x,y,z))

def action_signature(bpy):
    out=[]
    for action in bpy.data.actions:
        curves=[]
        if hasattr(action,'fcurves'):
            try:curves=list(action.fcurves)
            except RuntimeError:pass
        if not curves:
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        out.append((action.name,[(c.data_path,c.array_index,[(tuple(k.co),k.interpolation) for k in c.keyframe_points]) for c in curves]))
    return hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    rig=bpy.data.objects['MF coherent Nihang rig']
    if not rig.get('form354') or rig.get('tack354'):raise ValueError('TACK354_PARENT')
    actions=action_signature(bpy);scene=bpy.context.scene;frame=scene.frame_current
    scene.frame_set(283);bpy.context.view_layer.update()
    old=bpy.data.objects['fitted saddle blanket292'];horse=bpy.data.objects['horse']
    matworld=old.matrix_world.copy();inv=matworld.inverted();ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([horse.matrix_world@v.co for v in ev.data.vertices],[tuple(p.vertices) for p in ev.data.polygons])
    lo=[min(v.co[i] for v in old.data.vertices) for i in range(3)];hi=[max(v.co[i] for v in old.data.vertices) for i in range(3)]
    rows=33;cols=49;points=[];uvs=[];distances=[]
    for j in range(rows):
        for k in range(cols):
            u=k/(cols-1);v=j/(rows-1);probe=matworld@Vector(blanket_probe(u,v,lo,hi))
            hit,n,_,dist=tree.find_nearest(probe)
            if hit is None or dist>.30:raise ValueError('TACK354_BACK_SUPPORT')
            points.append(inv@(hit+n*(.008+.001*math.sin(v*21)*abs(2*u-1)**6)))
            uvs.append((u,v));distances.append(dist)
    faces=[]
    for j in range(rows-1):
        for k in range(cols-1):a=j*cols+k;faces.append((a,a+1,a+cols+1,a+cols))
    data=bpy.data.meshes.new('354 body-draped rounded saddlecloth');data.from_pydata(points,[],faces);data.update()
    uv=data.uv_layers.new(name='cloth354')
    for poly in data.polygons:
        poly.use_smooth=True
        for i in poly.loop_indices:uv.data[i].uv=uvs[data.loops[i].vertex_index]
    inventory=[dict(name=o.name,hidden=o.hide_render,type=o.type) for o in bpy.data.objects if 'saddle' in o.name.lower() or 'blanket' in o.name.lower()]
    old.data=data;old.hide_render=False;old.hide_viewport=False
    for name in ('MF Nihang body-fitted wool saddle pad','331 rounded draped saddle pad'):
        obj=bpy.data.objects.get(name)
        if obj:obj.hide_render=True
    for m in list(old.modifiers):old.modifiers.remove(m)
    sub=old.modifiers.new('354 softened draped edge','SUBSURF');sub.levels=1;sub.render_levels=1
    wrap=old.modifiers.new('354 compressed pad on animated horse','SHRINKWRAP');wrap.target=horse;wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.wrap_mode='OUTSIDE_SURFACE';wrap.offset=.008
    sol=old.modifiers.new('354 wool thickness','SOLIDIFY');sol.thickness=.006;sol.offset=0
    mat=bpy.data.materials.new('354 woven indigo pad narrow ochre binding');mat.use_nodes=True;data.materials.append(mat)
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.87;bs.inputs['Sheen Weight'].default_value=.25
    tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['UV'],sep.inputs[0]);axes=[]
    for axis in ('X','Y'):
        subn=n.new('ShaderNodeMath');subn.operation='SUBTRACT';subn.inputs[0].default_value=1;l.new(sep.outputs[axis],subn.inputs[1])
        mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';l.new(sep.outputs[axis],mn.inputs[0]);l.new(subn.outputs[0],mn.inputs[1]);axes.append(mn.outputs[0])
    mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';l.new(axes[0],mn.inputs[0]);l.new(axes[1],mn.inputs[1])
    edge=n.new('ShaderNodeMath');edge.operation='LESS_THAN';edge.inputs[1].default_value=.027;l.new(mn.outputs[0],edge.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.018,.032,.065,1);mix.inputs[2].default_value=(.16,.085,.027,1);l.new(edge.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=260;l.new(tc.outputs['UV'],noise.inputs[0])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.00055;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    rig['tack354']=1;scene.frame_set(frame);bpy.context.view_layer.update()
    after=action_signature(bpy)
    if actions!=after:raise ValueError('TACK354_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,action_signature=actions,actions_unchanged=True,vertices=len(points),maximum_support_distance=max(distances),inventory=inventory,scope='Rounded body-supported saddlecloth and narrow UV edge; actual posed review required, not physics simulation.')
    (out/'tack354.json').write_text(json.dumps(report,indent=2)+'\n');return report
