"""Fixed offline source-representation controls; not a production actor builder."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
SOURCE = ROOT / '.runtime/art-direction/series01-trellis298/head512/source.blend'
OUT = ROOT / '.runtime/art-direction/series01-trellis298'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if type(job) is not dict or set(job) != {'operation'} or job['operation'] not in ('smooth', 'remesh', 'dense', 'dense-remesh'):
        raise ValueError('Only fixed representation controls allowed')


def worker(job):
    import bpy
    import bmesh
    from trellis298_inspect import aim, snapshot
    validate(job)
    assert not bpy.app.online_access
    target = OUT / ('repair-' + job['operation'])
    target.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    obj = bpy.data.objects['geometry_0']
    if job['operation'].startswith('dense'):
        matrix = obj.matrix_world.copy()
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.wm.ply_import(filepath=str(OUT / 'dense-control/source-cluster.ply'))
        obj = bpy.context.object
        obj.name = 'Dense-source diagnostic'
        obj.matrix_world = matrix
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    before = snapshot()
    if not job['operation'].startswith('dense'):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
    # Drop imported split normals; preserve source UVs in the smooth control.
    if obj.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    if job['operation'] in ('remesh', 'dense-remesh'):
        mod = obj.modifiers.new('Coherent surface diagnostic', 'REMESH')
        mod.mode = 'VOXEL'
        mod.voxel_size = .003
        mod.use_smooth_shade = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod = obj.modifiers.new('Bounded surface relaxation', 'SMOOTH')
        mod.factor = .35
        mod.iterations = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.update()
    scene = bpy.context.scene
    camera = scene.camera
    views = [('front',0), ('left-quarter',45), ('right-quarter',315), ('back',180)]
    if job['operation'] == 'smooth':
        for name,degrees in views:
            a=math.radians(degrees)
            aim(camera,(2.5*math.sin(a),-2.5*math.cos(a),.04),(0,0,0))
            scene.render.filepath=str(target/(name+'.png'))
            assert 'FINISHED' in bpy.ops.render.render(write_still=True)
    clay = bpy.data.materials.get('Shape diagnostic only') or bpy.data.materials.new('Shape diagnostic only')
    clay.use_nodes = True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.36,.36,.36,1)
    clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .8
    bpy.context.view_layer.material_override=clay
    for name,degrees in views:
        a=math.radians(degrees)
        aim(camera,(2.5*math.sin(a),-2.5*math.cos(a),.04),(0,0,0))
        scene.render.filepath=str(target/(name+'-clay.png'))
        assert 'FINISHED' in bpy.ops.render.render(write_still=True)
    # The remesh has no valid UV/texture claim; deliberately save in clay.
    if job['operation']=='smooth':
        bpy.context.view_layer.material_override=None
    aim(camera,(0,-2.5,.04),(0,0,0))
    (target/'control.json').write_text(json.dumps({'source_sha256':sha(SOURCE),
        'before':before,'after':snapshot(),'operation':job['operation'],
        'production_ready':False,'limits':'Source representation diagnostic only; no rig, eye performance, cloth or body integration'},indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(target/'control.blend'))


def main(operation, packet_only=False):
    from movie_factory import production_knowledge as pk
    job={'operation':operation}
    validate(job)
    task=json.loads((ROOT/'results/trellis298/task.json').read_text())
    task.update(id='trellis298-representation-'+operation,phase='execution')
    for p in (Path(__file__),SOURCE,ROOT/'scripts/trellis298_inspect.py',ROOT/'results/trellis298/STRATEGY.md'):
        task['inputs'][str(p.relative_to(ROOT))]=sha(p)
    if operation.startswith('dense'):
        p = OUT / 'dense-control/source-cluster.ply'
        task['inputs'][str(p.relative_to(ROOT))] = sha(p)
    packet=pk.task_packet(ROOT,task)
    (ROOT/'results/trellis298'/('repair-'+operation+'-packet.json')).write_text(json.dumps(packet,indent=2))
    assert packet['dispatch_ready'],packet['blockers']
    if packet_only:
        print(pk.packet_markdown(packet))
        return
    target=OUT/('repair-'+operation)
    target.mkdir(exist_ok=True)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    with (target/'worker.log').open('w') as log:
        subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode',
            '--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),
            '--',json.dumps(job)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)


if __name__=='__main__':
    if '--' in sys.argv:
        worker(json.loads(sys.argv[sys.argv.index('--')+1]))
    else:
        import argparse
        p=argparse.ArgumentParser()
        p.add_argument('operation',choices=['smooth','remesh','dense','dense-remesh'])
        p.add_argument('--packet-only',action='store_true')
        a=p.parse_args()
        main(a.operation,a.packet_only)
