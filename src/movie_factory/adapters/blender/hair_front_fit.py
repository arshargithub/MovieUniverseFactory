"""Reference-led front edge/scalp fit; pinned non-hair state is immutable."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'hairflow-package-06/hair-flow.blend'
SOURCE_SHA='ab3e7d974d9495733866eebbc687a51182e71b0284d69f40a05b133b990b0ccd'
REFBASE=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES={
 'frontal-v02-individualized.png':'7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
 'portrait-v07-individualized.png':'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def smooth(t):
    t=max(0.,min(1.,t)); return t*t*(3-2*t)


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview','package') or type(job['candidate']) is not int or job['candidate'] not in (1,2,3):
        raise ValueError('Unsupported fixed operation')
    for p,h in [(SOURCE,SOURCE_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p)!=h: raise ValueError('Pinned input changed')
    out=BASE/f'frontfit-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve(): raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free<5_000_000_000: raise ValueError('Disk low')
    if job['operation']=='package':
        p=BASE/f'frontfit-preview-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file(): raise ValueError('Preview required')
        r=json.loads(p.read_text())
        if r.get('handler_sha256')!=digest(Path(__file__)) or not r.get('protected_exact') or not r.get('rear_geometry_exact'):
            raise ValueError('Stale preview or failed protection')
    return out


def weights(x,y,z,candidate):
    front=1-smooth((y+.55)/.65)
    opening=smooth((z+.05)/.30)*(1-smooth((z-1.02)/.38))
    # Local rise of the frontal edge; upper crown and rear stay in place.
    lift=(.17+.05*math.exp(-((abs(x)-.43)/.25)**2))*front*opening
    if candidate==3:
        # Matched face-scale reference: higher central apex, retained side
        # framing. A broad uniform opening reproduced the receded-cap error.
        lift=(.115*math.exp(-((x-.025)/.255)**2)-.085*math.exp(-((abs(x)-.50)/.22)**2))*front*opening
    rim=math.exp(-((z-(.94-.65*abs(x)**1.5))/.23)**2)
    fit=front*smooth((z-.08)/.30)*(1-smooth((z-1.15)/.35))*(.32+.36*rim)
    return lift,fit


def rear_signature():
    import bpy
    return hashlib.sha256(repr([(ob.name,tuple(tuple(v.co) for v in ob.data.vertices))
        for ob in sorted(bpy.context.scene.objects,key=lambda o:o.name)
        if ob.type=='MESH' and ob.name.startswith('MF_illustrated_hair_lock_') and not ob.hide_render]).encode()).hexdigest()


def frontal_boundary(tree,body):
    """World-space visibility estimate, not an aesthetic likeness score."""
    from mathutils import Vector
    result={}
    for x in (-.65,-.40,0.,.40,.65):
        found=None
        for j in range(151):
            z=.15+j*.01
            h,_,_,_=tree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
            b,_,_,_=body.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
            if h is not None and b is not None and h.y<b.y-.001:
                found=round(z,3); break
        result[str(x)]=found
    return result


def build(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    base=bpy.data.objects['MF_sculpt_hair_support']
    body=bpy.data.objects['MF_continuous_head_neck']
    deps=bpy.context.evaluated_depsgraph_get()
    bodytree=BVHTree.FromObject(body,deps)
    before=frontal_boundary(BVHTree.FromObject(base,deps),bodytree)
    origin=Vector((0,0,.3)); moved=0; maximum=0.; misses=0
    for v in base.data.vertices:
        old=v.co.copy(); lift,fit=weights(*old,candidate)
        if abs(lift)<1e-8 and fit<1e-8: continue
        target=old+Vector((0,0,lift))
        # Follow actual forehead curvature. These rays are frontal, above ears;
        # body and all accepted anatomy remain read-only.
        a,_,_,_=bodytree.ray_cast(origin,(old-origin).normalized())
        b,_,_,_=bodytree.ray_cast(origin,(target-origin).normalized())
        if a is None or b is None:
            misses+=1; continue
        offset=(old-origin).length-(a-origin).length
        offset=offset*(1-fit)
        target=origin+(target-origin).normalized()*((b-origin).length+offset)
        if candidate>=2:
            # Soften the artificial heart-shaped notch at the upper part,
            # without translating the hairstyle or lowering the front edge.
            target.z+=.047*math.exp(-(old.x/.115)**2)*smooth((old.z-1.20)/.18)*(1-smooth((old.y-.1)/.4))
        maximum=max(maximum,(target-old).length); v.co=target; moved+=1
    base.data.update(); bpy.context.view_layer.update()
    if misses>100: raise ValueError('Frontal fitting missed too many head rays')
    after=frontal_boundary(BVHTree.FromObject(base,bpy.context.evaluated_depsgraph_get()),bodytree)
    wisps=[]
    if candidate>=2:
        tree=BVHTree.FromObject(base,bpy.context.evaluated_depsgraph_get())
        mat=bpy.data.materials.new('MF_front_edge_fine_hair'); mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(.021,.0085,.0038,1)
        p.inputs['Roughness'].default_value=.77; p.inputs['Specular IOR Level'].default_value=.10
        for side in (-1,1):
            for i in range(12):
                x=side*(.11+i*.052+.009*math.sin(i*1.7))
                edge=None
                for j in range(150):
                    z=.2+j*.01
                    h,_,_,_=tree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
                    b,_,_,_=bodytree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
                    if h is not None and b is not None and h.y<b.y-.001:
                        edge=z; break
                if edge is None: raise ValueError('Fine edge location missed')
                curve=bpy.data.curves.new(f'MF_hair_front_edge_{side}_{i}','CURVE')
                curve.dimensions='3D'; curve.resolution_u=2; curve.bevel_resolution=2
                curve.bevel_depth=.0015+.0005*((i%3)/2)
                spline=curve.splines.new('POLY'); spline.points.add(8)
                for j,point in enumerate(spline.points):
                    t=j/8; px=x+side*.025*t; pz=edge+.065-(.084+.015*math.sin(i*1.9))*t
                    h,_,_,_=tree.ray_cast(Vector((px,-3,pz)),Vector((0,1,0)))
                    b,_,_,_=bodytree.ray_cast(Vector((px,-3,pz)),Vector((0,1,0)))
                    if b is None: raise ValueError('Fine edge skin projection missed')
                    py=min(h.y,b.y) if h is not None else b.y
                    point.co=(px,py-.0015,pz,1); point.radius=(1-t)**.65
                ob=bpy.data.objects.new(curve.name,curve); bpy.context.scene.collection.objects.link(ob)
                curve.materials.append(mat); wisps.append(ob.name)
    return {'moved_front_hair_vertices':moved,'maximum_vertex_shift':maximum,'missed_rays':misses,
            'frontal_visible_hair_boundary_before':before,'frontal_visible_hair_boundary_after':after,
            'boundary_measurement':'World Z, orthographic frontal raycast, .01 sampling; not a reference likeness metric',
            'fine_edge_strands':wisps,'face_or_skin_changed':False,'new_texture_or_provider_calls':False}


def run(job):
    out=validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection(); rear=rear_signature(); info=build(job['candidate']); visibility()
    assert protection()==before and rear_signature()==rear
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
            'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,
            'rear_geometry_exact':rear_signature()==rear,'changes':info,
            'clothing_rendered':False,'director_acceptance':'PENDING','hair_motion_qualified':False}
    if job['operation']=='package':
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
        native=out/'hair-front-fit.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['fresh_reopen_protected_exact']=protection()==before and rear_signature()==rear
        assert result['fresh_reopen_protected_exact']; result['native_sha256']=digest(native)
    assert protection()==before and rear_signature()==rear and digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
