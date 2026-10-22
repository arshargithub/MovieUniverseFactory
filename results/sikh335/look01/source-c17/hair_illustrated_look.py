"""Bounded textured hair continuation, with immutable accepted facial state.

Fixed authored volumes and native procedural brush-flow materials, not image
replacement, arbitrary job code, or a newly accepted rear haircut.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'hair-sculpt-package-03/hair-shape-study.blend'
SOURCE_SHA = '34682c0487bf9057961082fb122e48a4caa8aa3ff083fa412568a27acaca9d21'
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured job required')
    if job['operation'] not in ('preview', 'retry', 'repair', 'package') or type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3, 4, 5, 6):
        raise ValueError('Unsupported operation')
    if job['operation']=='retry' and job['candidate']!=3:
        raise ValueError('Only failed third preview retry supported')
    if job['operation']=='repair' and job['candidate']!=6:
        raise ValueError('Only final temporal wisp repair supported')
    for p, expected in [(SOURCE, SOURCE_SHA), *[(REFBASE/n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != expected:
            raise ValueError('Pinned input changed')
    out = BASE/f'hair-look-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes fixed directory')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    if job['operation'] == 'package':
        stage='repair' if job['candidate']==6 else 'retry' if job['candidate']==3 else 'preview'
        p = BASE/f'hair-look-{stage}-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file():
            raise ValueError('Preview required')
        data = json.loads(p.read_text())
        if not data['protected_exact'] or data['handler_sha256'] != digest(Path(__file__)):
            raise ValueError('Stale preview or protection failed')
    return out


def envelope(t):
    return max(0., math.sin(math.pi*t))**.48


def reference_uv(x,z):
    """Hair-only interior warp; excludes the blue scarf without editing pixels."""
    py=1647*(1-(.156*z+.677))
    # Interior silhouette measured on the approved frontal, not the failed cap.
    rows=[(208,445,548),(240,392,598),(280,337,652),(330,301,690),(400,274,707),(500,246,717),(600,247,719),(700,259,704)]
    py=max(217,min(695,py))
    i=next((i for i in range(len(rows)-1) if rows[i+1][0]>=py),len(rows)-2)
    a,b=rows[i],rows[i+1]; t=(py-a[0])/(b[0]-a[0])
    lo=a[1]*(1-t)+b[1]*t; hi=a[2]*(1-t)+b[2]*t
    raw=.5+.238*x
    # Compress only outside the usable patch; derivative remains continuous.
    px=raw*955
    center=488
    bound=hi if px>center else lo
    limit=abs(bound-center)
    delta=px-center
    if abs(delta)>limit*.75:
        delta=math.copysign(limit*(.75+.23*math.tanh((abs(delta)/limit-.75)/.23)),delta)
    return (center+delta)/955,1-py/1647


def material(seed, candidate, *, support=False):
    import bpy
    m = bpy.data.materials.new(f'MF_hair_brush_{seed}_{support}'); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.68
    p.inputs['Specular IOR Level'].default_value=.18
    if ((candidate>=2 and support) or candidate==3) and candidate<4:
        # Native surface projection from the unmodified approved frontal.
        # Back-of-head colour is separately authored, never claimed observed.
        uv=n.new('ShaderNodeUVMap'); uv.uv_map='ReferenceHair' if support else 'HairArt'
        tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=False)
        tex.image.pack(); l.new(uv.outputs[0],tex.inputs['Vector'])
        l.new(tex.outputs['Color'],p.inputs['Base Color'])
        l.new(tex.outputs['Color'],p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value=.25
        return m
    if support and candidate<4:
        p.inputs['Base Color'].default_value=(.013,.006,.003,1)
        return m
    uv=n.new('ShaderNodeTexCoord')
    scale=n.new('ShaderNodeVectorMath'); scale.operation='MULTIPLY'
    scale.inputs[1].default_value=((90,3.5,1) if candidate>=5 else (24,2.7,1) if candidate>=4 else (48,3.3,1)); l.new(uv.outputs['UV'],scale.inputs[0])
    add=n.new('ShaderNodeVectorMath'); add.operation='ADD'
    add.inputs[1].default_value=(seed*.71,seed*.13,0); l.new(scale.outputs['Vector'],add.inputs[0])
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=1
    noise.inputs['Detail'].default_value=2; noise.inputs['Roughness'].default_value=.65
    l.new(add.outputs['Vector'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    palette=[(.21,(.006,.0025,.0015,1)),(.42,(.022,.009,.004,1)),(.57,(.065,.028,.012,1)),(.70,(.18,.086,.035,1)),(.83,(.30,.16,.072,1))]
    cr=ramp.color_ramp; cr.elements.remove(cr.elements[1]); cr.elements[0].position=palette[0][0]; cr.elements[0].color=palette[0][1]
    for position,color in palette[1:]: cr.elements.new(position).color=tuple(c*.66 for c in color[:3])+(1,) if candidate>=5 else color
    l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],p.inputs['Base Color'])
    l.new(ramp.outputs[0],p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value=.22
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.11; bump.inputs['Distance'].default_value=.012
    l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],p.inputs['Normal'])
    if candidate>=4:
        p.inputs['Emission Strength'].default_value=.12
        if support or candidate>=5:
            refuv=n.new('ShaderNodeUVMap'); refuv.uv_map='ReferenceHair'
            tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=False); tex.image.pack()
            l.new(refuv.outputs[0],tex.inputs['Vector'])
            geom=n.new('ShaderNodeNewGeometry'); sep=n.new('ShaderNodeSeparateXYZ'); l.new(geom.outputs['Position'],sep.inputs[0])
            fade=n.new('ShaderNodeMapRange'); fade.inputs['From Min'].default_value=-.32; fade.inputs['From Max'].default_value=.32
            l.new(sep.outputs['Y'],fade.inputs['Value'])
            rgb=n.new('ShaderNodeSeparateColor'); l.new(tex.outputs['Color'],rgb.inputs[0])
            blue=n.new('ShaderNodeMath'); blue.operation='GREATER_THAN'; l.new(rgb.outputs['Blue'],blue.inputs[0]); l.new(rgb.outputs['Red'],blue.inputs[1])
            mask=n.new('ShaderNodeMath'); mask.operation='MAXIMUM'; l.new(blue.outputs[0],mask.inputs[0]); l.new(fade.outputs[0],mask.inputs[1])
            if candidate>=5:
                low=n.new('ShaderNodeMapRange'); low.inputs['From Min'].default_value=.3; low.inputs['From Max'].default_value=.05
                l.new(sep.outputs['Z'],low.inputs['Value'])
                finalmask=n.new('ShaderNodeMath'); finalmask.operation='MAXIMUM'; l.new(mask.outputs[0],finalmask.inputs[0]); l.new(low.outputs[0],finalmask.inputs[1]); mask=finalmask
            mix=n.new('ShaderNodeMixRGB'); l.new(mask.outputs[0],mix.inputs[0]); l.new(tex.outputs[0],mix.inputs[1]); l.new(ramp.outputs[0],mix.inputs[2])
            l.new(mix.outputs[0],p.inputs['Base Color']); l.new(mix.outputs[0],p.inputs['Emission Color'])
    return m


def lock(points, width, depth, index, mat, candidate=1, surface=None):
    """Closed solid lock with flow-aligned native UVs and tapered roots/tips."""
    import bpy
    import bmesh
    from mathutils import Vector
    from hair_volume_sculpt import spline
    ns,nr=84,20; verts=[]; faces=[]; uvcoords=[]
    def center(t):
        c=Vector(spline(points,t))
        if surface is not None:
            origin=Vector((0,0,.3)); hit,n,_,_=surface.ray_cast(origin,(c-origin).normalized())
            if hit is not None: c=hit+n*(.003+.028*envelope(t))
        return c
    for i in range(1,ns):
        t=i/ns; c=center(t)
        tangent=(center(min(1,t+.001))-center(max(0,t-.001))).normalized()
        outward=Vector((c.x, c.y+.04, max(.02,c.z-.1)))
        outward=(outward-tangent*outward.dot(tangent)).normalized()
        across=tangent.cross(outward).normalized()
        tap=envelope(t)
        for j in range(nr):
            theta=2*math.pi*j/nr
            w=width*(.86+.13*math.sin(t*9+index*.8))
            # A broad lock, with subtle uneven divisions rather than a cylinder.
            a=w*math.cos(theta)*tap
            b=depth*math.sin(theta)*tap
            b+=.0025*max(0,math.sin(theta))*math.sin(theta*13+t*5+index)*tap
            verts.append(tuple(c+across*a+outward*b)); uvcoords.append((j/nr,t))
    for i in range(ns-2):
        for j in range(nr):
            a=i*nr+j; b=i*nr+(j+1)%nr
            faces.append((a,b,b+nr,a+nr))
    start,end=len(verts),len(verts)+1
    verts.extend((tuple(center(0)),tuple(center(1)))); uvcoords.extend(((.5,0),(.5,1)))
    for j in range(nr):
        faces.append((start,(j+1)%nr,j))
        a=(ns-2)*nr+j; b=(ns-2)*nr+(j+1)%nr
        faces.append((end,a,b))
    mesh=bpy.data.meshes.new(f'MF_illustrated_hair_lock_{index}')
    mesh.from_pydata(verts,[],faces); mesh.update()
    uv=mesh.uv_layers.new(name='HairFlow')
    art=mesh.uv_layers.new(name='HairArt')
    for poly in mesh.polygons:
        seam=any(uvcoords[mesh.loops[k].vertex_index][0]>.9 for k in poly.loop_indices) and any(uvcoords[mesh.loops[k].vertex_index][0]==0 for k in poly.loop_indices)
        for k in poly.loop_indices:
            u,v=uvcoords[mesh.loops[k].vertex_index]
            uv.data[k].uv=(1 if seam and u==0 else u,v)
            # A curved hair-only patch from the reference's swept temporal
            # mass. The image remains untouched and packed into the native.
            from hair_volume_sculpt import spline
            px,py,_=spline([(425,270,0),(350,325,0),(300,410,0),(263,490,0),(255,550,0)],v)
            px+=(u-.5)*30+3*math.sin(index*2.1)
            art.data[k].uv=(px/955,1-py/1647)
        poly.use_smooth=True
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges)
    bm.to_mesh(mesh); bm.free()
    mesh.uv_layers.active_index=0
    mesh.uv_layers[0].active_render=True
    if candidate>=5: assign_flow(mesh)
    ob=bpy.data.objects.new(mesh.name,mesh); bpy.context.scene.collection.objects.link(ob); mesh.materials.append(mat)
    return ob


def assign_flow(mesh):
    """Identical spatial texture field on the crown and descending masses."""
    flow=mesh.uv_layers.get('HairFlow') or mesh.uv_layers.new(name='HairFlow')
    ref=mesh.uv_layers.get('ReferenceHair') or mesh.uv_layers.new(name='ReferenceHair')
    for poly in mesh.polygons:
        for k in poly.loop_indices:
            x,y,z=mesh.vertices[mesh.loops[k].vertex_index].co
            flow.data[k].uv=(math.atan2(x,y)/(2*math.pi),(1.4-z)*.3)
            ref.data[k].uv=reference_uv(x,z)
    mesh.uv_layers.active_index=list(mesh.uv_layers.keys()).index('HairFlow')
    flow.active_render=True


def build(candidate):
    import bpy
    from mathutils import Vector
    from hair_volume_sculpt import guides,skull_surface
    from hair_anatomy_refinement import is_hair
    for ob in bpy.context.scene.objects:
        if is_hair(ob): ob.hide_render=True
    base=bpy.data.objects['MF_sculpt_hair_support']; base.hide_render=False
    base.data.materials.clear(); base.data.materials.append(material(0,candidate,support=True))
    tree=skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    if candidate>=2:
        uv=base.data.uv_layers.new(name='ReferenceHair')
        for poly in base.data.polygons:
            for k in poly.loop_indices:
                x,y,z=base.data.vertices[base.data.loops[k].vertex_index].co
                # The upper portrait's scarf is outside the usable hair patch.
                u,v=reference_uv(x,z) if candidate>=3 else (.238*x+.5,min(.874,.156*z+.677))
                if candidate>=3 and y>.18:
                    # The portrait does not show a rear scalp. Extend only its
                    # existing hair palette/brushwork, not the front face/scarf.
                    u=(320+55*x)/955; v=1-(305+max(0,1.25-z)*115)/1647
                uv.data[k].uv=(u,v)
        if candidate>=4:
            flow=base.data.uv_layers.new(name='HairFlow')
            for poly in base.data.polygons:
                for k in poly.loop_indices:
                    x,y,z=base.data.vertices[base.data.loops[k].vertex_index].co
                    phase=(z+.55*abs(x)**1.6)*.35 if y<0 else math.atan2(x,y)/(2*math.pi)
                    flow.data[k].uv=(phase,(1.35-z)*.3)
            base.data.uv_layers.active_index=len(base.data.uv_layers)-1
            flow.active_render=True
        backmat=material(33,1,support=True); base.data.materials.append(backmat)
        for poly in base.data.polygons:
            if poly.center.y>.25 and candidate<3: poly.material_index=1
    mats=[material(i,candidate) for i in range(9)]
    if candidate>=5:
        shared=material(0,candidate,support=True)
        base.data.materials.clear(); base.data.materials.append(shared)
        for p in base.data.polygons: p.material_index=0
        assign_flow(base.data); mats=[shared]
    count=0
    for side in (-1,1):
        # Unequal root groups overlap broad primary flows. Endpoints tuck in.
        for i,(points,w,d) in enumerate(guides(3) if candidate==1 else []):
            for layer in range(3):
                fitted=[]
                for k,p in enumerate(points):
                    x,y,z=p
                    x=side*(x+.012*layer); y+=.044*(layer-1); z+=.016*math.sin(k*1.5+i+side)
                    co=Vector((x,y,z)); origin=Vector((0,0,.3))
                    hit,n,_,_=tree.ray_cast(origin,(co-origin).normalized())
                    if hit is None: raise ValueError('Hair control missed scalp')
                    lift=(.023+.018*layer)*math.sin(math.pi*k/(len(points)-1))
                    fitted.append(tuple(hit+n*(.014+lift)))
                width=w*(.40+.055*math.sin(i*3+layer+side))
                lock(fitted,width,d*(.32+.09*layer),count,mats[count%len(mats)]); count+=1
        # Visible length follows the portraits; hidden rear arrangement remains
        # explicitly provisional. No new scalp/face fitting is performed.
        for i in range(10 if candidate<3 else 0):
            f=i/9
            pts=[(side*(.79-.12*f),.12+.60*f,.60+.25*f),
                 (side*(.94-.25*f),.30+.56*f,.12),
                 (side*(.93-.37*f),.47+.49*f,-.28),
                 (side*(.84-.43*f),.55+.45*f,-.66),
                 (side*(.96-.61*f),.56+.52*f,-1.01),
                 (side*(.73-.56*f),.70+.34*f,-1.29+.20*math.sin(i*1.7))]
            pts=[(x+side*.045*math.sin(k*2.2+i+side),y,z+.025*math.sin(i+side)) for k,(x,y,z) in enumerate(pts)]
            if candidate>=2:
                # Bury roots on the scalp; rear sections spread to the midline.
                origin=Vector((0,0,.3)); root=Vector(pts[0]); hit,n,_,_=tree.ray_cast(origin,(root-origin).normalized())
                pts[0]=tuple(hit-n*.055)
                for k in range(1,len(pts)):
                    x,y,z=pts[k]
                    pts[k]=(x*(1-.77*f),y-.10,z)
            lock(pts,.14+.025*math.sin(i*2),.042,count,mats[count%len(mats)]); count+=1
        # A few temple edges soften the cap line, without a fibre forest.
        for i in range(4 if candidate==1 else 0):
            pts=[(side*.55,-.88,.84+i*.022),(side*(.73+i*.012),-.74,.64),
                 (side*(.84+i*.011),-.51,.40),(side*(.84+i*.016),-.31,.24-i*.03)]
            lock(pts,.012+.004*(i%2),.008,count,mats[count%len(mats)]); count+=1
    if candidate>=3:
        # A connected-looking curtain: roots begin on the actual crown proxy,
        # then descend in overlapping unequal waves, not two detached wings.
        for i in range(21):
            theta=math.radians((-88+176*i/20) if candidate>=6 else (-101+202*i/20))
            sx,sy=math.sin(theta),math.cos(theta)
            origin=Vector((0,0,.3)); desired=Vector((.79*sx,.77*sy,.87+.13*math.cos(i*1.1)))
            hit,n,_,_=tree.ray_cast(origin,(desired-origin).normalized())
            start=tuple(hit-n*.055)
            pts=[start, (.87*sx,.84*sy,.42),(.89*sx,.93*sy,-.06),
                 ((.91+.045*math.sin(i))*sx,(.87+.06*math.sin(i))*sy,-.51),
                 ((.79+.06*math.cos(i*1.7))*sx,.86*sy,-.91),
                 ((.70+.10*math.sin(i*1.4))*sx,.75*sy,-1.31+.12*math.cos(i*1.9))]
            if candidate>=4:
                # Start each volume high and inside the crown, with variation
                # in its entry and taper, avoiding a horizontal attachment row.
                desired=Vector((.46*sx,.52*sy,1.18))
                hit,n,_,_=tree.ray_cast(origin,(desired-origin).normalized())
                pts[0]=tuple(hit-n*.09)
                desired=Vector((.82*sx,.77*sy,.54+.07*math.sin(i)))
                hit,n,_,_=tree.ray_cast(origin,(desired-origin).normalized())
                pts[1]=tuple(hit-n*.015)
                pts[3]=((.89+.065*math.sin(i*1.4))*sx,(.95+.07*math.sin(i*.7))*sy,-.58)
                pts[4]=((.83+.10*math.cos(i*1.7))*sx,(.98+.07*math.cos(i))*sy,-1.09)
                pts[5]=((.78+.18*math.sin(i*1.4))*sx,(.94+.07*math.sin(i*.9))*sy,-1.64+.22*math.cos(i*1.9))
            if candidate>=5:
                for k in range(2,len(pts)):
                    x,y,z=pts[k]; phase=i*.83+k*1.8
                    pts[k]=(x+.065*math.sin(phase),y+.075*math.sin(phase+.6),z)
            lock(pts,.16+.025*math.sin(i*2.2),.054,count,mats[count%len(mats)],candidate); count+=1
    if candidate>=5:
        from mathutils.bvhtree import BVHTree
        surface=BVHTree.FromObject(base,bpy.context.evaluated_depsgraph_get())
        for side in (-1,1):
            for i in range(3):
                pts=[(side*.05,-.91+i*.05,1.01+i*.09),(side*.33,-.99,.96+i*.06),
                     (side*.63,-.84,.75+i*.06),(side*.83,-.52,.43+i*.04),(side*.87,-.18,.19+i*.04)]
                lock(pts,.026+.012*i,.010,count,mats[0],candidate,surface); count+=1
            # Free temple wisps from preview06 are deliberately omitted: their
            # unsolved far-side root projected above the brow in review.
    return {'locks':count,'native_procedural_material':True,'rear_design':'PROVISIONAL_EXTRAPOLATION','hair_motion_qualified':False}


def run(job):
    out=validate(job); out.mkdir()
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection(); info=build(job['candidate']); assert protection()==before
    visibility()
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    if job['candidate']>=6:
        # Context only: restore selected existing clothes, not their obsolete
        # donors or previous costume versions. No geometry/material changes.
        wardrobe=('MF_adapted_donor_hood','MF_diagonal_donor_wrap','MF_layered_upper_scarf',
                  'MF_upper_tunic','MF_loose_tunic_sleeve_','MF_fitted_inner_neckline',
                  'MF_reference_shoulder_harness_','MF_reference_buckle','MF_shoulder_stitch',
                  'MF_tunic_shoulder_underlayer')
        for ob in bpy.context.scene.objects:
            if ob.type in ('MESH','CURVE') and any(ob.name==n or (n.endswith('_') and ob.name.startswith(n)) for n in wardrobe):
                ob.hide_render=False
        review(bpy.context.scene,out,(0,0,-.63),4.9,(('context-front',0),('context-side',-45)))
        visibility()
        if job['operation']=='package':
            review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
    result={'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
            'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,
            'geometry':info,'director_acceptance':'PENDING','production_hair_qualified':False}
    assert result['protected_exact']
    if job['operation']=='package':
        native=out/'hair-textured.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['fresh_reopen_protected_exact']=protection()==before
        assert result['fresh_reopen_protected_exact']; result['native_sha256']=digest(native)
    assert digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
