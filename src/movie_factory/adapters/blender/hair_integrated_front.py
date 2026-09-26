"""Bounded reference-shaped hair sections. Trusted fixed operations, no job code.

Unlike the fused shell and circular lofts, each section has explicit illustrated
guide, unequal width stations and an authored depth path. No face edits.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'edge-package-03/hair-edge.blend'
SOURCE_SHA = '736d5b3e15b842ea533ce6af4abea9d9114865ddcf0f0f74ee8f96fa078d53de'
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}
# (image-x, image-y, depth-y). Front part -> lifted shoulder -> temple.
# Each side is traced separately, not a mirrored array. Widths are half-widths
# at the same stations. The blue scarf boundary is deliberately excluded.
SECTIONS = [
    ([(487,220,-.39),(439,220,-.52),(380,264,-.60),(323,325,-.48),(281,403,-.23)], [2,13,21,19,0], .045),
    ([(487,245,-.59),(437,243,-.73),(374,288,-.82),(298,359,-.63),(246,411,-.10)], [2,15,23,17,0], .070),
    ([(487,270,-.75),(442,265,-.91),(375,317,-1.00),(303,384,-.84),(232,431,-.13)], [2,16,21,15,0], .070),
    ([(487,296,-.89),(443,293,-1.02),(396,342,-1.05),(319,405,-.90),(245,457,-.18)], [2,15,20,19,0], .050),
    ([(486,318,-.94),(455,313,-1.04),(416,357,-1.08),(356,413,-1.01),(281,456,-.62),(237,488,-.03)], [1,10,12,16,12,0], .035),
    ([(342,410,-.92),(310,452,-.83),(283,492,-.63),(247,538,-.20),(256,571,.04)], [2,13,16,12,0], .040),
    ([(296,467,-.66),(284,498,-.63),(279,531,-.54),(271,562,-.27),(286,590,.05)], [1,7,9,6,0], .018),
    ([(493,221,-.39),(539,224,-.53),(586,260,-.63),(640,324,-.51),(678,388,-.20)], [2,12,21,22,0], .042),
    ([(492,246,-.60),(537,245,-.76),(604,289,-.86),(661,356,-.67),(712,413,-.09)], [2,15,24,17,0], .065),
    ([(493,270,-.75),(542,271,-.94),(598,313,-1.00),(663,382,-.80),(731,441,-.10)], [2,17,19,17,0], .065),
    ([(493,295,-.90),(535,291,-1.04),(586,337,-1.08),(642,397,-.91),(718,458,-.19)], [2,14,20,18,0], .045),
    ([(494,319,-.95),(520,317,-1.04),(561,358,-1.08),(618,413,-1.00),(679,453,-.62),(728,493,-.03)], [1,9,12,16,13,0], .030),
    ([(633,410,-.93),(658,450,-.84),(691,492,-.62),(727,540,-.20),(717,568,.06)], [2,13,17,12,0], .035),
    ([(679,469,-.66),(693,500,-.63),(697,532,-.52),(704,562,-.23),(688,592,.06)], [1,7,9,6,0], .018),
]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured keys required')
    # All three artistic candidates failed readiness. Keep this as a diagnostic
    # replay handler; no native packaging/promotion operation is authorized.
    if job['operation'] != 'preview' or type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3):
        raise ValueError('Unsupported fixed operation')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REFBASE/n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != h:
            raise ValueError('Pinned input changed')
    out = BASE / f'integrated-front-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    return out


def sample(points, t):
    n = len(points)-1
    f = max(0., min(n-1e-9, t*n)); i = int(f); u = f-i
    a, b, c, d = [points[max(0,min(n,j))] for j in (i-1,i,i+1,i+2)]
    return tuple(.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u) for k in range(len(b)))


def section_vertex(index, t, w, candidate):
    points, widths, lift = SECTIONS[index]
    px, py, y = sample(points,t)
    a,b = sample(points,max(0,t-.001)),sample(points,min(1,t+.001))
    dx,dy = b[0]-a[0], b[1]-a[1]
    norm = math.hypot(dx,dy)
    width = max(0., sample([(v,) for v in widths],t)[0])
    # A lobed wedge, not a circular/rolled cross section. Unequal borders and
    # selective ridges keep the broad painterly planes with thin tapered tips.
    width *= 1+.075*math.sin(t*18+index*.9)*w
    px += -dy/norm*width*w; py += dx/norm*width*w
    if candidate >= 2 and index in (4,11):
        # The frontmost lower margin must remain inside the illustrated hair,
        # not bring a strip of painted forehead onto a hair section.
        py -= 8*math.sin(math.pi*t)**.5
    x = (px-488)/227.29
    z = (532-py)/257 + .105
    shoulder = max(0,1-w*w)**1.8
    y -= lift*shoulder*(.35+.65*math.sin(math.pi*t))
    # Turn cross-section depth with the side of the head instead of leaving
    # frontal cards projecting sideways. The actual guides remain editable.
    y += .80*(abs(x)-abs((sample(points,t)[0]-488)/227.29))
    return (x,y,z), (px/955,1-py/1647), width


def hair_pixel_mask(u,v):
    """Explicit forehead boundary in the approved image, not skin brightness."""
    px,py=u*955,(1-v)*1647
    boundary=[(235,560),(270,553),(290,510),(315,462),(350,417),(390,365),(428,327),(454,320),(476,326),(490,332),(506,323),(526,325),(548,343),(582,389),(619,438),(651,473),(683,520),(718,564),(742,576)]
    i=next((i for i in range(len(boundary)-1) if boundary[i+1][0]>=px),len(boundary)-2)
    a,b=boundary[i],boundary[i+1]; f=max(0,min(1,(px-a[0])/(b[0]-a[0])))
    edge=a[1]*(1-f)+b[1]*f
    return max(0,min(1,(edge-py)/3))


def build(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    base = bpy.data.objects['MF_sculpt_hair_support']
    tree = BVHTree.FromObject(base,bpy.context.evaluated_depsgraph_get())
    from hair_volume_sculpt import skull_surface
    skull = skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    # Give the separate sections a quiet foundation; preserve back material.
    for i, source in enumerate(list(base.data.materials)):
        m = source.copy(); base.data.materials[i] = m
        n,l=m.node_tree.nodes,m.node_tree.links
        for p in [n for n in n if n.type=='BSDF_PRINCIPLED']:
            for socket in ('Base Color','Emission Color'):
                s=p.inputs[socket]
                if not s.is_linked: continue
                old=s.links[0].from_socket
                geo=n.new('ShaderNodeNewGeometry'); sep=n.new('ShaderNodeSeparateXYZ'); l.new(geo.outputs['Position'],sep.inputs[0])
                front=n.new('ShaderNodeMapRange'); front.clamp=True
                front.inputs['From Min'].default_value=-.55; front.inputs['From Max'].default_value=.12
                front.inputs['To Min'].default_value=.22; front.inputs['To Max'].default_value=1.
                l.new(sep.outputs['Y'],front.inputs['Value'])
                mult=n.new('ShaderNodeVectorMath'); mult.operation='SCALE'
                l.new(old,mult.inputs[0]); l.new(front.outputs['Result'],mult.inputs['Scale']); l.new(mult.outputs[0],s)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_hair_edge_wisp_','MF_hair_front_edge_')):
            ob.hide_render=True
    if candidate==3:
        for m in base.data.materials:
            n,l=m.node_tree.nodes,m.node_tree.links
            output=next(q for q in n if q.type=='OUTPUT_MATERIAL')
            original=output.inputs['Surface'].links[0].from_socket
            dark=n.new('ShaderNodeBsdfPrincipled'); dark.inputs['Base Color'].default_value=(.012,.0045,.002,1); dark.inputs['Roughness'].default_value=.9
            attr=n.new('ShaderNodeAttribute'); attr.attribute_name='MF_front_edge_opacity'; l.new(attr.outputs['Fac'],dark.inputs['Alpha'])
            geo=n.new('ShaderNodeNewGeometry'); sep=n.new('ShaderNodeSeparateXYZ'); l.new(geo.outputs['Position'],sep.inputs[0])
            amount=n.new('ShaderNodeMapRange'); amount.clamp=True; amount.inputs['From Min'].default_value=-.35; amount.inputs['From Max'].default_value=.20
            l.new(sep.outputs['Y'],amount.inputs['Value'])
            mix=n.new('ShaderNodeMixShader'); l.new(amount.outputs['Result'],mix.inputs[0]); l.new(dark.outputs[0],mix.inputs[1]); l.new(original,mix.inputs[2]); l.new(mix.outputs[0],output.inputs['Surface'])
    mat=bpy.data.materials.new('MF_hair_integrated_reference'); mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links; p=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=True); tex.image.pack()
    uv=n.new('ShaderNodeUVMap'); uv.uv_map='ReferenceHair'; l.new(uv.outputs[0],tex.inputs[0])
    l.new(tex.outputs[0],p.inputs['Base Color']); l.new(tex.outputs[0],p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value=.25; p.inputs['Roughness'].default_value=.82; p.inputs['Specular IOR Level'].default_value=.08
    attr=n.new('ShaderNodeAttribute'); attr.attribute_name='MF_section_opacity'
    l.new(attr.outputs['Fac'],p.inputs['Alpha'])
    if candidate == 2:
        # Exclude accidental skin/scarf sampling. This is a bounded texture
        # selection mask, not a new bitmap or claim of recovered albedo.
        rgb=n.new('ShaderNodeSeparateColor'); l.new(tex.outputs[0],rgb.inputs[0])
        dark=n.new('ShaderNodeMath'); dark.operation='LESS_THAN'; l.new(rgb.outputs['Red'],dark.inputs[0]); dark.inputs[1].default_value=.42
        brown=n.new('ShaderNodeMath'); brown.operation='GREATER_THAN'; l.new(rgb.outputs['Red'],brown.inputs[0]); l.new(rgb.outputs['Blue'],brown.inputs[1])
        a=n.new('ShaderNodeMath'); a.operation='MULTIPLY'; l.new(dark.outputs[0],a.inputs[0]); l.new(brown.outputs[0],a.inputs[1])
        b=n.new('ShaderNodeMath'); b.operation='MULTIPLY'; l.new(a.outputs[0],b.inputs[0]); l.new(attr.outputs['Fac'],b.inputs[1]); l.new(b.outputs[0],p.inputs['Alpha'])
    names=[]; ns,nw=72,16
    for idx in range(len(SECTIONS)):
        verts,uvs,faces,opacity=[],[],[],[]
        for i in range(ns+1):
            t=i/ns
            for j in range(nw+1):
                w=-1+2*j/nw; co,uv,width=section_vertex(idx,t,w,candidate)
                # Enforce scalp clearance without copying ear anatomy. The
                # authored depth remains primary; only collisions are lifted.
                hit,_,_,_=tree.ray_cast(Vector((co[0],-3,co[2])),Vector((0,1,0)))
                if hit is not None:
                    co=(co[0],min(co[1],hit.y-.012),co[2])
                if candidate == 2:
                    # Coupled scalp fitting and tip turn: ends sweep behind
                    # temples, rather than hanging as front-facing spikes.
                    origin=Vector((0,0,.3)); target=Vector(co)
                    target.x=math.copysign(.78+.22*math.tanh((abs(target.x)-.78)/.22),target.x) if abs(target.x)>.78 else target.x
                    hit,normal,_,_=skull.ray_cast(origin,(target-origin).normalized())
                    if hit is None: raise ValueError('Section scalp projection failed')
                    depth=.012+(.035+.028*(idx%7<4))*math.sin(math.pi*t)**.65*max(0,1-w*w)**1.4
                    target=hit+normal*depth
                    # Controlled return at tips around the ear/scalp edge.
                    back=max(0,(t-.62)/.38)**2
                    target.y+=.18*back; target.x*=1-.10*back
                    co=tuple(target)
                if candidate==3:
                    # Use the existing hair envelope for depth only, without
                    # its projected brushwork or fused-lock appearance. Front
                    # silhouette and individual margins stay reference-led.
                    x,y,z=co
                    if abs(x)>.80: x=math.copysign(.80+.19*math.tanh((abs(x)-.80)/.19),x)
                    hit,normal,_,_=tree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
                    if hit is None:
                        hit,normal,_,_=tree.find_nearest(Vector((x,-.35,z)))
                    if hit is None: raise ValueError('Envelope depth missing')
                    co=(x,hit.y-.012-(.035+.009*(idx%3))*max(0,1-w*w)**1.8*math.sin(math.pi*t)**.65,z)
                    # Tip thinning plus depth return eliminates pointed wings.
                    back=max(0,(t-.72)/.28)**2
                    co=(co[0]*(1-.045*back),co[1]+.12*back,co[2])
                verts.append(co); uvs.append(uv)
                edge=min(j,nw-j)
                opacity.append(min(1.,edge/.8)*min(1.,i/2,(ns-i)/2)*(hair_pixel_mask(*uv) if candidate==3 else 1))
        for i in range(ns):
            for j in range(nw):
                a=i*(nw+1)+j; faces.append((a,a+nw+1,a+nw+2,a+1))
        mesh=bpy.data.meshes.new(f'MF_hair_reference_section_{idx:02}'); mesh.from_pydata(verts,[],faces); mesh.update()
        ob=bpy.data.objects.new(mesh.name,mesh); bpy.context.scene.collection.objects.link(ob); mesh.materials.append(mat)
        uv=mesh.uv_layers.new(name='ReferenceHair'); attr=mesh.attributes.new('MF_section_opacity','FLOAT','POINT')
        for i,v in enumerate(attr.data): v.value=opacity[i]
        for p in mesh.polygons:
            p.use_smooth=True
            for li in p.loop_indices: uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
        ob['reference_authority']='pair-B; explicit front guides; inferred depth'
        names.append(ob.name)
    return {'section_names':names,'authoring':'Separate asymmetrical guide patches with explicit depth paths; no merged tubes','face_changed':False}


def run(job):
    out=validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_front_fit import rear_signature
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before,rear=protection(),rear_signature()
    info=build(job['candidate']); visibility()
    assert protection()==before and rear_signature()==rear
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'candidate':job['candidate'],'handler_sha256':digest(Path(__file__)),'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,'protected_exact':protection()==before,'rear_exact':rear_signature()==rear,'changes':info,'director_acceptance':'NOT_REVIEWED','review_ready':False}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    assert digest(SOURCE)==SOURCE_SHA


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
