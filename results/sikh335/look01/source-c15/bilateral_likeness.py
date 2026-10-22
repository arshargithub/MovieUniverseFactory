"""Pinned comparison and one-sided cheek material repair. Geometry is protected."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'scarf-reconstruct-03/head-reconstruction-candidate.blend'
SHA='c61e0ea06ba7973e416fc2d3cbc78f929d2f491e06286f70292246a2cd1a59fc'


def mask(x,y,z):
    def smooth(t):
        t=max(0.,min(1.,t)); return t*t*(3-2*t)
    return smooth((x-.22)/.27)*smooth((.2-y)/.5)*smooth((z+.95)/.25)*smooth((.35-z)/.25)


def continuous_mask(x,y,z):
    """Avoid terminating the donor at the jaw edge or nasal-cheek junction."""
    def smooth(t):
        t=max(0.,min(1.,t));return t*t*(3-2*t)
    return smooth((x-.025)/.15)*smooth((.4-y)/.6)*smooth((z+1.7)/.25)*smooth((.45-z)/.30)


def jaw_infill_mask(x,y,z):
    """Bounded right-side albedo infill, away from lips, chin centre and ear."""
    def smooth(t):
        t=max(0.,min(1.,t));return t*t*(3-2*t)
    centre=-.77+.40*x
    band=max(0.,1-((z-centre)/.17)**2)**2
    return .6*smooth((x-.18)/.20)*smooth((.9-x)/.15)*smooth((-.10-y)/.35)*band


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','output_name'}:raise ValueError('Invalid job')
    if job['operation'] not in {'diagnose','repair'} or job['output_name'] not in {'bilateral-01','bilateral-02','bilateral-03','bilateral-04'}:raise ValueError('Unsupported operation/output')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SHA:raise ValueError('Source changed')
    out=BASE/job['output_name']
    if out.exists():raise ValueError('No overwrite')
    return out


def repair(obj,continuous=False,jaw_infill=False):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    mesh=obj.data; mesh.calc_loop_triangles()
    triangles=list(mesh.loop_triangles)
    tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(t.vertices) for t in triangles],all_triangles=True)
    primary=mesh.uv_layers.active; active_index=mesh.uv_layers.active_index
    uv=mesh.uv_layers.new(name='MF_left_cheek_donor_uv')
    weight=mesh.attributes.new(name='MF_right_cheek_blend',type='FLOAT',domain='POINT')
    residual=[]
    for v in mesh.vertices:
        w=(continuous_mask if continuous else mask)(*v.co);weight.data[v.index].value=w
        if w>.9:
            hit,_,_,distance=tree.find_nearest(Vector((-v.co.x,v.co.y,v.co.z)))
            residual.append(distance)
    for loop in mesh.loops:
        v=mesh.vertices[loop.vertex_index].co
        hit,_,idx,_=tree.find_nearest(Vector((-v.x,v.y,v.z)))
        tri=triangles[idx]
        points=[mesh.vertices[i].co for i in tri.vertices]
        coords=[Vector((*primary.data[i].uv,0)) for i in tri.loops]
        uv.data[loop.index].uv=barycentric_transform(hit,*points,*coords).xy
    mesh.uv_layers.active_index=active_index
    mat=obj.data.materials[0].copy();obj.data.materials[0]=mat
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    original=bsdf.inputs['Base Color'].links[0].from_socket
    image=next(n.image for n in nodes if n.type=='TEX_IMAGE' and n.image)
    tex=nodes.new('ShaderNodeTexImage');tex.image=image
    uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name=weight.name
    mix=nodes.new('ShaderNodeMixRGB');links.new(attr.outputs['Fac'],mix.inputs[0]);links.new(original,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2])
    links.new(mix.outputs[0],bsdf.inputs['Base Color'])
    if jaw_infill:
        jaw_uv=mesh.uv_layers.new(name='MF_jaw_infill_uv')
        jaw_weight=mesh.attributes.new(name='MF_jaw_infill_weight',type='FLOAT',domain='POINT')
        for v in mesh.vertices:jaw_weight.data[v.index].value=jaw_infill_mask(*v.co)
        for loop in mesh.loops:
            v=mesh.vertices[loop.vertex_index].co
            hit,_,idx,_=tree.find_nearest(Vector((-v.x,v.y,v.z+.12)))
            tri=triangles[idx]
            jaw_uv.data[loop.index].uv=barycentric_transform(hit,*[mesh.vertices[i].co for i in tri.vertices],*[Vector((*primary.data[i].uv,0)) for i in tri.loops]).xy
        mesh.uv_layers.active_index=active_index
        nearby=nodes.new('ShaderNodeTexImage');nearby.image=image
        mapping=nodes.new('ShaderNodeUVMap');mapping.uv_map=jaw_uv.name;links.new(mapping.outputs['UV'],nearby.inputs['Vector'])
        factor=nodes.new('ShaderNodeAttribute');factor.attribute_name=jaw_weight.name
        infill=nodes.new('ShaderNodeMixRGB');links.new(factor.outputs['Fac'],infill.inputs[0]);links.new(mix.outputs[0],infill.inputs[1]);links.new(nearby.outputs['Color'],infill.inputs[2]);links.new(infill.outputs[0],bsdf.inputs['Base Color'])
    return {'protected_side':'x<=0','continuous_nasal_jaw_mask':continuous,'max_mirrored_surface_distance':max(residual),
            'mean_mirrored_surface_distance':sum(residual)/len(residual),'sample_count':len(residual),'jaw_infill':jaw_infill}


def run(job):
    out=validate(job)
    import bpy
    from mathutils import Vector
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest,render_views
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead'];before=geometry_digest(head)
    shape_values={k.name:k.value for k in head.data.shape_keys.key_blocks} if head.data.shape_keys else {}
    scene=bpy.context.scene;camera=scene.camera
    render_views(scene,camera,out,'before')
    oldlights={}
    for name,x in [('MF_key',-3),('MF_fill',3)]:
        light=bpy.data.objects[name];oldlights[name]=(light.location.copy(),light.rotation_euler.copy(),light.data.energy,light.data.size)
        light.location=(x,-4,3);light.rotation_euler=(Vector((0,0,-.1))-light.location).to_track_quat('-Z','Y').to_euler()
        light.data.energy=300;light.data.size=5
    mat=head.data.materials[0]
    render_views(scene,camera,out,'balanced-before')
    clay=bpy.data.materials.new('MF_bilateral_clay');clay.use_nodes=True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.35,.35,.35,1)
    head.data.materials[0]=clay;render_views(scene,camera,out,'clay')
    head.data.materials[0]=mat
    report={'source_sha256':SHA,'geometry_before':before,'operation':job['operation']}
    if job['operation']=='repair':
        report['repair']=repair(head,job['output_name'] in {'bilateral-03','bilateral-04'},job['output_name']=='bilateral-04')
        render_views(scene,camera,out,'balanced-after')
    for name,(location,rotation,power,size) in oldlights.items():
        light=bpy.data.objects[name];light.location=location;light.rotation_euler=rotation;light.data.energy=power;light.data.size=size
    render_views(scene,camera,out,'review')
    report['geometry_after']=geometry_digest(head)
    assert report['geometry_after']==before
    report['shape_values']=shape_values
    assert shape_values==({k.name:k.value for k in head.data.shape_keys.key_blocks} if head.data.shape_keys else {})
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-bilateral.blend'))
    (out/'result.json').write_text(json.dumps(report,indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One job file required')
    run(json.loads(Path(args[0]).read_text()))
