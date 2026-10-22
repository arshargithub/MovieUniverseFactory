"""Pinned native hair-curves authoring study, no arbitrary job code."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'edge-package-03/hair-edge.blend'
SOURCE_SHA='736d5b3e15b842ea533ce6af4abea9d9114865ddcf0f0f74ee8f96fa078d53de'
LIB=Path('/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/procedural_hair_node_assets.blend')
LIB_SHA='b69d8bd8975b9db7f89693f8f19dd7fcb241f5a3786d2edfb0a243e91c1109bb'
BRUSH_LIB=ROOT/'.runtime/brushstroke-tools-1.2.3-inspection/assets/core/brushstroke_tools-resources.blend'
BRUSH_SHA='11db84523ea8578b4aea112f227b7d1019c7d939d551c13701e3322a7b0bd95d'
REFBASE=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES={'frontal-v02-individualized.png':'7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75','portrait-v07-individualized.png':'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1'}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact structured keys required')
    if type(job['candidate']) is not int or (job['operation'],job['candidate']) not in (('inspect',0),('preview',1),('preview',2),('preview',3),('field',2),('field',3),('field-retry',2),('clumps',1),('clumps',2),('clumps',3),('checkpoint',2),('verify',2),('brush-inspect',0),('brush-inspect',1),('brush-inspect',2),('brush-inspect',3),('brush-preview',1),('brush-preview',2),('brush-preview',3),('brush-retry',3),('brush-locks',1),('brush-locks',2),('brush-locks',3)):
        raise ValueError('Unsupported fixed operation')
    if job['operation'].startswith('brush') and (BRUSH_LIB.is_symlink() or digest(BRUSH_LIB)!=BRUSH_SHA):
        raise ValueError('Pinned brush resource changed')
    for p,h in [(SOURCE,SOURCE_SHA),(LIB,LIB_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p)!=h: raise ValueError('Pinned input changed')
    out=BASE/f'native-groom-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():
        raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free<5_000_000_000: raise ValueError('Disk low')
    return out

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def guide_points(side,f,root,candidate=1):
    """Continuous roots-to-temple fall; reference-led shape, not image strips."""
    lift=.12+.035*math.sin(f*8+.4*side)
    points=[root,
        (side*.19,-1.00+1.03*f,root[2]+lift),
        (side*.43,-.93+1.09*f,1.075+.37*math.sin(f*math.pi*.78)),
        (side*.72,-.70+1.11*f,.82+.36*math.sin(f*math.pi*.70)),
        (side*(.96+.045*math.sin(f*8+side)),-.28+.95*f,.44+.18*f),
        (side*(1.015+.025*math.cos(f*9)),.12+.77*f,.015+.10*f),
        (side*(.98+.035*math.sin(f*13+side)),.34+.64*f,-.50-.12*f),
        (side*(.92+.050*math.cos(f*9+side)),.48+.53*f,-1.12-.10*f)]
    if candidate>=2:
        # The reference's lowest sweep descends from the part across the outer
        # brow and temple. The first groom arched above it, exposing its base.
        fall=(1-smooth(f/.8))
        dz=(0,-.065,-.23,-.29,-.23,-.10,0,0)
        for i in range(1,len(points)):
            x,y,z=points[i]
            points[i]=(x,y,z+dz[i]*fall)
        points[-2]=(side*(.88+.025*math.sin(f*13+side)),.30+.64*f,-.30-.20*f)
        points[-1]=(side*(.84+.035*math.cos(f*9+side)),.42+.53*f,-.64-.18*f)
    if candidate>=4:
        # Lifted, individually swept clumps must not all end at the same bob
        # line. Return them into the retained rear masses with unequal waves.
        points[-2]=(side*(.87+.07*math.sin(f*13+side)),.22+.58*f,-.28-.13*f)
        points[-1]=(side*(.88+.08*math.cos(f*17+side)),.38+.44*f,-.96-.25*(.5+.5*math.sin(f*11+side)))
    return points

def tint(f,t,side,candidate=1):
    # Hierarchical highlights span neighboring guides; fine variation is
    # subordinate. No portrait projection, no skin/scarf pixels on geometry.
    band=(.5+.5*math.sin(f*math.tau*6+.45*side))**5
    stroke=smooth((t-.06)/.16)*(1-smooth((t-.54-.12*math.sin(f*9))/.16))
    value=.025+.11*band*stroke+.012*math.sin(f*191+side)**2
    if candidate>=2:
        value=.004+.065*band*stroke+.003*math.sin(f*191+side)**2
    if candidate>=5:
        # Broad, grouped tonal strokes rather than equally legible fine fibres.
        band=(.5+.5*math.sin(f*math.tau*6+.45*side))**3
        value=.005+.12*band*stroke
    return (value,value*.43,value*.19,1)

def field_groom(skull,tree,candidate):
    """Two-dimensional scalp-root coverage for native interpolation."""
    import bpy
    from mathutils import Vector
    from hair_volume_sculpt import spline
    def path(side,f):
        y=-.953+1.19*f;x=side*(.019+.006*math.sin(f*32+side))
        hit,n,_,_=tree.ray_cast(Vector((x,y,3)),Vector((0,0,-1)))
        if hit is None:raise ValueError('Scalp part root missing')
        return guide_points(side,f,tuple(hit+n*.006),candidate)
    def root_at(points,t):
        co=Vector(spline(points,t));origin=Vector((0,0,.3))
        if candidate>=4 and abs(co.x)<.87 and co.y<0 and co.z>.18:
            hit,n,_,_=skull.ray_cast(Vector((co.x,-3,co.z)),Vector((0,1,0)))
            # Extreme crown points can lie above the projected silhouette.
            # Fall back to the same ear-excluding radial scalp attachment.
            if hit is None:hit,n,_,_=skull.ray_cast(origin,(co-origin).normalized())
        else:hit,n,_,_=skull.ray_cast(origin,(co-origin).normalized())
        if hit is None:raise ValueError('Field root projection failed')
        return hit+n*.006,n
    verts,faces,uvs=[],[],[];nf,nt=40,18
    for si,side in enumerate((-1,1)):
        for i in range(nf+1):
            f=i/nf;pts=path(side,f)
            for j in range(nt+1):
                t=.57*j/nt;co,_=root_at(pts,t)
                verts.append(tuple(co));uvs.append(((si+f*.94)/2+.015,.02+.96*j/nt))
        offset=si*(nf+1)*(nt+1)
        for i in range(nf):
            for j in range(nt):
                a=offset+i*(nt+1)+j
                face=(a,a+1,a+nt+2,a+nt+1)
                faces.append(face if side==-1 else tuple(reversed(face)))
    mesh=bpy.data.meshes.new('MF_groom_scalp_field');mesh.from_pydata(verts,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='GroomSurfaceUV')
    for li,loop in enumerate(mesh.loops):uv.data[li].uv=uvs[loop.vertex_index]
    surface=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(surface)
    surface.hide_render=True
    # Hidden emitter geometry is still available through the curves' attachment.
    hair=bpy.data.hair_curves.new('MF_native_groom_field_guides');steps=72;nfguide=32;ntguide=7
    hair.add_curves([steps+1]*(2*nfguide*ntguide));hair.surface=surface;hair.surface_uv_map=uv.name
    radius=hair.attributes.new('radius','FLOAT','POINT');color=hair.attributes.new('MF_groom_color','FLOAT_COLOR','POINT')
    attachment=hair.attributes.new('surface_uv_coordinate','FLOAT2','CURVE')
    index=0;corrections=0
    for si,side in enumerate((-1,1)):
        for i in range(nfguide):
            f=i/(nfguide-1);pts=path(side,f)
            for j in range(ntguide):
                t0=.57*j/(ntguide-1);root,n=root_at(pts,t0)
                attachment.data[index].vector=((si+f*.94)/2+.015,.02+.96*j/(ntguide-1))
                offset=root-Vector(spline(pts,t0))
                for k in range(steps+1):
                    u=k/steps;t=t0+(1-t0)*u;co=Vector(spline(pts,t))
                    co+=offset*(1-smooth(u/.23))
                    co.z+=.025*math.sin(f*math.tau*5+side)*math.sin(math.pi*u)
                    if candidate>=4:
                        co.x+=side*.045*math.sin(t*11+f*8)*smooth(u/.20)*math.sin(math.pi*t)
                        co.y+=.035*math.sin(t*12+f*10+side)*smooth(u/.20)*math.sin(math.pi*t)
                    if co.z>.18 and k:
                        near,normal,_,_=skull.find_nearest(co)
                        if (co-near).dot(normal)<.013:co=near+normal*.013;corrections+=1
                    pi=index*(steps+1)+k
                    hair.attributes['position'].data[pi].vector=co
                    radius.data[pi].value=(.004 if candidate>=5 else .0026)*(1-smooth((u-.70)/.30))+.00010
                    color.data[pi].color=tint(f,t,side,candidate)
                index+=1
    return hair,corrections

def authored_clumps(skull,variant):
    """Explicit reference-traced volumes, not one global parameterized sweep.

    The old section experiment supplies only traced guides/widths. No sampled
    illustration texture, section mesh or donor groom is used here.
    """
    import bpy
    from mathutils import Vector
    from hair_integrated_front import SECTIONS,sample
    count,steps=180,80
    hair=bpy.data.hair_curves.new('MF_native_authored_clumps')
    hair.add_curves([steps+1]*(len(SECTIONS)*count))
    radius=hair.attributes.new('radius','FLOAT','POINT')
    color=hair.attributes.new('MF_groom_color','FLOAT_COLOR','POINT')
    for idx,(points,widths,lift) in enumerate(SECTIONS):
        for j in range(count):
            w=-1+2*(j+.5)/count
            depth=math.sin(j*2.39996323)*.015
            for k in range(steps+1):
                t=k/steps
                px,py,y=sample(points,t)
                a,b=sample(points,max(0,t-.001)),sample(points,min(1,t+.001))
                dx,dy=b[0]-a[0],b[1]-a[1];norm=math.hypot(dx,dy)
                width=max(0,sample([(q,) for q in widths],t)[0])
                px+=-dy/norm*width*w;py+=dx/norm*width*w
                x=(px-488)/227.29;z=(532-py)/257+.105
                if variant>=3:
                    # Close the mechanical ladder-like part. Roots meet at
                    # the centre and diverge smoothly, not in paired teeth.
                    side=-1 if idx<7 else 1
                    x-=((points[0][0]-488)/227.29-side*.002)*(1-smooth(t/.22))
                # Wrap the traced tips around the head, retaining their front
                # stroke rather than ending all of them as a bob at the neck.
                if abs(x)>.82:x=math.copysign(.82+.22*math.tanh((abs(x)-.82)/.22),x)
                hit,n,_,_=skull.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
                bulge=(.04+.035*(idx%7<4))*math.sin(math.pi*t)**.6*(1-w*w)
                if hit is not None:y=hit.y-.007-bulge+depth*math.sin(math.pi*t)
                else:
                    origin=Vector((0,0,.3));co=Vector((x,y,z))
                    hit,n,_,_=skull.ray_cast(origin,(co-origin).normalized())
                    if hit is not None:
                        co=hit+n*(.008+bulge);x,y,z=co
                if variant>=3:
                    co=Vector((x,y,z));near,n,_,_=skull.find_nearest(co)
                    if (co-near).dot(n)<.009:co=near+n*.009
                    x,y,z=co
                if t>.82:
                    y+=.22*smooth((t-.82)/.18);x*=1-.035*smooth((t-.82)/.18)
                pi=(idx*count+j)*(steps+1)+k
                hair.attributes['position'].data[pi].vector=(x,y,z)
                radius.data[pi].value=.0028*(.25+.75*math.sin(math.pi*t)**.3)*(1-smooth((t-.88)/.12))+.00006
                stripe=(.5+.5*math.sin(w*12+idx))**8
                broad=max(0,1-(w+.2)**2)**3
                value=.004+(.035*broad+.06*stripe)*smooth(t/.12)*(1-smooth((t-.72)/.25))
                if variant>=3:
                    value=.004+(.019*broad+.047*stripe)*smooth(t/.08)*(1-smooth((t-.64-.06*math.sin(idx*4))/.30))
                color.data[pi].color=(value,value*.48,value*.23,1)
    ob=bpy.data.objects.new('MF_native_authored_clumps',hair);bpy.context.scene.collection.objects.link(ob)
    mat=bpy.data.materials['MF_native_groom_illustrated'].copy();mat.name='MF_authored_clump_illustrated';hair.materials.append(mat)
    return {'authored_clump_count':len(SECTIONS),'authored_clump_curves':len(hair.curves),'authoring_dependencies':['reference-traced SECTIONS guides only; no section meshes or projected pixels']}

def build(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from hair_volume_sculpt import spline,skull_surface
    body=bpy.data.objects['MF_continuous_head_neck']
    tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    skull=skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    base=bpy.data.objects['MF_sculpt_hair_support']
    # Make a scalp-hugging foundation instead of keeping a second hairstyle.
    for v in base.data.vertices:
        weight=1-smooth((v.co.y-.03)/.45)
        if weight:
            origin=Vector((0,0,.3));hit,normal,_,_=skull.ray_cast(origin,(v.co-origin).normalized())
            if hit is not None: v.co=v.co.lerp(hit+normal*.003,weight)
    base.data.update()
    for i,src in enumerate(list(base.data.materials)):
        m=src.copy();base.data.materials[i]=m;n,l=m.node_tree.nodes,m.node_tree.links
        output=next(x for x in n if x.type=='OUTPUT_MATERIAL'); old=output.inputs['Surface'].links[0].from_socket
        p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.009,.003,.0014,1);p.inputs['Roughness'].default_value=.9
        if candidate>=4:p.inputs['Specular IOR Level'].default_value=.02
        a=n.new('ShaderNodeAttribute');a.attribute_name='MF_front_edge_opacity';l.new(a.outputs['Fac'],p.inputs['Alpha'])
        geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0])
        fade=n.new('ShaderNodeMapRange');fade.clamp=True;fade.inputs['From Min'].default_value=.05;fade.inputs['From Max'].default_value=.50;l.new(sep.outputs['Y'],fade.inputs['Value'])
        mix=n.new('ShaderNodeMixShader');l.new(fade.outputs['Result'],mix.inputs[0]);l.new(p.outputs[0],mix.inputs[1]);l.new(old,mix.inputs[2]);l.new(mix.outputs[0],output.inputs['Surface'])
        if candidate>=5:
            # Isolate the exposed foundation from actual groom coverage. Rear
            # source support remains unchanged; no face material is touched.
            transparent=n.new('ShaderNodeBsdfTransparent')
            l.new(transparent.outputs[0],mix.inputs[1])
    for o in bpy.context.scene.objects:
        if o.name.startswith(('MF_hair_edge_wisp_','MF_hair_front_edge_')) or o.name in [f'MF_illustrated_hair_lock_{i}' for i in range(220,226)]:o.hide_render=True
    hair=bpy.data.hair_curves.new('MF_native_groom_guides')
    count,steps=80,72
    hair.add_curves([steps+1]*(count*2))
    radius=hair.attributes.new('radius','FLOAT','POINT')
    color=hair.attributes.new('MF_groom_color','FLOAT_COLOR','POINT')
    minimum=1.; collisions=0
    for s,side in enumerate((-1,1)):
        for k in range(count):
            f=k/(count-1); y=-.953+1.19*f; x=side*((.019 if candidate>=2 else .043)+.006*math.sin(f*32+side))
            hit,normal,_,_=tree.ray_cast(Vector((x,y,3)),Vector((0,0,-1)))
            if hit is None:raise ValueError('Native groom root missing')
            root=tuple(hit+normal*.009); pts=guide_points(side,f,root,candidate)
            for j in range(steps+1):
                t=j/steps;co=Vector(spline(pts,t))
                # Gentle coherent clump separation; the shape comes from
                # complete guides, not arbitrary per-vertex surface relief.
                co.z+=.020*math.sin(f*math.tau*6+side)*math.sin(math.pi*t)
                if j and co.z>.22:
                    nearest,n,_,_=skull.find_nearest(co)
                    clearance=(co-nearest).dot(n)
                    if clearance<.018:
                        co=nearest+n*.018;collisions+=1
                    minimum=min(minimum,max(clearance,.018))
                idx=(s*count+k)*(steps+1)+j
                hair.attributes['position'].data[idx].vector=co
                radius.data[idx].value=.0023*(1-smooth((t-.70)/.30))+.00012
                color.data[idx].color=tint(f,t,side,candidate)
    if candidate>=3:
        # Discard only this new unused datablock, never a source scene object.
        bpy.data.hair_curves.remove(hair)
        hair,collisions=field_groom(skull,tree,candidate)
    ob=bpy.data.objects.new('MF_native_hair_groom',hair);bpy.context.scene.collection.objects.link(ob)
    m=bpy.data.materials.new('MF_native_groom_illustrated');m.use_nodes=True;n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
    a=n.new('ShaderNodeAttribute');a.attribute_name='MF_groom_color';l.new(a.outputs['Color'],p.inputs['Base Color']);l.new(a.outputs['Color'],p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value=.35;p.inputs['Roughness'].default_value=.74;p.inputs['Specular IOR Level'].default_value=.15
    if candidate>=5:
        p.inputs['Emission Strength'].default_value=.75
        p.inputs['Specular IOR Level'].default_value=0
    hair.materials.append(m)
    with bpy.data.libraries.load(str(LIB),link=False) as (src,dst):
        dst.node_groups=['Interpolate Hair Curves' if candidate>=3 else 'Duplicate Hair Curves','Clump Hair Curves']
    graph=bpy.data.node_groups.new('MF_native_groom_pipeline','GeometryNodeTree')
    graph.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    graph.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n,l=graph.nodes,graph.links;gi=n.new('NodeGroupInput');go=n.new('NodeGroupOutput')
    dup=n.new('GeometryNodeGroup');dup.node_tree=dst.node_groups[0]
    if candidate>=3:
        dup.inputs['Density'].default_value=1500
        dup.inputs['Interpolation Guides'].default_value=3
        dup.inputs['Part by Mesh Islands'].default_value=True
    else:
        dup.inputs['Amount'].default_value=28;dup.inputs['Radius'].default_value=.026
        dup.inputs['Even Thickness'].default_value=True
        if candidate>=2:dup.inputs['Radius'].default_value=.017
    dup.inputs['Seed'].default_value=614
    clump=n.new('GeometryNodeGroup');clump.node_tree=dst.node_groups[1]
    clump.inputs['Factor'].default_value=.30;clump.inputs['Shape'].default_value=.7;clump.inputs['Guide Distance'].default_value=.13
    clump.inputs['Existing Guide Map'].default_value=False;clump.inputs['Tip Spread'].default_value=.012
    if candidate>=2:
        clump.inputs['Factor'].default_value=.55
        clump.inputs['Guide Distance'].default_value=.16
    if candidate>=3:
        clump.inputs['Factor'].default_value=.16
        clump.inputs['Guide Distance'].default_value=.22
    if candidate>=4:
        dup.inputs['Density'].default_value=2400
        clump.inputs['Factor'].default_value=.22
        p.inputs['Specular IOR Level'].default_value=.06
    if candidate>=5:
        clump.inputs['Factor'].default_value=.32
        p.inputs['Specular IOR Level'].default_value=0
    l.new(gi.outputs[0],dup.inputs['Geometry']);l.new(dup.outputs['Geometry'],clump.inputs['Geometry'])
    # Attach a native material after evaluation; retain named color attributes.
    matnode=n.new('GeometryNodeSetMaterial');matnode.inputs['Material'].default_value=m
    l.new(clump.outputs['Geometry'],matnode.inputs['Geometry']);l.new(matnode.outputs[0],go.inputs[0])
    mod=ob.modifiers.new('Native duplicate and clump','NODES');mod.node_group=graph
    bpy.context.view_layer.update()
    evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return {'editable_guides':len(hair.curves),'guide_points':len(hair.points),'evaluated_curve_count':len(evaluated.data.curves),'native_node_assets':[q.name for q in dst.node_groups],'corrected_guide_collisions':collisions,'library_sha256':LIB_SHA,'front_painted_overlay_removed':True,'new_asset_downloads':0,'manual_asset_edits':0}

def preview(job,out):
    import bpy
    from illustrated_hair_section import protection
    from hair_front_fit import rear_signature
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before,rear=protection(),rear_signature()
    effective=job['candidate']+2 if job['operation'].startswith('field') else job['candidate']
    if job['operation']=='clumps':effective=5
    result=build(effective)
    if job['operation']=='clumps':
        # Field is only an undercoat; independent clumps now carry the visible
        # reference structure. This tests a different guide organization.
        m=bpy.data.materials['MF_native_groom_illustrated']
        p=m.node_tree.nodes.get('Principled BSDF')
        for key in ('Base Color','Emission Color'):
            for link in list(p.inputs[key].links):m.node_tree.links.remove(link)
            p.inputs[key].default_value=(.004,.0015,.0008,1)
        from hair_volume_sculpt import skull_surface
        skull=skull_surface(bpy.data.objects['MF_reference_crown_hair'])
        if job['candidate']>=2:
            from mathutils import Vector
            under=bpy.data.objects['MF_native_hair_groom'].data
            for value in under.attributes['position'].data:
                co=value.vector.copy()
                if co.z>.12:
                    origin=Vector((0,0,.3));hit,n,_,_=skull.ray_cast(origin,(co-origin).normalized())
                    if hit is not None:
                        weight=smooth((co.z-.12)/.38) if job['candidate']>=3 else 1
                        value.vector=co.lerp(hit+n*.004,weight)
        result.update(authored_clumps(skull,job['candidate']))
        # Restore named color on the clumps only, leaving the undercoat quiet.
        c=bpy.data.materials['MF_authored_clump_illustrated'];cp=c.node_tree.nodes.get('Principled BSDF');a=next(n for n in c.node_tree.nodes if n.type=='ATTRIBUTE')
        for key in ('Base Color','Emission Color'):c.node_tree.links.new(a.outputs['Color'],cp.inputs[key])
    visibility()
    assert protection()==before and rear_signature()==rear
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result.update({'candidate':job['candidate'],'effective_variant':effective,'hypothesis':'SCALP_FIELD' if effective>=3 else 'PART_DUPLICATION','protected_exact':protection()==before,'rear_mesh_exact':rear_signature()==rear,'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),'reference_authority':REFERENCES,'review_ready':False,'director_acceptance':'NOT_REQUESTED'})
    if job['operation']=='clumps':result['hypothesis']='EXPLICIT_CLUMP_VOLUME_OVER_NATIVE_UNDERCOAT'
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')

def inspect(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    with bpy.data.libraries.load(str(LIB),link=False) as (src,dst):
        names=list(src.node_groups)
        dst.node_groups=[n for n in names if n in ('Duplicate Hair Curves','Interpolate Hair Curves','Clump Hair Curves','Set Hair Curve Profile')]
    interface={n.name:[{'name':s.name,'identifier':s.identifier,'type':s.socket_type,'in_out':s.in_out,'default':str(getattr(s,'default_value',None))} for s in n.interface.items_tree if s.item_type=='SOCKET'] for n in dst.node_groups if n}
    hair=bpy.data.hair_curves.new('MF_groom_probe')
    hair.add_curves([4,4])
    probe={'type':hair.bl_rna.identifier,'point_count':len(hair.points),'curve_count':len(hair.curves),'attributes':[(a.name,a.data_type,a.domain) for a in hair.attributes]}
    body=bpy.data.objects['MF_continuous_head_neck']; tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    part=[]
    for y in (-.94,-.86,-.78,-.68,-.55,-.4,-.2,0,.2,.4,.6):
        hit,normal,_,_=tree.ray_cast(Vector((.025,y,3)),Vector((0,0,-1)))
        part.append({'y':y,'hit':tuple(hit) if hit else None,'normal':tuple(normal) if normal else None})
    report={'node_assets':names,'interfaces':interface,'native_curves_probe':probe,'part_surface':part,'source_sha256':SOURCE_SHA,'library_sha256':digest(LIB)}
    (out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')

def curves_state():
    import bpy
    o=bpy.data.objects['MF_native_hair_groom'];data=o.data
    def points_hash(data):
        h=hashlib.sha256()
        for value in data.attributes['position'].data:
            h.update(struct.pack('<3f',*value.vector))
        return h.hexdigest()
    h=hashlib.sha256()
    for name,field in [('radius','value'),('MF_groom_color','color'),('surface_uv_coordinate','vector')]:
        for value in data.attributes[name].data:
            v=getattr(value,field);v=(v,) if isinstance(v,float) else tuple(v)
            h.update(struct.pack('<'+'f'*len(v),*v))
    bpy.context.view_layer.update()
    evaluated=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    return {'guides':len(data.curves),'points':len(data.points),'positions':points_hash(data),'attributes':h.hexdigest(),
            'surface':data.surface.name,'uv':data.surface_uv_map,'evaluated_curves':len(evaluated.curves),
            'evaluated_positions':points_hash(evaluated),'modifier_groups':[m.node_group.name for m in o.modifiers if m.type=='NODES']}

def checkpoint(out):
    """Research checkpoint only. This never promotes a visually failed groom."""
    import bpy
    from illustrated_hair_section import protection
    from hair_front_fit import rear_signature
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    protected,rear=protection(),rear_signature()
    info=build(4);visibility()
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('baseline',0),))
    assert protection()==protected and rear_signature()==rear
    state=curves_state()
    bpy.context.scene['asset_disposition']='DIAGNOSTIC_NOT_APPROVED; pair-B fidelity failed; not release canon'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic-groom.blend'))
    info.update({'protected':protected,'rear':rear,'curves':state,'disposition':'DIAGNOSTIC_NOT_APPROVED','source_sha256':SOURCE_SHA,
                 'native_sha256':digest(out/'diagnostic-groom.blend'),'handler_sha256':digest(Path(__file__)),
                 'reference_authority':REFERENCES,'visual_readiness':False,'director_acceptance':'NOT_REQUESTED'})
    (out/'checkpoint.json').write_text(json.dumps(info,indent=2)+'\n')

def inspect_brush(out):
    import bpy
    p=BRUSH_LIB
    with bpy.data.libraries.load(str(p),link=False) as (src,dst):
        groups=list(src.node_groups);materials=list(src.materials)
        dst.node_groups=[n for n in groups if n in ('.brushstroke_tools.surface_draw','.brushstroke_tools.pre_processing')]
        dst.materials=list(materials)
    report={'groups':groups,'materials':materials,'interfaces':{n.name:[{'name':s.name,'id':s.identifier,'type':s.socket_type,'in_out':s.in_out,'default':str(getattr(s,'default_value',None))} for s in n.interface.items_tree if s.item_type=='SOCKET'] for n in dst.node_groups},
            'material_nodes':{m.name:[{'name':n.name,'type':n.type,'group':n.node_tree.name if n.type=='GROUP' else None,'inputs':[(s.name,str(getattr(s,'default_value',None))) for s in n.inputs]} for n in m.node_tree.nodes] for m in dst.materials},
            'scripts_executed':False,'addon_installed':False,'resource_sha256':digest(p)}
    report['material_controls']={m.name:[{'name':n.name,'attribute':getattr(n,'attribute_name',None),'operation':getattr(n,'operation',None),'inputs':[(s.name,str(getattr(s,'default_value',None)),[(l.from_node.name,l.from_socket.name) for l in s.links]) for s in n.inputs]} for n in m.node_tree.nodes if n.name in ('Backface Culling','Mix Shader.002','Use Strength','Opacity','Brush Color','Brush Style') or n.type=='OUTPUT_MATERIAL'] for m in dst.materials}
    report['geometry_contract']={g.name:[{'name':n.name,'type':n.bl_idname,'group':n.node_tree.name if n.type=='GROUP' else None,'inputs':[(s.name,str(getattr(s,'default_value',None)),[(l.from_node.name,l.from_socket.name) for l in s.links]) for s in n.inputs]} for n in g.nodes] for g in bpy.data.node_groups if g.bl_idname=='GeometryNodeTree'}
    (out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')

def dominant_locks(variant):
    """Explicit broad strokes; only roots attach, depth remains authored."""
    import bpy
    from mathutils import Vector
    from hair_integrated_front import SECTIONS,sample
    from hair_volume_sculpt import skull_surface
    skull=skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    ob=bpy.data.objects['MF_native_hair_groom'];old=ob.data
    hair=bpy.data.hair_curves.new('MF_dominant_painterly_locks')
    steps=80;per=9 if variant>=2 else 5
    hair.add_curves([steps+1]*(len(SECTIONS)*per))
    radius=hair.attributes.new('radius','FLOAT','POINT')
    color=hair.attributes.new('MF_groom_color','FLOAT_COLOR','POINT')
    body=bpy.data.objects['MF_continuous_head_neck'];hair.surface=body
    hair.surface_uv_map=body.data.uv_layers.active.name
    for index,(points,widths,lift) in enumerate(SECTIONS):
        root=Vector(((points[0][0]-488)/227.29,points[0][2],(532-points[0][1])/257+.105))
        hit,n,_,_=skull.find_nearest(root);root_delta=hit+n*.008-root
        for j in range(per):
            accent=j>=5
            w=(j-2)/2 if not accent else (-.65,-.2,.3,.7)[j-5]
            for k in range(steps+1):
                u=k/steps
                t=(.12+.03*((index+j)%3))+u*(.66-.025*(index%3)) if accent else u
                px,py,y=sample(points,t)
                a,b=sample(points,max(0,t-.001)),sample(points,min(1,t+.001))
                dx,dy=b[0]-a[0],b[1]-a[1];norm=math.hypot(dx,dy)
                width=max(.1,sample([(v,) for v in widths],t)[0])
                px-=dy/norm*width*w*.8;py+=dx/norm*width*w*.8
                x=(px-488)/227.29;z=(532-py)/257+.105
                y-=lift*math.sin(math.pi*t)*(1-w*w*.5)
                co=Vector((x,y,z))+root_delta*(1-smooth(t/.25))
                if variant>=2:
                    # Keep the front-space trace and lift; recede lateral ends
                    # into the scalp/rear rather than leaving outward spikes.
                    if abs(co.x)>.78:co.x=math.copysign(.78+.16*math.tanh((abs(co.x)-.78)/.16),co.x)
                    hit,hn,_,_=skull.ray_cast(Vector((co.x,-3,co.z)),Vector((0,1,0)))
                    if hit is not None:
                        amount=smooth((t-.10)/.55)
                        co.y=co.y*(1-amount)+(hit.y-.025-.04*math.sin(math.pi*t))*amount
                    if t>.72:co.y+=.26*smooth((t-.72)/.28)
                    if accent:co.y-=.006
                # Collision guard only: never flatten external lifted paths.
                near,normal,_,_=skull.find_nearest(co)
                if (co-near).dot(normal)<.006:co=near+normal*.006
                if variant>=3:
                    # Continuous radial wrap avoids the front-ray hit/miss
                    # discontinuity at the silhouette seen in variant two.
                    origin=Vector((0,0,.3))
                    hit,normal,_,_=skull.ray_cast(origin,(co-origin).normalized())
                    if hit is not None:
                        lifted=hit+normal*(.015+.055*math.sin(math.pi*t)**.8)
                        co=co.lerp(lifted,smooth((t-.18)/.48))
                        if accent:co+=normal*.007
                pi=(index*per+j)*(steps+1)+k
                hair.attributes['position'].data[pi].vector=co
                radius.data[pi].value=max(.012,width/227.29*2.4/.32)
                if variant>=2:
                    radius.data[pi].value*=.90
                    if accent:radius.data[pi].value*=.13*math.sin(math.pi*u)**.6
                highlight=math.sin(math.pi*t)**1.4*(.5+.5*math.sin(t*9+index*.9))**2
                value=.012+(.022+.038*(j in (1,3)))*highlight
                if variant>=2:value=(.075+.018*((index+j)%3)) if accent else (.004,.012,.006,.019,.004)[j]
                color.data[pi].color=(value,value*.45,value*.20,1)
    ob.data=hair;bpy.data.hair_curves.remove(old)
    return {'dominant_locks':len(SECTIONS),'editable_strokes':len(hair.curves),'points':len(hair.points),'depth_policy':'Fixed roots, independent depth, collision guard only'}

def brush_preview(job,out):
    """Use verified official node assets directly; do not register add-on code."""
    import bpy
    from illustrated_hair_section import protection
    from hair_front_fit import rear_signature
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    protected,rear=protection(),rear_signature();build(4 if job['operation']=='brush-locks' else 5)
    lock_info=dominant_locks(job['candidate']) if job['operation']=='brush-locks' else {}
    with bpy.data.libraries.load(str(BRUSH_LIB),link=False) as (src,dst):
        dst.node_groups=['.brushstroke_tools.surface_draw','.brushstroke_tools.pre_processing']
        dst.materials=['Brush Material']
    material=dst.materials[0];nodes,links=material.node_tree.nodes,material.node_tree.links
    nodes['Canvas'].inputs['Strength'].default_value=0
    p=nodes.get('Principled BSDF');attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='brush_stroke.color'
    links.new(attr.outputs['Color'],p.inputs['Base Color']);links.new(attr.outputs['Color'],p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value=.7;p.inputs['Specular IOR Level'].default_value=.05;p.inputs['Roughness'].default_value=.8
    if job['candidate']>=3 or lock_info:
        # Stroke ribbons must face a coherent head surface, not the overlapping
        # UV emitter patches designed only for root distribution.
        # Official graph computes mask - backfacing. Keep the mask and remove
        # only the backfacing subtraction; zeroing input0 erases the strokes.
        for link in list(nodes['Backface Culling'].inputs[1].links):links.remove(link)
        nodes['Backface Culling'].inputs[1].default_value=0
        for link in list(nodes['Use Strength'].inputs[1].links):links.remove(link)
        nodes['Use Strength'].inputs[1].default_value=1
    for im in list(bpy.data.images):
        if im.source=='FILE' and not im.packed_file and 'canvas-linen_01.exr' in im.filepath:
            im.filepath=str(BRUSH_LIB.parent/'maps/canvas-linen_01.exr')
    ob=bpy.data.objects['MF_native_hair_groom'];ob.modifiers.clear()
    # Brushstroke drawing uses normalized pressure-radius, not hair diameter.
    if not lock_info:
        for index,value in enumerate(ob.data.attributes['radius'].data):
            value.value=.7*(1-smooth(((index%73)/72-.78)/.22))+.02
    graph=bpy.data.node_groups.new('MF_specialist_brushstroke_pipeline','GeometryNodeTree')
    graph.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    graph.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n,l=graph.nodes,graph.links;gi=n.new('NodeGroupInput');go=n.new('NodeGroupOutput')
    pre=n.new('GeometryNodeGroup');pre.node_tree=dst.node_groups[1]
    pre.inputs['Object'].default_value=ob.data.surface;pre.inputs['Deformation'].default_value=False
    draw=n.new('GeometryNodeGroup');draw.node_tree=dst.node_groups[0]
    settings={'Surface Object':ob.data.surface,'Surface UV Map':'GroomSurfaceUV','Use Rest Position':False,
              'Normal Offset':.005,'Shrinkwrap':0.,'Brush Width':.075,'Overdraw':0.,'Brush Material':material,
              'Color Attribute':'MF_groom_color','Mesh Loops':3,'Smoothing Steps':2,'Taper':.65,'Preview Base Curves':False,'Seed':614}
    if job['candidate']>=3 or lock_info:
        body=bpy.data.objects['MF_continuous_head_neck']
        pre.inputs['Object'].default_value=body
        settings.update({'Surface Object':body,'Surface UV Map':body.data.uv_layers.active.name,'Brush Width':.10,'Mesh Loops':2})
    if lock_info:
        settings.update({'Brush Width':.32,'Mesh Loops':3,'Taper':.12,'Smoothing Steps':1})
        nodes['Brush Style'].inputs['Fill Extent'].default_value=.94
        nodes['Brush Style'].inputs['Falloff'].default_value=.22
    for key,value in settings.items():draw.inputs[key].default_value=value
    l.new(gi.outputs[0],pre.inputs['Geometry']);l.new(pre.outputs['Geometry'],draw.inputs['Brushstroke Curves']);l.new(draw.outputs['Brushstroke Mesh'],go.inputs[0])
    if lock_info and job['candidate']==3:
        # Isolate strip conversion from surface_draw's sampled face/ear normal
        # field. Analytic scalp normals are continuous across the silhouette.
        direct=n.new('GeometryNodeGroup');direct.node_tree=bpy.data.node_groups['.brushstroke_tools.curves_to_brushstrokes']
        direct.inputs['Width'].default_value=.32
        direct.inputs['Material'].default_value=material
        direct.inputs['Resolution'].default_value=3
        direct.inputs['Opacity'].default_value=1
        position=n.new('GeometryNodeInputPosition')
        center=n.new('ShaderNodeVectorMath');center.operation='SUBTRACT';center.inputs[1].default_value=(0,0,.3)
        scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1/.86**2,1,1/1.25**2)
        norm=n.new('ShaderNodeVectorMath');norm.operation='NORMALIZE'
        colors=n.new('GeometryNodeInputNamedAttribute');colors.data_type='FLOAT_COLOR';colors.inputs['Name'].default_value='MF_groom_color'
        l.new(position.outputs[0],center.inputs[0]);l.new(center.outputs[0],scale.inputs[0]);l.new(scale.outputs[0],norm.inputs[0])
        l.new(norm.outputs[0],direct.inputs['Surface Normal']);l.new(colors.outputs['Attribute'],direct.inputs['Color'])
        l.new(gi.outputs[0],direct.inputs['Curves']);l.new(direct.outputs[0],go.inputs[0])
        lock_info['strip_orientation']='Continuous analytic scalp normals; direct inspected official strip converter'
    mod=ob.modifiers.new('Official Brushstroke Tools draw nodes','NODES');mod.node_group=graph
    visibility();bpy.context.scene.cycles.transparent_max_bounces=32
    # CURVES.to_mesh is unsupported even when its evaluated geometry set holds
    # mesh output. Inspect via a mesh carrier; keep editable guides intact.
    probe=bpy.data.objects.new('MF_groom_brush_probe',bpy.data.meshes.new('MF_groom_brush_probe'))
    bpy.context.scene.collection.objects.link(probe);probe.hide_render=True
    pg=bpy.data.node_groups.new('MF_groom_brush_probe','GeometryNodeTree')
    pg.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    oi=pg.nodes.new('GeometryNodeObjectInfo');oi.inputs['Object'].default_value=ob;oi.inputs['As Instance'].default_value=False
    output=pg.nodes.new('NodeGroupOutput');pg.links.new(oi.outputs['Geometry'],output.inputs[0])
    pm=probe.modifiers.new('Inspect evaluated brushstroke mesh','NODES');pm.node_group=pg
    bpy.context.view_layer.update();mesh=probe.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    vertices,polygons=len(mesh.vertices),len(mesh.polygons)
    assert vertices>0 and protection()==protected and rear_signature()==rear
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'hypothesis':'SPECIALIST_PAINTERLY_BRUSHSTROKE_GEOMETRY','candidate':job['candidate'],'evaluated_vertices':vertices,'evaluated_polygons':polygons,
            'protected_exact':protection()==protected,'rear_mesh_exact':rear_signature()==rear,'review_ready':False,'director_acceptance':'NOT_REQUESTED',
            'handler_sha256':digest(Path(__file__)),'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,'brush_resource_sha256':BRUSH_SHA,
            'addon_installed':False,'third_party_python_executed':False,'purchased_assets':False}
    result.update(lock_info)
    if lock_info:
        result['hypothesis']='DOMINANT_PAINTERLY_LOCKS_FIXED_ROOTS_INDEPENDENT_DEPTH'
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')

def verify(out):
    import bpy
    from illustrated_hair_section import protection
    from hair_front_fit import rear_signature
    from hijab_donor import review
    folder=BASE/'native-groom-checkpoint-02';native=folder/'diagnostic-groom.blend'
    info=json.loads((folder/'checkpoint.json').read_text())
    assert digest(native)==info['native_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    before=curves_state()
    assert before==info['curves'] and protection()==info['protected'] and rear_signature()==info['rear']
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('reopened',0),))
    data=bpy.data.objects['MF_native_hair_groom'].data
    old=[]
    # Fixed local revision: lift a small right-hand group of three guides.
    # It is a controllability probe, not a proposed artistic improvement.
    for i in range(7,10):
        curve=224+i*7+1
        for k in range(73):
            index=curve*73+k;value=data.attributes['position'].data[index]
            old.append((index,value.vector.copy()));co=value.vector.copy()
            co.z+=.06*math.sin(math.pi*k/72)**2;value.vector=co
    data.update_tag();bpy.context.view_layer.update()
    revised=curves_state()
    assert revised['positions']!=before['positions'] and revised['evaluated_positions']!=before['evaluated_positions']
    assert revised['evaluated_curves']==before['evaluated_curves'] and protection()==info['protected'] and rear_signature()==info['rear']
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('controlled-revision',0),))
    for index,co in old:data.attributes['position'].data[index].vector=co
    data.update_tag();bpy.context.view_layer.update()
    assert curves_state()==before and digest(native)==info['native_sha256']
    result={'fresh_process_reopen_exact':True,'native_evaluated_geometry_exact':True,'protected_nonhair_exact':True,
            'controlled_revision_guides':3,'controlled_revision_points':len(old),'revision_propagated_to_evaluated_curves':True,
            'revision_rollback_exact':True,'source_file_unchanged':digest(SOURCE)==SOURCE_SHA,'native_file_unchanged':True,
            'revision_visual_quality':'NOT_QUALIFIED_TECHNICAL_PROBE','motion':'NOT_RUN','review_ready':False}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')

def run(job):
    out=validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    if job['operation']=='inspect':inspect(out)
    elif job['operation']=='brush-inspect':inspect_brush(out)
    elif job['operation'] in ('brush-preview','brush-retry','brush-locks'):brush_preview(job,out)
    elif job['operation']=='checkpoint':checkpoint(out)
    elif job['operation']=='verify':verify(out)
    else:preview(job,out)

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
