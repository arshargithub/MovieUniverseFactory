"""Fixed reference-led front framing reset; accepted non-hair is immutable."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'hair-finish-package-03/hair-refined.blend'
SOURCE_SHA = '44234a6140baeaa03a7c9850ad7f58d8be86d54d244941bbe6153ca2cb3cf973'
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview', 'repair', 'package') or type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3):
        raise ValueError('Unsupported operation')
    if job['operation']=='repair' and job['candidate']!=3:
        raise ValueError('Only third-candidate defect cleanup supported')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REFBASE/n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != h: raise ValueError('Pinned input changed')
    out = BASE / f'framing-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free < 5_000_000_000: raise ValueError('Disk low')
    if job['operation'] == 'package':
        stage='repair' if job['candidate']==3 else 'preview'
        p = BASE / f'framing-{stage}-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file(): raise ValueError('Preview required')
        r = json.loads(p.read_text())
        if r.get('handler_sha256') != digest(Path(__file__)) or not r.get('protected_exact'):
            raise ValueError('Stale preview or failed protection')
    return out


def smooth(t):
    t = max(0., min(1., t)); return t*t*(3-2*t)


def warp(x, y, z, candidate):
    """Shared hair-only field: lifted shoulders of part, not a global lift."""
    front = 1-smooth((y+.25)/.75)
    edge = .085*(1-smooth((y+.55)/.5))*smooth((z+.05)/.45)*(1-smooth((z-.85)/.40))
    root = .19*math.exp(-((abs(x)-.36)/.36)**2-((y+.57)/.58)**2-((z-1.12)/.36)**2)
    if candidate==3:
        root *= .72*(1+.075*math.sin(x*5+.4))
        root += .039*math.exp(-(x/.20)**2-((y+.42)/.55)**2-((z-1.22)/.26)**2)
    side = .065*front*math.exp(-((abs(x)-.81)/.26)**2-((z-.48)/.46)**2)
    relief=0.
    if candidate>=2:
        for height,drop,width,amplitude in [(1.04,.55,.105,.055),(1.27,.49,.12,.045),(1.46,.41,.11,.034)]:
            curve=height-drop*abs(x)**1.55+.016*math.sin(x*7+height*2)
            relief+=amplitude*math.exp(-((z-curve)/width)**2)
        relief*=front*smooth(abs(x)/.11)*smooth((z-.10)/.35)
    return x+math.copysign(side+relief*abs(x)*.55, x), y-root*.22-relief, z+edge+root+relief*.3


def guide(layer, side):
    paths = [
        [(.015,-.94,.91),(.23,-1.01,1.10),(.51,-.94,1.02),(.77,-.76,.74),(.96,-.42,.37),(.98,-.02,.11),(.83,.34,-.10)],
        [(.018,-.68,1.16),(.23,-.79,1.37),(.56,-.65,1.29),(.86,-.38,.97),(1.03,.03,.52),(.91,.40,.10)],
        [(.020,-.28,1.32),(.26,-.37,1.49),(.59,-.14,1.35),(.88,.18,1.00),(.88,.57,.43),(.64,.75,.02)],
    ]
    return [(side*x,y+.018*math.sin(k+layer+side),z+.022*math.sin(k*1.8+side+layer)) for k,(x,y,z) in enumerate(paths[layer])]


def art_material():
    import bpy
    m = bpy.data.materials.new('MF_front_hair_reference_sweeps'); m.use_nodes=True
    n,l=m.node_tree.nodes,m.node_tree.links; p=n.get('Principled BSDF')
    uv=n.new('ShaderNodeUVMap'); uv.uv_map='HairArt'
    tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=True); tex.image.pack()
    l.new(uv.outputs[0],tex.inputs[0]); l.new(tex.outputs[0],p.inputs['Base Color'])
    l.new(tex.outputs[0],p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value=.18
    p.inputs['Roughness'].default_value=.78; p.inputs['Specular IOR Level'].default_value=.10
    return m


def upper_reference_uv(x,z):
    """Curve the sampling footprint through real upper hair, not one row."""
    from hair_finish_refinement import hair_uv
    old=hair_uv(x,z)
    py=max(210+105*abs(x)**1.5,532-257*z)
    rows=[(210,445,548),(240,392,598),(280,337,652),(330,301,690),(400,274,707)]
    py=max(210,min(399,py))
    i=next((i for i in range(len(rows)-1) if rows[i+1][0]>=py),len(rows)-2)
    a,b=rows[i],rows[i+1]; t=(py-a[0])/(b[0]-a[0])
    lo=a[1]*(1-t)+b[1]*t; hi=a[2]*(1-t)+b[2]*t
    center=488; raw=477.5+227.29*x; delta=raw-center
    limit=abs((hi if delta>0 else lo)-center)
    if abs(delta)>limit*.72:
        delta=math.copysign(limit*(.72+.25*math.tanh((abs(delta)/limit-.72)/.25)),delta)
    weight=smooth((z-1.02)/.22)
    return old[0]*(1-weight)+(center+delta)/955*weight, old[1]*(1-weight)+(1-py/1647)*weight


def build(candidate,repair=False):
    import bpy
    from mathutils import Vector
    from hair_volume_sculpt import skull_surface, spline
    from hair_illustrated_look import lock
    from hair_anatomy_refinement import is_hair
    tree=skull_surface(bpy.data.objects['MF_reference_crown_hair']); origin=Vector((0,0,.3))
    base=bpy.data.objects['MF_sculpt_hair_support']
    moved=0
    for ob in bpy.context.scene.objects:
        if not is_hair(ob): continue
        # Replace the old fine front strips; retain provisional rear masses.
        if ob.name in [f'MF_illustrated_hair_lock_{i}' for i in range(21,27)]: ob.hide_render=True
        ob.hide_set(ob.hide_render)
        if ob.hide_render or ob.type!='MESH': continue
        oldpoints=[v.co.copy() for v in ob.data.vertices]
        for v in ob.data.vertices:
            old=v.co.copy(); v.co=warp(*old,candidate)
            moved += (v.co-old).length>1e-8
        ob.data.update()
        if repair and ob==base:
            uv=ob.data.uv_layers.get('ReferenceHair')
            for loop in ob.data.loops:
                x,y,z=oldpoints[loop.vertex_index]
                if y<.2 and z>1.02: uv.data[loop.index].uv=upper_reference_uv(x,z)
    # Keep brushwork attached to the lifted roots; do not let world height
    # force the new front volume into the old vertically striped crown cap.
    mat=bpy.data.materials['MF_refined_hair_painted_flow']
    for node in mat.node_tree.nodes:
        if node.bl_idname=='ShaderNodeMapRange':
            node.interpolation_type='SMOOTHSTEP'
            if abs(node.inputs['From Min'].default_value-1.10)<.001:
                node.inputs['From Min'].default_value=1.43
                node.inputs['From Max'].default_value=1.65
    if candidate>=2:
        # A continuous shallow sculpt, not individual rolled/ribbon volumes.
        # The original front UV brushwork follows the shared displacement.
        flow=base.data.uv_layers.get('HairFlow')
        if flow:
            from hairline_placement import crown_flow
            for loop in base.data.loops:
                x,y,z=base.data.vertices[loop.vertex_index].co
                weight=smooth((z-.60)/.5)*(1-smooth((y+.45)/.4))
                flow.data[loop.index].uv.x=flow.data[loop.index].uv.x*(1-weight)+crown_flow(x,y,z)*weight
        wisps=[]
        if candidate==3 and not repair:
            from hair_finish_refinement import uv_layers
            for side in (-1,1):
                for i in range(3):
                    pts=[(side*(.57+.026*i),-.86,.64+.025*i),
                         (side*(.76+.018*i),-.69,.42+.021*i),
                         (side*(.865+.009*i),-.43,.23),
                         (side*(.875+.015*i),-.23,.055-.035*i)]
                    fitted=[]
                    for k,point in enumerate(pts):
                        co=Vector(point); hit,n,_,_=tree.ray_cast(origin,(co-origin).normalized())
                        if hit is None: raise ValueError('Temple projection missed')
                        p=Vector(warp(*(hit+n*(.018+.007*i)),candidate))
                        # Tips release a little from the crop edge, not a
                        # dark solid sideburn plate or a thick loose ringlet.
                        if k==3: p.z-=.028*(i+1); p.y-=.02
                        fitted.append(tuple(p))
                    ob=lock(fitted,.013+.003*i,.006,220+3*(side==1)+i,mat)
                    uv_layers(ob.data); wisps.append(ob.name)
        return {'source_precedes_rejected_lifts':True,'new_front_sweeps':[], 'temple_edge_locks':wisps,
                'continuous_sculpted_sweeps':3,'moved_hair_vertices':moved,'temple_tip_and_upper_uv_cleanup':repair,
                'face_skin_or_controls_changed':False,'rear_style':'PROVISIONAL_RETAINED'}
    newmat=art_material(); names=[]
    artpaths=[[(478,316,0),(423,282,0),(355,330,0),(296,417,0),(270,495,0),(280,558,0),(292,604,0)],
              [(483,269,0),(433,242,0),(370,281,0),(307,361,0),(276,439,0),(275,521,0)],
              [(483,225,0),(449,218,0),(388,264,0),(324,334,0),(290,414,0),(273,488,0)]]
    for side in (-1,1):
        for layer in range(3):
            pts=guide(layer,side); fitted=[]
            for k, point in enumerate(pts):
                co=Vector(point); hit,n,_,_=tree.ray_cast(origin,(co-origin).normalized())
                if hit is None: raise ValueError('Skull projection missed')
                f=k/(len(pts)-1)
                lift=.015+.075*math.sin(math.pi*f)**.7
                fitted.append(warp(*(hit+n*lift),candidate))
            ob=lock(fitted,.135+.025*layer,.052,200+3*(side==1)+layer,newmat)
            art=ob.data.uv_layers['HairArt']
            for loop in ob.data.loops:
                vi=loop.vertex_index
                t=(vi//20+1)/84 if vi<1660 else (0 if vi==1660 else 1)
                u=(vi%20)/20 if vi<1660 else .5
                px,py,_=spline(artpaths[layer],t)
                px+=(u-.5)*(24-9*t)
                if side==1: px=976-px
                art.data[loop.index].uv=(px/955,1-py/1647)
            names.append(ob.name)
    return {'source_precedes_rejected_lifts':True,'new_front_sweeps':names,'moved_hair_vertices':moved,
            'face_skin_or_controls_changed':False,'rear_style':'PROVISIONAL_RETAINED'}


def run(job):
    out=validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection(); info=build(job['candidate'],job['operation'] in ('repair','package') and job['candidate']==3); visibility(); assert protection()==before
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
            'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,'changes':info,
            'clothing_rendered':False,'director_acceptance':'PENDING','hair_motion_qualified':False}
    if job['operation']=='package':
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
        native=out/'hair-framing.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['fresh_reopen_protected_exact']=protection()==before
        assert result['fresh_reopen_protected_exact']; result['native_sha256']=digest(native)
    assert protection()==before and digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
