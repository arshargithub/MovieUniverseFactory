"""Fixed reference-led hairline lift. No accepted bust geometry/material edits."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'hair-finish-package-03/hair-refined.blend'
SOURCE_SHA='44234a6140baeaa03a7c9850ad7f58d8be86d54d244941bbe6153ca2cb3cf973'
REFBASE=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES={
 'frontal-v02-individualized.png':'7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
 'portrait-v07-individualized.png':'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview','package') or type(job['candidate']) is not int or job['candidate'] not in (1,2,3):
        raise ValueError('Unsupported operation')
    for p,h in [(SOURCE,SOURCE_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p)!=h: raise ValueError('Pinned input changed')
    out=BASE/f'hairline-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve(): raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free<5_000_000_000: raise ValueError('Disk low')
    if job['operation']=='package':
        p=BASE/f'hairline-preview-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file(): raise ValueError('Preview required')
        r=json.loads(p.read_text())
        if r.get('handler_sha256')!=digest(Path(__file__)) or not r.get('protected_exact'):
            raise ValueError('Stale preview or failed protection')
    return out


def smooth(t):
    t=max(0.,min(1.,t)); return t*t*(3-2*t)


def displacement(x,y,z,candidate):
    height=.15
    front=1-smooth((y+.55)/.50)
    vertical=smooth((z+.05)/.45)*(1-smooth((z-.90)/.5))
    return height*front*vertical


def crown_flow(x,y,z):
    back=math.atan2(x,y)/(2*math.pi)
    front=math.copysign(.5-(1.4-z-.70*abs(x)**1.5)*.23,x)
    weight=smooth((y+.20)/.70)
    return front*(1-weight)+back*weight


def build(candidate):
    import bpy
    from mathutils import Vector
    from hair_volume_sculpt import skull_surface
    from hair_anatomy_refinement import is_hair
    tree=skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    origin=Vector((0,0,.3)); moved=0; maximum=0
    for ob in bpy.context.scene.objects:
        if not is_hair(ob): continue
        ob.hide_set(ob.hide_render)
        if ob.hide_render or ob.type!='MESH': continue
        for v in ob.data.vertices:
            old=v.co.copy(); dz=displacement(*old,candidate)
            if dz<1e-8: continue
            target=old+Vector((0,0,dz))
            # Follow the immutable skull curvature while preserving the old
            # radial stand-off; all overlapping hair sheets share this map.
            a,_,_,_=tree.ray_cast(origin,(old-origin).normalized())
            b,_,_,_=tree.ray_cast(origin,(target-origin).normalized())
            if a is not None and b is not None:
                offset=(old-origin).length-(a-origin).length
                target=origin+(target-origin).normalized()*((b-origin).length+offset)
            maximum=max(maximum,(target-old).length); v.co=target; moved+=1
        ob.data.update()
        uv=ob.data.uv_layers.get('HairFlow')
        if uv:
            for loop in ob.data.loops:
                x,y,z=ob.data.vertices[loop.vertex_index].co
                weight=smooth((z-.45)/.5)*(1-smooth((y+.55)/.25))
                uv.data[loop.index].uv.x=uv.data[loop.index].uv.x*(1-weight)+crown_flow(x,y,z)*weight
    mat=bpy.data.materials['MF_refined_hair_painted_flow']
    for node in mat.node_tree.nodes:
        if node.bl_idname=='ShaderNodeMapRange':
            node.interpolation_type='SMOOTHSTEP'
            if abs(node.inputs['From Min'].default_value-1.10)<.001:
                node.inputs['From Min'].default_value=.96
                node.inputs['From Max'].default_value=1.25
    return {'moved_hair_vertices':moved,'maximum_vertex_shift':maximum,
            'nominal_front_lift':.15,
            'reference_uv_unchanged':True,'face_skin_or_controls_changed':False,
            'rear_style':'PROVISIONAL_PREVIOUS_WAVES_RETAINED'}


def run(job):
    out=validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection(); info=build(job['candidate']); visibility(); assert protection()==before
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
            'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,'changes':info,
            'clothing_rendered':False,'director_acceptance':'PENDING','hair_motion_qualified':False}
    if job['operation']=='package':
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
        native=out/'hair-raised.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
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
