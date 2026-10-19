"""Supporting cast only: restore donor anatomy materials and authored cloth detail."""
import json,math
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from sikh292_assets import surface
from sikh257_native import material
ROOT=Path(__file__).resolve().parents[1]
def earth_finish(out,source):
    from mathutils.bvhtree import BVHTree
    from sikh315_scene import noise
    from movie_factory import sikh315_motion as m
    road=bpy.data.objects['irregular packed farm track'];old=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    supports=json.loads((source/'terrain.json').read_text())['supports']
    def hill(x,y):
        hit=old.ray_cast(Vector((x,y,9)),Vector((0,0,-1)))[0]
        if hit is None:return 0.
        previous=hit.z
        if not (1.6<x<24 and -46<y<-12 and previous>.18):return previous
        dx=x-7.5;dy=y+29;theta=math.atan2(dy,dx)
        r=math.hypot(dx/(5.7 if dx<0 else 9.4),dy/12.5)/(1+.16*math.sin(3*theta+.6)+.07*math.sin(5*theta-1.2))
        base=3.25*max(0,1-r**1.7)
        z=base+.075*noise(x,y,1.8)+.035*noise(x,y,6)-.10*abs(noise(x*.7,y,3.1))
        w=1-m.ease((r-.82)/.18);z=z*w+previous*(1-w)
        for sx,sy,sz in supports:
            wt=1-m.ease((math.hypot(x-sx,y-sy)-.16)/.38);z=z*(1-wt)+sz*wt
        return z
    for v in road.data.vertices:
        x,y,z=v.co
        if 1.6<x<24 and -46<y<-12:v.co.z=hill(x,y)
    for ob in bpy.data.objects:
        if ob.type!='MESH' or not ob.name.startswith(('304 rooted ditch','314 clustered drainage vegetation','315 collapsed clay bank clods')):continue
        for v in ob.data.vertices:
            x,y=v.co.x+ob.location.x,v.co.y+ob.location.y
            if 1.6<x<24 and -46<y<-12:
                hit=old.ray_cast(Vector((x,y,9)),Vector((0,0,-1)))[0]
                if hit:v.co.z+=hill(x,y)-hit.z
    road.data.update()
    # Skids are timed color in the actual ground, not a polygon carpet above it.
    trace=json.loads((source/'coordinated-motion.json').read_text());samples=[r for r in trace if r['slip']]
    xy=np.array([(v.co.x,v.co.y) for v in road.data.vertices]);dist=np.full(len(xy),1e9);birth=np.full(len(xy),40.)
    for r in samples:
        p=r['rear_tread_contact'];d=np.sum((xy-np.array(p[:2]))**2,axis=1);mask=d<dist;dist[mask]=d[mask];birth[mask]=r['source_t']
    strength=np.exp(-dist/(.065**2))*.30
    attr=road.data.color_attributes.new(name='315 contact wear',type='FLOAT_COLOR',domain='POINT')
    values=np.column_stack((strength,birth/40,np.zeros(len(xy)),np.ones(len(xy)))).astype(np.float32);attr.data.foreach_set('color',values.ravel())
    mat=road.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];color=b.inputs['Base Color'].links[0].from_socket
    a=n.new('ShaderNodeAttribute');a.attribute_name='315 contact wear';sep=n.new('ShaderNodeSeparateColor');l.new(a.outputs['Color'],sep.inputs[0]);time=n.new('ShaderNodeValue');time.name='315 contact birth source clock'
    for f in (1,696):time.outputs[0].default_value=(f-1)/24*m.RATE;time.outputs[0].keyframe_insert('default_value',frame=f)
    scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=40;l.new(sep.outputs['Green'],scale.inputs[0]);gate=n.new('ShaderNodeMath');gate.operation='GREATER_THAN';l.new(time.outputs[0],gate.inputs[0]);l.new(scale.outputs[0],gate.inputs[1]);mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(gate.outputs[0],mask.inputs[0]);l.new(sep.outputs['Red'],mask.inputs[1]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.42,.38,.29,1);l.new(mask.outputs[0],mix.inputs[0]);l.new(color,mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color'])
    for ob in bpy.data.objects:
        if ob.name.startswith('299 ground-integrated'):ob.hide_render=True;ob.animation_data_clear()
    (out/'ground-finish.json').write_text(json.dumps({'hill':'asymmetric continuous crest without broad flat cap; actual existing hoof supports retained','skid':'timed ground vertex attribute; no overlay geometry','stroke_samples':len(samples)},indent=2))

def finish(out):
    from sikh315_run import source_for
    job=json.loads((out/'job.json').read_text());source=source_for('finish',job['version']).parent
    if job['version']==6:
        import shutil
        for p in source.glob('*.json'):
            if p.name not in ('job.json','bindings.json'):shutil.copy2(p,out/p.name)
        settings=[]
        for light in bpy.data.lights:
            if hasattr(light,'use_shadow_jitter'):
                light.use_shadow_jitter=True
                settings.append({'name':light.name,'jitter':True})
        (out/'shadow-control.json').write_text(json.dumps({'cause':'Matched volume-off control retains patches; these are hard overlapping light shadows, not skid overlays or dust surfaces','change':'Enable sampling of existing light emitter size; preserve light energy/color/placement','lights':settings},indent=2))
        return
    if job['version']>=5:
        from sikh315_surface import refine
        refine(out,source)
        return
    earth_finish(out,source)
    from sikh315_scene import horse
    horse(out)
    from movie_factory import sikh315_motion as motion
    from sikh257_native import camera_at
    from sikh257_layout import key
    s=bpy.context.scene;cam=s.camera
    for f in range(1,697):
        t=(f-1)/24*motion.RATE
        if t<23.45:continue
        s.frame_set(f);u=motion.ease((t-23.45)/4);y=motion.travel(t)
        loc=Vector((-2.8,motion.travel(22.6)+3.8,2.1)).lerp(Vector((-4.8,motion.travel(22.6)+1,4.5)),u)
        camera_at(cam,loc,Vector((0,y-.15,1.05)).lerp(Vector((0,-145,1.2)),u));cam.data.lens=34+8*u;key(cam,f);cam.data.keyframe_insert('lens',frame=f)
    s=bpy.context.scene;s.frame_set(1);body=bpy.data.objects['horse']
    with bpy.data.libraries.load(str(ROOT/'.runtime/assets/demonstrator-01/horse.blend'),link=False) as (_,dest):dest.objects=['horse']
    donor=dest.objects[0]
    assert len(donor.data.vertices)==len(body.data.vertices) and len(donor.data.polygons)==len(body.data.polygons)
    assert all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(donor.data.polygons,body.data.polygons))
    coat=surface('315 living silver grey coat',[(.16,.155,.142),(.31,.305,.275)],11,rough=.51,bump=.00065)
    nodes=coat.node_tree.nodes;links=coat.node_tree.links;bs=nodes['Principled BSDF'];bs.inputs['Sheen Weight'].default_value=.22
    coord=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(75,18,90);links.new(coord.outputs['Object'],scale.inputs[0])
    fiber=nodes.new('ShaderNodeTexNoise');fiber.inputs['Scale'].default_value=3.0;links.new(scale.outputs[0],fiber.inputs[0]);bump=nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0006;bump.inputs['Strength'].default_value=.28;links.new(fiber.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],bs.inputs['Normal'])
    # Actual mesh regions, not guessed painted eyeballs or blanket material.
    mats=[]
    for i,src in enumerate(donor.data.materials):
        if i==0:mat=coat
        elif 'hooves' in src.name:mat=surface('315 dark horn hoof',[(.025,.021,.017),(.085,.073,.057)],27,rough=.56,bump=.0005)
        elif 'gums' in src.name:mat=material('315 dark natural mouth',(.075,.028,.022));mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.44
        elif 'teeth' in src.name:mat=material('315 warm ivory teeth',(.54,.48,.34));mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.43
        else:mat=src.copy();mat.name='315 restored '+src.name
        mats.append(mat)
    body.data.materials.clear()
    for mat in mats:body.data.materials.append(mat)
    for a,b in zip(body.data.polygons,donor.data.polygons):a.material_index=b.material_index
    # Vertex colour adds soft muzzle/leg pigmentation without painting over
    # the correctly separated eyes, mouth and hoof materials.
    colors=body.data.color_attributes.new(name='315 coat pigmentation',type='FLOAT_COLOR',domain='POINT')
    for v,c in zip(body.data.vertices,colors.data):
        x,y,z=v.co
        muzzle=max(0,min(1,(-y-1.58)/.22))*max(0,min(1,(z-1.5)/.22))
        legs=max(0,min(1,(.50-z)/.36));shade=1-.53*muzzle-.20*legs;c.color=(shade,shade,shade,1)
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='315 coat pigmentation';base=bs.inputs['Base Color'].links[0].from_socket;mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;links.new(base,mix.inputs[1]);links.new(attr.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
    bpy.data.objects.remove(donor,do_unlink=True)
    rng=np.random.default_rng(3154);changed=[]
    # Keep secondary parts and existing animated joints; modify cloth shape
    # coherently through all shape keys, never the principal rider proxy.
    cloth_prefix=('commander fitted chola','secondary chola292','297 continuous leader sleeve','297 crowd sleeve','297 continuous crowd trousers','297 continuous leader trousers')
    clothmats=[surface('315 worn indigo '+str(i),[(.012+i*.002,.022+i*.002,.052+i*.004),(.045+i*.004,.071+i*.004,.14+i*.008)],36,rough=.91,bump=.00065) for i in range(4)]
    for index,ob in enumerate(list(bpy.data.objects)):
        if ob.type!='MESH' or not ob.name.startswith(cloth_prefix):continue
        ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(clothmats[index%4]);changed.append(ob.name)
        for v in ob.data.vertices:
            p=v.co.copy();a=math.atan2(p.y,p.x);z=p.z
            if 'chola' in ob.name:
                radius=math.hypot(p.x,p.y)
                if radius<.04:continue
                waist=.06 if ob.name.startswith('commander') else .88
                amplitude=.003+.009*min(1,abs(z-waist)/.35)
                d=amplitude*(math.sin(a*9+z*2.5)+.35*math.sin(a*17-z*6));offset=Vector((p.x/radius*d,p.y/radius*d,0))
            else:offset=v.normal.copy()*(.0018*math.sin(z*48+p.x*17)+.0011*math.sin(z*73+p.y*31))
            v.co+=offset
            if ob.data.shape_keys:
                for sk in ob.data.shape_keys.key_blocks:sk.data[v.index].co+=offset
    # Existing turbans remain Nihang-style tied crowns; fabric takes worn
    # indigo treatment and subtle local fold variation, not a new style choice.
    for i,ob in enumerate(bpy.data.objects):
        if ob.type=='MESH' and ob.name.startswith(('297 tapered crown','297 overlapping fabric crown')):
            ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(clothmats[i%4])
    # Mane/forelock gain rooted volume, not uniformly thick wire strands.
    groom=[]
    for ob in list(bpy.data.objects):
        if ob.type=='CURVE' and ob.name.startswith(('rooted mane locks292','horse forelock292','horse tail fullness292')):
            ob.data=ob.data.copy();ob.data.bevel_depth*=1.35
            for sp in ob.data.splines:
                for j,p in enumerate(sp.points):p.radius=max(.12,(1-j/max(1,len(sp.points)))**.65)*float(rng.uniform(.8,1.15))
            if ob.name.startswith(('rooted mane locks292','horse forelock292')):groom.append(ob)
    for ob in groom:
        for k in range(3):
            copy=ob.copy();copy.data=ob.data.copy();s.collection.objects.link(copy);copy.name='315 rooted companion lock';copy.data.bevel_depth*=float(rng.uniform(.55,.85))
            offsets={}
            for si,sp in enumerate(copy.data.splines):
                for j,p in enumerate(sp.points):
                    u=j/max(1,len(sp.points)-1);offset=Vector((float(rng.uniform(-.013,.013))*u,float(rng.uniform(-.009,.009))*u,0,0));p.co+=offset;offsets[f'splines[{si}].points[{j}].co']=offset
            if copy.data.animation_data and copy.data.animation_data.action:
                copy.data.animation_data.action=copy.data.animation_data.action.copy()
                for layer in copy.data.animation_data.action.layers:
                    for strip in layer.strips:
                        for bag in strip.channelbags:
                            for fc in bag.fcurves:
                                if fc.data_path not in offsets:continue
                                delta=offsets[fc.data_path][fc.array_index]
                                for p in fc.keyframe_points:p.co.y+=delta;p.handle_left.y+=delta;p.handle_right.y+=delta
    # Recover material feature contrasts in supporting leather and steel.
    for mat in bpy.data.materials:
        if mat.name.startswith('297 worn rider boots'):
            mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.64
    missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
    (out/'supporting-cast.json').write_text(json.dumps({'horse_materials':[x.name for x in mats],'topology_exact':True,'changed_cloth':changed,'companion_locks':len(groom)*3,'missing_image_paths':missing,'principal_changed':False,'material_restore_reason':'staging had replaced eyes hooves mouth and teeth with one coat shader','visual_status':'NOT_RUN'},indent=2))
    # Carry the source's action records; no old landing/audio record allowed.
    import shutil
    for name in ('impact-events.json','launch-phases.json','dust-ownership.json','coordinated-motion.json','terrain.json','debris.json'):
        shutil.copy2(source/name,out/name)
    from sikh315_scene import dust
    dust(out,json.loads((source/'coordinated-motion.json').read_text()))
    from sikh305_impacts import build_impacts
    events=json.loads((source/'impact-events.json').read_text())['events'];definitions=[]
    for e in events:
        label=e['event'];bone=None if label=='spear' else ('DEF-r_toe.' if 'hind-drive' in label else 'DEF-f_toe.')+('L' if label.endswith('left') else 'R')
        definitions.append((label,e['source_t'],bone,e['power']))
    build_impacts(out,event_definitions=definitions,follow_terrain=True)
