"""Pinned local crown/hairline and hanging-wave refinement; no costume renders.

Only authored, reviewed handlers execute. Job data cannot supply code or paths.
Accepted non-hair geometry, UVs, materials and expression controls stay exact.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'hair-look-package-06/hair-textured.blend'
SOURCE_SHA='a21d56f687611f1e20298eda1bfa98c3189c1e582b2934c24013a5c90b9ba9b1'
REFBASE=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES={
    'frontal-v02-individualized.png':'7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png':'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview','repair','finish','package') or type(job['candidate']) is not int or job['candidate'] not in (1,2,3):
        raise ValueError('Unsupported fixed operation')
    if job['operation']=='repair' and job['candidate']!=3:
        raise ValueError('Only third-preview junction repair supported')
    if job['operation'] in ('finish','package') and job['candidate']!=3:
        raise ValueError('Only third-candidate finalization supported')
    for p,h in [(SOURCE,SOURCE_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p)!=h: raise ValueError('Pinned input changed')
    out=BASE/f'hair-finish-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():
        raise ValueError('Output exists or escapes fixed directory')
    if shutil.disk_usage(BASE).free<5_000_000_000: raise ValueError('Disk low')
    if job['operation']=='package':
        stage='finish'
        p=BASE/f'hair-finish-{stage}-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file(): raise ValueError('Preview required')
        result=json.loads(p.read_text())
        if result['handler_sha256']!=digest(Path(__file__)) or not result['protected_exact']:
            raise ValueError('Stale preview or failed protection')
    return out


def smooth(t):
    t=max(0.,min(1.,t)); return t*t*(3-2*t)


def hair_uv(x,z):
    """Keep the lower rim inside painted hair, not painted forehead skin."""
    # The upper mapping continues smoothly; a material feather removes the
    # unavailable upper image region instead of stretching one clamped row.
    py=1647*(1-(.156*z+.677))
    py=max(220.,min(695.,py))
    rows=[(220,425,563),(240,392,598),(280,337,652),(330,301,690),(400,274,707),(500,246,717),(600,247,719),(700,259,704)]
    i=next((i for i in range(len(rows)-1) if rows[i+1][0]>=py),len(rows)-2)
    a,b=rows[i],rows[i+1]; t=(py-a[0])/(b[0]-a[0])
    lo=a[1]*(1-t)+b[1]*t; hi=a[2]*(1-t)+b[2]*t
    px=477.5+227.29*x; center=488
    bound=hi if px>center else lo; limit=abs(bound-center); delta=px-center
    if abs(delta)>limit*.75:
        delta=math.copysign(limit*(.75+.23*math.tanh((abs(delta)/limit-.75)/.23)),delta)
    px=center+delta
    # Shift the lower sampling window into real brushwork instead of clamping
    # to a single row (the first diagnostic produced a stretched fringe).
    py-=20*smooth((py-275)/65)
    return px/955,1-py/1647


def lift(x,y,z):
    # Slight lift on viewer-left, not a mirrored/reshaped face or a bouffant.
    return .046*math.exp(-((x+.38)/.32)**2-((y+.71)/.42)**2-((z-1.05)/.26)**2)


def guide(index,count=17):
    theta=math.radians(-86+172*index/(count-1))
    phase=index*.83
    points=[]
    for k,(z,r) in enumerate(((1.18,.57),(.61,.88),(.14,1.02),(-.37,1.04),(-.84,1.01),(-1.28,.96),(-1.77,.82))):
        weight=smooth(k/3)
        angle=theta+weight*(.13*math.sin(k*1.83+phase)+.042*math.sin(phase*2))
        radius=r+weight*.08*math.sin(k*1.65+phase+.9)
        if k==6: z+=.21*math.sin(index*1.9)
        points.append((radius*math.sin(angle),radius*math.cos(angle),z))
    return points


def material():
    import bpy
    m=bpy.data.materials.new('MF_refined_hair_painted_flow'); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.69; p.inputs['Specular IOR Level'].default_value=.16
    uv=n.new('ShaderNodeUVMap'); uv.uv_map='HairFlow'
    scale=n.new('ShaderNodeVectorMath'); scale.operation='MULTIPLY'; scale.inputs[1].default_value=(105,3.8,1); l.new(uv.outputs[0],scale.inputs[0])
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=1; noise.inputs['Detail'].default_value=2.5
    l.new(scale.outputs[0],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB'); cr=ramp.color_ramp
    cr.elements.remove(cr.elements[1]); cr.elements[0].position=.25; cr.elements[0].color=(.004,.0017,.001,1)
    for at,c in ((.44,(.014,.0057,.0025,1)),(.59,(.042,.017,.007,1)),(.72,(.12,.052,.021,1)),(.86,(.22,.11,.044,1))): cr.elements.new(at).color=c
    l.new(noise.outputs['Fac'],ramp.inputs[0])
    refuv=n.new('ShaderNodeUVMap'); refuv.uv_map='ReferenceHair'
    tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=False); tex.image.pack(); l.new(refuv.outputs[0],tex.inputs[0])
    geom=n.new('ShaderNodeNewGeometry'); sep=n.new('ShaderNodeSeparateXYZ'); l.new(geom.outputs['Position'],sep.inputs[0])
    def fade(socket,a,b):
        node=n.new('ShaderNodeMapRange'); node.inputs['From Min'].default_value=a; node.inputs['From Max'].default_value=b; l.new(socket,node.inputs['Value']); return node.outputs[0]
    def maximum(a,b):
        node=n.new('ShaderNodeMath'); node.operation='MAXIMUM'; l.new(a,node.inputs[0]); l.new(b,node.inputs[1]); return node.outputs[0]
    mask=maximum(fade(sep.outputs['Y'],-.32,.32),fade(sep.outputs['Z'],.3,.05))
    mask=maximum(mask,fade(sep.outputs['Z'],1.10,1.29))
    rgb=n.new('ShaderNodeSeparateColor'); l.new(tex.outputs[0],rgb.inputs[0])
    blue=n.new('ShaderNodeMath'); blue.operation='GREATER_THAN'; l.new(rgb.outputs['Blue'],blue.inputs[0]); l.new(rgb.outputs['Red'],blue.inputs[1]); mask=maximum(mask,blue.outputs[0])
    mix=n.new('ShaderNodeMixRGB'); l.new(mask,mix.inputs[0]); l.new(tex.outputs[0],mix.inputs[1]); l.new(ramp.outputs[0],mix.inputs[2])
    l.new(mix.outputs[0],p.inputs['Base Color']); l.new(mix.outputs[0],p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value=.12
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.09; bump.inputs['Distance'].default_value=.010
    l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],p.inputs['Normal'])
    return m


def uv_layers(mesh,points=None):
    from hair_volume_sculpt import spline
    flow=mesh.uv_layers.get('HairFlow') or mesh.uv_layers.new(name='HairFlow')
    ref=mesh.uv_layers.get('ReferenceHair') or mesh.uv_layers.new(name='ReferenceHair')
    for poly in mesh.polygons:
        for k in poly.loop_indices:
            vi=mesh.loops[k].vertex_index; x,y,z=mesh.vertices[vi].co
            u=math.atan2(x,y)/(2*math.pi)
            if points is not None:
                t=(vi//20+1)/84 if vi<1660 else (0 if vi==1660 else 1)
                cx,cy,cz=spline(points,min(1,t))
                u+=smooth((.05-z)/.9)*(math.atan2(points[0][0],points[0][1])-math.atan2(cx,cy))/(2*math.pi)
            flow.data[k].uv=(u,(1.4-z)*.3)
            ref.data[k].uv=hair_uv(x,z)
    mesh.uv_layers.active_index=list(mesh.uv_layers.keys()).index('HairFlow'); flow.active_render=True


def merge_join(base,locks,mat):
    """Union authored hair only; transfer exact source UVs to the new surface."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    bpy.ops.object.select_all(action='DESELECT')
    copies=[]
    for ob in [base]+locks:
        dupe=ob.copy(); dupe.data=ob.data.copy(); bpy.context.scene.collection.objects.link(dupe)
        dupe.hide_set(False); dupe.hide_render=False; dupe.select_set(True); copies.append(dupe)
    bpy.context.view_layer.objects.active=copies[0]; bpy.ops.object.join()
    source=copies[0]; source.name='MF_hair_join_uv_donor'
    mesh=source.data; mesh.calc_loop_triangles()
    verts=[v.co.copy() for v in mesh.vertices]
    triangles=list(mesh.loop_triangles)
    tree=BVHTree.FromPolygons(verts,[t.vertices[:] for t in triangles],all_triangles=True)
    target=source.copy(); target.data=source.data.copy(); bpy.context.scene.collection.objects.link(target)
    target.name='MF_hair_continuous_wave_shell'
    bpy.ops.object.select_all(action='DESELECT'); target.select_set(True); bpy.context.view_layer.objects.active=target
    remesh=target.modifiers.new('Continuous authored hair junction','REMESH')
    remesh.mode='VOXEL'; remesh.voxel_size=.012; remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    # Smooth only the rear crown/length junction; retain front and tapered tips.
    group=target.vertex_groups.new(name='Rear junction only')
    for v in target.data.vertices:
        x,y,z=v.co
        weight=smooth((y-.05)/.4)*math.exp(-((z-.50)/.29)**2)
        if weight>.005: group.add([v.index],weight,'REPLACE')
    mod=target.modifiers.new('Soften rear junction','SMOOTH'); mod.factor=.7; mod.iterations=7; mod.vertex_group=group.name
    bpy.ops.object.modifier_apply(modifier=mod.name)
    names=('HairFlow','ReferenceHair'); cache={}
    for v in target.data.vertices:
        co,normal,index,distance=tree.find_nearest(v.co)
        if index is None: raise ValueError('UV transfer failed')
        tri=triangles[index]; a,b,c=[verts[i] for i in tri.vertices]
        cache[v.index]=[]
        for name in names:
            uv=mesh.uv_layers[name]
            ua,ub,uc=[Vector((*uv.data[k].uv,0)) for k in tri.loops]
            cache[v.index].append(barycentric_transform(co,a,b,c,ua,ub,uc)[:2])
    for j,name in enumerate(names):
        uv=target.data.uv_layers.get(name) or target.data.uv_layers.new(name=name)
        for loop in target.data.loops: uv.data[loop.index].uv=cache[loop.vertex_index][j]
    target.data.materials.clear(); target.data.materials.append(mat)
    for p in target.data.polygons: p.material_index=0; p.use_smooth=True
    for ob in [base,source]+locks: ob.hide_render=True; ob.hide_set(True)
    return target


def build(candidate,repair=False,union=False):
    import bpy
    from mathutils import Vector
    from hair_volume_sculpt import skull_surface
    from hair_illustrated_look import lock
    from hair_anatomy_refinement import is_hair
    base=bpy.data.objects['MF_sculpt_hair_support']
    keep=[base]+[bpy.data.objects[f'MF_illustrated_hair_lock_{i}'] for i in range(21,27)]
    for ob in bpy.context.scene.objects:
        if is_hair(ob): ob.hide_render=ob not in keep; ob.hide_set(ob.hide_render)
    mat=material()
    for ob in keep:
        for v in ob.data.vertices:
            # A shared spatial warp keeps overlapping crown sheets aligned;
            # separate normal displacement made them intersect in preview 1.
            v.co.z+=lift(*v.co)
            if abs(v.co.x)<.13 and v.co.z>1.24:
                v.co.z+=.018*math.exp(-(v.co.x/.09)**2)*smooth((v.co.z-1.24)/.06)
        ob.data.update(); uv_layers(ob.data)
        ob.data.materials.clear(); ob.data.materials.append(mat)
        for p in ob.data.polygons: p.material_index=0
    tree=skull_surface(bpy.data.objects['MF_reference_crown_hair']); origin=Vector((0,0,.3))
    count=17
    new=[]
    for i in range(count):
        points=guide(i,count)
        if repair and i in (0,count-1):
            x,y,z=points[2]; points[2]=(x+math.copysign(.018,x),y-.065,z)
        for k,depth in ((0,-.075),(1,-.015)):
            co=Vector(points[k]); hit,n,_,_=tree.ray_cast(origin,(co-origin).normalized())
            if hit is None: raise ValueError('Root projection failed')
            points[k]=tuple(hit+n*depth)
        ob=lock(points,.18+.025*math.sin(i*2.4),.059+.008*math.sin(i),100+i,mat,1)
        # Feather the final third instead of ending a broad lock abruptly.
        from hair_volume_sculpt import spline
        for v in ob.data.vertices:
            if v.index>=1660: continue
            t=(v.index//20+1)/84
            if t>.67:
                center=Vector(spline(points,t))
                v.co=center+(v.co-center)*(1-.88*smooth((t-.67)/.33))
        ob.data.update()
        uv_layers(ob.data,points); new.append(ob)
    if union: merge_join(base,new,mat)
    return {'new_wave_locks':len(new),'retained_front_locks':6,'hairline_skin_sampling_removed':True,
            'crown_row_repeat_feathered':True,'junction_unioned':union,'face_or_skin_edited':False,'rear_design':'PROVISIONAL'}


def run(job):
    out=validate(job); out.mkdir()
    shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection()
    if job=={'operation':'preview','candidate':1}:
        visibility(hair=False)
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('diagnostic-source-no-hair',0),))
    info=build(job['candidate'],job['operation'] in ('repair','finish','package'),job['operation']=='repair'); visibility(); assert protection()==before
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
            'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,'changes':info,
            'clothing_rendered':False,'director_acceptance':'PENDING','hair_motion_qualified':False}
    if job['operation']=='package':
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
        native=out/'hair-refined.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['fresh_reopen_protected_exact']=protection()==before
        assert result['fresh_reopen_protected_exact']; result['native_sha256']=digest(native)
    assert protection()==before and digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
