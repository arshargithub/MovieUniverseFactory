"""Pinned, structured live-groom refinement and authorized local ear work."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'edge-package-03/hair-edge.blend'
SOURCE_SHA='736d5b3e15b842ea533ce6af4abea9d9114865ddcf0f0f74ee8f96fa078d53de'
DONOR=ROOT/'.runtime/assets/series01-hair-donor22/bystedt-hair-demo.blend'
DONOR_SHA='1ad6202095c1793678fee7d69a7e9f8b5fdb6e5c293d300eb1062d2d437e8d48'
HEAD='MF_continuous_head_neck'
EAR_KEY='MF_natural147_ear_definition'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def forehead_delta(p,t,candidate=7):
    """Small front-fringe lift, with roots, temples and upper crown pinned."""
    x,y,z=p
    weight=smooth(t/(.22 if candidate>=8 else .12))*smooth((-y-.55)/.22)
    weight*=smooth((z-.48)/.20)*(1-smooth((z-1.06)/.23))
    weight*=1-smooth((abs(x)-.45)/.30)
    return (0.,0.,(.050 if candidate>=8 else .075)*weight)

def output_prefix(candidate):
    return 'natural152' if candidate>=16 else 'natural151' if candidate>=10 else 'natural150' if candidate>=9 else 'natural149' if candidate>=7 else 'natural148' if candidate>=5 else 'natural147'

def trim_temple_tip(row,radii,cutoff):
    """Retain the upper lock exactly; feather and end before the cheek spike."""
    points=[];widths=[]
    for i,p in enumerate(row):
        if p[2]<=cutoff:
            if not points:raise ValueError('Temple root below trim plane')
            a=row[i-1];t=(a[2]-cutoff)/(a[2]-p[2])
            points.append(tuple(a[j]+t*(p[j]-a[j]) for j in range(3)));widths.append(0.)
            break
        points.append(p);widths.append(radii[i]*smooth((p[2]-cutoff)/.16))
    return points,widths

def scalp_position(p):
    """Small front-only rotation along the head arc, not vertical flotation."""
    x,y,z=p
    weight=smooth((-y-.40)/.40)*smooth((z-.48)/.35)
    weight*=1-smooth((z-1.20)/.30)
    weight*=1-smooth((abs(x)-.40)/.45)
    if weight==0:return tuple(p)
    angle=-.065*weight;c=math.cos(angle);s=math.sin(angle)
    return (x,y*c-(z-.30)*s,.30+y*s+(z-.30)*c)

def lift_front_scalp(main,strands,surface):
    """Move guides and growth mesh together; keep UV/parting topology intact."""
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    head=bpy.data.objects[HEAD];mesh=head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    tree=BVHTree.FromPolygons([head.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])
    record={}
    for ob in (main,strands,surface):
        matrix=ob.matrix_world.copy();inverse=matrix.inverted();changed=0;maximum=0.;roots=[]
        if ob.type=='CURVES':
            for curve in ob.data.curves:
                old=matrix@curve.points[0].position;new=Vector(scalp_position(old))
                if (new-old).length>1e-7:
                    near,n,_,_=tree.find_nearest(old);before=(old-near).dot(n)
                    near,n,_,_=tree.find_nearest(new);after=(new-near).dot(n)
                    roots.append({'old':list(old),'new':list(new),'old_signed_distance':before,'new_signed_distance':after})
            points=ob.data.points;field='position'
        else:
            assert not ob.data.shape_keys
            points=ob.data.vertices;field='co'
        for point in points:
            old=matrix@getattr(point,field);new=Vector(scalp_position(old));delta=(new-old).length
            if delta>1e-8:setattr(point,field,inverse@new);changed+=1;maximum=max(maximum,delta)
        if ob.type=='MESH':ob.data.update()
        else:ob.data.update_tag()
        record[ob.name]={'changed_points':changed,'max_world_displacement':maximum,'changed_roots':roots}
    bpy.context.view_layer.update()
    assert record[surface.name]['changed_points']>0 and record[main.name]['changed_roots']
    bpy.context.scene['MF_front_scalp_fit']=json.dumps(record,sort_keys=True)
    return record

def ear_delta(p):
    """Bounded local auricle relief; leave face, scalp, neck and lobe unchanged."""
    x,y,z=p
    if abs(x)<=.65 or not -.12<y<.16 or not -.035<z<.355:return (0.,0.,0.)
    weight=smooth((abs(x)-.65)/.06)*smooth((y+.12)/.045)*(1-smooth((y-.11)/.05))
    weight*=smooth((z+.035)/.07)*(1-smooth((z-.30)/.055))
    concha=-.050*math.exp(-((y+.025)/.044)**2-((z-.125)/.072)**2)
    # Curved antihelix above the concha, branching toward the upper rim.
    ridge_y=.047-.022*math.sin((z-.10)*9)
    ridge=.055*math.exp(-((y-ridge_y)/.027)**2-((z-.205)/.12)**4)
    branch=.027*math.exp(-((y-(.015-.30*(z-.24)))/.025)**2-((z-.27)/.06)**2)
    tragus=.044*math.exp(-((y+.075)/.025)**2-((z-.085)/.035)**2)
    return ((1 if x>0 else -1)*weight*(concha+ridge+branch+tragus),0.,0.)

def protected_state():
    """Full existing protection, excluding only the explicitly allowed new ear key."""
    import bpy
    from illustrated_hair_section import protection
    head=bpy.data.objects[HEAD]
    key=head.data.shape_keys.key_blocks.get(EAR_KEY) if head.data.shape_keys else None
    if key is None:return protection()
    basis=head.data.shape_keys.key_blocks['Basis']
    saved=[tuple(v.co) for v in key.data];value=key.value
    # No new ear-key displacement outside the fixed authorized region.
    for b,k in zip(basis.data,key.data):
        if ear_delta(b.co)==(0.,0.,0.):assert (b.co-k.co).length<1e-8
    head.shape_key_remove(key)
    result=protection()
    key=head.shape_key_add(name=EAR_KEY,from_mix=False)
    for v,p in zip(key.data,saved):v.co=p
    key.value=value
    return result

def define_ears():
    import bpy
    from mathutils import Vector
    head=bpy.data.objects[HEAD]
    assert EAR_KEY not in head.data.shape_keys.key_blocks
    key=head.shape_key_add(name=EAR_KEY,from_mix=False)
    count=0
    for v,b in zip(key.data,head.data.shape_keys.key_blocks['Basis'].data):
        delta=Vector(ear_delta(b.co));v.co=b.co+delta
        count+=delta.length>1e-8
    key.value=1
    return count

def refine_groom(main,strands,material,candidate):
    import bpy
    from mathutils import Vector
    for ob in (main,strands):
        if candidate>=3:
            for mod in ob.modifiers:
                if mod.type=='NODES':
                    for node in mod.node_group.nodes:
                        if node.type=='GROUP' and node.node_tree.name.startswith('Hair Curves Noise'):
                            node.inputs['Distance'].default_value*=.50
        matrix=ob.matrix_world.copy();inverse=matrix.inverted()
        for curve in ob.data.curves:
            root=matrix@curve.points[0].position
            end=matrix@curve.points[-1].position
            for k,p in enumerate(curve.points):
                t=k/max(1,len(curve.points)-1);q=matrix@p.position
                lower=smooth((.35-q.z)/.65)*smooth((t-.25)/.40)
                phase=root.x*3+root.y*2
                q.x+=.055*math.sin(q.z*6+phase)*lower
                q.y+=.070*math.sin(q.z*6+phase+.7)*lower
                if candidate>=2:
                    tip=smooth((t-.68)/.32)*smooth((.1-q.z)/.45)
                    q.x-=math.copysign(.11*tip,q.x)
                    q.z-=.24*tip
                if candidate>=4 and end.z>0 and abs(end.x)>.65:
                    temple=smooth((t-.3)/.6)*math.exp(-((q.z-.28)/.23)**4-((q.y+.11)/.30)**4)
                    q.y+=.11*temple
                    q.z+=.04*temple
                if candidate>=7:q+=Vector(forehead_delta(q,t,candidate))
                p.position=inverse@q
        ob.data.update_tag()
        tree=ob.modifiers['MF live finish'].node_group;n,l=tree.nodes,tree.links
        radius=next(v for v in n if v.bl_idname=='GeometryNodeSetCurveRadius')
        factor=n.new('GeometryNodeSplineParameter')
        taper=n.new('ShaderNodeMapRange');taper.clamp=True
        taper.inputs['From Min'].default_value=.65;taper.inputs['From Max'].default_value=1
        taper.inputs['To Min'].default_value=.0015;taper.inputs['To Max'].default_value=.00012
        l.new(factor.outputs['Factor'],taper.inputs['Value']);l.new(taper.outputs[0],radius.inputs['Radius'])
    ramp=next(n for n in material.node_tree.nodes if n.type=='VALTORGB')
    ramp.color_ramp.elements[0].color=(.009,.0034,.0016,1)
    ramp.color_ramp.elements[1].color=(.055,.023,.011,1)
    p=material.node_tree.nodes.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.85;p.inputs['Specular IOR Level'].default_value=.08

def temple_wisps(material,candidate):
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    head=bpy.data.objects[HEAD];mesh=head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    tree=BVHTree.FromPolygons([head.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])
    rows=[];radii=[];rng=np.random.default_rng(147)
    for side in (-1,1):
        for ci in range(72 if candidate>=14 else 96 if candidate>=10 else 18 if candidate>=5 else 36 if candidate>=3 else 55 if candidate>=2 else 90):
            jitter=float(rng.uniform(-1,1));length=float(rng.uniform(.22,.44));row=[];row_radii=[]
            if candidate>=5:
                length=float(rng.uniform(.09,.23));root_y=float(rng.uniform(-.42,-.24));root_z=float(rng.uniform(.45,.54))
            if candidate>=10:
                # Three loose overlapping locks, rooted under existing swept hair.
                group=ci%3
                root_y=(-.30,-.38,-.44)[group]+float(rng.uniform(-.035,.035))
                root_z=(.59,.66,.72)[group]+float(rng.uniform(-.065,.065))
                length=(.50,.48,.40)[group]+float(rng.uniform(-.09,.09))
                bow=float(rng.uniform(.018,.065));width=float(rng.uniform(.00065,.00125))
                if candidate>=11:
                    length+=.10
                    width*=2.6
                if candidate>=12:
                    root_y=(-.21,-.26,-.31)[group]+float(rng.uniform(-.025,.025))
                    root_z=(.56,.63,.68)[group]+float(rng.uniform(-.045,.045))
                    length=(.72,.73,.70)[group]+float(rng.uniform(-.08,.08))
                    width=float(rng.uniform(.0013,.0025))
                if candidate>=13:
                    # Anterior cheek strip, not projection across the pinna.
                    root_y=(-.39,-.43,-.47)[group]+float(rng.uniform(-.015,.015))
                    root_z=(.55,.61,.67)[group]+float(rng.uniform(-.03,.03))
                    length=(.70,.72,.75)[group]+float(rng.uniform(-.07,.07))
                    width=float(rng.uniform(.0018,.0032))
                if candidate>=14:
                    root_y=(-.40,-.43,-.46)[group]+float(rng.uniform(-.02,.02))
                    length=(.64,.69,.66)[group]+float(rng.uniform(-.09,.09))
                    width=float(rng.uniform(.0008,.0016))
                if candidate>=15:
                    root_y=float(rng.uniform(-.30,-.24))
                    root_z=float(rng.uniform(.80,.90))
                    length=float(rng.uniform(.78,1.02))
                    width=float(rng.uniform(.0006,.0012))
            for k in range(48):
                t=k/47
                if candidate>=2:
                    # Stay anterior to the pinna. A sideward ray preserves a
                    # smooth path; nearest-point projection jumped across rims.
                    y=-.43+.055*t+.022*jitter
                    z=.49-length*t+.025*jitter
                    if candidate>=5:
                        y=root_y+.045*t+.018*math.sin(math.pi*t+jitter)*t
                        z=root_z-length*t
                    if candidate>=10:
                        y=root_y+.07*t+bow*math.sin(math.pi*t)+.010*math.sin(2*math.pi*t+jitter)*t
                        z=root_z-length*t+.015*math.sin(math.pi*t+jitter)*t
                    if candidate>=12:
                        y=root_y+.025*t-.025*math.sin(math.pi*t)+.010*math.sin(2*math.pi*t+jitter)*t
                    if candidate>=13:
                        y=root_y+.04*math.sin(math.pi*t)-.025*t
                    if candidate>=14:
                        y=root_y+.06*math.sin(math.pi*t)-.035*math.sin(2*math.pi*t)-.01*t
                    if candidate>=15:
                        y=root_y-(.15+.025*jitter)*smooth(t)+.025*math.sin(2*math.pi*t)
                    hit,normal,_,_=tree.ray_cast(Vector((side*2,y,z)),Vector((-side,0,0)))
                    if hit is None:raise ValueError('Temple strand misses skin')
                    q=hit+normal*(.005+.008*math.sin(math.pi*t))
                    q.y+=.004*math.sin(t*5+ci)*math.sin(math.pi*t)
                    radius=.00065*(1-t)**.8+.000015
                    if candidate>=5:radius=.00036*(1-t)**1.2+.000008
                    if candidate>=10:
                        q+=normal*(.008*math.sin(math.pi*t))
                        radius=width*(1-t)**1.35+.000008
                    if candidate>=12:radius=width*(1-smooth((t-.4)/.6))+.000008
                    if candidate>=14:radius=width*(1-smooth((t-.12)/.88))+.000008
                else:
                    p=Vector((side*(.745+.015*t),-.32+.12*t+.035*jitter,.50-length*t+.035*jitter))
                    hit,normal,_,_=tree.find_nearest(p)
                    q=hit+normal*(.006+.008*math.sin(math.pi*t))
                    q.y+=.008*math.sin(t*7+ci)*math.sin(math.pi*t)
                    radius=.0012*(1-t)**.7+.00003
                row.append(tuple(q));row_radii.append(radius)
            if candidate>=16:
                row,row_radii=trim_temple_tip(row,row_radii,.26+.07*(ci%7)/6)
            radii.extend(row_radii)
            rows.append(row)
    curves=bpy.data.hair_curves.new('MF_natural147_hair_temples');curves.add_curves([len(row) for row in rows])
    curves.attributes['position'].data.foreach_set('vector',np.concatenate([np.array(row,dtype=np.float32) for row in rows]).ravel())
    radius=curves.attributes.new('radius','FLOAT','POINT');radius.data.foreach_set('value',radii)
    curves.materials.append(material)
    ob=bpy.data.objects.new(curves.name,curves);bpy.context.scene.collection.objects.link(ob)
    return ob

def add_brown_accents(main,strands,material,candidate):
    """Root-localized colour fields follow whole native curves, not image bands."""
    import bpy
    from mathutils import Vector
    for ob in (main,strands):
        tree=ob.modifiers['MF live finish'].node_group;n,l=tree.nodes,tree.links
        gi=next(v for v in n if v.type=='GROUP_INPUT')
        radius=next(v for v in n if v.bl_idname=='GeometryNodeSetCurveRadius')
        sample=n.new('GeometryNodeSampleCurve');sample.data_type='FLOAT_VECTOR';sample.use_all_curves=False
        index=n.new('GeometryNodeInputIndex')
        l.new(gi.outputs['Geometry'],sample.inputs['Curves']);l.new(index.outputs['Index'],sample.inputs['Curve Index'])
        combined=None
        for centre,width in [((-.40,-.66,1.09),.19),((.28,-.77,1.07),.16),((.72,-.24,1.00),.15),((-.36,.65,.96),.16)]:
            distance=n.new('ShaderNodeVectorMath');distance.operation='DISTANCE'
            distance.inputs[1].default_value=ob.matrix_world.inverted()@Vector(centre)
            l.new(sample.outputs['Position'],distance.inputs[0])
            falloff=n.new('ShaderNodeMapRange');falloff.clamp=True;falloff.interpolation_type='SMOOTHERSTEP'
            falloff.inputs['From Min'].default_value=0;falloff.inputs['From Max'].default_value=width
            falloff.inputs['To Min'].default_value=1;falloff.inputs['To Max'].default_value=0
            l.new(distance.outputs['Value'],falloff.inputs['Value'])
            if combined is None:combined=falloff.outputs[0]
            else:
                maximum=n.new('ShaderNodeMath');maximum.operation='MAXIMUM'
                l.new(combined,maximum.inputs[0]);l.new(falloff.outputs[0],maximum.inputs[1]);combined=maximum.outputs[0]
        store=n.new('GeometryNodeStoreNamedAttribute');store.data_type='FLOAT';store.domain='CURVE'
        store.inputs['Name'].default_value='MF_brown_accent'
        l.new(gi.outputs['Geometry'],store.inputs['Geometry']);l.new(combined,store.inputs['Value'])
        l.new(store.outputs['Geometry'],radius.inputs['Curve'])
    n,l=material.node_tree.nodes,material.node_tree.links
    p=n.get('Principled BSDF');ramp=next(v for v in n if v.type=='VALTORGB')
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='MF_brown_accent'
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX'
    mix.inputs[2].default_value=(.17,.076,.031,1)
    if candidate>=6:
        warm=n.new('ShaderNodeValToRGB')
        warm.color_ramp.elements[0].color=(.065,.025,.010,1)
        warm.color_ramp.elements[1].color=(.20,.095,.039,1)
        info=next(v for v in n if v.type=='HAIR_INFO')
        l.new(info.outputs['Random'],warm.inputs['Fac']);l.new(warm.outputs['Color'],mix.inputs[2])
    l.new(attr.outputs['Fac'],mix.inputs[0]);l.new(ramp.outputs['Color'],mix.inputs[1])
    l.new(mix.outputs[0],p.inputs['Base Color']);l.new(mix.outputs[0],p.inputs['Emission Color'])

def accent_state(main):
    import bpy,struct
    from hijab_donor import material_signature
    evaluated=main.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    attr=evaluated.attributes['MF_brown_accent']
    values=[p.value for p in attr.data]
    assert attr.domain=='CURVE' and min(values)>=0 and max(values)<=1
    assert 0<sum(v>.05 for v in values)<len(values)/2
    return {'count':len(values),'accented_over_005':sum(v>.05 for v in values),
            'weights_sha256':hashlib.sha256(b''.join(struct.pack('f',v) for v in values)).hexdigest(),
            'material':material_signature(bpy.data.materials['MF_natural147_hair'])}

def validate(job):
    if (not isinstance(job,dict) or set(job)!={'operation','candidate'}
        or type(job['candidate']) is not int or job['candidate'] not in range(0,17)
        or job['operation'] not in ('audit','accent-audit','attachment-audit','inspect','ear-preview','preview','seal','verify')):
        raise ValueError('Fixed natural-groom job required')
    from hair_uncovered_finish import PINS,ORIGINAL_PINS,REF,ORIGINAL_REF
    for p,h in [(SOURCE,SOURCE_SHA),(DONOR,DONOR_SHA),*[(REF/n,h) for n,h in PINS.items()],*[(ORIGINAL_REF/n,h) for n,h in ORIGINAL_PINS.items()]]:
        if p.is_symlink() or digest(p)!=h:raise ValueError('Pinned input changed')
    prefix=output_prefix(job['candidate'])
    out=BASE/f'{prefix}-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():raise ValueError('Fresh confined output required')
    if shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Disk low')
    if job['operation'] in ('seal','verify'):
        stage='preview' if job['operation']=='seal' else 'seal'
        folder=BASE/f'{prefix}-{stage}-{job["candidate"]:02}'
        if folder.is_symlink() or (folder/'result.json').is_symlink():raise ValueError('Linked prerequisite')
        r=json.loads((folder/'result.json').read_text())
        if not r['protected_exact'] or r['handler_sha256']!=digest(Path(__file__)):raise ValueError('Stale prerequisite')
        if not r['live_control_changed'] or not r['rollback_exact']:raise ValueError('Live control prerequisite')
        if r['dependency_hashes']!=dependency_hashes():raise ValueError('Changed handler dependency')
        if stage=='seal' and ((folder/'natural-hair.blend').is_symlink() or digest(folder/'natural-hair.blend')!=r['native_sha256']):raise ValueError('Native changed')
    return out

def load_groom():
    import bpy
    from mathutils import Matrix
    from hair_anatomy_refinement import is_hair,visibility
    for ob in bpy.context.scene.objects:
        if is_hair(ob):ob.hide_render=True
    existing=set(bpy.data.objects)
    with bpy.data.libraries.load(str(DONOR),link=False) as (a,b):
        b.objects=['long hair main','long hair strands','long hair growth mesh']
    main,strands,surface=b.objects
    imported=set(bpy.data.objects)-existing
    for ob in imported:
        if ob.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(ob)
        ob.hide_render=True;ob.hide_viewport=False;ob.hide_set(False)
    bpy.context.view_layer.update()
    worlds={ob:ob.matrix_world.copy() for ob in imported}
    root=bpy.data.objects.new('MF_natural147_hair_retarget',None);bpy.context.scene.collection.objects.link(root)
    root.matrix_world=Matrix(((1.17,0,0,-5*1.17),(0,1.15,0,.62),(0,0,1.10,1.36-16.400089263916016*1.10),(0,0,0,1)))
    for ob in imported:
        ob.name='MF_natural147_hair_'+ob.name
        ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=worlds[ob]
    bpy.context.view_layer.update()
    material=bpy.data.materials.new('MF_natural147_hair');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.72;p.inputs['Specular IOR Level'].default_value=.13
    info=n.new('ShaderNodeHairInfo');ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.008,.0025,.0012,1);ramp.color_ramp.elements[1].color=(.085,.038,.017,1)
    l.new(info.outputs['Random'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    l.new(ramp.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.12
    for ob in (main,strands):
        tree=bpy.data.node_groups.new('MF_natural147_hair_finish','GeometryNodeTree')
        tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        n,l=tree.nodes,tree.links;gi=n.new('NodeGroupInput');go=n.new('NodeGroupOutput')
        radius=n.new('GeometryNodeSetCurveRadius');radius.inputs['Radius'].default_value=.0016
        mat=n.new('GeometryNodeSetMaterial');mat.inputs['Material'].default_value=material
        l.new(gi.outputs['Geometry'],radius.inputs['Curve']);l.new(radius.outputs['Curve'],mat.inputs['Geometry']);l.new(mat.outputs['Geometry'],go.inputs['Geometry'])
        ob.modifiers.new('MF live finish','NODES').node_group=tree
    visibility()
    for ob in imported:ob.hide_render=ob not in (main,strands)
    return main,strands,surface,material

def dependency_hashes():
    return {p.name:digest(p) for p in Path(__file__).parent.glob('*.py')}

def control_check(main):
    from hair_donor import curve_state
    from mathutils import Vector
    baseline=curve_state(main)
    point=main.data.curves[0].points[4];old=point.position.copy()
    point.position=old+Vector((0,-.08,.04));main.data.update_tag()
    changed=curve_state(main)
    point.position=old;main.data.update_tag();restored=curve_state(main)
    assert baseline!=changed and baseline==restored
    return {'baseline':baseline,'changed':changed,'live_control_changed':True,'rollback_exact':True}

def ear_record():
    import bpy,struct
    from mathutils import Vector
    head=bpy.data.objects[HEAD];keys=head.data.shape_keys.key_blocks
    key=keys[EAR_KEY];h=hashlib.sha256();count=0;maximum=0
    for b,k in zip(keys['Basis'].data,key.data):
        delta=k.co-b.co
        assert (delta-Vector(ear_delta(b.co))).length<1e-6
        count+=delta.length>1e-8;maximum=max(maximum,delta.length)
        h.update(struct.pack('fff',*k.co))
    assert key.value==1
    return {'key':EAR_KEY,'changed_vertices':count,'max_displacement':maximum,'coordinates_sha256':h.hexdigest(),'value':key.value}

def native_state():
    import bpy,struct
    from hair_donor import curve_state
    from neck_anatomy_review import signature
    result={}
    for suffix in ('long hair main','long hair strands','temples'):
        ob=bpy.data.objects['MF_natural147_hair_'+suffix]
        h=hashlib.sha256()
        for p in ob.data.points:h.update(struct.pack('fff',*p.position))
        result[suffix]={'source_positions':h.hexdigest(),'source_curves':len(ob.data.curves),'evaluated':curve_state(ob)}
    result['surface']=signature(bpy.data.objects['MF_natural147_hair_long hair growth mesh'])
    return result

def run(job):
    out=validate(job)
    import bpy
    from illustrated_hair_section import protection
    from hijab_donor import review
    from hair_anatomy_refinement import visibility
    out.mkdir();shutil.copyfile(__file__,out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    protected=protection()
    prefix=output_prefix(job['candidate'])
    if job['operation']=='attachment-audit':
        checkpoint=BASE/'natural149-seal-08/natural-hair.blend'
        assert digest(checkpoint)=='9169f2d3731cd56b29a81dff6c9efe6fc8802d9bb0bfed7de8627f7a4eeeac31'
        bpy.ops.wm.open_mainfile(filepath=str(checkpoint),load_ui=False,use_scripts=False)
        info={}
        for suffix in ('long hair main','long hair strands','long hair growth mesh'):
            ob=bpy.data.objects['MF_natural147_hair_'+suffix]
            data={'type':ob.type,'matrix':[list(row) for row in ob.matrix_world],
                  'attributes':[(a.name,a.data_type,a.domain,len(a.data)) for a in ob.data.attributes],
                  'modifiers':[]}
            if ob.type=='CURVES':data['surface']=ob.data.surface.name if ob.data.surface else None
            if ob.type=='MESH':data['shape_keys']=list(ob.data.shape_keys.key_blocks.keys()) if ob.data.shape_keys else []
            for mod in ob.modifiers:
                item={'name':mod.name,'type':mod.type}
                if mod.type=='NODES':
                    item['nodes']=[{'name':n.name,'group':n.node_tree.name if n.type=='GROUP' else None,
                                    'inputs':[(s.name,str(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]} for n in mod.node_group.nodes]
                data['modifiers'].append(item)
            info[suffix]=data
        (out/'inspection.json').write_text(json.dumps(info,indent=2)+'\n');return
    if job['operation']=='accent-audit':
        checkpoint=BASE/'natural147-seal-04/natural-hair.blend'
        assert digest(checkpoint)=='31835579b66300c562ef0faccfbaef1a0edf6816abb6ddf7eaed47fb9442da67'
        bpy.ops.wm.open_mainfile(filepath=str(checkpoint),load_ui=False,use_scripts=False)
        main=bpy.data.objects['MF_natural147_hair_long hair main']
        evaluated=main.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        graph=bpy.data.node_groups.new('accent-inspection','GeometryNodeTree')
        node=graph.nodes.new('GeometryNodeSampleCurve');node.data_type='FLOAT_VECTOR';node.use_all_curves=False
        info={'attributes':[(a.name,a.data_type,a.domain) for a in evaluated.attributes],
              'roots':[list(main.matrix_world@c.points[0].position) for c in main.data.curves],
              'sample_inputs':[(s.name,s.bl_idname) for s in node.inputs],'sample_outputs':[s.name for s in node.outputs]}
        (out/'inspection.json').write_text(json.dumps(info,indent=2)+'\n')
        bpy.data.objects['MF_natural147_hair_temples'].hide_render=True
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('front-no-wisps',0),('left-no-wisps',-45)))
        return
    if job['operation']=='ear-preview':
        from hair_anatomy_refinement import is_hair
        for ob in bpy.context.scene.objects:
            if is_hair(ob):ob.hide_render=True
        define_ears();head=bpy.data.objects[HEAD];key=head.data.shape_keys.key_blocks[EAR_KEY]
        for side,angle in ((-1,-75),(1,75)):
            review(bpy.context.scene,out,(side*.80,.01,.16),.85,((f'ear-{side}',angle),))
        originals=list(head.data.materials)
        clay=bpy.data.materials.new('ear-relief-clay');clay.use_nodes=True
        clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.3,.3,.3,1)
        clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
        for i in range(len(originals)):head.data.materials[i]=clay
        for side,angle in ((-1,-75),(1,75)):
            review(bpy.context.scene,out,(side*.80,.01,.16),.85,((f'clay-{side}',angle),))
        for i,m in enumerate(originals):head.data.materials[i]=m
        assert protected_state()==protected
        (out/'result.json').write_text(json.dumps(ear_record(),indent=2)+'\n');return
    if job['operation']=='inspect':
        define_ears();head=bpy.data.objects[HEAD];key=head.data.shape_keys.key_blocks[EAR_KEY]
        states=[]
        for value in (0.,1.):
            key.value=value;bpy.context.view_layer.update()
            mesh=head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
            states.append([tuple(v.co) for v in mesh.vertices])
        from mathutils import Vector
        changes=[(Vector(a)-Vector(b)).length for a,b in zip(*states)]
        info={'show_only_shape_key':head.show_only_shape_key,'use_relative':head.data.shape_keys.use_relative,'active_shape_key_index':head.active_shape_key_index,'all_keys':[(k.name,k.value,k.mute,k.relative_key.name,k.vertex_group) for k in head.data.shape_keys.key_blocks],'max_evaluated_delta':max(changes),'changed':sum(d>1e-7 for d in changes),'ear_record':ear_record()}
        (out/'inspection.json').write_text(json.dumps(info,indent=2)+'\n');return
    if job['operation']=='audit':
        visibility(hair=False)
        head=bpy.data.objects[HEAD]
        vertices=[{'index':v.index,'p':list(head.matrix_world@v.co),'n':list(v.normal)} for v in head.data.vertices if abs((head.matrix_world@v.co).x)>.65 and -.4<(head.matrix_world@v.co).z<.7]
        (out/'head-audit.json').write_text(json.dumps({'vertices':vertices,'matrix':[list(r) for r in head.matrix_world],'modifiers':[(m.name,m.type) for m in head.modifiers],'shape_keys':list(head.data.shape_keys.key_blocks.keys()) if head.data.shape_keys else [],'attributes':[(a.name,a.data_type,a.domain) for a in head.data.attributes]},indent=2)+'\n')
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('bare-front',0),('bare-left',-75),('bare-right',75)))
        originals=list(head.data.materials)
        clay=bpy.data.materials.new('ear-clay');clay.diffuse_color=(.45,.45,.45,1)
        for i in range(len(head.data.materials)):head.data.materials[i]=clay
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('clay-left',-75),('clay-right',75)))
        for i,m in enumerate(originals):head.data.materials[i]=m
        assert protection()==protected
        return
    if job['operation']=='verify':
        seal=BASE/f'{prefix}-seal-{job["candidate"]:02}'
        prior=json.loads((seal/'result.json').read_text())
        bpy.ops.wm.open_mainfile(filepath=str(seal/'natural-hair.blend'),load_ui=False,use_scripts=False)
        main=bpy.data.objects['MF_natural147_hair_long hair main']
        strands=bpy.data.objects['MF_natural147_hair_long hair strands']
    else:
        main,strands,surface,material=load_groom()
        if job['candidate']>=1:
            refine_groom(main,strands,material,job['candidate'])
            define_ears()
            if job['candidate']>=9:lift_front_scalp(main,strands,surface)
            bpy.context.view_layer.update()
            temple_wisps(material,job['candidate'])
            if job['candidate']>=5:add_brown_accents(main,strands,material,job['candidate'])
    assert protected_state()==protected
    control=control_check(main)
    ears=ear_record() if job['candidate']>=1 else None
    state=native_state() if job['candidate']>=1 else None
    accents=accent_state(main) if job['candidate']>=5 else None
    if job['operation']=='verify':
        assert control['baseline']==prior['baseline'] and ears==prior['ears'] and state==prior['native_state']
        assert accents==prior.get('accents')
    views=(('front',0),) if job['operation'] in ('seal','verify') else (('front',0),('left',-45),('right',45),('back',180))
    review(bpy.context.scene,out,(0,0,-.03),3.8,views)
    if 1<=job['candidate']<7 and job['operation']=='preview':
        from hair_anatomy_refinement import is_hair
        saved={ob:ob.hide_render for ob in bpy.context.scene.objects}
        for ob in bpy.context.scene.objects:
            if is_hair(ob):ob.hide_render=True
        review(bpy.context.scene,out,(.80,.01,.16),.85,(('ear-right',75),))
        review(bpy.context.scene,out,(-.80,.01,.16),.85,(('ear-left',-75),))
        key=bpy.data.objects[HEAD].data.shape_keys.key_blocks[EAR_KEY];key.value=0
        review(bpy.context.scene,out,(-.80,.01,.16),.85,(('ear-left-before',-75),))
        key.value=1
        for ob,value in saved.items():ob.hide_render=value
    result={'protected_exact':protected_state()==protected,'protected_digest':protected,'handler_sha256':digest(out/'handler-source.py'),'dependency_hashes':dependency_hashes(),'source_sha256':SOURCE_SHA,'donor_sha256':DONOR_SHA,'candidate':job['candidate'],'ears':ears,'native_state':state,'guide_counts':[len(main.data.curves),len(strands.data.curves)],'director_acceptance':'PENDING','scalp_animation_binding':'NOT_VALIDATED',**control}
    result['accents']=accents
    if job['candidate']>=9:
        result['front_scalp_fit']=json.loads(bpy.context.scene['MF_front_scalp_fit'])
        if job['operation']=='verify':assert result['front_scalp_fit']==prior['front_scalp_fit']
    if job['operation']=='seal':
        preview=json.loads((BASE/f'{prefix}-preview-{job["candidate"]:02}'/'result.json').read_text())
        assert preview['baseline']==result['baseline'] and preview['ears']==result['ears'] and preview['native_state']==state
        bpy.context.scene['MF_natural147_status']='STATIC_CREATIVE_REVIEW_PENDING'
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'natural-hair.blend'),compress=True)
        result['native_sha256']=digest(out/'natural-hair.blend')
    result['render_hashes']={p.name:digest(p) for p in out.glob('*.png')}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One data-only job required')
    run(json.loads(Path(args[0]).read_text()))
