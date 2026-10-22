"""Small posterior-only contour correction on the immutable anatomy-15 asset."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'neck-anatomy-build-15/character-upperbody.blend'
SOURCE_SHA='21c39b7215eddff50520621c7e8cc9184eb08915375617592d02e834caa0ebb6'


def smooth(t):
    t=max(0.,min(1.,t));return t**3*(10-15*t+6*t*t)


def weight(x,y,z):
    if not -1.45<z<-.50:return 0.
    radius=math.hypot(x,y-.1)
    if radius<.1:return 0.
    rear=(y-.1)/radius
    return math.sin(math.pi*(z+1.45)/.95)**4*smooth((rear+.12)/.75)*smooth((y-.02)/.16)


def point(x,y,z,candidate):
    w=weight(x,y,z)
    if w==0:return x,y,z
    radius=math.hypot(x,y-.1)
    strength={16:.045,17:.065,18:.080}[candidate]
    scale=(radius-strength*w)/radius
    return x*scale,.1+(y-.1)*scale,z


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:raise ValueError('Exact job keys required')
    if job['operation'] not in ('build','verify','raking') or type(job['candidate']) is not int or job['candidate'] not in (16,17,18):raise ValueError('Unsupported job')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('Pinned source changed')
    out=BASE/f'posterior-neck-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Existing output or disk low')
    return out


def invariants(indices):
    import bpy
    from neck_anatomy_review import signature
    from hijab_donor import material_signature
    ob=bpy.data.objects['MF_continuous_head_neck'];mesh=ob.data
    def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    return {'protected_vertices':digest([(i,list(mesh.vertices[i].co)) for i in indices]),
            'all_z':digest([v.co.z for v in mesh.vertices]),
            'topology':digest([list(p.vertices) for p in mesh.polygons]),
            'all_uvs':digest([[list(p.uv) for p in layer.data] for layer in mesh.uv_layers]),
            'materials':[material_signature(m) for m in mesh.materials],
            'other_objects':{o.name:signature(o) for o in bpy.context.scene.objects if o.type in ('MESH','CURVE') and o!=ob}}


def run(job):
    out=validate(job)
    import bpy
    from mathutils import Vector
    from neck_anatomy_review import clay,mesh_diagnostics,profiles
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck']
    indices=[v.index for v in ob.data.vertices if weight(*v.co)==0]
    baseline=invariants(indices);out.mkdir()
    result={'job':job,'source_sha256':SOURCE_SHA,'handler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'director_accepted':False,'scope':'Static posterior neck contour only; not full-body or motion qualification',
        'protected_vertex_count':len(indices),
        'posterior_scope':'z=-0.50..-1.45; y>0.02 and rear cosine > -0.12; compact C3 vertical and C2 angular falloff. Includes nape above earlier horizontal guard; anterior face/jaw, throat, collarbones and lower shoulders excluded.'}
    if job['operation']=='build':
        moved=[]
        for v in ob.data.vertices:
            old=v.co.copy();v.co=point(*old,job['candidate'])
            if (v.co-old).length>1e-8:moved.append((v.co-old).length)
        ob.data.update();bpy.context.view_layer.update()
        assert invariants(indices)==baseline,'Protected source state changed'
        result['edited_vertices']=len(moved);result['max_displacement']=max(moved)
        native=out/'character-upperbody.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
    else:
        folder=BASE/f'posterior-neck-build-{job["candidate"]:02}'
        native=folder/'character-upperbody.blend';record=json.loads((folder/'result.json').read_text())
        if hashlib.sha256(native.read_bytes()).hexdigest()!=record['native_sha256']:raise ValueError('Saved native changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        assert invariants(indices)==baseline,'Protected state changed on reopen'
    result['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
    result['protected_state_pass']=True
    result['invariants']=baseline
    result['mesh_diagnostics']=mesh_diagnostics()
    assert not result['mesh_diagnostics']['inward_faces'] and not result['mesh_diagnostics']['tiny_faces']
    result['packed_images']=[{'name':im.name,'packed':bool(im.packed_file or im.packed_files)} for im in bpy.data.images if im.source=='FILE']
    assert all(im['packed'] for im in result['packed_images'])
    result['sections']=profiles()
    if job['operation']=='build':clay(out)
    if job['operation']=='raking':clay(out,raking=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
