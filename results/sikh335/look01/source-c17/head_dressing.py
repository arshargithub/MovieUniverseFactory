"""Bounded static head dressing handler. No job-supplied code or asset paths."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'cleanup-portable-01/head-baked.blend'
HASH = '51e2a3d4c9df966e44f6a217d3535115bf19eef8e7ef9561cf6da75dc0ebd9b4'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'output_name'} or job['operation'] != 'static_dressing':
        raise ValueError('Unsupported job')
    name = job['output_name']
    if not isinstance(name, str) or not name.startswith('dressing-') or len(name)>64 or not all(c.isalnum() or c=='-' for c in name):
        raise ValueError('Invalid output')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=HASH:
        raise ValueError('Source changed')
    out = BASE/name
    if out.exists():
        raise ValueError('Refusing overwrite')
    return out


def hood_point(t, depth):
    angle = t*math.pi/2
    x = 1.13*math.sin(angle)
    z = 1.52*math.cos(angle)
    if abs(t)>1:
        x = math.copysign(1.13+.16*(abs(t)-1),t)
        z = -1.65*(abs(t)-1)
    fold = .035*math.sin(19*t+depth*4)*(.3+depth)
    return (x*(1-.85*depth*depth)+fold, -.20+1.35*depth, z*(1-.70*depth*depth))


def run(job):
    out = validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest, render_views
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    head = bpy.data.objects['FBHead']; before = geometry_digest(head)
    # Inventory before any dressing: eye and blink prerequisites, not animation.
    inventory = {'objects': [{'name':o.name,'type':o.type} for o in bpy.context.scene.objects],
                 'shape_keys': [k.name for k in head.data.shape_keys.key_blocks] if head.data.shape_keys else [],
                 'head_vertices':len(head.data.vertices), 'head_polygons':len(head.data.polygons)}
    verts = [hood_point(-2+4*i/80,j/16) for i in range(81) for j in range(17)]
    faces = [(i*17+j,(i+1)*17+j,(i+1)*17+j+1,i*17+j+1) for i in range(80) for j in range(16)]
    mesh=bpy.data.meshes.new('MF_indigo_drape_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    scarf=bpy.data.objects.new('MF_indigo_headscarf',mesh); bpy.context.scene.collection.objects.link(scarf)
    for p in mesh.polygons: p.use_smooth=True
    solid=scarf.modifiers.new('Cloth thickness','SOLIDIFY'); solid.thickness=.018
    mat=bpy.data.materials.new('MF_indigo_cloth'); mat.use_nodes=True
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bsdf=nodes.get('Principled BSDF'); bsdf.inputs['Roughness'].default_value=.95
    noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=22; noise.inputs['Detail'].default_value=2
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.008,.019,.05,1)
    ramp.color_ramp.elements[1].color=(.045,.09,.20,1)
    links.new(noise.outputs['Fac'],ramp.inputs[0]); links.new(ramp.outputs[0],bsdf.inputs['Base Color'])
    mesh.materials.append(mat)
    # A separate static shoulder wrap closes the bust; no cloth simulation.
    wrapverts=[]
    for i in range(41):
        x=-1.5+3*i/40
        for j in range(9):
            t=j/8
            wrapverts.append((x*(1+.08*t),-.72+.22*x*x+.045*math.sin(j*2+i*.17),
                              -1.10+.15*x+.10*x*x-1.5*t))
    wrapfaces=[(i*9+j,(i+1)*9+j,(i+1)*9+j+1,i*9+j+1) for i in range(40) for j in range(8)]
    wm=bpy.data.meshes.new('MF_wrap_mesh'); wm.from_pydata(wrapverts,[],wrapfaces); wm.update()
    wrap=bpy.data.objects.new('MF_shoulder_wrap',wm); scene_collection=bpy.context.scene.collection
    scene_collection.objects.link(wrap); wm.materials.append(mat)
    for p in wm.polygons: p.use_smooth=True
    wrap.modifiers.new('Cloth thickness','SOLIDIFY').thickness=.018
    # Separate dark-chestnut side locks; scalp portrait remains a provisional cap.
    hair=bpy.data.materials.new('MF_chestnut_locks'); hair.use_nodes=True
    hair.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.028,.013,.007,1)
    hair.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
    for sign in [-1,1]:
        for k in range(5):
            curve=bpy.data.curves.new('MF_hair_lock','CURVE'); curve.dimensions='3D'
            curve.bevel_depth=.014+.002*k; curve.bevel_resolution=2
            spline=curve.splines.new('BEZIER'); spline.bezier_points.add(4)
            for i,p in enumerate(spline.bezier_points):
                t=i/4
                p.co=(sign*(.77+.025*k+.045*math.sin(t*5+k)), -.20+.18*t-.015*k,
                      .75-1.85*t)
                p.handle_left_type='AUTO'; p.handle_right_type='AUTO'; p.radius=1-.85*t
            lock=bpy.data.objects.new('MF_side_lock',curve); scene_collection.objects.link(lock)
            curve.materials.append(hair)
    scene=bpy.context.scene; camera=scene.camera; camera.data.ortho_scale=4.4
    render_views(scene,camera,out,'dressed')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-dressed.blend'))
    assert geometry_digest(head)==before
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==HASH
    (out/'result.json').write_text(json.dumps({'source_sha256':HASH,'head_geometry_preserved':True,
        'inventory':inventory,'scope':'Static indigo drape blockout; not final cloth/hair or motion'},indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One job file required')
    run(json.loads(Path(args[0]).read_text()))
